"""Main Dash application."""

from typing import Any

import dash_bootstrap_components as dbc
import duckdb
import plotly.graph_objects as go
from dash import Dash, Input, Output, State, dcc, html, no_update

from dashboard.components import create_choropleth_map, create_navbar
from dashboard.constants import REVERSE_ISO3
from dashboard.data import (
    get_daily_metric_timeseries,
    get_last_updated,
)
from dashboard.data.queries import get_country_health_scores
from dashboard.layouts import (
    get_country_comparison_layout,
    get_metric_detail_layout,
    get_overview_layout,
    get_timeseries_layout,
)
from dashboard.layouts.country_comparison import (
    create_comparison_bar_chart,
    create_radar_chart,
)
from dashboard.layouts.metric_detail import (
    build_country_detail_cards,
    create_distribution_chart,
    create_metric_ranking,
)
from dashboard.layouts.timeseries import (
    create_multi_country_chart,
    create_timeseries_chart,
)

app = Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css",
    ],
    title="Internet Health Monitor",
    update_title="",
)

app.config.suppress_callback_exceptions = True

app.layout = dbc.Container(
    [
        create_navbar(last_updated=get_last_updated()),
        dcc.Location(id="url", refresh=False),
        dcc.Loading(dcc.Store(id="selected-country-store"), type="circle", fullscreen=False),
        dcc.Loading(html.Div(id="page-content"), type="circle"),
    ],
    fluid=True,
    className="py-4",
)


@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def display_page(pathname: str) -> dbc.Container | dbc.Alert:
    """Route to the appropriate page based on URL.

    Args:
        pathname: The URL path from the dcc.Location component.

    Returns:
        The layout component for the matched route, or the overview
        layout for the default route.
    """
    if pathname == "/compare":
        return get_country_comparison_layout()
    elif pathname == "/trends":
        return get_timeseries_layout()
    elif pathname == "/detail":
        return get_metric_detail_layout()
    else:
        return get_overview_layout()


@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar(n_clicks: int, is_open: bool) -> bool:
    """Toggle mobile navbar collapse on toggler click.

    Args:
        n_clicks: Number of times the navbar toggler button has been clicked.
        is_open: Current collapse state of the navbar.

    Returns:
        The toggled collapse state (True if open, False if closed).
    """
    if n_clicks:
        return not is_open
    return is_open


@app.callback(
    Output("url", "pathname"),
    Output("selected-country-store", "data"),
    Input("overview-map", "clickData"),
    prevent_initial_call=True,
)
def on_map_click(click_data: dict | None) -> tuple[Any, Any]:
    """Navigate to Detail page and store the clicked country.

    Args:
        click_data: Click data from the choropleth map containing location info.

    Returns:
        A tuple of (url_pathname, store_data). Use no_update for both
        values when click data is invalid or country is not found.
    """
    if not click_data or "points" not in click_data:
        return no_update, no_update
    iso3 = click_data["points"][0].get("location")
    if not iso3:
        return no_update, no_update

    country_code = REVERSE_ISO3.get(iso3)
    if not country_code:
        return no_update, no_update
    return "/detail", country_code


