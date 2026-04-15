"""Overview page layout."""

import dash_bootstrap_components as dbc
from dash import dcc, html

from dashboard.components import create_choropleth_map, create_kpi_card
from dashboard.components.kpi_card import score_to_color
from dashboard.data.queries import (
    get_country_health_scores,
    get_global_health_summary,
    get_top_bottom_countries,
)


def get_overview_layout() -> dbc.Container | dbc.Alert:
    """Get the overview page layout.

    Returns:
        A Dash Container with the overview UI, or an Alert if data is unavailable.
    """
    try:
        summary = get_global_health_summary()
        country_scores = get_country_health_scores()
    except Exception:
        return dbc.Alert(
            "Database not found. Please run the pipeline first with 'just run-pipeline'.",
            color="warning",
            className="mt-4",
        )

    if summary.empty:
        return dbc.Alert(
            "No data available. Please run the pipeline to ingest data.",
            color="info",
            className="mt-4",
        )

    try:
        top_bottom = get_top_bottom_countries(5)
    except Exception:
        top_bottom = {"top": [], "bottom": []}

    global_score = round(summary.iloc[0]["global_health_score"], 1)
    ipv6_score = round(summary.iloc[0]["ipv6_score"], 1)
    https_score = round(summary.iloc[0]["https_score"], 1)
    dnssec_score = round(summary.iloc[0]["dnssec_score"], 1)
    roa_score = round(summary.iloc[0]["roa_score"], 1)

    kpi_row_1 = dbc.Row(
        [
            dbc.Col(
                create_kpi_card(
                    "Global Health Score",
                    f"{global_score}/100",
                    "Composite of 4 metrics",
                    color=score_to_color(global_score),
                ),
                md=3,
            ),
            dbc.Col(
                create_kpi_card(
                    "IPv6 Adoption",
                    f"{ipv6_score}%",
                    "Protocol availability",
                    color=score_to_color(ipv6_score),
                ),
                md=3,
            ),
            dbc.Col(
                create_kpi_card(
                    "HTTPS Adoption",
                    f"{https_score}%",
                    "Encryption adoption",
                    color=score_to_color(https_score),
                ),
                md=3,
            ),
            dbc.Col(
                create_kpi_card(
                    "DNSSEC Validation",
                    f"{dnssec_score}%",
                    "DNS security",
                    color=score_to_color(dnssec_score),
                ),
                md=3,
            ),
        ],
        className="mb-3",
    )

    kpi_row_2 = dbc.Row(
        [
            dbc.Col(
                create_kpi_card(
                    "Routing Security (RPKI/ROA)",
                    f"{roa_score}%",
                    "BGP route protection",
                    color=score_to_color(roa_score),
                ),
                md=6,
            ),
            dbc.Col(
                create_kpi_card(
                    "Countries Tracked",
                    f"{len(country_scores['country_code'].unique())}",
                    "In dataset",
                    color="dark",
                ),
                md=6,
            ),
        ],
        className="mb-4",
    )

    map_fig = create_choropleth_map(country_scores)

    map_component = (
        dcc.Loading(
            dcc.Graph(
                id="overview-map", figure=map_fig, style={"height": "500px"}, className="mb-4"
            ),
            type="circle",
        )
        if map_fig
        else dbc.Alert("No map data available", color="secondary")
    )

    top_countries = top_bottom.get("top", [])
    bottom_countries = top_bottom.get("bottom", [])

    ranking_row = dbc.Row(
        [
            dbc.Col(
                [
                    html.H5("Top Countries by Health Score", className="mb-3"),
                    dbc.ListGroup(
                        [
                            dbc.ListGroupItem(
                                [
                                    html.Span(f"{i + 1}. ", className="fw-bold text-success"),
                                    html.Span(
                                        f"{c['country_code']} - {c['health_score']:.1f}",
                                        className=f"text-{score_to_color(c['health_score'])}",
                                    ),
                                ]
                            )
                            for i, c in enumerate(top_countries)
                        ],
                        flush=True,
                    )
                    if top_countries
                    else dbc.Alert(
                        "No ranking data available.", color="secondary", className="py-2"
                    ),
                ],
                md=6,
            ),
            dbc.Col(
                [
                    html.H5("Countries Needing Attention", className="mb-3"),
                    dbc.ListGroup(
                        [
                            dbc.ListGroupItem(
                                [
                                    html.Span(f"{i + 1}. ", className="fw-bold text-danger"),
                                    html.Span(
                                        f"{c['country_code']} - {c['health_score']:.1f}",
                                        className=f"text-{score_to_color(c['health_score'])}",
                                    ),
                                ]
                            )
                            for i, c in enumerate(bottom_countries)
                        ],
                        flush=True,
                    )
                    if bottom_countries
                    else dbc.Alert(
                        "No ranking data available.", color="secondary", className="py-2"
                    ),
                ],
                md=6,
            ),
        ],
        className="mb-4",
    )

    return dbc.Container(
        [
            html.H2("Internet Health Overview", className="mb-4"),
            kpi_row_1,
            kpi_row_2,
            html.H4("Geographic Distribution", className="mb-3"),
            map_component,
            html.H4("Country Rankings", className="mb-3"),
            ranking_row,
        ],
        fluid=True,
    )
