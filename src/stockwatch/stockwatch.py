#!/usr/bin/env python3
"""
Read csv files with stock portfolio data from De Giro and visualize in the browser.

Classes:

    SharePosition
    SharePortfolio

Functions:

    create_share_portfolios(folder: Path,
                            rename: bool = True) -> tuple[SharePortfolio, ...]
    analyse_trend(share_portfolios: tuple[SharePortfolio], totals: bool = False) -> None
    main(folder: Path) -> int
"""
import argparse
import csv
import os
from sys import exit
import time
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Optional

import plotly.graph_objects as go  # type: ignore

STOCKWATCH_ENV_VAR = "STOCKWATCH_DIR"


# @dataclass(frozen=True)
@dataclass(frozen=False)
class SharePosition:
    """
    For representing a stock shares position at a certain date

    Attributes
    ----------
    name            : the name of the share
    isin            : the ISIN code / Symbol string used to identify a share
    curr            : the currency shorthand in which the stock is traded, e.g. EUR
    investment      : the amount in EUR spent in purchasing the shares
    nr              : the number of shares
    price           : the current price of the shares, in curr
    value           : the current value of the shares, in EUR
    realized        : the realized result in EUR (including trading costs)
    datum           : the date for which the value of the share position is registered
    """

    name: str
    isin: str
    curr: str
    investment: float
    nr: int
    price: float
    value: float
    realized: float
    datum: date


@dataclass(frozen=True)
class SharePortfolio:
    """
    For representing a stock shares portfolio (i.e. multiple positions) at a certain date

    Attributes
    ----------
    share_positions : the collection of share positions
    datum           : the date of the registered share positions
    """

    share_positions: tuple[SharePosition, ...]
    datum: date

    @property
    def total_value(self) -> float:
        """The total value of this portfolio"""
        return round(sum([share_pos.value for share_pos in self.share_positions]), 2)

    @property
    def total_investment(self) -> float:
        """The total iinvestment of this portfolio"""
        return round(
            sum([share_pos.investment for share_pos in self.share_positions]), 2
        )

    def contains(self, an_isin: str) -> bool:
        """Return True if self has a share position with ISIN an_isin"""
        return an_isin in [share_pos.isin for share_pos in self.share_positions]

    def get_position(self, the_isin: str) -> SharePosition | None:
        """Return the share position with ISIN the_isin or None if not present"""
        for share_pos in self.share_positions:
            if share_pos.isin == the_isin:
                return share_pos
        return None

    def value_of(self, the_isin: str) -> float:
        """Return the value in EUR of the share position with ISIN the_isin"""
        return round(
            sum(
                [
                    share_pos.value if share_pos.isin == the_isin else 0.0
                    for share_pos in self.share_positions
                ]
            ),
            2,
        )

    def investment_of(self, the_isin: str) -> float:
        """Return the investment in EUR of the share position with ISIN the_isin"""
        return round(
            sum(
                [
                    share_pos.investment if share_pos.isin == the_isin else 0.0
                    for share_pos in self.share_positions
                ]
            ),
            2,
        )

    def realized_return_of(self, the_isin: str) -> float:
        """Return the realized return in EUR of the share position with ISIN the_isin"""
        return round(
            sum(
                [
                    share.realized if share.isin == the_isin else 0.0
                    for share in self.share_positions
                ]
            ),
            2,
        )

    def all_isins(self) -> tuple[str, ...]:
        """Return the ISIN codes of the share positions"""
        return tuple(share_pos.isin for share_pos in self.share_positions)

    def all_isins_and_names(self) -> dict[str, str]:
        """Return the ISIN codes and names of the share positions"""
        return {share_pos.isin: share_pos.name for share_pos in self.share_positions}

    def is_date_consistent(self) -> bool:
        """Return True if the datums of the share positions all match with self.datum"""
        return all(share_pos.datum == self.datum for share_pos in self.share_positions)


