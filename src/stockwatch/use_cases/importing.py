"""Here are all the use cases related to importing data from the DeGiro exported
files."""
import csv
from datetime import date, datetime, timedelta
from typing import Any

from stockwatch.entities import (
    CurrencyExchange,
    IsinStr,
    PortfoliosDictionary,
    SharePortfolio,
    SharePosition,
    ShareTransaction,
    ShareTransactionKind,
    apply_transactions,
    to_portfolios,
)

from . import stockdir


def _process_buy_transaction_row(
    transaction_datetime: datetime,
    isin: IsinStr,
    row: dict[str, str],
) -> ShareTransaction:
    descr = row["Omschrijving"].split()
    key_index = descr.index("Koop")
    nr_stocks = float(descr[key_index + 1].replace(",", "."))
    price = float(descr[key_index + 3].replace(",", "."))
    curr = row["Mutatie"]
    return ShareTransaction(
        transaction_datetime, isin, curr, nr_stocks, price, ShareTransactionKind.BUY
    )


def _process_sell_transaction_row(
    transaction_datetime: datetime,
    isin: IsinStr,
    row: dict[str, str],
) -> ShareTransaction:
    descr = row["Omschrijving"].split()
    key_index = descr.index("Verkoop")
    nr_stocks = float(descr[key_index + 1].replace(",", "."))
    price = float(descr[key_index + 3].replace(",", "."))
    curr = row["Mutatie"]
    return ShareTransaction(
        transaction_datetime,
        isin,
        curr,
        nr_stocks,
        price,
        ShareTransactionKind.SELL,
    )


def _process_dividend_transaction_row(
    transaction_datetime: datetime,
    isin: IsinStr,
    row: dict[str, str],
) -> ShareTransaction:
    amount = float(row["Bedrag"].replace(",", "."))
    curr = row["Mutatie"]
    return ShareTransaction(
        transaction_datetime,
        isin,
        curr,
        1,
        amount,
        ShareTransactionKind.DIVIDEND,
    )


def _process_valuta_exchange_row(row: dict[str, str]) -> CurrencyExchange:
    exchange_rate = float(row["FX"].replace(",", "."))
    date_time_str = row["Datum"] + ";" + row["Tijd"]
    exchange_datetime = datetime.strptime(date_time_str, "%d-%m-%Y;%H:%M")
    curr_from = row["Mutatie"]
    value_from = round(float(row["Bedrag"].replace(",", ".")), 2)
    return CurrencyExchange(exchange_datetime, exchange_rate, value_from, curr_from)


def _process_transaction_row(
    transaction_datetime: datetime,
    isin: IsinStr,
    row: dict[str, str],
) -> ShareTransaction | None:
    descr = row["Omschrijving"].split()

    if "Koop" in descr:
        return _process_buy_transaction_row(
            transaction_datetime=transaction_datetime,
            isin=isin,
            row=row,
        )
    if "Verkoop" in descr:
        return _process_sell_transaction_row(
            transaction_datetime=transaction_datetime,
            isin=isin,
            row=row,
        )
    if "Dividend" in descr:
        return _process_dividend_transaction_row(
            transaction_datetime=transaction_datetime,
            isin=isin,
            row=row,
        )
    return None


def process_transactions(isins: set[IsinStr]) -> tuple[ShareTransaction, ...]:
    """Get a list of all the transactions from the CSV files in the account folder.

    The csv files should be formatted as done by De Giro and should named as follows:
    yymmdd_Account.csv, where the date is from the Einddatum that was selected.
    """
    transactions_file = stockdir.get_account_report_file()

    if not transactions_file.is_file():
        print(f"No transactions file can be found at: {transactions_file}")
        return tuple()

    exchanges: list[CurrencyExchange] = []
    transactions: list[ShareTransaction] = []
    with transactions_file.open(mode="r") as csv_file:
        contents = csv_file.readlines()
        # headers are missing for columns with the transaction amount
        # and the balance; modify contents[0] here to include header for amount
        contents[0] = contents[0].replace("Mutatie,,", "Mutatie,Bedrag,")
        csv_reader = csv.DictReader(contents)
        # first collect valuta transactions
        for row in reversed(list(csv_reader)):
            if row["Omschrijving"] == "Valuta Debitering" and row["Bedrag"][0] == "-":
                exchanges.append(_process_valuta_exchange_row(row))
        print(f"{exchanges}")
        for row in reversed(list(csv_reader)):
            # we're only interested in real stock positions (not cash)
            if (isin := IsinStr(row["ISIN"])) in isins:
                date_time_str = row["Datum"] + ";" + row["Tijd"]
                transaction_datetime = datetime.strptime(
                    date_time_str, "%d-%m-%Y;%H:%M"
                )

                transaction = _process_transaction_row(
                    transaction_datetime=transaction_datetime,
                    isin=isin,
                    row=row,
                )

                if transaction is not None:
                    transactions.append(transaction)
    return tuple(transactions)


def _to_share_position(
    position_date: date, position_row: dict[str | Any, str | Any]
) -> SharePosition:
    isin = IsinStr(position_row["Symbool/ISIN"])
    name = position_row["Product"]
    curr = position_row["Lokale waarde"].split()[0]
    nr_stocks = float(position_row["Aantal"].replace(",", "."))
    price = round(float(position_row["Slotkoers"].replace(",", ".")), 2)
    value = round(float(position_row["Waarde in EUR"].replace(",", ".")), 2)
    # investment and realization will be set via transactions
    return SharePosition(
        position_date=position_date,
        value=value,
        isin=isin,
        name=name,
        curr=curr,
        investment=0.0,
        nr_stocks=nr_stocks,
        price=price,
        realized=0.0,
    )


