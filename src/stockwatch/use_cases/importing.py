"""Here are all the use cases related to importing data from the DeGiro exported
files."""
import csv
from datetime import date, datetime, timedelta
from typing import Any

from stockwatch.entities.money import Amount, CurrencyExchange
from stockwatch.entities.shares import (
    PortfoliosDictionary,
    SharePortfolio,
    SharePosition,
    apply_transactions,
    to_portfolios,
)
from stockwatch.entities.transactions import (
    CashSettlement,
    IsinStr,
    ShareTransaction,
    ShareTransactionKind,
)

from . import stockdir


def apply_exchange(
    transaction_datetime: datetime,
    amount: Amount,
    exchanges: list[CurrencyExchange],
) -> Amount:
    "Return the value in EUR by tracing the currency exchange that fits or 0.0 if there's no fit"
    if amount.curr == "EUR":
        return amount
    exchange_options = sorted(
        [
            curr_ex
            for curr_ex in exchanges
            if curr_ex.amount_from.curr == amount.curr
            and curr_ex.exchange_datetime > transaction_datetime
        ]
    )
    if not exchange_options:
        # no currency exchange found
        return Amount(0.0)
    for curr_exch in exchange_options:
        if curr_exch.can_take_exchange(amount):
            return curr_exch.take_exchange(amount)
    return Amount(0.0)


def _process_buy_transaction_row(
    transaction_datetime: datetime,
    isin: IsinStr,
    row: dict[str, str],
) -> ShareTransaction:
    descr = row["Omschrijving"].split()
    key_index = descr.index("Koop")
    nr_stocks = float(descr[key_index + 1].replace(",", "."))
    curr = row["Mutatie"]
    price = Amount(float(descr[key_index + 3].replace(",", ".")), curr)
    return ShareTransaction(
        transaction_datetime,
        isin,
        nr_stocks,
        price,
        ShareTransactionKind.BUY,
        nr_stocks * price,
    )


def _process_delisting_transaction_row(
    transaction_datetime: datetime,
    isin: IsinStr,
    row: dict[str, str],
    exchanges: list[CurrencyExchange],
    cash_settlements: list[CashSettlement],
) -> ShareTransaction:
    # we have a delisting-sell row, which unfortunately has no amount sold
    # (not due to exchanges, but because it is specified as 0)
    # the amount sold can be found in a cash settlement row
    # the cash settlement row can be specified in non-EUR, in which case we will apply the corresponding exchange

    # so far only a single example of delisting has been presented
    # this example is processed correctly
    # if more examples become available, correctness of the processing needs to be checked further
    descr = row["Omschrijving"].split()
    key_index = descr.index("Verkoop")
    nr_stocks = float(descr[key_index + 1].replace(",", "."))
    amount = Amount(0.0)
    # find the cash settlement for this delisting:
    for csh_sttlmnt in cash_settlements:
        if (
            csh_sttlmnt.isin == isin
            and csh_sttlmnt.settlement_date == transaction_datetime.date()
        ):
            amount = csh_sttlmnt.amount
            break
    else:
        print("No cash settlement found for DELISTING: {row}")

    if amount.curr != "EUR" and amount.value_exact != 0.0:
        amount = apply_exchange(
            transaction_datetime,
            amount,
            exchanges,
        )
    # our price is always in EUR
    price = amount * (1.0 / nr_stocks)

    return ShareTransaction(
        transaction_datetime,
        isin,
        nr_stocks,
        price,
        ShareTransactionKind.SELL,
        amount,
    )


def _process_sell_transaction_row(
    transaction_datetime: datetime,
    isin: IsinStr,
    row: dict[str, str],
    exchanges: list[CurrencyExchange],
) -> ShareTransaction:
    descr = row["Omschrijving"].split()
    key_index = descr.index("Verkoop")
    nr_stocks = float(descr[key_index + 1].replace(",", "."))
    curr = row["Mutatie"]
    price = Amount(float(descr[key_index + 3].replace(",", ".")), curr)
    amount = apply_exchange(transaction_datetime, nr_stocks * price, exchanges)

    return ShareTransaction(
        transaction_datetime,
        isin,
        nr_stocks,
        price,
        ShareTransactionKind.SELL,
        amount,
    )


