"""Country comparison page layout.

This module provides the layout and chart components for the
Country Comparison page in the dashboard.
"""

from __future__ import annotations

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html

from dashboard.data.queries import get_country_health_scores, get_country_list


def get_country_comparison_layout() -> dbc.Container | dbc.Alert:
    """Get the country comparison page layout.

    Returns:
        A Dash Container with the comparison UI, or an Alert if
        data is unavailable.
    """
    try:
        country_scores = get_country_health_scores()
        country_list = get_country_list()
    except (FileNotFoundError, Exception):
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

    default_countries = country_list[:3] if len(country_list) >= 3 else country_list

    control_panel = dbc.Card(
        dbc.CardBody(
            [
                html.H5("Select Countries to Compare", className="card-title"),
                dcc.Dropdown(
                    id="compare-country-selector",
                    options=[{"label": c, "value": c} for c in country_list],
                    value=default_countries,
                    multi=True,
                    placeholder="Select countries",
                    className="mb-3",
                ),
            ]
        ),
        className="mb-4",
    )

    table_rows = []
    for _, row in country_scores.head(10).iterrows():
        table_rows.append(
            html.Tr(
                [
                    html.Td(row["country_code"]),
                    html.Td(f"{row['health_score']:.1f}"),
                    html.Td(f"{row['ipv6_score']:.1f}"),
                    html.Td(f"{row['https_score']:.1f}"),
                    html.Td(f"{row['dnssec_score']:.1f}"),
                    html.Td(f"{row['roa_score']:.1f}"),
                ]
            )
        )

    table = dbc.Table(
        [
            html.Thead(
                html.Tr(
                    [
                        html.Th("Country"),
                        html.Th("Health Score"),
                        html.Th("IPv6"),
                        html.Th("HTTPS"),
                        html.Th("DNSSEC"),
                        html.Th("ROA/RPKI"),
                    ]
                )
            ),
            html.Tbody(table_rows),
        ],
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
    )

    return dbc.Container(
        [
            html.H2("Country Comparison", className="mb-4"),
            control_panel,
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H4("Radar Chart", className="mb-3"),
                            dcc.Loading(
                                dcc.Graph(id="radar-chart", style={"height": "400px"}),
                                type="circle",
                            ),
                        ],
                        md=6,
                    ),
                    dbc.Col(
                        [
                            html.H4("Bar Chart Comparison", className="mb-3"),
                            dcc.Loading(
                                dcc.Graph(id="bar-chart", style={"height": "400px"}),
                                type="circle",
                            ),
                        ],
                        md=6,
                    ),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H4("Detailed Metrics", className="mb-3"),
                            table,
                        ],
                        md=12,
                    ),
                ]
            ),
        ],
        fluid=True,
    )


def create_radar_chart(df: pd.DataFrame, countries: list[str]) -> go.Figure | None:
    """Create a radar chart for comparing countries.

    Args:
        df: DataFrame containing country health scores.
        countries: List of country codes to include in the chart.

    Returns:
        A Plotly Figure object configured as a radar chart,
        or None if no valid data is available.
    """
    if df.empty or not countries:
        return None

    df_filtered = df[df["country_code"].isin(countries)].copy()

    if df_filtered.empty:
        return None

    metrics = ["ipv6_score", "https_score", "dnssec_score", "roa_score"]
    metric_labels = ["IPv6", "HTTPS", "DNSSEC", "ROA/RPKI"]

    df_melted = df_filtered.melt(
        id_vars=["country_code"],
        value_vars=metrics,
        var_name="metric",
        value_name="score",
    )
    df_melted["metric"] = df_melted["metric"].map(dict(zip(metrics, metric_labels, strict=True)))

    fig = px.line_polar(
        df_melted,
        r="score",
        theta="metric",
        color="country_code",
        line_close=True,
        title="Country Comparison - Radar Chart",
    )

    fig.update_traces(fill="toself", opacity=0.3)
    fig.update_layout(
        polar={
            "radialaxis": {
                "visible": True,
                "range": [0, 100],
            }
        }
    )

    return fig


def create_comparison_bar_chart(df: pd.DataFrame, countries: list[str]) -> go.Figure | None:
    """Create a grouped bar chart for comparison.

    Args:
        df: DataFrame containing country health scores.
        countries: List of country codes to include in the chart.

    Returns:
        A Plotly Figure object configured as a grouped bar chart,
        or None if no valid data is available.
    """
    if df.empty or not countries:
        return None

    df_filtered = df[df["country_code"].isin(countries)].copy()

    metrics = ["ipv6_score", "https_score", "dnssec_score", "roa_score"]
    metric_labels = ["IPv6", "HTTPS", "DNSSEC", "ROA/RPKI"]

    df_melted = df_filtered.melt(
        id_vars=["country_code"],
        value_vars=metrics,
        var_name="metric",
        value_name="score",
    )
    df_melted["metric"] = df_melted["metric"].map(dict(zip(metrics, metric_labels, strict=True)))

    fig = px.bar(
        df_melted,
        x="metric",
        y="score",
        color="country_code",
        barmode="group",
        title="Metric Comparison",
        labels={"metric": "Metric", "score": "Score", "country_code": "Country"},
    )

    fig.update_layout(
        yaxis={"range": [0, 100]},
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
    )

    fig.add_hline(y=50, line_dash="dash", line_color="gray", opacity=0.7)
    fig.add_hline(y=80, line_dash="dash", line_color="green", opacity=0.7)

    return fig
