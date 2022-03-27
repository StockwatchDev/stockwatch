"""
This module contains the application logic for holding a stock portfolio with DeGiro.

This package has a clean architecture. Hence, this module should only depend on the
entities module (apart from plain Python).
"""
import csv
import time
from datetime import date, datetime, timedelta
from pathlib import Path

from .entities import (
    SharePortfolio,
    SharePosition,
    ShareTransaction,
    ShareTransactionKind,
)


def _process_buy_transaction_row(
    transaction_date: date,
    isin: str,
    row: dict[str, str],
) -> ShareTransaction:
    descr = row["Omschrijving"].split()
    key_index = descr.index("Koop")
    nr = round(float(descr[key_index + 1].replace(",", ".")))
    price = float(descr[key_index + 3].replace(",", "."))
    curr = row["Mutatie"]
    return ShareTransaction(
        ShareTransactionKind.BUY, isin, curr, nr, price, transaction_date
    )


def _process_sell_transaction_row(
    transaction_date: date,
    isin: str,
    row: dict[str, str],
) -> ShareTransaction:
    descr = row["Omschrijving"].split()
    key_index = descr.index("Verkoop")
    nr = round(float(descr[key_index + 1].replace(",", ".")))
    price = float(descr[key_index + 3].replace(",", "."))
    curr = row["Mutatie"]
    return ShareTransaction(
        ShareTransactionKind.SELL, isin, curr, nr, price, transaction_date
    )


def _process_dividend_transaction_row(
    transaction_date: date,
    isin: str,
    row: dict[str, str],
) -> ShareTransaction:
    amount = float(row["Bedrag"].replace(",", "."))
    curr = row["Mutatie"]
    return ShareTransaction(
        ShareTransactionKind.DIVIDEND, isin, curr, 1, amount, transaction_date
    )


def _process_transaction_row(
    transaction_date: date,
    isin: str,
    row: dict[str, str],
) -> ShareTransaction | None:
    descr = row["Omschrijving"].split()

    if "Koop" in descr:
        return _process_buy_transaction_row(
            transaction_date=transaction_date,
            isin=isin,
            row=row,
        )
    if "Verkoop" in descr:
        return _process_sell_transaction_row(
            transaction_date=transaction_date,
            isin=isin,
            row=row,
        )
    if "Dividend" in descr:
        return _process_dividend_transaction_row(
            transaction_date=transaction_date,
            isin=isin,
            row=row,
        )
    return None


def process_transactions(
    isins: set[str], folder: Path, rename: bool = True
) -> tuple[ShareTransaction, ...]:
    """
    Get a list of all the transactions from the CSV files in the account folder.

    The csv files should be formatted as done by De Giro and should named as follows:
    yymmdd_Account.csv, where the date is from the Einddatum that was selected.
    """
    account_folder = folder.joinpath("account")
    files = sorted(account_folder.glob("*.csv"))
    print(f"Number of files to process: {len(files)}")

    transactions: list[ShareTransaction] = []
    for file_path in files:
        with file_path.open(mode="r") as csv_file:
            contents = csv_file.readlines()
            # headers are missing for columns with the transaction amount
            # and the balance; modify contents[0] here to include header for amount
            contents[0] = contents[0].replace("Mutatie,,", "Mutatie,Bedrag,")
            csv_reader = csv.DictReader(contents)
            line_count = 0
            for row in reversed(list(csv_reader)):
                if line_count > 0:
                    isin = row["ISIN"]
                    # we're only interested in real stock positions (not cash)
                    if isin in isins:
                        transaction_date = datetime.strptime(
                            row["Datum"], "%d-%m-%Y"
                        ).date()

                        transaction = _process_transaction_row(
                            transaction_date=transaction_date,
                            isin=isin,
                            row=row,
                        )

                        if transaction is not None:
                            transactions.append(transaction)
                line_count += 1
    if rename:
        time.sleep(1)
        for file_path in files:
            file_path.rename(file_path.with_suffix(".csvprocessed"))

    return tuple(transactions)


