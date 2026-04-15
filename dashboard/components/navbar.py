"""Dashboard navbar component."""

import dash_bootstrap_components as dbc
from dash import html


def create_navbar(last_updated: str = "N/A") -> dbc.Navbar:
    """Create the main navigation bar.

    Args:
        last_updated: The date string of the last data update.
            Defaults to "N/A".

    Returns:
        A dbc.Navbar component with navigation links to all four
        pages and a label showing the last data update time.
    """
    return dbc.Navbar(
        dbc.Container(
            [
                dbc.NavbarBrand(
                    [html.I(className="bi bi-globe me-2"), "Internet Health Monitor"],
                    href="/",
                    className="fw-bold",
                ),
                dbc.NavbarToggler(id="navbar-toggler"),
                dbc.Collapse(
                    dbc.Nav(
                        [
                            dbc.NavItem(dbc.NavLink("Overview", href="/", active="exact")),
                            dbc.NavItem(dbc.NavLink("Compare", href="/compare", active="exact")),
                            dbc.NavItem(dbc.NavLink("Trends", href="/trends", active="exact")),
                            dbc.NavItem(dbc.NavLink("Detail", href="/detail", active="exact")),
                        ],
                        className="ms-auto",
                        navbar=True,
                    ),
                    id="navbar-collapse",
                    is_open=False,
                    navbar=True,
                ),
                html.Span(f"Updated: {last_updated}", className="text-muted me-3"),
            ],
            fluid=True,
        ),
        color="dark",
        dark=True,
        className="mb-4",
    )
