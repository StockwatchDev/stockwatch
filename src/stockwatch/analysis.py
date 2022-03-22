import csv
import time
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import List, Optional

import plotly.graph_objects as go


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
    position_date           : the date for which the value of the share position is registered
    """

    name: str
    isin: str
    curr: str
    investment: float
    nr: int
    price: float
    value: float
    realized: float
    position_date: date


@dataclass(frozen=True)
class SharePortfolio:
    """
    For representing a stock shares portfolio (i.e. multiple positions) at a certain date

    Attributes
    ----------
    share_positions : the collection of share positions
    portfolio_date           : the date of the registered share positions
    """

    share_positions: tuple[SharePosition, ...]
    portfolio_date: date

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
        """Return True if the share positions dates all match self.portfolio_date"""
        return all(
            share_pos.position_date == self.portfolio_date
            for share_pos in self.share_positions
        )


def create_share_portfolios(
    folder: Path, rename: bool = True
) -> tuple[SharePortfolio, ...]:
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


def _add_investment_realization(
    investment: float,
    realization: float,
    transaction_date: date,
    isin: str,
    sorted_portfolios: tuple[SharePortfolio, ...],
) -> None:
    portfolios_to_modify = [
        spf for spf in sorted_portfolios if spf.portfolio_date > transaction_date
    ]
    for spf in portfolios_to_modify:
        pos = spf.get_position(isin)
        if pos:
            pos.investment = round(pos.investment + investment, 2)
            pos.realized = round(pos.realized + realization, 2)
    if len(portfolios_to_modify) > 0 and (
        pos := portfolios_to_modify[0].get_position(isin)
    ):
        print(f"Total investment: {pos.investment}")
        print(f"Total realization: {pos.realized}\n")


def _process_buy_transaction_row(
    transaction_date: date,
    isin: str,
    sorted_portfolios: tuple[SharePortfolio, ...],
    row: dict[str, str],
) -> None:
    descr = row["Omschrijving"].split()
    key_index = descr.index("Koop")
    nr = float(descr[key_index + 1].replace(",", "."))
    buy_price = float(descr[key_index + 3].replace(",", "."))
    investment = nr * buy_price
    realization = 0.0
    print(f"Buy transaction date: {transaction_date} for ISIN {isin}")
    print(f"Transaction amount: {-nr * buy_price}")
    _add_investment_realization(
        investment=investment,
        realization=realization,
        transaction_date=transaction_date,
        isin=isin,
        sorted_portfolios=sorted_portfolios,
    )


def _process_sell_transaction_row(
    transaction_date: date,
    isin: str,
    sorted_portfolios: tuple[SharePortfolio, ...],
    row: dict[str, str],
) -> None:
    descr = row["Omschrijving"].split()
    key_index = descr.index("Verkoop")
    nr = float(descr[key_index + 1].replace(",", "."))
    price = float(descr[key_index + 3].replace(",", "."))
    investment = 0.0
    realization = 0.0
    index_first_change = next(
        (
            x[0]
            for x in enumerate(sorted_portfolios)
            if x[1].portfolio_date > transaction_date
        ),
        None,
    )
    current_pos = None
    next_pos = None
    buy_price = None
    if not index_first_change:
        current_pos = sorted_portfolios[-1].get_position(isin)
    else:
        next_pos = sorted_portfolios[index_first_change].get_position(isin)
        if index_first_change > 0:
            current_pos = sorted_portfolios[index_first_change - 1].get_position(isin)
    if current_pos:
        buy_price = current_pos.investment / current_pos.nr
        if not next_pos:
            # the portfolio on the next date does not exist or
            # does not have this share because we sell all
            # so let's create a position with the realization
            if index_first_change:
                next_date = sorted_portfolios[index_first_change].portfolio_date
            else:
                next_date = transaction_date
            next_pos = SharePosition(
                name=current_pos.name,
                isin=current_pos.isin,
                curr=current_pos.curr,
                investment=0.0,
                nr=0,
                price=1.0,
                value=0.0,
                realized=round(current_pos.realized + nr * (price - buy_price), 2),
                position_date=next_date,
            )
            # and now... what to do with it??
            print(
                f"ISIN {isin} has been sold, total realization: {next_pos.realized}\n"
            )
    if not buy_price:
        print("Error: we can't determine the buy price for this sell transaction")
        buy_price = 0.0
    investment = -nr * buy_price
    realization = nr * (price - buy_price)
    print(f"Sell transaction date: {transaction_date} for ISIN {isin}")
    print(f"Transaction amount: {nr * price}")
    _add_investment_realization(
        investment=investment,
        realization=realization,
        transaction_date=transaction_date,
        isin=isin,
        sorted_portfolios=sorted_portfolios,
    )


def _process_dividend_transaction_row(
    transaction_date: date,
    isin: str,
    sorted_portfolios: tuple[SharePortfolio, ...],
    row: dict[str, str],
) -> None:
    amount = float(row["Bedrag"].replace(",", "."))
    curr = row["Mutatie"]
    investment = 0.0
    # for now, we do as if amount is always EUR
    # TODO: take currency into account
    realization = amount
    print(f"Dividend transaction date: {transaction_date} for ISIN {isin}")
    print(f"Dividend amount: {curr} {amount}")
    _add_investment_realization(
        investment=investment,
        realization=realization,
        transaction_date=transaction_date,
        isin=isin,
        sorted_portfolios=sorted_portfolios,
    )


def _process_transaction_row(
    transaction_date: date,
    isin: str,
    sorted_portfolios: tuple[SharePortfolio, ...],
    row: dict[str, str],
) -> None:
    descr = row["Omschrijving"].split()
    if "Koop" in descr:
        _process_buy_transaction_row(
            transaction_date=transaction_date,
            isin=isin,
            sorted_portfolios=sorted_portfolios,
            row=row,
        )
    if "Verkoop" in descr:
        _process_sell_transaction_row(
            transaction_date=transaction_date,
            isin=isin,
            sorted_portfolios=sorted_portfolios,
            row=row,
        )
    if "Dividend" in descr:
        _process_dividend_transaction_row(
            transaction_date=transaction_date,
            isin=isin,
            sorted_portfolios=sorted_portfolios,
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

    # preparation: make sure the portfolios are sorted by date:
    sorted_portfolios = tuple(sorted(share_portfolios, key=lambda x: x.portfolio_date))

    # preparation: collect all ISINs in the portfolio, so that we can easily
    # check if a transaction is related to our stocks
    isins_in_portfolio: set[str] = set()
    for share_portfolio in sorted_portfolios:
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
            print(contents[0])
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
                            sorted_portfolios=sorted_portfolios,
                            row=row,
                        )
                line_count += 1
    if rename:
        time.sleep(1)
        for file_path in files:
            file_path.rename(file_path.with_suffix(".csvprocessed"))
    return tuple(share_portfolios)


def plot_returns(share_portfolios: tuple[SharePortfolio]) -> go.Figure:
    # make sure the portfolios are sorted by date:
    sorted_portfolios = sorted(share_portfolios, key=lambda x: x.portfolio_date)

    # horizontal axis to be the date
    dates = [share_pf.portfolio_date for share_pf in sorted_portfolios]

    investments = []
    returns = []
    totals = []
    for share_pf in sorted_portfolios:
        investments.append(share_pf.total_investment)
        totals.append(share_pf.total_value)
        returns.append(share_pf.total_value - share_pf.total_investment)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=investments,
            hovertemplate="<b>invested: </b>€%{y:0.2f}<extra></extra>",
            name="Investments",
            mode="none",
            fill="tozeroy",
            line=dict(width=0.5),
            legendrank=2,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=totals,
            hovertemplate="<b>total: </b>€%{y:0.2f}<extra></extra>",
            name="Totals",
            mode="none",
            fill="tonexty",
            line=dict(width=0.5),
            legendrank=3,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=returns,
            hovertemplate="<b>returns: </b>€%{y:0.2f}<extra></extra>",
            name="Returns",
            line=dict(color="black", width=2.0),
            legendrank=1,
        )
    )
    fig.update_layout(hovermode="x unified")
    return fig


def plot_positions(share_portfolios: tuple[SharePortfolio, ...]) -> go.Figure:
    """
    Plot the value of all positions in the portfolios through time
    """

    # make sure the portfolios are sorted by date:
    sorted_portfolios = sorted(share_portfolios, key=lambda x: x.portfolio_date)
    # horizontal axis to be the date
    dates = [share_pf.portfolio_date for share_pf in sorted_portfolios]

    sorted_isins_and_names_list = []
    # first collect all position names / isins
    all_isins_and_names = {}
    for share_portfolio in share_portfolios:
        all_isins_and_names.update(share_portfolio.all_isins_and_names())
    # sort for increasing value at final date,
    # such that all zero values are at the horizontal axis
    sorted_isins_and_names_list = sorted(
        all_isins_and_names.items(),
        key=lambda x: share_portfolios[-1].value_of(x[0]),
    )

    fig = go.Figure()
    for (isin, name) in sorted_isins_and_names_list:
        hovertemplate = f"<b>{name} - {isin}</b><br>value €%{{y:0.2f}}<br>date: %{{x}}<extra></extra>"
        # vertical axis to be the value of each position in the portfolio
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=[share_pf.value_of(isin) for share_pf in sorted_portfolios],
                hovertemplate=hovertemplate,
                name=isin,
                mode="lines",
                line=dict(width=0.5),
                stackgroup="one",
            )
        )
    return fig
