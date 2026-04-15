"""Tests for dashboard data query functions.

These tests use a session-scoped DuckDB fixture to test the actual
SQL behavior of all query functions. The fixture creates a temporary
database with realistic test data matching the pipeline schema.

Note: Country count assertions are derived from TRACKED_COUNTRIES to avoid
hardcoding. Adding a new country requires no test changes.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pandas as pd
import pytest

from dashboard.constants import TRACKED_COUNTRIES


@pytest.fixture
def patched_db_path(duckdb_test_db: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    """Patch dashboard.data.queries.DB_PATH to use the test database."""
    from dashboard.data import queries

    db_path = Path(duckdb_test_db)
    monkeypatch.setattr(queries, "DB_PATH", db_path)
    yield db_path


@pytest.fixture
def patched_empty_db(duckdb_empty_db: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    """Patch DB_PATH to use the empty test database."""
    from dashboard.data import queries

    db_path = Path(duckdb_empty_db)
    monkeypatch.setattr(queries, "DB_PATH", db_path)
    yield db_path


class TestGetGlobalHealthSummary:
    """Tests for get_global_health_summary()."""

    def test_returns_correct_columns(self, patched_db_path) -> None:
        """Should return a DataFrame with all required columns."""
        from dashboard.data.queries import get_global_health_summary

        df = get_global_health_summary()

        assert isinstance(df, pd.DataFrame)
        assert "ipv6_score" in df.columns
        assert "https_score" in df.columns
        assert "dnssec_score" in df.columns
        assert "roa_score" in df.columns
        assert "global_health_score" in df.columns

    def test_global_health_score_is_weighted_average(self, patched_db_path) -> None:
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

    def test_returns_single_row(self, patched_db_path) -> None:
        """Should return exactly one row (the global aggregate)."""
        from dashboard.data.queries import get_global_health_summary

        df = get_global_health_summary()

        assert len(df) == 1

    def test_scores_within_0_to_100(self, patched_db_path) -> None:
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

    def test_returns_all_columns(self, patched_db_path) -> None:
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

    def test_returns_sorted_desc(self, patched_db_path) -> None:
        """Results should be sorted by health_score in descending order."""
        from dashboard.data.queries import get_country_health_scores

        df = get_country_health_scores()

        scores = df["health_score"].tolist()
        assert scores == sorted(scores, reverse=True)

    def test_top_country_has_highest_score(self, patched_db_path) -> None:
        """First entry should have the highest health score."""
        from dashboard.data.queries import get_country_health_scores

        df = get_country_health_scores()

        assert df.iloc[0]["health_score"] == df["health_score"].max()


class TestGetCountryList:
    """Tests for get_country_list()."""

    def test_returns_sorted_list(self, patched_db_path) -> None:
        """Should return a sorted list of country codes."""
        from dashboard.data.queries import get_country_list

        result = get_country_list()

        assert result == sorted(result)

    def test_returns_n_entries(self, patched_db_path) -> None:
        """Should return one entry per tracked country."""
        from dashboard.data.queries import get_country_list

        result = get_country_list()

        assert len(result) == len(TRACKED_COUNTRIES)

    def test_contains_expected_codes(self, patched_db_path) -> None:
        """Should contain all 5 tracked country codes."""
        from dashboard.data.queries import get_country_list

        result = get_country_list()

        for code in ["US", "DE", "BR", "IN", "JP"]:
            assert code in result


class TestGetDailyMetricTimeseries:
    """Tests for get_daily_metric_timeseries()."""

    def test_valid_metric_returns_data(self, patched_db_path) -> None:
        """A valid metric should return a DataFrame with date, country_code, {metric}_score."""
        from dashboard.data.queries import get_daily_metric_timeseries

        df = get_daily_metric_timeseries(metric="https")

        assert isinstance(df, pd.DataFrame)
        assert "date" in df.columns
        assert "country_code" in df.columns
        assert "https_score" in df.columns

    def test_invalid_metric_returns_empty_df(self, patched_db_path) -> None:
        """An invalid metric name should return an empty DataFrame."""
        from dashboard.data.queries import get_daily_metric_timeseries

        df = get_daily_metric_timeseries(metric="invalid_metric")

        assert df.empty

    def test_filters_by_country_code(self, patched_db_path) -> None:
        """When country_code is provided, should only return rows for that country."""
        from dashboard.data.queries import get_daily_metric_timeseries

        df = get_daily_metric_timeseries(metric="https", country_code="US")

        assert all(df["country_code"] == "US")
        assert len(df) == 3

    def test_all_countries_when_no_filter(self, patched_db_path) -> None:
        """When country_code is None, should return data for all tracked countries."""
        from dashboard.data.queries import get_daily_metric_timeseries

        df = get_daily_metric_timeseries(metric="https")

        assert df["country_code"].nunique() == len(TRACKED_COUNTRIES)

    def test_ipv6_metric(self, patched_db_path) -> None:
        """IPv6 metric should return ipv6_score column."""
        from dashboard.data.queries import get_daily_metric_timeseries

        df = get_daily_metric_timeseries(metric="ipv6")

        assert "ipv6_score" in df.columns

    def test_dnssec_metric(self, patched_db_path) -> None:
        """DNSSEC metric should return dnssec_score column."""
        from dashboard.data.queries import get_daily_metric_timeseries

        df = get_daily_metric_timeseries(metric="dnssec")

        assert "dnssec_score" in df.columns

    def test_roa_metric(self, patched_db_path) -> None:
        """ROA metric should return roa_score column."""
        from dashboard.data.queries import get_daily_metric_timeseries

        df = get_daily_metric_timeseries(metric="roa")

        assert "roa_score" in df.columns


class TestGetTopBottomCountries:
    """Tests for get_top_bottom_countries()."""

    def test_returns_dict_with_top_and_bottom_keys(self, patched_db_path) -> None:
        """Should return a dict with 'top' and 'bottom' keys."""
        from dashboard.data.queries import get_top_bottom_countries

        result = get_top_bottom_countries()

        assert isinstance(result, dict)
        assert "top" in result
        assert "bottom" in result

    def test_default_n_returns_5_entries_each(self, patched_db_path) -> None:
        """Default n=5 should return up to 5 entries in top and bottom."""
        from dashboard.data.queries import get_top_bottom_countries

        result = get_top_bottom_countries()

        assert len(result["top"]) <= 5
        assert len(result["bottom"]) <= 5

    def test_custom_n(self, patched_db_path) -> None:
        """Custom n value should limit the number of entries."""
        from dashboard.data.queries import get_top_bottom_countries

        result = get_top_bottom_countries(n=2)

        assert len(result["top"]) == 2
        assert len(result["bottom"]) == 2

    def test_top_has_highest_score(self, patched_db_path) -> None:
        """Top entries should have the highest health scores."""
        from dashboard.data.queries import get_top_bottom_countries

        result = get_top_bottom_countries(n=5)
        top_scores = [c["health_score"] for c in result["top"]]

        assert top_scores == sorted(top_scores, reverse=True)

    def test_bottom_has_lowest_score(self, patched_db_path) -> None:
        """Bottom entries should have the lowest health scores."""
        from dashboard.data.queries import get_top_bottom_countries

        result = get_top_bottom_countries(n=5)
        bottom_scores = [c["health_score"] for c in result["bottom"]]

        assert bottom_scores == sorted(bottom_scores, reverse=True)


class TestGetLastUpdated:
    """Tests for get_last_updated()."""

    def test_returns_date_string_when_data_exists(self, patched_db_path) -> None:
        """Should return a date string (not 'Never') when data exists."""
        from dashboard.data.queries import get_last_updated

        result = get_last_updated()

        assert result != "Never"
        assert "2024" in result


class TestEdgeCases:
    """Edge case tests using the empty database fixture."""

    def test_db_connection_raises_file_not_found(self, monkeypatch) -> None:
        """_db_connection should raise FileNotFoundError when DB does not exist."""
        from dashboard.data import queries

        monkeypatch.setattr(queries, "DB_PATH", Path("/nonexistent/path/db.db"))
        from dashboard.data.queries import _db_connection

        with pytest.raises(FileNotFoundError):
            with _db_connection():
                pass

    def test_get_last_updated_returns_never_on_missing_db(self, monkeypatch) -> None:
        """Should return 'Never' when database file does not exist."""
        from dashboard.data import queries

        monkeypatch.setattr(queries, "DB_PATH", Path("/nonexistent/path/db.db"))
        from dashboard.data.queries import get_last_updated

        result = get_last_updated()
        assert result == "Never"

    def test_get_global_health_summary_with_empty_db(self, patched_empty_db) -> None:
        """Should return DataFrame with NaN values when table is empty."""
        from math import isnan

        from dashboard.data.queries import get_global_health_summary

        df = get_global_health_summary()

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1
        assert isnan(df.iloc[0]["ipv6_score"])

    def test_get_country_list_with_empty_db(self, patched_empty_db) -> None:
        """Should return tracked country codes sorted, regardless of DB state."""
        from dashboard.data.queries import get_country_list

        result = get_country_list()
        assert result == sorted(TRACKED_COUNTRIES.keys())
