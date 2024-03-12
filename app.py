import plotly.express as px
from shiny.express import input, ui
from shinywidgets import render_plotly, render_widget
from palmerpenguins import load_penguins  # This package provides the Palmer Penguins dataset
import pandas as pd
import seaborn as sns
import plotly.graph_objects as go
from shiny import reactive, render, req

# Use the built-in function to load the Palmer Penguins dataset
penguins = load_penguins()

# Clean data as necessary right after loading
penguins.fillna(0, inplace=True)
penguins.dropna(inplace=True)

ui.page_opts(title="TFMONTAGUE's Penguin Data", fillable=True)

# Add a Shiny UI sidebar for user interaction
with ui.sidebar(open="open"):  
    # Use ui.HTML() to include an h2 header with custom styling
    ui.HTML('<h2 style="font-size: smaller;">Dashboard Configuration Options</h2>')
    ui.input_selectize("selected_attribute", "Select an attribute below:", 
                       ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"])
    ui.input_numeric("plotly_bin_count", "Number of Plotly Histogram Bins", value=20, min=1, max=100)
    ui.input_slider("seaborn_bin_count", "Number of Seaborn Bins", min=1, max=50, value=10)
    ui.input_checkbox_group("selected_species_list", "Filter by Species", 
                            choices=["Adelie", "Gentoo", "Chinstrap"], 
                            selected=["Adelie"], inline=True)
    ui.hr()
    ui.a("TFMONTAGUE's P2 Repo", href="https://github.com/tfmontague/cintel-02-data", target="_blank")

    @render.ui
    def selected_info2():
        selected_attribute = input.selected_attribute()
        plotly_bin_count = input.plotly_bin_count()
        seaborn_bin_count = input.seaborn_bin_count()
        info_html = f"""
        <div style="font-size: 65%; line-height: 1;">
            <h4 style="margin-bottom: 0;">Selected Configuration:</h4>
            <p style="margin-top: 0; margin-bottom: 0;"><strong>Selected attribute:</strong> {selected_attribute}</p>
            <p style="margin-top: 0; margin-bottom: 0;"><strong>Plotly bin count:</strong> {plotly_bin_count}</p>
            <p style="margin-top: 0;"><strong>Seaborn bin count:</strong> {seaborn_bin_count}</p>
        </div>
        """
        return ui.HTML(info_html)

# Main content
with ui.layout_columns():
    # Displaying DataTable and DataGrid
    with ui.card():
        ui.card_header("Palmer Penguins Data Table")
        penguins = load_penguins()
        @render.data_frame  
        def penguins_df():
            return render.DataTable(penguins)  
    with ui.card():
        ui.card_header("Palmer Penguins Data Grid")
        @render.data_frame
        def penguins_df2():
            return render.DataGrid(penguins)

# Plotly Histogram, Seaborn Histogram
with ui.layout_columns():
    with ui.card():
        ui.card_header("Plotly Histogram: All Species")
        @render_widget  
        def plot():  
            scatterplot = px.histogram(
                data_frame=penguins,
                x="body_mass_g",
                nbins=input.plotly_bin_count(),
                ).update_layout(
                    title={"text": "Penguin Mass", "x": 0.5},
                    yaxis_title="Count",
                    xaxis_title="Body Mass (g)",
                )
            return scatterplot
    with ui.card():
        ui.card_header("Seaborn Histogram: All Species")
        @render.plot
        def plot2():
            # Generate the Seaborn histogram based on the selected attribute and bin count
            ax = sns.histplot(data=penguins, x=input.selected_attribute(), bins=input.seaborn_bin_count())  
            ax.set_title("Palmer Penguins")
            ax.set_xlabel(input.selected_attribute())  # Use the selected attribute as the x-axis label
            ax.set_ylabel("Count")
            return ax           

# Full screen card for Plotly Scatterplot
penguins['bill_length_mm'].fillna(penguins['bill_length_mm'].median(), inplace=True)

with ui.card(full_screen=True):
    ui.card_header("Plotly Scatterplot: Species")
    @render_plotly
    def plotly_scatterplot():
        scatterplot2 = px.scatter(
            data_frame=penguins,
            x="flipper_length_mm",
            y="body_mass_g",
            color="species",
            size="bill_length_mm",
            hover_name="island",
            labels={
                "flipper_length_mm": "Flipper Length (mm)",
                "body_mass_g": "Body Mass (g)",
                "species": "Species",
                "bill_length_mm": "Bill Length (mm)",
                "island": "Island"
            },
            title="Penguin Species Measurements"
        )
        return scatterplot2