def create_share_portfolios(
    folder: Path, rename: bool = True
) -> tuple[SharePortfolio, ...]:
    """
    Creates the dated portfolios from the Portfolio csv's found in folder.
    The csv files should be formatted as done by De Giro and should named as follows:
    yymmdd_Portfolio.csv
    """

    files = sorted(folder.glob("*Portfolio.csv"))
    print("Number of files to process:", len(files))
    share_portfolios = []

    for file_path in files:
        filename = file_path.name
        datum = datetime.strptime(filename[:6], "%y%m%d").date()
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
                            datum=datum,
                        )
                        sep_stocks.append(the_position)
                line_count += 1
        the_portfolio = SharePortfolio(share_positions=tuple(sep_stocks), datum=datum)
        share_portfolios.append(the_portfolio)
    if rename:
        time.sleep(1)
        for file_path in files:
            file_path.rename(file_path.with_suffix(".csvprocessed"))
    return tuple(share_portfolios)


def _process_buy_sell_transaction_row(
    sorted_portfolios: tuple[SharePortfolio, ...], row: dict[str, str], is_buy: bool
):
    isin = row["ISIN"]
    datum = datetime.strptime(row["Datum"], "%d-%m-%Y").date()
    descr = row["Omschrijving"].split()
    key_index = -1
    sgn = 1.0
    if is_buy:
        key_index = descr.index("Koop")
    else:
        key_index = descr.index("Verkoop")
        sgn = -1.0
    print("Transaction date:", datum)
    nr = float(descr[key_index + 1].replace(",", "."))
    price = float(descr[key_index + 3].replace(",", "."))
    investment = 0.0
    realization = 0.0
    index_first_invest = next(
        x[0] for x in enumerate(sorted_portfolios) if x[1].datum > datum
    )
    next_pos = sorted_portfolios[index_first_invest].get_position(isin)
    if sgn == 1.0:
        # we buy shares
        investment = sgn * nr * price
    if sgn == -1.0:
        # we sell shares
        buy_price = price
        if index_first_invest > 0:
            current_pos = sorted_portfolios[index_first_invest - 1].get_position(isin)
            if current_pos:
                buy_price = current_pos.investment / current_pos.nr
                if not next_pos:
                    # we are selling all shares
                    # the portfolio on the next date does not
                    # have this share
                    # so let's create one with the realization
                    next_pos = SharePosition(
                        name=current_pos.name,
                        isin=current_pos.isin,
                        curr=current_pos.curr,
                        investment=0.0,
                        nr=0,
                        price=1.0,
                        value=0.0,
                        realized=current_pos.realized
                        + round(nr * (price - buy_price), 2),
                        datum=sorted_portfolios[index_first_invest].datum,
                    )
                    # and now... what to do with it??
        investment = round(sgn * nr * buy_price, 2)
        realization = round(nr * (price - buy_price), 2)
    print("Transaction amount:", sgn * nr * price)
    print("Investment:", investment)
    print("Realization:", realization)
    for cnt in range(index_first_invest, len(sorted_portfolios)):
        pos = sorted_portfolios[cnt].get_position(isin)
        if pos:
            pos.investment += investment
            pos.realized += realization
    print("Resulting position:", next_pos, "\n")


def _process_transaction_row(
    sorted_portfolios: tuple[SharePortfolio, ...], row: dict[str, str]
):
    descr = row["Omschrijving"].split()
    if "Koop" in descr:
        _process_buy_sell_transaction_row(sorted_portfolios, row, is_buy=True)
    if "Verkoop" in descr:
        _process_buy_sell_transaction_row(sorted_portfolios, row, is_buy=False)


