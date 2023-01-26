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


class PlottingId(_BaseDashId):
    """The ids for plotting."""

    GRAPH_TOTAL = "plotting-graph-total"
    GRAPH_RESULT = "plotting-graph-result"
    REFRESH = "plotting-refresh"

    START_DATE = "plotting-start-date"
    END_DATE = "plotting-end-date"

    YTD_BTN = "plotting-ytd-button"
    MTD_BTN = "plotting-mtd-button"
    LY_BTN = "plotting-ly-button"
    LM_BTN = "plotting-lm-button"
    ALL_BTN = "plotting-all-button"


class HeaderIds(_BaseDashId):
    """The ids for the header items."""

    PLOTS = "header-plots"
    SCRAPING = "header-scraping"
    ABOUT = "header-about"
    LOCATION = "header-location"
    CONTENT = "header-content"


class PageIds(_BaseDashId):
    """The pages link."""

    PLOTS = "/plots"
    SCRAPING = "/scraping"
    ABOUT = "/about"
