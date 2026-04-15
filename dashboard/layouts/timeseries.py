"""Time series page layout.

This module provides the layout and chart components for the
Trends (Time Series) page in the dashboard.
"""

from __future__ import annotations

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html

from dashboard.constants import COUNTRY_OPTIONS, METRICS
from dashboard.data.queries import get_country_list


def get_timeseries_layout() -> dbc.Container | dbc.Alert:
    """Get the time series page layout.

    Returns:
        A Dash Container with the timeseries UI, or an Alert if
        data is unavailable.
    """
    try:
        country_list = get_country_list()
    except Exception:
        return dbc.Alert(
            "Database not found. Please run the pipeline first with 'just run-pipeline'.",
            color="warning",
            className="mt-4",
        )

    default_country = country_list[0] if country_list else None

    if not country_list:
        return dbc.Alert(
            "No countries available. Please run the pipeline to ingest data.",
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
                                html.Label("Country", className="fw-bold"),
                                dcc.Dropdown(
                                    id="timeseries-country",
                                    options=COUNTRY_OPTIONS,
                                    value=default_country,
                                    clearable=False,
                                ),
                            ],
                            md=4,
                        ),
                        dbc.Col(
                            [
                                html.Label("Metric", className="fw-bold"),
                                dcc.Dropdown(
                                    id="timeseries-metric",
                                    options=METRICS,
                                    value="ipv6",
                                    clearable=False,
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
            html.H2("Internet Health Trends", className="mb-4"),
            control_panel,
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H4("Single Country Trend", className="mb-3"),
                            dcc.Loading(
                                dcc.Graph(id="timeseries-chart", style={"height": "400px"}),
                                type="circle",
                            ),
                        ],
                        md=12,
                    ),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H4("Multi-Country Comparison", className="mb-3"),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dcc.Dropdown(
                                            id="multi-country-selector",
                                            options=COUNTRY_OPTIONS,
                                            value=["US", "DE", "JP"],
                                            multi=True,
                                            placeholder="Select countries to compare",
                                            className="mb-3",
                                        ),
                                        md=10,
                                    ),
                                    dbc.Col(
                                        html.Button(
                                            "Download CSV",
                                            id="trend-download-btn",
                                            className="btn btn-outline-primary btn-sm",
                                            style={"margin-top": "4px"},
                                        ),
                                        md=2,
                                    ),
                                ],
                                className="mb-3",
                            ),
                            dcc.Loading(
                                dcc.Graph(id="multi-country-chart", style={"height": "400px"}),
                                type="circle",
                            ),
                        ],
                        md=12,
                    ),
                ]
            ),
            dcc.Download(id="trend-download"),
        ],
        fluid=True,
    )


def create_timeseries_chart(df: pd.DataFrame, country_code: str, metric: str) -> go.Figure | None:
    """Create a line chart for a specific country and metric.

    Args:
        df: DataFrame containing time series metric data.
        country_code: ISO 3166-1 alpha-2 country code.
        metric: Metric name to visualize.

    Returns:
        A Plotly Figure object configured as a line chart,
        or None if no valid data is available.
    """
    if df.empty:
        return None

    score_col = f"{metric}_score"

    df_filtered = df[df["country_code"] == country_code].copy()

    if df_filtered.empty or score_col not in df_filtered.columns:
        return None

    fig = px.line(
        df_filtered,
        x="date",
        y=score_col,
        title=f"{metric.upper()} - {country_code}",
        labels={score_col: f"{metric.upper()} Score", "date": "Date"},
    )

    fig.update_traces(mode="lines+markers")
    fig.update_layout(yaxis={"range": [0, 100]}, hovermode="x unified")

    if metric == "ipv6":
        fig.add_annotation(
            text="Note: IPv6 data is monthly resolution",
            xref="paper",
            yref="paper",
            x=0.5,
            y=-0.15,
            showarrow=False,
            font={"size": 10, "color": "gray"},
            align="center",
        )

    return fig


def create_multi_country_chart(
    df: pd.DataFrame, countries: list[str], metric: str
) -> go.Figure | None:
    """Create a line chart comparing multiple countries.

    Args:
        df: DataFrame containing time series metric data.
        countries: List of country codes to include.
        metric: Metric name to visualize.

    Returns:
        A Plotly Figure object configured as a multi-country line chart,
        or None if no valid data is available.
    """
    if df.empty or not countries:
        return None

    score_col = f"{metric}_score"

    df_filtered = df[df["country_code"].isin(countries)].copy()

    if df_filtered.empty or score_col not in df_filtered.columns:
        return None

    fig = px.line(
        df_filtered,
        x="date",
        y=score_col,
        color="country_code",
        title=f"{metric.upper()} - Multi-Country Comparison",
        labels={score_col: f"{metric.upper()} Score", "date": "Date", "country_code": "Country"},
    )

    fig.update_traces(mode="lines+markers")
    fig.update_layout(
        yaxis={"range": [0, 100]},
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
        hovermode="x unified",
    )

    return fig
