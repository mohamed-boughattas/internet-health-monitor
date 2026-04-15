"""Dashboard layouts package."""

from .country_comparison import get_country_comparison_layout
from .metric_detail import get_metric_detail_layout
from .overview import get_overview_layout
from .timeseries import get_timeseries_layout

__all__ = [
    "get_overview_layout",
    "get_country_comparison_layout",
    "get_timeseries_layout",
    "get_metric_detail_layout",
]
