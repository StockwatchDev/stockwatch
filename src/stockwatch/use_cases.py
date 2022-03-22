import time
from datetime import date, datetime
from pathlib import Path
import csv
from .entities import *


def _process_buy_transaction_row(
    transaction_date: date,
    isin: str,
    portfolios: tuple[SharePortfolio, ...],
    row: dict[str, str],
) -> None:
    descr = row["Omschrijving"].split()
    key_index = descr.index("Koop")
    nr = round(float(descr[key_index + 1].replace(",", ".")))
    price = float(descr[key_index + 3].replace(",", "."))
    curr = row["Mutatie"]
    transaction = ShareTransaction(
        ShareTransactionKind.BUY, isin, curr, nr, price, transaction_date
    )
    # for now, we do as if amount is always EUR
    # TODO: take currency into account
    process_buy_transaction(transaction, portfolios)


def _process_sell_transaction_row(
    transaction_date: date,
    isin: str,
    portfolios: tuple[SharePortfolio, ...],
    row: dict[str, str],
) -> None:
    descr = row["Omschrijving"].split()
    key_index = descr.index("Verkoop")
    nr = round(float(descr[key_index + 1].replace(",", ".")))
    price = float(descr[key_index + 3].replace(",", "."))
    curr = row["Mutatie"]
    transaction = ShareTransaction(
        ShareTransactionKind.SELL, isin, curr, nr, price, transaction_date
    )
    # for now, we do as if amount is always EUR
    # TODO: take currency into account
    process_sell_transaction(transaction, portfolios)


def _process_dividend_transaction_row(
    transaction_date: date,
    isin: str,
    portfolios: tuple[SharePortfolio, ...],
    row: dict[str, str],
) -> None:
    amount = float(row["Bedrag"].replace(",", "."))
    curr = row["Mutatie"]
    transaction = ShareTransaction(
        ShareTransactionKind.DIVIDEND, isin, curr, 1, amount, transaction_date
    )
    # for now, we do as if amount is always EUR
    # TODO: take currency into account
    process_dividend_transaction(transaction, portfolios)


def _process_transaction_row(
    transaction_date: date,
    isin: str,
    portfolios: tuple[SharePortfolio, ...],
    row: dict[str, str],
) -> None:
    descr = row["Omschrijving"].split()
    if "Koop" in descr:
        _process_buy_transaction_row(
            transaction_date=transaction_date,
            isin=isin,
            portfolios=portfolios,
            row=row,
        )
    if "Verkoop" in descr:
        _process_sell_transaction_row(
            transaction_date=transaction_date,
            isin=isin,
            portfolios=portfolios,
            row=row,
        )
    if "Dividend" in descr:
        _process_dividend_transaction_row(
            transaction_date=transaction_date,
            isin=isin,
            portfolios=portfolios,
            row=row,
        )


def process_transactions(
    share_portfolios: tuple[SharePortfolio, ...], folder: Path, rename: bool = True
) -> tuple[SharePortfolio, ...]:
    """
    Fills the attributes investment and realized of the dated portfolios from the Account
    csv's found in folder.
    The csv files should be formatted as done by De Giro and should named as follows:
    yymmdd_Account.csv, where the date is from the Einddatum that was selected.
    """

    # preparation: collect all ISINs in the portfolio, so that we can easily
    # check if a transaction is related to our stocks
    isins_in_portfolio: set[str] = set()
    for share_portfolio in share_portfolios:
        isins_in_portfolio.update(share_portfolio.all_isins())

    account_folder = folder.joinpath("account")
    files = sorted(account_folder.glob("*.csv"))
    print(f"Number of files to process: {len(files)}")
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
                    if isin in isins_in_portfolio:
                        transaction_date = datetime.strptime(
                            row["Datum"], "%d-%m-%Y"
                        ).date()
                        _process_transaction_row(
                            transaction_date=transaction_date,
                            isin=isin,
                            portfolios=share_portfolios,
                            row=row,
                        )
                line_count += 1
    if rename:
        time.sleep(1)
        for file_path in files:
            file_path.rename(file_path.with_suffix(".csvprocessed"))
    return tuple(share_portfolios)


def process_portfolios(folder: Path, rename: bool = True) -> tuple[SharePortfolio, ...]:
    """
    Creates the dated portfolios from the Portfolio csv's found in folder.
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
                        investment = 0.0
                        nr = int(float(row["Aantal"].replace(",", ".", 2)))
                        price = round(float(row["Slotkoers"].replace(",", ".")), 2)
                        value = round(float(row["Waarde in EUR"].replace(",", ".")), 2)
                        realized = 0.0
                        the_position = SharePosition(
                            name=name,
                            isin=isin,
                            curr=curr,
                            investment=investment,
                            nr=nr,
                            price=price,
                            value=value,
                            realized=realized,
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