def _process_dividend_transaction_row(
    transaction_datetime: datetime,
    isin: IsinStr,
    row: dict[str, str],
    exchanges: list[CurrencyExchange],
) -> ShareTransaction:
    curr = row["Mutatie"]
    price = Amount(float(row["Bedrag"].replace(",", ".")), curr)
    amount = apply_exchange(
        transaction_datetime,
        price,
        exchanges,
    )
    return ShareTransaction(
        transaction_datetime,
        isin,
        1,
        price,
        ShareTransactionKind.DIVIDEND,
        amount,
    )


def _process_expenses_row(
    transaction_datetime: datetime,
    isin: IsinStr,
    row: dict[str, str],
) -> ShareTransaction:
    # Expenses are always in EUR
    amount = Amount(float(row["Bedrag"].replace(",", ".")))
    return ShareTransaction(
        transaction_datetime,
        isin,
        1,
        amount,
        ShareTransactionKind.EXPENSES,
        amount,
    )


def _process_valuta_exchange_row(row: dict[str, str]) -> CurrencyExchange:
    rate = float(row["FX"].replace(",", "."))
    date_time_str = row["Datum"] + ";" + row["Tijd"]
    exchange_datetime = datetime.strptime(date_time_str, "%d-%m-%Y;%H:%M")
    curr = row["Mutatie"]
    amount_from = Amount(float(row["Bedrag"].replace(",", ".")), curr)
    return CurrencyExchange(exchange_datetime, rate, amount_from)


def _process_cash_settlement_row(
    row: dict[str, str],
) -> CashSettlement:
    date_time_str = row["Datum"] + ";" + row["Tijd"]
    settlement_datetime = datetime.strptime(date_time_str, "%d-%m-%Y;%H:%M")
    isin = IsinStr(row["ISIN"])
    curr = row["Mutatie"]
    amount = Amount(float(row["Bedrag"].replace(",", ".")), curr)
    return CashSettlement(settlement_datetime, isin, amount)