def process_transactions(
    share_portfolios: tuple[SharePortfolio, ...], folder: Path, rename: bool = True
) -> tuple[SharePortfolio, ...]:
    """
    Fills the attributes investment and realized of the dated portfolios from the Account
    csv's found in folder.
    The csv files should be formatted as done by De Giro and should named as follows:
    yymmdd_Account.csv, where the date is from the Einddatum that was selected.
    """

    # make sure the portfolios are sorted by date:
    sorted_portfolios = sorted(share_portfolios, key=lambda x: x.datum)
    files = sorted(folder.glob("*Account.csv"))
    print("Number of files to process:", len(files))
    isins_in_portfolio: set[str] = set()
    for share_portfolio in sorted_portfolios:
        isins_in_portfolio.update(share_portfolio.all_isins())

    for file_path in files:
        with file_path.open(mode="r") as csv_file:
            csv_reader = csv.DictReader(csv_file)
            line_count = 0
            for row in reversed(list(csv_reader)):
                if line_count > 0:
                    isin = row["ISIN"]
                    # we're only interested in real stock positions (not cash)
                    if isin in isins_in_portfolio:
                        _process_transaction_row(share_portfolios, row)
                line_count += 1
    if rename:
        time.sleep(1)
        for file_path in files:
            file_path.rename(file_path.with_suffix(".csvprocessed"))
    return tuple(share_portfolios)


def analyse_trend(
    share_portfolios: tuple[SharePortfolio, ...], totals: bool = False
) -> None:
    """
    Plot the value of all positions in the portfolios through time
    """
    fig = go.Figure()
    # make sure the portfolios are sorted by date:
    sorted_portfolios = sorted(share_portfolios, key=lambda x: x.datum)
    # horizontal axis to be the date
    hor = [share_pf.datum for share_pf in sorted_portfolios]
    sorted_isins_and_names_list = []
    # first collect all position names / isins
    if totals:
        sorted_isins_and_names_list = [("no_isin", "Portfolio totals")]
    else:
        all_isins_and_names = {}
        for share_portfolio in share_portfolios:
            all_isins_and_names.update(share_portfolio.all_isins_and_names())
        # sort for increasing value at final date,
        # such that all zero values are at the horizontal axis
        sorted_isins_and_names_list = sorted(
            all_isins_and_names.items(),
            key=lambda x: share_portfolios[-1].value_of(x[0]),
        )
    for (isin, name) in sorted_isins_and_names_list:
        if totals:
            # vertical axis to be the portfolio value
            vert1 = [share_pf.total_investment for share_pf in sorted_portfolios]
            vert2 = [share_pf.total_value for share_pf in sorted_portfolios]
        else:
            # vertical axis to be the value of each position in the portfolio
            vert1 = [0.0 for share_pf in sorted_portfolios]
            vert2 = [share_pf.value_of(isin) for share_pf in sorted_portfolios]
        fig.add_trace(
            go.Scatter(
                x=hor,
                y=vert1,
                hoverinfo="name+x+y",
                name=isin + ": " + name,
                mode="lines",
                line=dict(width=0.5),
                stackgroup="one",  # define stack group
            )
        )
        fig.add_trace(
            go.Scatter(
                x=hor,
                y=vert2,
                hoverinfo="name+x+y",
                name=isin + ": " + name,
                mode="lines",
                line=dict(width=0.5),
                stackgroup="two",  # define stack group
            )
        )
    fig.show()


def main(folder: Path) -> int:
    """The main function to run the stockwatcher."""

    share_portfolios = create_share_portfolios(folder=folder, rename=False)
    print(
        "All consistent?",
        all(
            share_portfolio.is_date_consistent() for share_portfolio in share_portfolios
        ),
    )
    process_transactions(share_portfolios=share_portfolios, folder=folder, rename=False)
    analyse_trend(share_portfolios, totals=True)
    analyse_trend(share_portfolios)
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dir", nargs="?", default=None, type=Path)

    args = parser.parse_args()
    folder: Optional[Path] = args.dir

    if not folder or not folder.is_dir():
        # Let's try to read from the environment variables.
        env_path = os.environ.get(STOCKWATCH_ENV_VAR, "")
        if env_path:
            folder = Path(env_path)

    if not folder or not folder.is_dir():
        parser.error(
            f"Folder: '{folder}' does not exist, please pass as commandline argument, or define the"
            f" '{STOCKWATCH_ENV_VAR}' environment variable."
        )

    print(f"Parsing the porfolio files in directory: '{folder}'")
    exit(main(folder))
