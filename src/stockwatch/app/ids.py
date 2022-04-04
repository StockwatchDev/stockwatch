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
    SESSION_ID = "scraping-sessionid"
    ACCOUNT_ID = "scraping-accountid"
    START_DATE = "scraping-end-date"
    END_DATE = "scraping-start-date"
    PROGRESS = "scraping-progress"
    INTERVAL = "scraping-interval"
    CURRENT = "scraping-current"
    PLACEHOLDER = "scraping-placeholder"
    FOLDER = "scraping-folder"


class PlottingId(_BaseDashId):
    """The ids for plotting."""

    GRAPH_TOTAL = "plotting-graph-total"
    GRAPH_RESULT = "plotting-graph-result"
    REFRESH = "plotting-refresh"
