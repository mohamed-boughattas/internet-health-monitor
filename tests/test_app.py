"""Tests for dashboard app.py module.

This module tests the Dash app callbacks and helper functions.
"""

from __future__ import annotations

from unittest.mock import patch


class TestErrorFigure:
    """Tests for _error_figure() helper function."""

    def test_returns_figure_object(self):
        """Should return a go.Figure object."""
        from dashboard.app import _error_figure

        fig = _error_figure()

        assert fig is not None
        assert hasattr(fig, "layout")

    def test_default_message(self):
        """Should contain default error message."""
        from dashboard.app import _error_figure

        fig = _error_figure()

        annotations = fig.layout.annotations
        assert len(annotations) == 1
        assert annotations[0].text == "Error loading data"

    def test_custom_message(self):
        """Should contain custom error message when provided."""
        from dashboard.app import _error_figure

        fig = _error_figure("Custom error message")

        annotations = fig.layout.annotations
        assert len(annotations) == 1
        assert annotations[0].text == "Custom error message"

    def test_has_no_axes(self):
        """Should have invisible axes."""
        from dashboard.app import _error_figure

        fig = _error_figure()

        assert fig.layout.xaxis.visible is False
        assert fig.layout.yaxis.visible is False

    def test_has_white_plot_background(self):
        """Should have white plot background."""
        from dashboard.app import _error_figure

        fig = _error_figure()

        assert fig.layout.plot_bgcolor == "white"


class TestDisplayPage:
    """Tests for display_page() callback."""

    def test_routes_to_overview(self):
        """Should return overview layout for root path."""
        from dashboard.app import display_page

        result = display_page("/")

        assert result is not None

    def test_routes_to_compare(self):
        """Should return comparison layout for /compare path."""
        from dashboard.app import display_page

        result = display_page("/compare")

        assert result is not None

    def test_routes_to_trends(self):
        """Should return trends layout for /trends path."""
        from dashboard.app import display_page

        result = display_page("/trends")

        assert result is not None

    def test_routes_to_detail(self):
        """Should return detail layout for /detail path."""
        from dashboard.app import display_page

        result = display_page("/detail")

        assert result is not None

    def test_routes_to_shutdowns(self):
        """Should return shutdowns layout for /shutdowns path."""
        from dashboard.app import display_page

        result = display_page("/shutdowns")

        assert result is not None

    def test_unknown_path_defaults_to_overview(self):
        """Should return overview layout for unknown paths."""
        from dashboard.app import display_page

        result = display_page("/unknown")

        assert result is not None


class TestToggleNavbar:
    """Tests for toggle_navbar() callback."""

    def test_toggles_open_to_closed(self):
        """Should toggle open state to closed on click."""
        from dashboard.app import toggle_navbar

        result = toggle_navbar(n_clicks=1, is_open=True)

        assert result is False

    def test_toggles_closed_to_open(self):
        """Should toggle closed state to open on click."""
        from dashboard.app import toggle_navbar

        result = toggle_navbar(n_clicks=1, is_open=False)

        assert result is True

    def test_maintains_state_when_no_clicks(self):
        """Should maintain current state when n_clicks is 0 or None."""
        from dashboard.app import toggle_navbar

        assert toggle_navbar(n_clicks=0, is_open=True) is True
        assert toggle_navbar(n_clicks=None, is_open=False) is False


class TestUpdateComparisonCharts:
    """Tests for update_comparison_charts() callback."""

    def test_returns_error_figures_when_no_countries(self):
        """Should return error figures when countries list is empty."""
        from dashboard.app import update_comparison_charts

        radar, bar = update_comparison_charts([])

        assert radar is not None
        assert bar is not None

    def test_returns_error_on_database_error(self):
        """Should return error figures when database query fails."""
        from dashboard.app import update_comparison_charts

        with patch("dashboard.data.queries.get_country_health_scores") as mock_scores:
            mock_scores.side_effect = FileNotFoundError("Database not found")
            radar, bar = update_comparison_charts(["US", "DE"])

            assert radar is not None
            assert bar is not None


