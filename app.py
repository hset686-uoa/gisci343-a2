from pathlib import Path

from shiny import App, ui, render, reactive
from shinywidgets import render_widget, output_widget
import pandas as pd
import matplotlib.pyplot as plt
import ipyleaflet

# File paths that work locally and after ShinyLive deployment
BASE_DIR = Path(__file__).parent

# Load clean patronage data
df = pd.read_csv(BASE_DIR / "data" / "clean_patronage_by_route.csv")
df["month"] = pd.to_datetime(df["month"])
df["year"] = df["month"].dt.year

# Load bus stop spatial data
stops = pd.read_csv(BASE_DIR / "data" / "bus_stops.csv")

modes = ["All"] + sorted(df["Mode"].dropna().unique().tolist())

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h4("Filters"),
        ui.input_select("mode", "Transport mode", choices=modes),
        ui.input_slider(
            "year_range",
            "Year range",
            min=int(df["year"].min()),
            max=int(df["year"].max()),
            value=(int(df["year"].min()), int(df["year"].max())),
            step=1,
            sep=""
        ),
        ui.input_slider(
            "top_n",
            "Number of top routes",
            min=5,
            max=20,
            value=10
        ),
    ),

    ui.h2("Auckland Public Transport Patronage Dashboard"),
    ui.p(
        "This dashboard explores which Auckland public transport routes carry the most passengers "
        "and how usage has changed over time."
    ),

    ui.card(
        ui.h4("How to read this dashboard"),
        ui.p(
            "Use the filters on the left to choose a transport mode, year range, "
            "and number of top routes. The bar chart ranks routes by total passengers, "
            "the line chart shows how patronage changes month by month, and the map "
            "shows the spatial distribution of Auckland bus stops."
        )
    ),

    ui.card(
        ui.h4("Top routes by total passengers"),
        ui.output_plot("top_routes_plot")
    ),

    ui.card(
        ui.h4("Monthly patronage trend for top routes"),
        ui.output_plot("trend_plot")
    ),

    ui.card(
        ui.h4("Bus stops map"),
        output_widget("map")
    ),

    ui.card(
        ui.h4("Summary"),
        ui.output_text("summary_text")
    )
)


def server(input, output, session):

    @reactive.calc
    def filtered_data():
        data = df.copy()

        start_year, end_year = input.year_range()
        data = data[(data["year"] >= start_year) & (data["year"] <= end_year)]

        if input.mode() != "All":
            data = data[data["Mode"] == input.mode()]

        return data

    @output
    @render.plot
    def top_routes_plot():
        data = filtered_data()

        top_routes = (
            data.groupby(["Route Num", "Route Name"], as_index=False)["passengers"]
            .sum()
            .sort_values("passengers", ascending=False)
            .head(input.top_n())
        )

        top_routes["passengers_millions"] = top_routes["passengers"] / 1_000_000

        labels = (
            top_routes["Route Num"].astype(str)
            + " - "
            + top_routes["Route Name"].astype(str)
        )

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(labels, top_routes["passengers_millions"])
        ax.invert_yaxis()
        ax.set_xlabel("Total passengers (millions)")
        ax.set_ylabel("Route")
        ax.set_title("Top Auckland public transport routes by patronage")

        return fig

    @output
    @render.plot
    def trend_plot():
        data = filtered_data()

        top_routes = (
            data.groupby(["Route Num", "Route Name"], as_index=False)["passengers"]
            .sum()
            .sort_values("passengers", ascending=False)
            .head(min(input.top_n(), 6))
        )

        selected_routes = top_routes["Route Num"].tolist()
        trend_data = data[data["Route Num"].isin(selected_routes)]

        trend_summary = (
            trend_data
            .groupby(["month", "Route Num", "Route Name"], as_index=False)["passengers"]
            .sum()
        )

        fig, ax = plt.subplots(figsize=(10, 6))

        for route_num, group in trend_summary.groupby("Route Num"):
            route_name = group["Route Name"].iloc[0]
            label = f"{route_num} - {route_name}"
            ax.plot(group["month"], group["passengers"], marker="o", label=label)

        ax.set_title("Monthly patronage trend for selected top routes")
        ax.set_xlabel("Month")
        ax.set_ylabel("Passengers")
        ax.legend(fontsize=8, loc="best")
        fig.autofmt_xdate()

        return fig

    @output
    @render_widget
    def map():
        m = ipyleaflet.Map(
            center=(-36.85, 174.76),
            zoom=13
        )

        sample = stops.sample(n=min(100, len(stops)), random_state=1)

        for _, row in sample.iterrows():
            marker = ipyleaflet.CircleMarker(
                location=(row["lat"], row["lon"]),
                radius=5,
                color="red",
                fill_color="red",
                fill_opacity=0.65
            )
            m.add_layer(marker)

        return m

    @output
    @render.text
    def summary_text():
        data = filtered_data()

        total_passengers = data["passengers"].sum()
        route_count = data["Route Num"].nunique()

        return (
            f"The selected data includes {route_count} routes and "
            f"{total_passengers:,.0f} passenger boardings."
        )


app = App(app_ui, server)