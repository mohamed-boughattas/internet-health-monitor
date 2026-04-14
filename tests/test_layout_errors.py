"""Tests for layout error handling branches.

These tests verify that layout functions correctly handle error
conditions by mocking the underlying query functions.
"""

from __future__ import annotations

from unittest.mock import patch

import pandas as pd


class TestOverviewLayoutErrors:
    """Error branch tests for get_overview_layout()."""

    def test_returns_alert_when_db_not_found(self, monkeypatch):
        """Should return a warning Alert when database file is not found."""
        with patch("dashboard.layouts.overview.get_global_health_summary") as mock_summary:
            with patch("dashboard.layouts.overview.get_country_health_scores") as mock_scores:
                mock_summary.side_effect = FileNotFoundError("Database not found")
                mock_scores.side_effect = FileNotFoundError("Database not found")
                from dashboard.layouts.overview import get_overview_layout

                result = get_overview_layout()

                assert "Database not found" in str(result)

    def test_returns_alert_when_summary_empty(self, monkeypatch):
        """Should return an info Alert when summary DataFrame is empty."""
        with patch("dashboard.layouts.overview.get_global_health_summary") as mock_summary:
            with patch("dashboard.layouts.overview.get_country_health_scores") as mock_scores:
                mock_summary.return_value = pd.DataFrame()
                mock_scores.return_value = pd.DataFrame()
                from dashboard.layouts.overview import get_overview_layout

                result = get_overview_layout()

                assert "No data available" in str(result)


class TestCountryComparisonLayoutErrors:
    """Error branch tests for get_country_comparison_layout()."""

    def test_returns_alert_when_db_not_found(self, monkeypatch):
        """Should return a warning Alert when database file is not found."""
        with patch("dashboard.layouts.country_comparison.get_country_health_scores") as mock_scores:
            with patch("dashboard.layouts.country_comparison.get_country_list") as mock_list:
                mock_scores.side_effect = FileNotFoundError("Database not found")
                mock_list.side_effect = FileNotFoundError("Database not found")
                from dashboard.layouts.country_comparison import get_country_comparison_layout

                result = get_country_comparison_layout()

                assert "Database not found" in str(result)

    def test_returns_alert_when_scores_empty(self, monkeypatch):
        """Should return an info Alert when country_scores DataFrame is empty."""
        with patch("dashboard.layouts.country_comparison.get_country_health_scores") as mock_scores:
            with patch("dashboard.layouts.country_comparison.get_country_list") as mock_list:
                mock_scores.return_value = pd.DataFrame()
                mock_list.return_value = []
                from dashboard.layouts.country_comparison import get_country_comparison_layout

                result = get_country_comparison_layout()

                assert "No data available" in str(result)


class TestTimeseriesLayoutErrors:
    """Error branch tests for get_timeseries_layout()."""

    def test_returns_alert_when_db_not_found(self, monkeypatch):
        """Should return a warning Alert when database file is not found."""
        with patch("dashboard.layouts.timeseries.get_country_list") as mock_list:
            mock_list.side_effect = FileNotFoundError("Database not found")
            from dashboard.layouts.timeseries import get_timeseries_layout

            result = get_timeseries_layout()

            assert "Database not found" in str(result)

    def test_returns_alert_when_country_list_empty(self, monkeypatch):
        """Should return an info Alert when no countries are available."""
        with patch("dashboard.layouts.timeseries.get_country_list") as mock_list:
            mock_list.return_value = []
            from dashboard.layouts.timeseries import get_timeseries_layout

            result = get_timeseries_layout()

            assert "No countries available" in str(result)


class TestMetricDetailLayoutErrors:
    """Error branch tests for get_metric_detail_layout()."""

    def test_returns_alert_when_db_not_found(self, monkeypatch):
        """Should return a warning Alert when database file is not found."""
        with patch("dashboard.layouts.metric_detail.get_country_health_scores") as mock_scores:
            mock_scores.side_effect = FileNotFoundError("Database not found")
            from dashboard.layouts.metric_detail import get_metric_detail_layout

            result = get_metric_detail_layout()

            assert "Database not found" in str(result)

    def test_returns_alert_when_scores_empty(self, monkeypatch):
        """Should return an info Alert when country_scores DataFrame is empty."""
        with patch("dashboard.layouts.metric_detail.get_country_health_scores") as mock_scores:
            mock_scores.return_value = pd.DataFrame()
            from dashboard.layouts.metric_detail import get_metric_detail_layout

            result = get_metric_detail_layout()

            assert "No data available" in str(result)


class TestShutdownsLayoutErrors:
    """Error branch tests for get_shutdowns_layout()."""

    def test_returns_alert_when_db_not_found(self, monkeypatch):
        """Should return a warning Alert when database file is not found."""
        with patch("dashboard.layouts.shutdowns.get_shutdown_summary") as mock_summary:
            with patch("dashboard.layouts.shutdowns.get_shutdown_events") as mock_events:
                mock_summary.side_effect = FileNotFoundError("Database not found")
                mock_events.side_effect = FileNotFoundError("Database not found")
                from dashboard.layouts.shutdowns import get_shutdowns_layout

                result = get_shutdowns_layout()

                assert "Database not found" in str(result)

    def test_returns_alert_when_events_empty(self, monkeypatch):
        """Should return an info Alert when no shutdown events exist."""
        with patch("dashboard.layouts.shutdowns.get_shutdown_summary") as mock_summary:
            with patch("dashboard.layouts.shutdowns.get_shutdown_events") as mock_events:
                mock_summary.return_value = {
                    "total_shutdowns": 0,
                    "avg_duration": 0.0,
                    "total_gdp_impact": 0.0,
                    "avg_freedom_score": 100.0,
                }
                mock_events.return_value = pd.DataFrame()
                from dashboard.layouts.shutdowns import get_shutdowns_layout

                result = get_shutdowns_layout()

                assert "No shutdown data available" in str(result)
