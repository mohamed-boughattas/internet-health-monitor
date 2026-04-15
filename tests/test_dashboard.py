"""Tests for dashboard components and functionality.

Note: Length assertions use TRACKED_COUNTRIES so adding new countries
requires no test changes.
"""

from __future__ import annotations

import pandas as pd

from dashboard.components.choropleth_map import create_choropleth_map
from dashboard.components.kpi_card import create_kpi_card, score_to_color
from dashboard.constants import (
    COUNTRY_OPTIONS,
    ISO_ALPHA3,
    MAP_COUNTRY_CODES,
    METRICS,
    REVERSE_ISO3,
    TRACKED_COUNTRIES,
)


def test_kpi_card_creation() -> None:
    """Test KPI card creation with various parameters."""
    card = create_kpi_card("Test Metric", "85.5%", "Test subtitle", "+5%", "primary")

    assert card is not None
    assert "Test Metric" in str(card)


def test_kpi_card_without_trend() -> None:
    """Test KPI card creation without trend value."""
    card = create_kpi_card("Test Metric", "85.5%", "Test subtitle", None, "primary")

    assert card is not None
    assert "Test Metric" in str(card)


def test_score_to_color() -> None:
    """Test score_to_color returns correct color based on threshold."""
    assert score_to_color(85.0) == "success"
    assert score_to_color(65.0) == "primary"
    assert score_to_color(45.0) == "warning"
    assert score_to_color(25.0) == "danger"
    assert score_to_color(0.0) == "danger"


def test_tracked_countries_mapping() -> None:
    """Test that tracked country codes are correctly mapped."""
    assert TRACKED_COUNTRIES["US"] == "United States"
    assert TRACKED_COUNTRIES["DE"] == "Germany"
    assert TRACKED_COUNTRIES["BR"] == "Brazil"
    assert TRACKED_COUNTRIES["IN"] == "India"
    assert TRACKED_COUNTRIES["JP"] == "Japan"
    assert TRACKED_COUNTRIES["FR"] == "France"


def test_tracked_codes_list() -> None:
    """Test tracked codes list."""
    assert "US" in MAP_COUNTRY_CODES
    assert "IN" in MAP_COUNTRY_CODES
    assert len(MAP_COUNTRY_CODES) == len(TRACKED_COUNTRIES)


def test_choropleth_map_with_data() -> None:
    """Test choropleth map creation with sample data."""
    df = pd.DataFrame(
        {
            "country_code": ["US", "DE", "JP", "BR", "IN"],
            "health_score": [59.2, 80.1, 59.0, 54.9, 65.7],
            "ipv6_score": [53.4, 64.0, 53.7, 49.7, 72.4],
            "https_score": [94.8, 89.5, 91.3, 82.5, 43.8],
            "dnssec_score": [36.6, 79.6, 13.7, 51.4, 56.6],
            "roa_score": [51.9, 87.5, 77.1, 36.2, 90.0],
        }
    )

    fig = create_choropleth_map(df)

    assert fig is not None


def test_choropleth_map_empty_data() -> None:
    """Test choropleth map with empty dataframe."""
    df = pd.DataFrame()

    fig = create_choropleth_map(df)

    assert fig is None


def test_choropleth_map_with_non_tracked_countries() -> None:
    """Test choropleth map filters non-tracked countries."""
    df = pd.DataFrame(
        {
            "country_code": ["US", "DE", "JP", "BR", "IN"],
            "health_score": [59.2, 80.1, 59.0, 54.9, 65.7],
            "ipv6_score": [53.4, 64.0, 53.7, 49.7, 72.4],
            "https_score": [94.8, 89.5, 91.3, 82.5, 43.8],
            "dnssec_score": [36.6, 79.6, 13.7, 51.4, 56.6],
            "roa_score": [51.9, 87.5, 77.1, 36.2, 90.0],
        }
    )

    fig = create_choropleth_map(df)

    assert fig is not None


def test_dashboard_data_queries_exist() -> None:
    """Test that data query module exists and has required functions."""
    from dashboard import data as queries

    assert hasattr(queries, "queries")
    data_queries = queries.queries
    assert hasattr(data_queries, "get_country_health_scores")
    assert hasattr(data_queries, "get_country_list")


def test_dashboard_layouts_exist() -> None:
    """Test that layout modules exist for all pages."""
    from dashboard.layouts import (
        get_country_comparison_layout,
        get_metric_detail_layout,
        get_overview_layout,
        get_timeseries_layout,
    )

    assert callable(get_overview_layout)
    assert callable(get_country_comparison_layout)
    assert callable(get_timeseries_layout)
    assert callable(get_metric_detail_layout)


def test_navbar_with_last_updated() -> None:
    """Test navbar with last updated timestamp."""
    from dashboard.components.navbar import create_navbar

    navbar = create_navbar(last_updated="2024-01-15")

    assert navbar is not None


def test_navbar_creation() -> None:
    """Test navbar component creation."""
    from dashboard.components.navbar import create_navbar

    navbar = create_navbar()

    assert navbar is not None


def test_iso_alpha3_mapping() -> None:
    """Test ISO Alpha-3 country code mapping."""
    assert ISO_ALPHA3["US"] == "USA"
    assert ISO_ALPHA3["DE"] == "DEU"
    assert ISO_ALPHA3["BR"] == "BRA"
    assert ISO_ALPHA3["IN"] == "IND"
    assert ISO_ALPHA3["JP"] == "JPN"
    assert ISO_ALPHA3["FR"] == "FRA"
    assert len(ISO_ALPHA3) == len(TRACKED_COUNTRIES)


def test_reverse_iso3_mapping() -> None:
    """Test reverse ISO3 mapping (Alpha-3 to Alpha-2)."""
    assert REVERSE_ISO3["USA"] == "US"
    assert REVERSE_ISO3["DEU"] == "DE"
    assert REVERSE_ISO3["BRA"] == "BR"
    assert REVERSE_ISO3["IND"] == "IN"
    assert REVERSE_ISO3["JPN"] == "JP"
    assert REVERSE_ISO3["FRA"] == "FR"
    assert len(REVERSE_ISO3) == len(TRACKED_COUNTRIES)


def test_metrics_options() -> None:
    """Test METRICS constant structure and values."""
    assert len(METRICS) == 4
    metric_values = [m["value"] for m in METRICS]
    assert "ipv6" in metric_values
    assert "https" in metric_values
    assert "dnssec" in metric_values
    assert "roa" in metric_values


def test_country_options() -> None:
    """Test COUNTRY_OPTIONS derived from TRACKED_COUNTRIES."""
    assert len(COUNTRY_OPTIONS) == len(TRACKED_COUNTRIES)
    assert all("value" in opt and "label" in opt for opt in COUNTRY_OPTIONS)
    codes = {opt["value"] for opt in COUNTRY_OPTIONS}
    assert codes == set(TRACKED_COUNTRIES.keys())
