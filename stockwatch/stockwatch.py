# -*- coding: utf-8 -*-
"""
Created on Thu Apr 22 12:49:55 2021

@author: Robin en Theo
"""
from datetime import date, datetime
import time

from dataclasses import dataclass
from pathlib import Path
import csv
import plotly.graph_objects as go


@dataclass(frozen=True)
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
    For representing a stock shares portfolio (i.e., a set of positions) at a certain date

    Attributes
    ----------
    share_positions : the collection of share positions
    datum           : the date of the registered share positions
    """

    share_positions: tuple[SharePosition]
    datum: date

    @property
    def total_value(self) -> float:
        """The total value of this portfolio"""
        return round(sum([share_pos.value for share_pos in self.share_positions]), 2)

    def contains(self, an_isin: str) -> bool:
        """Return True of this portfolio has a share position with ISIN the_isin or False otherwise"""
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
        """Return the original investment in EUR of the share position with ISIN the_isin"""
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

    def all_isins(self) -> tuple[str]:
        """Return the ISIN codes of the share positions"""
        return (share_pos.isin for share_pos in self.share_positions)

    def all_isins_and_names(self) -> dict[str, str]:
        """Return the ISIN codes and names of the share positions"""
        return {share_pos.isin: share_pos.name for share_pos in self.share_positions}

    def date_is_consistent(self) -> bool:
        """Return True if the datums of the share positions all match with self.datum, False otherwise"""
        return all(share_pos.datum == self.datum for share_pos in self.share_positions)


def create_share_portfolios(folder: str, rename: bool = True) -> tuple[SharePortfolio]:
    """
    This function creates the dated portfolios from the csv's found in the folder.
    Make sure that the csv files are formatted as done by De Giro and named as follows:
    yymmdd_Portfolio.csv
    """

    files = sorted(Path(folder).glob("*.csv"))
    print("Files:", files)
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
                    print("stock:", isin)
                    # we're only interested in real stock positions (not cash)
                    if isin:
                        name = row["Product"]
                        print("name:", name)
                        curr = row["Lokale waarde"].split()[0]
                        print("curr:", curr)
                        investment = 0.0
                        nr = int(row["Aantal"])
                        print("nr:", nr)
                        price = round(float(row["Slotkoers"].replace(",", ".")), 2)
                        print("price:", price)
                        value = round(float(row["Waarde in EUR"].replace(",", ".")), 2)
                        print("value:", value)
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
            print(f"Processed {line_count} lines.")
        the_portfolio = SharePortfolio(share_positions=tuple(sep_stocks), datum=datum)
        share_portfolios.append(the_portfolio)
    if rename:
        time.sleep(1)
        for file_path in files:
            file_path.rename(file_path.with_suffix(".csvprocessed"))
    return tuple(share_portfolios)


def analyse_trend(
    share_portfolios: tuple[SharePortfolio], totals: bool = False
) -> None:
    """
    function to plot the value of all positions in the portfolios through time
    """
    fig = go.Figure()
    # make sure the portfolios are sorted by date:
    sorted_portfolios = sorted(share_portfolios, key=lambda x: x.datum)
    hor = [share_pf.datum for share_pf in sorted_portfolios]
    all_isins_and_names = {}
    # first collect all position names / isins
    if totals:
        all_isins_and_names.update({"no_isin": "Portfolio totals"})
    else:
        for share_portfolio in share_portfolios:
            all_isins_and_names.update(share_portfolio.all_isins_and_names())
    all_isins_and_names_list = all_isins_and_names.items()
    sorted_isins_and_names_list = sorted(
        all_isins_and_names_list, key=lambda x: share_portfolios[-1].value_of(x[0])
    )
    for (isin, name) in sorted_isins_and_names_list:
        if totals:
            vert = [share_pf.total_value for share_pf in sorted_portfolios]
            fig.add_trace(
                go.Scatter(
                    x=hor,
                    y=vert,
                    hoverinfo="name+x+y",
                    name=name,
                    mode="lines",
                    line=dict(width=0.5),
                    stackgroup="one",  # define stack group
                )
            )
        else:
            vert = [share_pf.value_of(isin) for share_pf in sorted_portfolios]
            fig.add_trace(
                go.Scatter(
                    x=hor,
                    y=vert,
                    hoverinfo="name+x+y",
                    name=isin + ": " + name,
                    mode="lines",
                    line=dict(width=0.5),
                    stackgroup="one",  # define stack group
                )
            )
    fig.show()


folder = r"c:\Users\tjade\Dropbox\tvs\prive\financien\robin\portfolio"
share_portfolios = create_share_portfolios(folder=folder, rename=False)
print("All consistent?", all(share_portfolio.date_is_consistent() for share_portfolio in share_portfolios))
# analyse_trend(share_portfolios, totals = True)
analyse_trend(share_portfolios)
