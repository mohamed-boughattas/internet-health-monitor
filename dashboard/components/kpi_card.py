"""KPI card component for the dashboard.

This module provides a reusable KPI (Key Performance Indicator) card
component for displaying metrics in the dashboard using Dash.

Usage:
    from dashboard.components import create_kpi_card

Example:
    >>> card = create_kpi_card("Health Score", "85.5%", "+5%", color="success")
"""

from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import html


def score_to_color(score: float) -> str:
    """Map a 0-100 score value to a Bootstrap color.

    Args:
        score: Numeric score value (0-100).

    Returns:
        Bootstrap color name: "success" (>=80), "primary" (>=60),
        "warning" (>=40), "danger" (<40).
    """
    if score >= 80:
        return "success"
    if score >= 60:
        return "primary"
    if score >= 40:
        return "warning"
    return "danger"


def create_kpi_card(
    title: str,
    value: str,
    subtitle: str | None = None,
    trend: str | None = None,
    color: str = "primary",
) -> dbc.Card:
    """Create a reusable KPI card component.

    Args:
        title: The metric title displayed above the value.
            Should be in uppercase (e.g., "HEALTH SCORE").
        value: The main metric value to display (e.g., "85.5%").
        subtitle: Optional descriptive text below the value.
            Defaults to None.
        trend: Optional trend indicator showing change (e.g., "+5%", "-10%").
            Defaults to None. Shown with an arrow icon.
        color: Bootstrap color theme for the value text.
            Options: "primary", "success", "warning", "danger", "info".
            Defaults to "primary".

    Returns:
        A Dash Bootstrap Components Card with the KPI display.

    Example:
        >>> card = create_kpi_card(
        ...     title="HEALTH SCORE",
        ...     value="85.5%",
        ...     subtitle="Global average",
        ...     trend="+2.5%",
        ...     color="success"
        ... )
    """
    trend_icon: str | None = None
    trend_color: str = "success"

    if trend:
        if trend.startswith("+"):
            trend_icon = "▲"
            trend_color = "success"
        elif trend.startswith("-"):
            trend_icon = "▼"
            trend_color = "danger"

    return dbc.Card(
        dbc.CardBody(
            [
                html.H6(title, className="card-title text-muted text-uppercase"),
                html.H3(value, className=f"mb-0 text-{color} fw-bold"),
                html.Small(subtitle, className="text-muted") if subtitle else None,
                html.Div(
                    [
                        html.Span(trend_icon, className=f"me-1 text-{trend_color}"),
                        html.Span(trend, className=f"text-{trend_color}"),
                    ],
                    className="mt-2",
                )
                if trend
                else None,
            ]
        ),
        className="text-center h-100",
        style={"min-height": "120px"},
    )
