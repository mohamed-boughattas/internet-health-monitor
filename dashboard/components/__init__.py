"""Dashboard components package.

This package provides reusable UI components for the dashboard,
including KPI cards, choropleth maps, and navigation.
"""

from .choropleth_map import create_choropleth_map
from .kpi_card import create_kpi_card, score_to_color
from .navbar import create_navbar

__all__ = [
    "create_kpi_card",
    "score_to_color",
    "create_choropleth_map",
    "create_navbar",
]
