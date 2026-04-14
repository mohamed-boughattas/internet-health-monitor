"""Tests for dashboard data query functions.

These tests use a session-scoped DuckDB fixture to test the actual
SQL behavior of all query functions. The fixture creates a temporary
database with realistic test data matching the pipeline schema.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest


@pytest.fixture
def patched_db_path(duckdb_test_db, monkeypatch):
    """Patch dashboard.data.queries.DB_PATH to use the test database."""
    from dashboard.data import queries

    db_path = Path(duckdb_test_db)
    monkeypatch.setattr(queries, "DB_PATH", db_path)
    yield db_path


@pytest.fixture
def patched_empty_db(duckdb_empty_db, monkeypatch):
    """Patch DB_PATH to use the empty test database."""
    from dashboard.data import queries

    db_path = Path(duckdb_empty_db)
    monkeypatch.setattr(queries, "DB_PATH", db_path)
    yield db_path


class TestGetGlobalHealthSummary:
    """Tests for get_global_health_summary()."""

    def test_returns_correct_columns(self, patched_db_path):
        """Should return a DataFrame with all required columns."""
        from dashboard.data.queries import get_global_health_summary

        df = get_global_health_summary()

        assert isinstance(df, pd.DataFrame)
        assert "ipv6_score" in df.columns
        assert "https_score" in df.columns
        assert "dnssec_score" in df.columns
        assert "roa_score" in df.columns
        assert "global_health_score" in df.columns

    def test_global_health_score_is_weighted_average(self, patched_db_path, sample_country_scores):
        """global_health_score should equal AVG of 4 metrics weighted 0.25 each."""
        from dashboard.data.queries import get_global_health_summary

        df = get_global_health_summary()
        row = df.iloc[0]

        expected_global = (
            (row["ipv6_score"] * 0.25)
            + (row["https_score"] * 0.25)
            + (row["dnssec_score"] * 0.25)
            + (row["roa_score"] * 0.25)
        )
        assert abs(row["global_health_score"] - expected_global) < 0.01

    def test_returns_single_row(self, patched_db_path):
        """Should return exactly one row (the global aggregate)."""
        from dashboard.data.queries import get_global_health_summary

        df = get_global_health_summary()

        assert len(df) == 1

    def test_scores_within_0_to_100(self, patched_db_path):
        """All score columns should be within 0-100 range."""
        from dashboard.data.queries import get_global_health_summary

        df = get_global_health_summary()
        row = df.iloc[0]

        for col in [
            "ipv6_score",
            "https_score",
            "dnssec_score",
            "roa_score",
            "global_health_score",
        ]:
            assert 0 <= row[col] <= 100


class TestGetCountryHealthScores:
    """Tests for get_country_health_scores()."""

    def test_returns_all_columns(self, patched_db_path):
        """Should return a DataFrame with all required columns."""
        from dashboard.data.queries import get_country_health_scores

        df = get_country_health_scores()

        expected = {
            "country_code",
            "health_score",
            "ipv6_score",
            "https_score",
            "dnssec_score",
            "roa_score",
            "date",
        }
        assert set(df.columns) == expected

    def test_sorted_by_health_score_desc(self, patched_db_path):
        """Results should be sorted by health_score in descending order."""
        from dashboard.data.queries import get_country_health_scores

        df = get_country_health_scores()

        scores = df["health_score"].tolist()
        assert scores == sorted(scores, reverse=True)

    def test_returns_5_rows(self, patched_db_path):
        """Should return exactly 5 rows (one per tracked country)."""
        from dashboard.data.queries import get_country_health_scores

        df = get_country_health_scores()

        assert len(df) == 5

    def test_top_country_de(self, patched_db_path):
        """DE has the highest score (80.1) so should be first."""
        from dashboard.data.queries import get_country_health_scores

        df = get_country_health_scores()

        assert df.iloc[0]["country_code"] == "DE"
        assert df.iloc[0]["health_score"] == 80.1


class TestGetCountryList:
    """Tests for get_country_list()."""

    def test_returns_sorted_list(self, patched_db_path):
        """Should return a sorted list of country codes."""
        from dashboard.data.queries import get_country_list

        result = get_country_list()

        assert result == sorted(result)

    def test_returns_5_entries(self, patched_db_path):
        """Should return exactly 5 country codes."""
        from dashboard.data.queries import get_country_list

        result = get_country_list()

        assert len(result) == 5

    def test_contains_expected_codes(self, patched_db_path):
        """Should contain all 5 tracked country codes."""
        from dashboard.data.queries import get_country_list

        result = get_country_list()

        for code in ["US", "DE", "BR", "IN", "JP"]:
            assert code in result


class TestGetDailyMetricTimeseries:
    """Tests for get_daily_metric_timeseries()."""

    def test_valid_metric_returns_data(self, patched_db_path):
        """A valid metric should return a DataFrame with date, country_code, {metric}_score."""
        from dashboard.data.queries import get_daily_metric_timeseries

        df = get_daily_metric_timeseries(metric="https")

        assert isinstance(df, pd.DataFrame)
        assert "date" in df.columns
        assert "country_code" in df.columns
        assert "https_score" in df.columns

    def test_invalid_metric_returns_empty_df(self, patched_db_path):
        """An invalid metric name should return an empty DataFrame."""
        from dashboard.data.queries import get_daily_metric_timeseries

        df = get_daily_metric_timeseries(metric="invalid_metric")

        assert df.empty

    def test_filters_by_country_code(self, patched_db_path):
        """When country_code is provided, should only return rows for that country."""
        from dashboard.data.queries import get_daily_metric_timeseries

        df = get_daily_metric_timeseries(metric="https", country_code="US")

        assert all(df["country_code"] == "US")
        assert len(df) == 3

    def test_all_countries_when_no_filter(self, patched_db_path):
        """When country_code is None, should return data for all countries."""
        from dashboard.data.queries import get_daily_metric_timeseries

        df = get_daily_metric_timeseries(metric="https")

        assert df["country_code"].nunique() == 5

    def test_ipv6_metric(self, patched_db_path):
        """IPv6 metric should return ipv6_score column."""
        from dashboard.data.queries import get_daily_metric_timeseries

        df = get_daily_metric_timeseries(metric="ipv6")

        assert "ipv6_score" in df.columns

    def test_dnssec_metric(self, patched_db_path):
        """DNSSEC metric should return dnssec_score column."""
        from dashboard.data.queries import get_daily_metric_timeseries

        df = get_daily_metric_timeseries(metric="dnssec")

        assert "dnssec_score" in df.columns

    def test_roa_metric(self, patched_db_path):
        """ROA metric should return roa_score column."""
        from dashboard.data.queries import get_daily_metric_timeseries

        df = get_daily_metric_timeseries(metric="roa")

        assert "roa_score" in df.columns


class TestGetTopBottomCountries:
    """Tests for get_top_bottom_countries()."""

    def test_returns_dict_with_top_and_bottom_keys(self, patched_db_path):
        """Should return a dict with 'top' and 'bottom' keys."""
        from dashboard.data.queries import get_top_bottom_countries

        result = get_top_bottom_countries()

        assert isinstance(result, dict)
        assert "top" in result
        assert "bottom" in result

    def test_default_n_returns_5_entries_each(self, patched_db_path):
        """Default n=5 should return up to 5 entries in top and bottom."""
        from dashboard.data.queries import get_top_bottom_countries

        result = get_top_bottom_countries()

        assert len(result["top"]) <= 5
        assert len(result["bottom"]) <= 5

    def test_custom_n(self, patched_db_path):
        """Custom n value should limit the number of entries."""
        from dashboard.data.queries import get_top_bottom_countries

        result = get_top_bottom_countries(n=2)

        assert len(result["top"]) == 2
        assert len(result["bottom"]) == 2

    def test_top_has_highest_score(self, patched_db_path):
        """Top entries should have the highest health scores."""
        from dashboard.data.queries import get_top_bottom_countries

        result = get_top_bottom_countries(n=5)
        top_scores = [c["health_score"] for c in result["top"]]

        assert top_scores == sorted(top_scores, reverse=True)

    def test_bottom_has_lowest_score(self, patched_db_path):
        """Bottom entries should have the lowest health scores."""
        from dashboard.data.queries import get_top_bottom_countries

        result = get_top_bottom_countries(n=5)
        bottom_scores = [c["health_score"] for c in result["bottom"]]

        assert bottom_scores == sorted(bottom_scores, reverse=True)


class TestGetNetLossData:
    """Tests for get_net_loss_data()."""

    def test_returns_expected_columns(self, patched_db_path):
        """Should return a DataFrame with all required columns."""
        from dashboard.data.queries import get_net_loss_data

        df = get_net_loss_data()

        for col in ["date", "country", "duration", "shutdown__gdp", "freedom_score"]:
            assert col in df.columns

    def test_sorted_by_date_desc(self, patched_db_path):
        """Should be sorted by date in descending order."""
        from dashboard.data.queries import get_net_loss_data

        df = get_net_loss_data()

        dates = df["date"].tolist()
        assert dates == sorted(dates, reverse=True)

    def test_has_3_events(self, patched_db_path):
        """Should return 3 shutdown events from test data."""
        from dashboard.data.queries import get_net_loss_data

        df = get_net_loss_data()

        assert len(df) == 3


class TestGetShutdownSummary:
    """Tests for get_shutdown_summary()."""

    def test_returns_dict_with_all_keys(self, patched_db_path):
        """Should return a dict with all 4 expected keys."""
        from dashboard.data.queries import get_shutdown_summary

        result = get_shutdown_summary()

        assert "total_shutdowns" in result
        assert "avg_duration" in result
        assert "total_gdp_impact" in result
        assert "avg_freedom_score" in result

    def test_total_shutdowns_is_int(self, patched_db_path):
        """total_shutdowns should be an integer."""
        from dashboard.data.queries import get_shutdown_summary

        result = get_shutdown_summary()

        assert isinstance(result["total_shutdowns"], int)

    def test_values_are_reasonable(self, patched_db_path):
        """Values should be within expected ranges."""
        from dashboard.data.queries import get_shutdown_summary

        result = get_shutdown_summary()

        assert result["total_shutdowns"] == 3
        assert result["total_gdp_impact"] > 0
        assert 0 <= result["avg_freedom_score"] <= 100


class TestGetShutdownEvents:
    """Tests for get_shutdown_events()."""

    def test_maps_country_names_to_codes(self, patched_db_path):
        """Should map country names (e.g. 'United States') to ISO codes ('US')."""
        from dashboard.data.queries import get_shutdown_events

        df = get_shutdown_events()

        assert "country_code" in df.columns
        us_row = df[df["country"] == "United States"]
        assert len(us_row) == 1
        assert us_row.iloc[0]["country_code"] == "US"

    def test_has_country_code_column(self, patched_db_path):
        """Should add a country_code column via mapping."""
        from dashboard.data.queries import get_shutdown_events

        df = get_shutdown_events()

        assert "country_code" in df.columns


class TestGetLastUpdated:
    """Tests for get_last_updated()."""

    def test_returns_date_string_when_data_exists(self, patched_db_path):
        """Should return a date string (not 'Never') when data exists."""
        from dashboard.data.queries import get_last_updated

        result = get_last_updated()

        assert result != "Never"
        assert "2024" in result


class TestEdgeCases:
    """Edge case tests using the empty database fixture."""

    def test_db_connection_raises_file_not_found(self, monkeypatch):
        """_db_connection should raise FileNotFoundError when DB does not exist."""
        from dashboard.data import queries

        monkeypatch.setattr(queries, "DB_PATH", Path("/nonexistent/path/db.db"))
        from dashboard.data.queries import _db_connection

        with pytest.raises(FileNotFoundError):
            with _db_connection():
                pass

    def test_get_last_updated_returns_never_on_missing_db(self, monkeypatch):
        """Should return 'Never' when database file does not exist."""
        from dashboard.data import queries

        monkeypatch.setattr(queries, "DB_PATH", Path("/nonexistent/path/db.db"))
        from dashboard.data.queries import get_last_updated

        result = get_last_updated()
        assert result == "Never"

    def test_get_global_health_summary_with_empty_db(self, patched_empty_db):
        """Should return DataFrame with NaN values when table is empty."""
        from math import isnan

        from dashboard.data.queries import get_global_health_summary

        df = get_global_health_summary()

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1
        assert isnan(df.iloc[0]["ipv6_score"])

    def test_get_country_list_with_empty_db(self, patched_empty_db):
        """Should return empty list when country_rankings is empty."""
        from dashboard.data.queries import get_country_list

        result = get_country_list()
        assert result == []

    def test_get_shutdown_summary_with_empty_db(self, patched_empty_db):
        """Should return default dict values when net_loss table is empty."""
        from dashboard.data.queries import get_shutdown_summary

        result = get_shutdown_summary()
        assert result["total_shutdowns"] == 0
        assert result["avg_freedom_score"] == 100.0