class TestUpdateTimeseriesChart:
    """Tests for update_timeseries_chart() callback."""

    def test_returns_error_when_missing_params(self):
        """Should return error figure when country or metric is missing."""
        from dashboard.app import update_timeseries_chart

        fig = update_timeseries_chart("", "https")
        assert fig is not None

        fig = update_timeseries_chart("US", "")
        assert fig is not None

    def test_returns_error_on_database_error(self):
        """Should return error figure when database query fails."""
        from dashboard.app import update_timeseries_chart

        with patch("dashboard.app.get_daily_metric_timeseries") as mock_ts:
            mock_ts.side_effect = FileNotFoundError("Database not found")
            fig = update_timeseries_chart("US", "https")

            assert fig is not None


class TestUpdateMultiCountryChart:
    """Tests for update_multi_country_chart() callback."""

    def test_returns_error_when_missing_params(self):
        """Should return error figure when metric or countries is missing."""
        from dashboard.app import update_multi_country_chart

        fig = update_multi_country_chart("", ["US", "DE"])
        assert fig is not None

        fig = update_multi_country_chart("https", [])
        assert fig is not None

    def test_returns_error_on_database_error(self):
        """Should return error figure when database query fails."""
        from dashboard.app import update_multi_country_chart

        with patch("dashboard.app.get_daily_metric_timeseries") as mock_ts:
            mock_ts.side_effect = FileNotFoundError("Database not found")
            fig = update_multi_country_chart("https", ["US", "DE"])

            assert fig is not None


class TestSyncCountryFromStore:
    """Tests for sync_country_from_store() callback."""

    def test_returns_no_update_when_not_on_detail_page(self):
        """Should return no_update when pathname is not /detail."""
        from dash import no_update

        from dashboard.app import sync_country_from_store

        result = sync_country_from_store("US", "/overview")

        assert result is no_update

    def test_returns_store_data_on_detail_page(self):
        """Should return store data when on /detail page."""
        from dashboard.app import sync_country_from_store

        result = sync_country_from_store("US", "/detail")

        assert result == "US"

    def test_returns_no_update_when_no_store_data(self):
        """Should return no_update when store_data is None."""
        from dash import no_update

        from dashboard.app import sync_country_from_store

        result = sync_country_from_store(None, "/detail")

        assert result is no_update


class TestOnMapClick:
    """Tests for on_map_click() callback."""

    def test_returns_no_update_when_no_click_data(self):
        """Should return no_update when click_data is None."""
        from dash import no_update

        from dashboard.app import on_map_click

        result = on_map_click(None)

        assert result == (no_update, no_update)

    def test_returns_no_update_when_no_location(self):
        """Should return no_update when location is missing."""
        from dash import no_update

        from dashboard.app import on_map_click

        result = on_map_click({"points": [{}]})

        assert result == (no_update, no_update)

    def test_navigates_to_detail_with_valid_iso3(self):
        """Should return /detail and country code for valid ISO3."""
        from dashboard.app import on_map_click

        result = on_map_click({"points": [{"location": "USA"}]})

        assert result == ("/detail", "US")

    def test_returns_no_update_for_unknown_iso3(self):
        """Should return no_update when ISO3 is not tracked."""
        from dash import no_update

        from dashboard.app import on_map_click

        result = on_map_click({"points": [{"location": "XXX"}]})

        assert result == (no_update, no_update)


class TestDownloadShutdowns:
    """Tests for download_shutdowns() callback."""

    def test_returns_none_on_error(self):
        """Should return None when database query fails."""
        from dashboard.app import download_shutdowns

        with patch("dashboard.app.get_shutdown_events") as mock_events:
            mock_events.side_effect = FileNotFoundError("Database not found")
            result = download_shutdowns(n_clicks=1)

            assert result is None


class TestDownloadTrends:
    """Tests for download_trends() callback."""

    def test_returns_none_when_no_metric(self):
        """Should return None when metric is not selected."""
        from dashboard.app import download_trends

        result = download_trends(n_clicks=1, metric="")

        assert result is None

    def test_returns_none_on_error(self):
        """Should return None when database query fails."""
        from dashboard.app import download_trends

        with patch("dashboard.app.get_daily_metric_timeseries") as mock_ts:
            mock_ts.side_effect = FileNotFoundError("Database not found")
            result = download_trends(n_clicks=1, metric="https")

            assert result is None
