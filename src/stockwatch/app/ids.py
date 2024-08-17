""" The module with all the specified ids used for the Dash application."""

import enum


class _BaseDashId(str, enum.Enum):
    pass


class ScrapingId(_BaseDashId):
    """The ids for scraping data."""

    MODAL = "scraping-modal"
    START = "scraping-start"
    CLOSE = "scraping-close"
    EXECUTE = "scraping-execute"
    START_DATE = "scraping-end-date"
    END_DATE = "scraping-start-date"
    PROGRESS = "scraping-progress"
    INTERVAL = "scraping-interval"
    CURRENT = "scraping-current"
    PLACEHOLDER = "scraping-placeholder"
    FOLDER = "scraping-folder"

    USERNAME = "scraping-username"
    PASSWORD = "scraping-password"
    GOAUTH = "scraping-goauth"
    LOGIN_FAIL = "scraping-loginfail"


class PortfolioId(_BaseDashId):
    """The ids for portfolio plotting."""

    GRAPH_TOTAL = "portfolio-graph-total"
    GRAPH_RESULT = "portfolio-graph-result"
    REFRESH = "portfolio-refresh"

    START_DATE = "portfolio-start-date"
    END_DATE = "portfolio-end-date"

    YTD_BTN = "portfolio-ytd-button"
    MTD_BTN = "portfolio-mtd-button"
    LY_BTN = "portfolio-ly-button"
    LM_BTN = "portfolio-lm-button"
    ALL_BTN = "portfolio-all-button"


class ReturnsId(_BaseDashId):
    """The ids for returns plots."""

    GRAPH_COMPARISON = "returns-graph-comparison"
    REFRESH = "returns-refresh"

    START_DATE = "returns-start-date"
    END_DATE = "returns-end-date"


class HeaderIds(_BaseDashId):
    """The ids for the header items."""

    PORTFOLIO = "header-portfolio"
    RETURNS = "header-returns"
    SCRAPING = "header-scraping"
    ABOUT = "header-about"
    LOCATION = "header-location"
    CONTENT = "header-content"


class PageIds(_BaseDashId):
    """The pages link."""

    PORTFOLIO = "/portfolio"
    RETURNS = "/returns"
    SCRAPING = "/scraping"
    ABOUT = "/about"
