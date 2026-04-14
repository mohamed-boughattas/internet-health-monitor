"""Main Dash application."""

import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import Dash, Input, Output, State, dcc, html, no_update

from dashboard.components import create_navbar
from dashboard.data import (
    get_daily_metric_timeseries,
    get_last_updated,
    get_shutdown_events,
)
from dashboard.layouts import (
    get_country_comparison_layout,
    get_metric_detail_layout,
    get_overview_layout,
    get_shutdowns_layout,
    get_timeseries_layout,
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
def display_page(pathname: str):
    """Route to the appropriate page based on URL."""
    if pathname == "/compare":
        return get_country_comparison_layout()
    elif pathname == "/trends":
        return get_timeseries_layout()
    elif pathname == "/detail":
        return get_metric_detail_layout()
    elif pathname == "/shutdowns":
        return get_shutdowns_layout()
    else:
        return get_overview_layout()


@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar(n_clicks: int, is_open: bool):
    """Toggle mobile navbar collapse on toggler click."""
    if n_clicks:
        return not is_open
    return is_open


@app.callback(
    Output("url", "pathname"),
    Output("selected-country-store", "data"),
    Input("overview-map", "clickData"),
    prevent_initial_call=True,
)
def on_map_click(click_data: dict | None):
    """Navigate to Detail page and store the clicked country."""
    if not click_data or "points" not in click_data:
        return no_update, no_update
    iso3 = click_data["points"][0].get("location")
    if not iso3:
        return no_update, no_update
    from dashboard.constants import REVERSE_ISO3

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
def sync_country_from_store(store_data: dict | None, pathname: str):
    """Sync the selected country from store to the dropdown when on the detail page."""
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
def update_comparison_charts(countries: list):
    """Update charts on country selection change."""
    from dashboard.data.queries import get_country_health_scores
    from dashboard.layouts.country_comparison import create_comparison_bar_chart, create_radar_chart

    if not countries:
        return _error_figure("Select at least one country to compare."), _error_figure()

    try:
        df = get_country_health_scores()
    except (FileNotFoundError, Exception):
        return _error_figure("Database error. Please run the pipeline."), _error_figure()

    radar = create_radar_chart(df, countries)
    bar = create_comparison_bar_chart(df, countries)

    return radar, bar


@app.callback(
    Output("timeseries-chart", "figure"),
    Input("timeseries-country", "value"),
    Input("timeseries-metric", "value"),
)
def update_timeseries_chart(country_code: str, metric: str):
    """Update timeseries chart on selection change."""
    from dashboard.layouts.timeseries import create_timeseries_chart

    if not country_code or not metric:
        return _error_figure()

    try:
        df = get_daily_metric_timeseries(metric=metric, country_code=country_code)
    except (FileNotFoundError, Exception):
        return _error_figure("Database error. Please run the pipeline.")

    return create_timeseries_chart(df, country_code, metric)


@app.callback(
    Output("multi-country-chart", "figure"),
    Input("timeseries-metric", "value"),
    Input("multi-country-selector", "value"),
)
def update_multi_country_chart(metric: str, countries: list):
    """Update multi-country comparison chart."""
    from dashboard.layouts.timeseries import create_multi_country_chart

    if not metric or not countries:
        return _error_figure()

    try:
        df = get_daily_metric_timeseries(metric=metric)
    except (FileNotFoundError, Exception):
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
def update_metric_detail(metric: str, country_code: str):
    """Update metric detail page on selection change."""
    from dashboard.components import create_choropleth_map
    from dashboard.data.queries import get_country_health_scores
    from dashboard.layouts.metric_detail import (
        build_country_detail_cards,
        create_distribution_chart,
        create_metric_ranking,
    )

    if not metric or not country_code:
        return (
            _error_figure(),
            _error_figure(),
            _error_figure(),
            dbc.Alert("Please select a metric and country.", color="secondary"),
        )

    try:
        df = get_country_health_scores()
    except (FileNotFoundError, Exception):
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
    Output("shutdown-download", "data"),
    Input("shutdown-download-btn", "n_clicks"),
    prevent_initial_call=True,
)
def download_shutdowns(n_clicks: int):
    """Export shutdown events as CSV."""
    try:
        df = get_shutdown_events()
    except (FileNotFoundError, Exception):
        return None
    return dcc.send_data_frame(df.to_csv, "shutdown_events.csv", index=False)


@app.callback(
    Output("trend-download", "data"),
    Input("trend-download-btn", "n_clicks"),
    State("timeseries-metric", "value"),
    prevent_initial_call=True,
)
def download_trends(n_clicks: int, metric: str):
    """Export trend data as CSV."""
    if not metric:
        return None
    try:
        df = get_daily_metric_timeseries(metric=metric)
    except (FileNotFoundError, Exception):
        return None
    return dcc.send_data_frame(df.to_csv, f"{metric}_trends.csv", index=False)


def _error_figure(message: str = "Error loading data") -> go.Figure:
    """Create a placeholder figure with an error message."""
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