def _process_transaction_row(
    isin: IsinStr,
    row: dict[str, str],
    exchanges: list[CurrencyExchange],
    cash_settlements: list[CashSettlement],
) -> ShareTransaction | None:
    date_time_str = row["Datum"] + ";" + row["Tijd"]
    transaction_datetime = datetime.strptime(date_time_str, "%d-%m-%Y;%H:%M")

    descr = row["Omschrijving"].split()

    if "Koop" in descr:
        return _process_buy_transaction_row(
            transaction_datetime=transaction_datetime,
            isin=isin,
            row=row,
        )
    if "Verkoop" in descr:
        if "DELISTING:" in descr:
            return _process_delisting_transaction_row(
                transaction_datetime=transaction_datetime,
                isin=isin,
                row=row,
                exchanges=exchanges,
                cash_settlements=cash_settlements,
            )
        return _process_sell_transaction_row(
            transaction_datetime=transaction_datetime,
            isin=isin,
            row=row,
            exchanges=exchanges,
        )
    if "Dividend" in descr:
        return _process_dividend_transaction_row(
            transaction_datetime=transaction_datetime,
            isin=isin,
            row=row,
            exchanges=exchanges,
        )
    if "Transactiekosten" in descr:
        return _process_expenses_row(
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
    cash_settlements: list[CashSettlement] = []
    transactions: list[ShareTransaction] = []
    with transactions_file.open(mode="r") as csv_file:
        contents = csv_file.readlines()
        # headers are missing for columns with the transaction amount
        # and the balance; modify contents[0] here to include header for amount
        contents[0] = contents[0].replace("Mutatie,,", "Mutatie,Bedrag,")
        all_transactions = list(csv.DictReader(contents))
        # first collect valuta transactions and cash settlements
        for row in reversed(all_transactions):
            # Exchanges apply only for amounts first received in other currencies
            # and subsequently exchanged into EUR.
            # The exchange rate is found in lines labeled "Valuta Debitering"
            if row["Omschrijving"] == "Valuta Debitering" and row["Mutatie"] != "EUR":
                exchanges.append(_process_valuta_exchange_row(row))
            if row["Omschrijving"] == "Contante Verrekening Aandelen":
                cash_settlements.append(_process_cash_settlement_row(row))
        # then process dividend and stock transactions
        for row in reversed(all_transactions):
            # we're only interested in real stock positions (not cash)
            if (isin := IsinStr(row["ISIN"])) in isins:
                transaction = _process_transaction_row(
                    isin=isin,
                    row=row,
                    exchanges=exchanges,
                    cash_settlements=cash_settlements,
                )

                if transaction is not None:
                    transactions.append(transaction)
        unmatched_exchanges = [
            exch for exch in exchanges if exch.amount_trans_remaining.value != 0.0
        ]
        if unmatched_exchanges:
            print(f"The following exchanges are not matched: {unmatched_exchanges}")
    return tuple(transactions)


def _to_share_position(
    position_date: date, position_row: dict[str | Any, str | Any]
) -> SharePosition:
    isin = IsinStr(position_row["Symbool/ISIN"])
    name = position_row["Product"]
    curr = position_row["Lokale waarde"].split()[0]
    nr_stocks = float(position_row["Aantal"].replace(",", "."))
    price = Amount(float(position_row["Slotkoers"].replace(",", ".")), curr)
    value = Amount(float(position_row["Waarde in EUR"].replace(",", ".")))
    # investment and realization will be set via transactions
    return SharePosition(
        position_date=position_date,
        value=value,
        isin=isin,
        name=name,
        investment=Amount(0.0),
        nr_stocks=nr_stocks,
        price=price,
        realized=Amount(0.0),
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
                    if isin not in all_isins:
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
    invested = Amount(0.0)
    realized = Amount(0.0)
    nr_stocks = 0.0

    for transaction in transactions:
        if transaction.transaction_datetime.date() > index_date:
            continue
        if transaction.kind == ShareTransactionKind.DIVIDEND:
            continue

        if transaction.price.curr != "EUR":
            print(
                f"Ignored transaction because the currency '{transaction.price.curr}'"
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
        index_change = value.value_exact / index_price

        if transaction.kind == ShareTransactionKind.BUY:
            nr_stocks += index_change
            invested = invested + value
        elif transaction.kind == ShareTransactionKind.SELL:
            nr_stocks -= index_change
            realized = realized + value
        else:
            # Ignore the other types for now...
            continue

    if price := _get_first_valid_price(index_prices, index_date):
        return SharePosition(
            position_date=index_date,
            value=nr_stocks * Amount(price),
            isin=IsinStr(index_name),
            name=index_name.replace("_", " "),
            investment=invested,
            nr_stocks=nr_stocks,
            price=Amount(price),
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


def get_portfolios_index_positions() -> (
    tuple[tuple[SharePortfolio, ...], list[tuple[SharePosition, ...]]]
):
    """Return all portfolios and equivalent index positions."""
    # first get the positions (investment and returns both equal 0.0)
    all_isins, spfdict = process_portfolios()

    # second get the transactions
    transactions = process_transactions(all_isins)

    # third apply transactions to positions to determine investment and returns
    apply_transactions(transactions, spfdict)

    # fourth convert dicts to tuple with shareportfolios
    spfs = to_portfolios(spfdict)

    # TODO: implement the processing of index prices
    # indices = use_cases.process_index_prices()
    indices: list[tuple[SharePosition, ...]] = []

    return spfs, indices
