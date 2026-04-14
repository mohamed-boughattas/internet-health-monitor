"""Choropleth map component for the dashboard.

This module provides functions to create interactive choropleth maps
visualizing internet health data by country using Plotly.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from dashboard.constants import ISO_ALPHA3, MAP_COUNTRY_CODES, TRACKED_COUNTRIES


def create_choropleth_map(
    df: pd.DataFrame,
    value_col: str = "health_score",
    title: str = "Internet Health Score by Country",
) -> go.Figure | None:
    """Create an interactive choropleth map for tracked countries.

    Countries are colored by the selected metric score. Untracked countries
    appear in neutral gray. Tracked country labels show the name and score
    value. Clicking a tracked country triggers a callback for navigation.

    Args:
        df: DataFrame containing health metric data with columns:
            - country_code: ISO 3166-1 alpha-2 country code
            - health_score: Composite health score
            - ipv6_score: IPv6 adoption score
            - https_score: HTTPS adoption score
            - dnssec_score: DNSSEC validation score
            - roa_score: ROA/RPKI score
        value_col: Column name to use for color shading.
            Defaults to "health_score".
        title: Chart title displayed at the top.
            Defaults to "Internet Health Score by Country".

    Returns:
        A Plotly Figure object configured as a choropleth map, or None if no
        valid data is present in the DataFrame.
    """
    if df.empty:
        return None

    df_map = df.copy()
    df_map["iso_alpha3"] = df_map["country_code"].map(ISO_ALPHA3)
    df_map["country_name"] = df_map["country_code"].map(TRACKED_COUNTRIES)
    df_map = df_map[df_map["country_code"].isin(MAP_COUNTRY_CODES)].copy()

    if df_map.empty:
        return None

    fig = go.Figure()

    fig.add_trace(
        go.Choropleth(
            locations=df_map["iso_alpha3"],
            z=df_map[value_col],
            colorscale="RdYlGn",
            zmin=0,
            zmax=100,
            colorbar_title="Score",
            colorbar_tickformat=".0f",
            marker_line_color="white",
            marker_line_width=0.5,
            hovertemplate=None,
        )
    )

    tracked_iso3 = df_map["iso_alpha3"].tolist()
    tracked_labels = [
        f"{row['country_name']}<br>{row[value_col]:.0f}"
        if pd.notna(row.get(value_col))
        else row["country_name"]
        for _, row in df_map.iterrows()
    ]
    fig.add_trace(
        go.Scattergeo(
            locations=tracked_iso3,
            locationmode="ISO-3",
            text=tracked_labels,
            mode="text",
            textfont={
                "size": 10,
                "color": "black",
                "family": "Arial, sans-serif",
                "weight": "bold",
            },
            textposition="middle center",
            hoverinfo="skip",
            showlegend=False,
        )
    )

    fig.update_geos(
        showcountries=True,
        countrycolor="rgba(200,200,200,0.6)",
        showcoastlines=True,
        coastlinecolor="white",
        showland=True,
        landcolor="rgba(235,235,235,0.4)",
        showocean=True,
        oceancolor="rgba(200,220,240,0.5)",
        showlakes=True,
        lakecolor="rgba(200,220,240,0.5)",
        showframe=False,
        projection_type="natural earth",
    )

    fig.update_layout(
        title={
            "text": f"{title}<br><sup>{len(df_map)} Countries Tracked</sup>",
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 16},
        },
        margin={"l": 0, "r": 0, "t": 80, "b": 0},
        paper_bgcolor="white",
        geo_bgcolor="white",
    )

    return fig