@app.callback(
    Output("detail-country-selector", "value"),
    Input("selected-country-store", "data"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def sync_country_from_store(store_data: str | None, pathname: str) -> str | Any:
    """Sync the selected country from store to the dropdown when on the detail page.

    Args:
        store_data: Country code stored in dcc.Store from map click.
        pathname: Current URL path.

    Returns:
        The country code if on the detail page and store has data,
        otherwise no_update.
    """
    if pathname != "/detail":
        return no_update
    if store_data:
        return store_data
    return no_update


@app.callback(
    Output("radar-chart", "figure"),
    Output("bar-chart", "figure"),
    Input("compare-country-selector", "value"),
)
def update_comparison_charts(countries: list[str]) -> tuple[go.Figure | None, go.Figure | None]:
    """Update charts on country selection change.

    Args:
        countries: List of selected country codes for comparison.

    Returns:
        A tuple of (radar_chart, bar_chart) figures. Both are
        error figures if inputs are invalid or a database error occurs.
    """
    if not countries:
        return _error_figure("Select at least one country to compare."), _error_figure()

    try:
        df = get_country_health_scores()
    except (FileNotFoundError, duckdb.IOException, duckdb.CatalogException):
        return _error_figure("Database error. Please run the pipeline."), _error_figure()

    radar = create_radar_chart(df, countries)
    bar = create_comparison_bar_chart(df, countries)

    return radar, bar


@app.callback(
    Output("timeseries-chart", "figure"),
    Input("timeseries-country", "value"),
    Input("timeseries-metric", "value"),
)
def update_timeseries_chart(country_code: str, metric: str) -> go.Figure | None:
    """Update timeseries chart on selection change.

    Args:
        country_code: ISO 3166-1 alpha-2 country code.
        metric: Selected metric (ipv6, https, dnssec, roa).

    Returns:
        A timeseries figure for the selected country and metric,
        or an error figure if inputs are invalid or a database error occurs.
    """
    if not country_code or not metric:
        return _error_figure()

    try:
        df = get_daily_metric_timeseries(metric=metric, country_code=country_code)
    except (FileNotFoundError, duckdb.IOException, duckdb.CatalogException):
        return _error_figure("Database error. Please run the pipeline.")

    return create_timeseries_chart(df, country_code, metric)


@app.callback(
    Output("multi-country-chart", "figure"),
    Input("timeseries-metric", "value"),
    Input("multi-country-selector", "value"),
)
def update_multi_country_chart(metric: str, countries: list[str]) -> go.Figure | None:
    """Update multi-country comparison chart.

    Args:
        metric: Selected metric for the comparison.
        countries: List of country codes to include in the chart.

    Returns:
        A multi-country timeseries figure for the selected metric,
        or an error figure if inputs are invalid or a database error occurs.
    """
    if not metric or not countries:
        return _error_figure()

    try:
        df = get_daily_metric_timeseries(metric=metric)
    except (FileNotFoundError, duckdb.IOException, duckdb.CatalogException):
        return _error_figure("Database error. Please run the pipeline.")

    return create_multi_country_chart(df, countries, metric)


@app.callback(
    Output("metric-map", "figure"),
    Output("ranking-chart", "figure"),
    Output("distribution-chart", "figure"),
    Output("country-detail-cards", "children"),
    Input("metric-selector", "value"),
    Input("detail-country-selector", "value"),
)
def update_metric_detail(
    metric: str, country_code: str
) -> tuple[go.Figure | None, go.Figure | None, go.Figure | None, dbc.Alert | list]:
    """Update metric detail page on selection change.

    Args:
        metric: Selected metric (ipv6, https, dnssec, roa).
        country_code: ISO 3166-1 alpha-2 country code.

    Returns:
        A tuple of (choropleth_map, ranking_chart, distribution_chart, detail_cards).
        All figures are error figures on database error. Cards show an alert if
        inputs are missing.
    """
    if not metric or not country_code:
        return (
            _error_figure(),
            _error_figure(),
            _error_figure(),
            dbc.Alert("Please select a metric and country.", color="secondary"),
        )

    try:
        df = get_country_health_scores()
    except (FileNotFoundError, duckdb.IOException, duckdb.CatalogException):
        return (
            _error_figure("Database error. Please run the pipeline."),
            _error_figure(),
            _error_figure(),
            dbc.Alert("Database error. Please run the pipeline.", color="danger"),
        )

    score_col = f"{metric}_score"
    map_fig = create_choropleth_map(df, value_col=score_col, title=f"{metric.upper()} by Country")
    ranking_fig = create_metric_ranking(df, metric)
    dist_fig = create_distribution_chart(df, metric)
    detail_cards = build_country_detail_cards(df, country_code)

    return map_fig, ranking_fig, dist_fig, detail_cards


@app.callback(
    Output("trend-download", "data"),
    Input("trend-download-btn", "n_clicks"),
    State("timeseries-metric", "value"),
    prevent_initial_call=True,
)
def download_trends(n_clicks: int, metric: str) -> Any | None:
    """Export trend data as CSV.

    Args:
        n_clicks: Number of times the download button has been clicked.
        metric: Selected metric for the trend data.

    Returns:
        A CSV file download triggered via dcc.send_data_frame, or None
        if no metric is selected or a database error occurs.
    """
    if not metric:
        return None
    try:
        df = get_daily_metric_timeseries(metric=metric)
    except (FileNotFoundError, duckdb.IOException, duckdb.CatalogException):
        return None
    return dcc.send_data_frame(df.to_csv, f"{metric}_trends.csv", index=False)


def _error_figure(message: str = "Error loading data") -> go.Figure:
    """Create a placeholder figure with an error message.

    Args:
        message: The error message to display in the figure.

    Returns:
        A Plotly Figure with an centered annotation displaying the error message.
    """
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        font={"size": 16, "color": "gray"},
    )
    fig.update_layout(
        xaxis={"visible": False},
        yaxis={"visible": False},
        plot_bgcolor="white",
    )
    return fig


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
