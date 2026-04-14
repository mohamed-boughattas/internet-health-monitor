"""Shutdowns page layout.

This module provides the layout and chart components for the
Internet Shutdowns page in the dashboard.
"""

from __future__ import annotations

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html

from dashboard.components import create_kpi_card
from dashboard.data.queries import get_shutdown_events, get_shutdown_summary


def get_shutdowns_layout() -> dbc.Container | dbc.Alert:
    """Get the internet shutdowns page layout.

    Returns:
        A Dash Container with the shutdowns UI, or an Alert if
        data is unavailable.
    """
    try:
        summary = get_shutdown_summary()
        events = get_shutdown_events()
    except FileNotFoundError:
        return dbc.Alert(
            "Database not found. Please run the pipeline first with 'just run-pipeline'.",
            color="warning",
            className="mt-4",
        )
    except Exception:
        return dbc.Alert(
            "Shutdown data unavailable. Please ensure the pipeline has been run.",
            color="warning",
            className="mt-4",
        )

    if events.empty:
        return dbc.Alert(
            "No shutdown data available yet.",
            color="info",
            className="mt-4",
        )

    total_shutdowns = summary["total_shutdowns"]
    avg_duration = round(summary["avg_duration"], 1)
    total_gdp = round(summary["total_gdp_impact"], 4)
    avg_freedom = round(summary["avg_freedom_score"], 1)

    kpi_row = dbc.Row(
        [
            dbc.Col(
                create_kpi_card(
                    "Total Shutdowns",
                    f"{total_shutdowns}",
                    "Recorded events",
                    color="danger",
                ),
                md=3,
            ),
            dbc.Col(
                create_kpi_card(
                    "Avg Duration",
                    f"{avg_duration} hrs",
                    "Per shutdown event",
                    color="warning",
                ),
                md=3,
            ),
            dbc.Col(
                create_kpi_card(
                    "Total GDP Impact",
                    f"{total_gdp}",
                    "Cumulative cost",
                    color="danger",
                ),
                md=3,
            ),
            dbc.Col(
                create_kpi_card(
                    "Avg Freedom Score",
                    f"{avg_freedom}%",
                    "Across all events",
                    color="info",
                ),
                md=3,
            ),
        ],
        className="mb-4",
    )

    timeline_fig = create_shutdown_timeline(events)
    gdp_fig = create_gdp_impact_chart(events)

    download_row = dbc.Row(
        [
            dbc.Col(
                html.Div(
                    [
                        html.Button(
                            "Download CSV",
                            id="shutdown-download-btn",
                            className="btn btn-outline-primary btn-sm",
                        ),
                    ],
                    className="mb-3",
                ),
                md=12,
            ),
        ],
    )

    table_rows = []
    for _, row in events.iterrows():
        table_rows.append(
            html.Tr(
                [
                    html.Td(str(row["date"])[:10] if row["date"] else ""),
                    html.Td(row["country"]),
                    html.Td(f"{row['duration']:.1f}" if pd.notna(row["duration"]) else "N/A"),
                    html.Td(
                        f"{row['shutdown__gdp']:.4f}" if pd.notna(row["shutdown__gdp"]) else "N/A"
                    ),
                    html.Td(
                        f"{row['freedom_score']:.1f}" if pd.notna(row["freedom_score"]) else "N/A"
                    ),
                ]
            )
        )

    table = dbc.Table(
        [
            html.Thead(
                html.Tr(
                    [
                        html.Th("Date"),
                        html.Th("Country"),
                        html.Th("Duration (hrs)"),
                        html.Th("GDP Impact"),
                        html.Th("Freedom Score"),
                    ]
                )
            ),
            html.Tbody(table_rows),
        ],
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
        className="mb-4",
    )

    return dbc.Container(
        [
            html.H2("Internet Shutdowns", className="mb-4"),
            kpi_row,
            download_row,
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H4("Shutdown Timeline", className="mb-3"),
                            dcc.Graph(
                                id="shutdown-timeline",
                                figure=timeline_fig,
                                style={"height": "400px"},
                            ),
                        ],
                        md=12,
                    ),
                ],
                className="mb-4",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H4("GDP Impact by Country", className="mb-3"),
                            dcc.Graph(
                                id="shutdown-gdp-chart",
                                figure=gdp_fig,
                                style={"height": "350px"},
                            ),
                        ],
                        md=6,
                    ),
                    dbc.Col(
                        [
                            html.H4("Freedom Scores by Country", className="mb-3"),
                            dcc.Graph(
                                id="shutdown-freedom-chart",
                                figure=create_freedom_chart(events),
                                style={"height": "350px"},
                            ),
                        ],
                        md=6,
                    ),
                ],
                className="mb-4",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H4("All Events", className="mb-3"),
                            table,
                        ],
                        md=12,
                    ),
                ]
            ),
            dcc.Download(id="shutdown-download"),
        ],
        fluid=True,
    )


