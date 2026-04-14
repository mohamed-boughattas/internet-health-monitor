"""Tests for dashboard components and functionality."""

import pandas as pd

from dashboard.components.choropleth_map import create_choropleth_map
from dashboard.components.kpi_card import _score_to_color, create_kpi_card
from dashboard.constants import MAP_COUNTRY_CODES, TRACKED_COUNTRIES


def test_kpi_card_creation():
    """Test KPI card creation with various parameters."""
    card = create_kpi_card("Test Metric", "85.5%", "Test subtitle", "+5%", "primary")

    assert card is not None
    assert "Test Metric" in str(card)
    assert "85.5%" in str(card)


def test_kpi_card_without_trend():
    """Test KPI card without trend indicator."""
    card = create_kpi_card("Health Score", "75", "Average", color="info")

    assert card is not None


def test_score_to_color():
    """Test score-to-color threshold mapping."""
    assert _score_to_color(85.0) == "success"
    assert _score_to_color(80.0) == "success"
    assert _score_to_color(75.0) == "primary"
    assert _score_to_color(60.0) == "primary"
    assert _score_to_color(55.0) == "warning"
    assert _score_to_color(40.0) == "warning"
    assert _score_to_color(35.0) == "danger"
    assert _score_to_color(0.0) == "danger"


def test_tracked_countries_mapping():
    """Test that tracked country codes are correctly mapped."""
    assert len(TRACKED_COUNTRIES) == 5
    assert TRACKED_COUNTRIES["US"] == "United States"
    assert TRACKED_COUNTRIES["DE"] == "Germany"
    assert TRACKED_COUNTRIES["BR"] == "Brazil"
    assert TRACKED_COUNTRIES["IN"] == "India"
    assert TRACKED_COUNTRIES["JP"] == "Japan"


def test_tracked_codes_list():
    """Test tracked codes list."""
    assert "US" in MAP_COUNTRY_CODES
    assert "IN" in MAP_COUNTRY_CODES
    assert len(MAP_COUNTRY_CODES) == 5


def test_choropleth_map_with_data():
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


def test_choropleth_map_empty_data():
    """Test choropleth map with empty dataframe."""
    df = pd.DataFrame()

    fig = create_choropleth_map(df)

    assert fig is None


def test_choropleth_map_with_non_tracked_countries():
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


def test_dashboard_data_queries_exist():
    """Test that dashboard data queries module can be imported."""
    from dashboard.data import queries

    assert hasattr(queries, "get_global_health_summary")
    assert hasattr(queries, "get_country_health_scores")
    assert hasattr(queries, "get_country_list")
    assert hasattr(queries, "get_daily_metric_timeseries")
    assert hasattr(queries, "get_net_loss_data")
    assert hasattr(queries, "get_shutdown_summary")
    assert hasattr(queries, "get_shutdown_events")
    assert hasattr(queries, "get_last_updated")


def test_dashboard_layouts_exist():
    """Test that dashboard layouts can be imported."""
    from dashboard.layouts import (
        get_country_comparison_layout,
        get_metric_detail_layout,
        get_overview_layout,
        get_shutdowns_layout,
        get_timeseries_layout,
    )

    assert callable(get_overview_layout)
    assert callable(get_country_comparison_layout)
    assert callable(get_timeseries_layout)
    assert callable(get_metric_detail_layout)
    assert callable(get_shutdowns_layout)


def test_navbar_creation():
    """Test navbar creation with various parameters."""
    from dashboard.components.navbar import create_navbar

    navbar = create_navbar()
    assert navbar is not None
    assert "Internet Health Monitor" in str(navbar)


def test_navbar_with_last_updated():
    """Test navbar with custom last_updated value."""
    from dashboard.components.navbar import create_navbar

    navbar = create_navbar(last_updated="2024-03-15")
    assert navbar is not None
    assert "2024-03-15" in str(navbar)


def test_iso_alpha3_mapping():
    """Test ISO Alpha-3 country code mapping."""
    from dashboard.constants import ISO_ALPHA3

    assert ISO_ALPHA3["US"] == "USA"
    assert ISO_ALPHA3["DE"] == "DEU"
    assert ISO_ALPHA3["BR"] == "BRA"
    assert ISO_ALPHA3["IN"] == "IND"
    assert ISO_ALPHA3["JP"] == "JPN"
    assert len(ISO_ALPHA3) == 5


def test_reverse_iso3_mapping():
    """Test reverse ISO3 mapping (Alpha-3 to Alpha-2)."""
    from dashboard.constants import REVERSE_ISO3

    assert REVERSE_ISO3["USA"] == "US"
    assert REVERSE_ISO3["DEU"] == "DE"
    assert REVERSE_ISO3["BRA"] == "BR"
    assert REVERSE_ISO3["IND"] == "IN"
    assert REVERSE_ISO3["JPN"] == "JP"
    assert len(REVERSE_ISO3) == 5


def test_metrics_options():
    """Test METRICS constant structure and values."""
    from dashboard.constants import METRICS

    assert len(METRICS) == 4
    metric_values = [m["value"] for m in METRICS]
    assert "ipv6" in metric_values
    assert "https" in metric_values
    assert "dnssec" in metric_values
    assert "roa" in metric_values


def test_country_options():
    """Test COUNTRY_OPTIONS constant structure."""
    from dashboard.constants import COUNTRY_OPTIONS

    assert len(COUNTRY_OPTIONS) == 5
    codes = [opt["value"] for opt in COUNTRY_OPTIONS]
    assert "US" in codes
    assert "DE" in codes
    assert "BR" in codes
    assert "IN" in codes
    assert "JP" in codes