def process_portfolios() -> tuple[set[IsinStr], PortfoliosDictionary]:
    """Create the dated portfolios from the Portfolio csv's found in the portfolio folder.

    The csv files should be formatted as done by De Giro and should named as follows:
    yymmdd_Portfolio.csv
    """
    share_portfolio_data: PortfoliosDictionary = {}
    all_isins: set[IsinStr] = set()

    # start with the oldest and work towards the newest portfolios
    previous_date = None
    for file_path in sorted(stockdir.get_portfolio_folder().glob("*.csv")):
        file_date = datetime.strptime(file_path.name[:6], "%y%m%d").date()
        if file_date in share_portfolio_data:
            print(
                f"Error: multiple files with date {file_date}, this will lead to errors."
            )
        share_positions = {}
        isins_in_file: set[IsinStr] = set()
        with file_path.open(mode="r") as csv_file:
            for row in csv.DictReader(csv_file):
                # we're only interested in real stock positions (not cash)
                if isin := IsinStr(row["Symbool/ISIN"]):
                    isins_in_file.add(isin)
                    the_position = _to_share_position(file_date, row)
                    if not isin in all_isins:
                        # create empty positions for all previous portfolios
                        for spf_date, previous_spf in share_portfolio_data.items():
                            previous_spf[isin] = SharePosition.empty_position(
                                position_date=spf_date,
                                isin=isin,
                                name=the_position.name,
                            )
                        all_isins.add(isin)
                    share_positions[isin] = the_position
        if previous_date:
            # add empty positions for isins that are no longer present
            for sold_isin in all_isins - isins_in_file:
                sold_name = share_portfolio_data[previous_date][sold_isin].name
                share_positions[sold_isin] = SharePosition.empty_position(
                    position_date=file_date, isin=sold_isin, name=sold_name
                )

        share_portfolio_data[file_date] = share_positions
        previous_date = file_date

    return all_isins, share_portfolio_data


def _get_first_valid_price(
    prices: dict[date, float], price_date: date, limit: int = 10
) -> float | None:
    for i in range(limit):
        if price := prices.get(price_date + timedelta(days=i)):
            return price
    return None


def _determine_index_values(
    transactions: tuple[ShareTransaction, ...],
    index_name: str,
    index_date: date,
    index_prices: dict[date, float],
) -> SharePosition | None:
    invested = 0.0
    realized = 0.0
    nr_stocks = 0.0

    for transaction in transactions:
        if transaction.transaction_datetime.date() > index_date:
            continue
        if transaction.kind == ShareTransactionKind.DIVIDEND:
            continue

        if transaction.curr != "EUR":
            print(
                f"Ignored transaction because the currency '{transaction.curr}'"
                f" is not in Euros"
            )
            continue

        if not (
            index_price := _get_first_valid_price(
                index_prices, transaction.transaction_datetime.date()
            )
        ):
            continue

        value = transaction.nr_stocks * transaction.price
        index_change = value / index_price

        if transaction.kind == ShareTransactionKind.BUY:
            nr_stocks += index_change
            invested += value
        elif transaction.kind == ShareTransactionKind.SELL:
            nr_stocks -= index_change
            realized += value
        else:
            # Ignore the other types for now...
            continue

    if price := _get_first_valid_price(index_prices, index_date):
        return SharePosition(
            position_date=index_date,
            value=nr_stocks * price,
            isin=IsinStr(index_name),
            name=index_name.replace("_", " "),
            curr="EUR",
            nr_stocks=nr_stocks,
            price=price,
            investment=invested,
            realized=realized,
        )
    return None


def process_indices(
    indices: dict[str, dict[date, float]],
    transactions: tuple[ShareTransaction, ...],
    dates: list[date],
) -> list[tuple[SharePosition, ...]]:
    """Create the positions for the indices in the dict, given the transactions done."""
    ret_val = []

    for index_name, index_prices in indices.items():
        index_positions = []

        for position_date in dates:
            if new_pos := _determine_index_values(
                transactions, index_name, position_date, index_prices
            ):
                index_positions.append(new_pos)

        ret_val.append(tuple(index_positions))

    return ret_val


def process_index_prices() -> dict[str, dict[date, float]]:
    """Read in all the index prices from the index folder."""
    files = stockdir.get_indices_folder().glob("*.csv")

    ret_val: dict[str, dict[date, float]] = {}

    for index_file in files:
        with index_file.open(mode="r") as csv_file:
            contents = csv_file.readlines()
        prices = csv.DictReader(contents)

        ret_val[index_file.name[:-4]] = {
            datetime.strptime(r["Date"], "%Y-%m-%d").date(): float(r["Close"])
            for r in prices
        }

    return ret_val


def get_portfolios_index_positions() -> tuple[
    tuple[SharePortfolio, ...], list[tuple[SharePosition, ...]]
]:
    """Return all portfolios and equivalent index positions."""
    # first get the positions (investment and returns both equal 0.0)
    all_isins, spfdict = process_portfolios()

    # second get the transactions
    transactions = process_transactions(all_isins)

    # TODO: third determine exchange rate and apply to transactions

    # fourth apply transactions to positions to determine investment and returns
    apply_transactions(transactions, spfdict)

    # fifth convert dicts to tuple with shareportfolios
    spfs = to_portfolios(spfdict)

    # TODO: implement the processing of index prices
    # indices = use_cases.process_index_prices()
    indices: list[tuple[SharePosition, ...]] = []

    return spfs, indices
