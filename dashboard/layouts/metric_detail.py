"""Metric detail page layout.

This module provides the layout and chart components for the
Metric Detail page in the dashboard.
"""

from __future__ import annotations

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html

from dashboard.components.kpi_card import create_kpi_card, score_to_color
from dashboard.constants import COUNTRY_OPTIONS, METRICS, TRACKED_COUNTRIES
from dashboard.data.queries import get_country_health_scores


def get_metric_detail_layout() -> dbc.Container | dbc.Alert:
    """Get the metric detail page layout.

    Returns:
        A Dash Container with the metric detail UI, or an Alert if
        data is unavailable.
    """
    try:
        country_scores = get_country_health_scores()
    except Exception:
        return dbc.Alert(
            "Database not found. Please run the pipeline first with 'just run-pipeline'.",
            color="warning",
            className="mt-4",
        )

    if country_scores.empty:
        return dbc.Alert(
            "No data available. Please run the pipeline to ingest data.",
            color="info",
            className="mt-4",
        )

    control_panel = dbc.Card(
        dbc.CardBody(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Label("Select Metric", className="fw-bold mb-2 d-block"),
                                dcc.Dropdown(
                                    id="metric-selector",
                                    options=METRICS,
                                    value="ipv6",
                                    clearable=False,
                                    className="mb-3",
                                ),
                            ],
                            md=6,
                        ),
                        dbc.Col(
                            [
                                html.Label("Select Country", className="fw-bold mb-2 d-block"),
                                dcc.Dropdown(
                                    id="detail-country-selector",
                                    options=COUNTRY_OPTIONS,
                                    value="US",
                                    clearable=False,
                                    className="mb-3",
                                ),
                            ],
                            md=6,
                        ),
                    ]
                )
            ]
        ),
        className="mb-4",
    )

    return dbc.Container(
        [
            html.H2("Metric Detail Analysis", className="mb-4"),
            control_panel,
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H4("Geographic Distribution", className="mb-3"),
                            dcc.Loading(
                                dcc.Graph(id="metric-map", style={"height": "400px"}),
                                type="circle",
                            ),
                        ],
                        md=8,
                    ),
                    dbc.Col(
                        [
                            html.H4("Country Rankings", className="mb-3"),
                            dcc.Loading(
                                dcc.Graph(id="ranking-chart", style={"height": "400px"}),
                                type="circle",
                            ),
                        ],
                        md=4,
                    ),
                ],
                className="mb-4",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H4("Score Breakdown", className="mb-3"),
                            dcc.Loading(
                                dcc.Graph(id="distribution-chart", style={"height": "350px"}),
                                type="circle",
                            ),
                        ],
                        md=6,
                    ),
                    dbc.Col(
                        [
                            html.H4("Country Detail", className="mb-3"),
                            html.Div(id="country-detail-cards"),
                        ],
                        md=6,
                    ),
                ],
                className="mb-4",
            ),
        ],
        fluid=True,
    )


def create_metric_ranking(df: pd.DataFrame, metric: str) -> go.Figure | None:
    """Create a horizontal bar chart ranking countries by metric.

    Args:
        df: DataFrame containing country health scores.
        metric: Metric name to visualize (e.g., 'ipv6', 'https').

    Returns:
        A Plotly Figure object configured as a horizontal bar chart,
        or None if no valid data is available.
    """
    if df.empty:
        return None

    score_col = f"{metric}_score"

    if score_col not in df.columns:
        return None

    df_sorted = df.sort_values(score_col, ascending=True).tail(20)

    fig = px.bar(
        df_sorted,
        y="country_code",
        x=score_col,
        orientation="h",
        title=f"Country Rankings - {metric.upper()}",
        labels={"country_code": "Country", score_col: "Score"},
    )

    fig.update_layout(yaxis={"categoryorder": "total ascending"}, xaxis={"range": [0, 100]})
    fig.add_vline(x=50, line_dash="dash", line_color="gray", opacity=0.7)

    return fig


def create_distribution_chart(df: pd.DataFrame, metric: str) -> go.Figure | None:
    """Create a score breakdown chart for the selected metric.

    Displays each country's score as a horizontal bar for the chosen metric.
    More meaningful than a histogram when tracking only 5 countries.

    Args:
        df: DataFrame containing country health scores.
        metric: Metric name to visualize.

    Returns:
        A Plotly Figure object configured as a horizontal bar chart,
        or None if no valid data is available.
    """
    if df.empty:
        return None

    score_col = f"{metric}_score"

    if score_col not in df.columns:
        return None

    df_sorted = df.sort_values(score_col, ascending=True)

    fig = px.bar(
        df_sorted,
        y="country_code",
        x=score_col,
        orientation="h",
        title=f"{metric.upper()} Score by Country",
        labels={"country_code": "Country", score_col: "Score"},
        color=score_col,
        color_continuous_scale="RdYlGn",
        range_x=[0, 100],
    )

    fig.update_layout(
        showlegend=False,
        xaxis={"range": [0, 100]},
        yaxis={"categoryorder": "total ascending"},
    )

    return fig


def build_country_detail_cards(df: pd.DataFrame, country_code: str) -> list[dbc.Col | dbc.Alert]:
    """Build KPI cards for a specific country's all metric scores.

    Args:
        df: DataFrame containing country health scores.
        country_code: ISO 3166-1 alpha-2 country code.

    Returns:
        A list of dbc.Col elements, each containing a KPI card.
    """
    row = df[df["country_code"] == country_code]
    if row.empty:
        return [dbc.Alert("No data for selected country.", color="secondary")]

    row = row.iloc[0]
    country_name = TRACKED_COUNTRIES.get(country_code, country_code)

    cards = []
    for metric, label in [
        ("ipv6", "IPv6"),
        ("https", "HTTPS"),
        ("dnssec", "DNSSEC"),
        ("roa", "ROA/RPKI"),
    ]:
        score_col = f"{metric}_score"
        if score_col in row and pd.notna(row[score_col]):
            score = float(row[score_col])
            cards.append(
                dbc.Col(
                    create_kpi_card(
                        label,
                        f"{score:.1f}%",
                        country_name,
                        color=score_to_color(score),
                    ),
                    md=3,
                )
            )

    return cards  # pyrefly: ignore[bad-return]