def process_portfolios(folder: Path, rename: bool = True) -> tuple[SharePortfolio, ...]:
    """
    Create the dated portfolios from the Portfolio csv's found in folder.

    The csv files should be formatted as done by De Giro and should named as follows:
    yymmdd_Portfolio.csv
    """
    portfolio_folder = folder.joinpath("portfolio")
    files = sorted(portfolio_folder.glob("*.csv"))
    print(f"Number of files to process: {len(files)}")
    share_portfolios = []

    for file_path in files:
        filename = file_path.name
        file_date = datetime.strptime(filename[:6], "%y%m%d").date()
        with file_path.open(mode="r") as csv_file:
            csv_reader = csv.DictReader(csv_file)
            line_count = 0
            sep_stocks = []
            for row in csv_reader:
                if line_count > 0:
                    isin = row["Symbool/ISIN"]
                    # we're only interested in real stock positions (not cash)
                    if isin:
                        name = row["Product"]
                        curr = row["Lokale waarde"].split()[0]
                        nr = int(float(row["Aantal"].replace(",", ".", 2)))
                        price = round(float(row["Slotkoers"].replace(",", ".")), 2)
                        value = round(float(row["Waarde in EUR"].replace(",", ".")), 2)
                        the_position = SharePosition(
                            name=name,
                            isin=isin,
                            curr=curr,
                            investment=0.0,
                            nr=nr,
                            price=price,
                            value=value,
                            realized=0.0,
                            position_date=file_date,
                        )
                        sep_stocks.append(the_position)
                line_count += 1
        the_portfolio = SharePortfolio(
            share_positions=tuple(sep_stocks), portfolio_date=file_date
        )
        share_portfolios.append(the_portfolio)
    if rename:
        time.sleep(1)
        for file_path in files:
            file_path.rename(file_path.with_suffix(".csvprocessed"))
    return tuple(share_portfolios)


def _get_first_valid_price(
    prices: dict[date, float], price_date: date, limit: int = 10
) -> float | None:
    for i in range(limit):
        price = prices.get(price_date + timedelta(days=i), None)
        if price is not None:
            return price
    return None


def process_indices(
    indices: dict[str, dict[date, float]],
    transactions: tuple[ShareTransaction, ...],
    dates: list[date],
) -> list[tuple[SharePosition, ...]]:
    """Create the positions for the indices in the dict, given the transactions done."""
    ret_val = []

    for index_name, prices in indices.items():
        index_positions = []

        # Let's create the index prices at all the transaction dates.
        index_prices = {}
        for transaction in transactions:
            index_price = _get_first_valid_price(prices, transaction.transaction_date)
            if index_price is None:
                print(
                    f"Could not find an index price of '{index_name}' within 10 days "
                    f"for {transaction.transaction_date}"
                )
                continue
            index_prices[transaction.transaction_date] = index_price

        for position_date in dates:
            invested = 0.0
            realized = 0.0
            nr = 0.0

            for transaction in transactions:
                if transaction.transaction_date > position_date:
                    continue
                if transaction.kind == ShareTransactionKind.DIVIDEND:
                    continue

                if transaction.curr != "EUR":
                    print(
                        f"Ignored transaction because the currency '{transaction.curr}'"
                        f" is not in Euros"
                    )
                    continue

                index_price = index_prices.get(transaction.transaction_date, None)
                if index_price is None:
                    continue

                value = transaction.nr * transaction.price
                index_change = value / index_price

                if transaction.kind == ShareTransactionKind.BUY:
                    nr += index_change
                    invested += value
                elif transaction.kind == ShareTransactionKind.SELL:
                    nr -= index_change
                    realized += value
                else:
                    # Ignore the other types for now...
                    continue

            price = _get_first_valid_price(prices, position_date)
            if price is None:
                continue

            index_positions.append(
                SharePosition(
                    name=index_name.replace("_", " "),
                    isin="",
                    curr="EUR",
                    nr=nr,
                    price=price,
                    value=nr * price,
                    investment=invested,
                    realized=realized,
                    position_date=position_date,
                ),
            )
        ret_val.append(tuple(index_positions))

    return ret_val


def process_index_prices(folder: Path) -> dict[str, dict[date, float]]:
    """Read in all the index prices from the index folder."""
    index_folder = folder.joinpath("indices")
    files = index_folder.glob("*.csv")

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
