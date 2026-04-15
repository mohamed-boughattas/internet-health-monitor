"""Tests for chart and visualization functions.

These tests verify the behavior of individual chart-creation functions
using sample DataFrames.
"""

from __future__ import annotations

import pandas as pd
import pytest


@pytest.fixture
def sample_timeseries_df() -> pd.DataFrame:
    """Provide a multi-date timeseries DataFrame for testing."""
    dates = ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"]
    return pd.DataFrame(
        {
            "date": pd.to_datetime(dates * 3),
            "country_code": ["US"] * 4 + ["DE"] * 4 + ["BR"] * 4,
            "https_score": [
                90.0,
                91.0,
                92.0,
                93.0,
                85.0,
                86.0,
                87.0,
                88.0,
                75.0,
                76.0,
                77.0,
                78.0,
            ],
            "ipv6_score": [50.0, 51.0, 52.0, 53.0] * 3,
            "dnssec_score": [30.0, 32.0, 34.0, 36.0] * 3,
            "roa_score": [60.0, 62.0, 64.0, 66.0] * 3,
        }
    )


class TestCreateRadarChart:
    """Tests for create_radar_chart()."""

    def test_returns_figure_for_valid_data(self, sample_country_scores) -> None:
        """Should return a go.Figure when given valid data and countries."""
        from dashboard.layouts.country_comparison import create_radar_chart

        fig = create_radar_chart(sample_country_scores, ["US", "DE"])

        assert fig is not None

    def test_returns_none_for_empty_df(self) -> None:
        """Should return None when DataFrame is empty."""
        from dashboard.layouts.country_comparison import create_radar_chart

        fig = create_radar_chart(pd.DataFrame(), ["US", "DE"])

        assert fig is None

    def test_returns_none_for_empty_countries_list(self, sample_country_scores) -> None:
        """Should return None when countries list is empty."""
        from dashboard.layouts.country_comparison import create_radar_chart

        fig = create_radar_chart(sample_country_scores, [])

        assert fig is None

    def test_returns_none_when_no_countries_match(self, sample_country_scores) -> None:
        """Should return None when no requested countries are in the DataFrame."""
        from dashboard.layouts.country_comparison import create_radar_chart

        fig = create_radar_chart(sample_country_scores, ["XX", "YY"])

        assert fig is None

    def test_returns_figure_for_single_country(self, sample_country_scores) -> None:
        """Should return a figure for a single country."""
        from dashboard.layouts.country_comparison import create_radar_chart

        fig = create_radar_chart(sample_country_scores, ["US"])

        assert fig is not None


class TestCreateComparisonBarChart:
    """Tests for create_comparison_bar_chart()."""

    def test_returns_figure_for_valid_data(self, sample_country_scores) -> None:
        """Should return a go.Figure when given valid data."""
        from dashboard.layouts.country_comparison import create_comparison_bar_chart

        fig = create_comparison_bar_chart(sample_country_scores, ["US", "DE"])

        assert fig is not None

    def test_returns_none_for_empty_df(self) -> None:
        """Should return None when DataFrame is empty."""
        from dashboard.layouts.country_comparison import create_comparison_bar_chart

        fig = create_comparison_bar_chart(pd.DataFrame(), ["US", "DE"])

        assert fig is None

    def test_returns_none_for_empty_countries_list(self, sample_country_scores) -> None:
        """Should return None when countries list is empty."""
        from dashboard.layouts.country_comparison import create_comparison_bar_chart

        fig = create_comparison_bar_chart(sample_country_scores, [])

        assert fig is None

    def test_figure_has_two_hline_shapes(self, sample_country_scores) -> None:
        """Should have reference lines at y=50 and y=80."""
        from dashboard.layouts.country_comparison import create_comparison_bar_chart

        fig = create_comparison_bar_chart(sample_country_scores, ["US", "DE"])
        assert fig is not None
        shapes = [s for s in fig.layout.shapes if s.y0 is not None]
        hlines = [s for s in shapes if s.y0 == s.y1 and isinstance(s.y0, (int, float))]
        assert len(hlines) >= 2


class TestCreateTimeseriesChart:
    """Tests for create_timeseries_chart()."""

    def test_returns_figure_for_valid_data(self, sample_timeseries_df) -> None:
        """Should return a go.Figure for valid timeseries data."""
        from dashboard.layouts.timeseries import create_timeseries_chart

        fig = create_timeseries_chart(sample_timeseries_df, "US", "https")

        assert fig is not None

    def test_returns_none_for_empty_df(self) -> None:
        """Should return None when DataFrame is empty."""
        from dashboard.layouts.timeseries import create_timeseries_chart

        fig = create_timeseries_chart(pd.DataFrame(), "US", "https")

        assert fig is None

    def test_returns_none_for_country_not_in_df(self, sample_timeseries_df) -> None:
        """Should return None when country_code is not in the DataFrame."""
        from dashboard.layouts.timeseries import create_timeseries_chart

        fig = create_timeseries_chart(sample_timeseries_df, "XX", "https")

        assert fig is None

    def test_returns_none_when_score_column_missing(self, sample_timeseries_df) -> None:
        """Should return None when the metric score column is missing."""
        from dashboard.layouts.timeseries import create_timeseries_chart

        fig = create_timeseries_chart(sample_timeseries_df, "US", "invalid_metric")

        assert fig is None

    def test_figure_yaxis_range_is_0_to_100(self, sample_timeseries_df) -> None:
        """Y-axis range should be [0, 100]."""
        from dashboard.layouts.timeseries import create_timeseries_chart

        fig = create_timeseries_chart(sample_timeseries_df, "US", "https")
        assert fig is not None
        assert fig.layout.yaxis.range == (0, 100)