def create_shutdown_timeline(df: pd.DataFrame) -> go.Figure:
    """Create a Gantt-style timeline of shutdown events.

    Args:
        df: DataFrame containing shutdown events with columns:
            - date: Event date
            - country: Country name
            - duration: Shutdown duration in hours

    Returns:
        A Plotly Figure configured as a horizontal bar timeline.
    """
    if df.empty:
        return go.Figure()

    df_clean = df[df["duration"].notna()].copy()
    if df_clean.empty:
        return go.Figure()

    df_clean["end_date"] = pd.to_datetime(df_clean["date"]) + pd.to_timedelta(
        df_clean["duration"], unit="D"
    )

    country_order = df_clean.groupby("country")["duration"].sum().sort_values(ascending=True).index
    df_clean["country"] = pd.Categorical(
        df_clean["country"], categories=country_order, ordered=True
    )

    fig = px.timeline(
        df_clean,
        x_start="date",
        x_end="end_date",
        y="country",
        color="country",
        hover_data={"duration": ":.1f", "shutdown__gdp": ":.4f"},
        title="Shutdown Duration Timeline",
    )

    fig.update_yaxes(categoryorder="total ascending")
    fig.update_xaxes(title="Date")
    fig.update_layout(
        showlegend=False,
        height=max(300, len(df_clean["country"].cat.categories) * 40),
        margin={"l": 120, "r": 20, "t": 50, "b": 20},
    )

    return fig


def create_gdp_impact_chart(df: pd.DataFrame) -> go.Figure:
    """Create a horizontal bar chart of GDP impact by country.

    Args:
        df: DataFrame containing shutdown events with shutdown__gdp column.

    Returns:
        A Plotly Figure configured as a horizontal bar chart.
    """
    if df.empty or "shutdown__gdp" not in df.columns:
        return go.Figure()

    gdp_by_country = (
        df.groupby("country")["shutdown__gdp"].sum().sort_values(ascending=True).reset_index()
    )
    gdp_by_country.columns = ["country", "total_gdp_impact"]

    fig = px.bar(
        gdp_by_country,
        y="country",
        x="total_gdp_impact",
        orientation="h",
        title="Cumulative GDP Impact by Country",
        labels={"total_gdp_impact": "GDP Impact", "country": "Country"},
        color="total_gdp_impact",
        color_continuous_scale="Reds",
    )

    fig.update_yaxes(categoryorder="total ascending")
    fig.update_layout(
        showlegend=False,
        coloraxis_showscale=False,
        margin={"l": 120, "r": 20, "t": 50, "b": 20},
    )

    return fig


def create_freedom_chart(df: pd.DataFrame) -> go.Figure:
    """Create a bar chart of average freedom scores by country.

    Args:
        df: DataFrame containing shutdown events with freedom_score column.

    Returns:
        A Plotly Figure configured as a bar chart.
    """
    if df.empty or "freedom_score" not in df.columns:
        return go.Figure()

    freedom_by_country = (
        df.groupby("country")["freedom_score"].mean().sort_values(ascending=True).reset_index()
    )
    freedom_by_country.columns = ["country", "avg_freedom_score"]

    fig = px.bar(
        freedom_by_country,
        y="country",
        x="avg_freedom_score",
        orientation="h",
        title="Average Freedom Score by Country",
        labels={"avg_freedom_score": "Freedom Score", "country": "Country"},
        color="avg_freedom_score",
        color_continuous_scale="RdYlGn",
        range_x=[0, 100],
    )

    fig.update_yaxes(categoryorder="total ascending")
    fig.update_layout(
        showlegend=False,
        coloraxis_showscale=False,
        margin={"l": 120, "r": 20, "t": 50, "b": 20},
        xaxis={"range": [0, 100]},
    )

    return fig