class TestCreateMultiCountryChart:
    """Tests for create_multi_country_chart()."""

    def test_returns_figure_for_valid_data(self, sample_timeseries_df) -> None:
        """Should return a go.Figure for valid data."""
        from dashboard.layouts.timeseries import create_multi_country_chart

        fig = create_multi_country_chart(sample_timeseries_df, ["US", "DE"], "https")

        assert fig is not None

    def test_returns_none_for_empty_df(self) -> None:
        """Should return None when DataFrame is empty."""
        from dashboard.layouts.timeseries import create_multi_country_chart

        fig = create_multi_country_chart(pd.DataFrame(), ["US", "DE"], "https")

        assert fig is None

    def test_returns_none_for_empty_countries_list(self, sample_timeseries_df) -> None:
        """Should return None when countries list is empty."""
        from dashboard.layouts.timeseries import create_multi_country_chart

        fig = create_multi_country_chart(sample_timeseries_df, [], "https")

        assert fig is None

    def test_returns_none_when_score_column_missing(self, sample_timeseries_df) -> None:
        """Should return None when the metric score column is missing."""
        from dashboard.layouts.timeseries import create_multi_country_chart

        fig = create_multi_country_chart(sample_timeseries_df, ["US", "DE"], "invalid")

        assert fig is None


class TestCreateMetricRanking:
    """Tests for create_metric_ranking()."""

    def test_returns_figure_for_valid_data(self, sample_country_scores) -> None:
        """Should return a go.Figure for valid data."""
        from dashboard.layouts.metric_detail import create_metric_ranking

        fig = create_metric_ranking(sample_country_scores, "https")

        assert fig is not None

    def test_returns_none_for_empty_df(self) -> None:
        """Should return None when DataFrame is empty."""
        from dashboard.layouts.metric_detail import create_metric_ranking

        fig = create_metric_ranking(pd.DataFrame(), "https")

        assert fig is None

    def test_returns_none_when_score_column_missing(self, sample_country_scores) -> None:
        """Should return None when the score column is missing."""
        from dashboard.layouts.metric_detail import create_metric_ranking

        fig = create_metric_ranking(sample_country_scores, "invalid")

        assert fig is None

    def test_figure_has_vline_at_50(self, sample_country_scores) -> None:
        """Should have a vertical reference line at x=50."""
        from dashboard.layouts.metric_detail import create_metric_ranking

        fig = create_metric_ranking(sample_country_scores, "https")
        assert fig is not None
        vlines = [s for s in fig.layout.shapes if hasattr(s, "x0") and s.x0 == 50]
        assert len(vlines) >= 1


class TestCreateDistributionChart:
    """Tests for create_distribution_chart()."""

    def test_returns_figure_for_valid_data(self, sample_country_scores) -> None:
        """Should return a go.Figure for valid data."""
        from dashboard.layouts.metric_detail import create_distribution_chart

        fig = create_distribution_chart(sample_country_scores, "https")

        assert fig is not None

    def test_returns_none_for_empty_df(self) -> None:
        """Should return None when DataFrame is empty."""
        from dashboard.layouts.metric_detail import create_distribution_chart

        fig = create_distribution_chart(pd.DataFrame(), "https")

        assert fig is None

    def test_returns_none_when_score_column_missing(self, sample_country_scores) -> None:
        """Should return None when the score column is missing."""
        from dashboard.layouts.metric_detail import create_distribution_chart

        fig = create_distribution_chart(sample_country_scores, "invalid")

        assert fig is None

    def test_figure_xaxis_range_is_0_to_100(self, sample_country_scores) -> None:
        """X-axis range should be [0, 100]."""
        from dashboard.layouts.metric_detail import create_distribution_chart

        fig = create_distribution_chart(sample_country_scores, "https")
        assert fig is not None
        assert fig.layout.xaxis.range == (0, 100)


class TestBuildCountryDetailCards:
    """Tests for build_country_detail_cards()."""

    def test_returns_cards_for_existing_country(self, sample_country_scores) -> None:
        """Should return a list of cards for a country in the DataFrame."""
        from dashboard.layouts.metric_detail import build_country_detail_cards

        cards = build_country_detail_cards(sample_country_scores, "US")

        assert len(cards) == 4

    def test_returns_alert_for_nonexistent_country(self, sample_country_scores) -> None:
        """Should return an Alert component when country is not in DataFrame."""
        from dashboard.layouts.metric_detail import build_country_detail_cards

        cards = build_country_detail_cards(sample_country_scores, "XX")

        assert len(cards) == 1

    def test_skips_metrics_with_nan_scores(self) -> None:
        """Should skip metrics where the score is NaN."""
        from dashboard.layouts.metric_detail import build_country_detail_cards

        df = pd.DataFrame(
            {
                "country_code": ["XX"],
                "health_score": [50.0],
                "ipv6_score": [50.0],
                "https_score": [pd.NA],
                "dnssec_score": [50.0],
                "roa_score": [50.0],
                "date": pd.to_datetime(["2024-01-01"]),
            }
        )
        cards = build_country_detail_cards(df, "XX")

        assert len(cards) == 3
