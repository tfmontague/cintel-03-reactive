import plotly.express as px
from shiny.express import input, ui
from shinywidgets import render_plotly, render_widget
from palmerpenguins import load_penguins# This package provides the Palmer Penguins dataset
import palmerpenguins
import pandas as pd
import seaborn as sns
import plotly.graph_objects as go
from shiny import reactive, render, req

# Use the built-in function to load the Palmer Penguins dataset
penguins_df = palmerpenguins.load_penguins()

# Name the page
ui.page_opts(title="TFMONTAGUE's Penguin Data", fillable=True)

# Change the background color of the dashboard
ui.HTML("""
<style>
  body {
    background-color: #808080; /* dark gray background */
  }
</style>
""")

# Add a Shiny UI sidebar for user interaction
with ui.sidebar(open="open"):  
    # Use ui.HTML() to include an h2 header with custom styling
    ui.HTML('<h3 style="font-size: medium;">Dashboard Configuration Options</h3>')

    # Create dropdown input
    ui.input_selectize("selected_attribute", "Select an attribute below:", 
                       ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"])

    # Create numeric input for number of plotly histogram bins
    ui.input_numeric("plotly_bin_count", "Number of Plotly Histogram Bins", value=20, min=1, max=100)

    # Create slider input for number of seaborn bins
    ui.input_slider("seaborn_bin_count", "Number of Seaborn Bins", min=1, max=50, value=10)

    # Create checkbox for species group input
    ui.input_checkbox_group("selected_species_list", "Filter by Species", 
                            choices=["Adelie", "Gentoo", "Chinstrap"], 
                            selected=["Adelie"], inline=True)

    # Add horizontal rule to sidebar
    ui.hr()

    # Add hyperlink to github repo
    ui.a("TFMONTAGUE's P2 Repo", href="https://github.com/tfmontague/cintel-02-data", target="_blank")

    # Create text output of selected inputs
    @render.ui
    def selected_info2():
        selected_attribute = input.selected_attribute()
        plotly_bin_count = input.plotly_bin_count()
        seaborn_bin_count = input.seaborn_bin_count()
        selected_species = input.selected_species_list()  # Get the selected species from the checkbox group
        selected_species_str = ", ".join(selected_species)
        
        # Style text output
        info_html = f"""
        <div style="font-size: 65%; line-height: 1;">
            <h6 style="margin-bottom: 0;">Selected Configuration:</h6>
            <p style="margin-top: 1; margin-bottom: 1;"><strong>Selected attribute:</strong> {selected_attribute}</p>
            <p style="margin-top: 1; margin-bottom: 1;"><strong>Plotly bin count:</strong> {plotly_bin_count}</p>
            <p style="margin-top: 1; margin-bottom: 1;"><strong>Seaborn bin count:</strong> {seaborn_bin_count}</p>
            <p style="margin-top: 1; margin-bottom: 1;"><strong>Selected species:</strong> {selected_species_str}</p>
        </div>
        """
        return ui.HTML(info_html)

# Main content
with ui.layout_columns():
    
    # Display DataTable with all data
    with ui.card():
        ui.card_header("Palmer Penguins Data Table")
        penguins = load_penguins()
        @render.data_frame
        def render_penguins_table():
            return filtered_data()
            
    # Display DataGrid with all data
    with ui.card():
        ui.card_header("Palmer Penguins Data Grid")
        @render.data_frame
        def penguins_data():
            return render.DataGrid(filtered_data(), row_selection_mode="multiple")


with ui.layout_columns():
    # Create Plotly Histogram with all species
    with ui.card():
        ui.card_header("Plotly Histogram: All Species")
        @render_plotly  
        def plotly_histogram():  
            return px.histogram(
              filtered_data(), 
              x=input.selected_attribute(), 
              nbins=input.plotly_bin_count(),  # Add a comma here
              color="species",
              )     

    # Create Seaborn Histogram with all species
    with ui.card():
        ui.card_header("Seaborn Histogram: All Species")
        @render.plot
        def seaborn_histogram():
            # Generate the Seaborn histogram based on the selected attribute and bin count
            ax = sns.histplot(data=penguins, x=input.selected_attribute(), bins=input.seaborn_bin_count())  
            ax.set_title("Palmer Penguins")
            ax.set_xlabel(input.selected_attribute())  # Use the selected attribute as the x-axis label
            ax.set_ylabel("Count")
            return ax           

# Create full screen card for Plotly Scatterplot
with ui.card(full_screen=True):
    ui.card_header("Plotly Scatterplot: Species")
    @render_plotly
    def plotly_scatterplot():
        return px.scatter(filtered_data(),
            x="flipper_length_mm",
            y="body_mass_g",
            color="species",
            hover_name="island",
            labels={
                "flipper_length_mm": "Flipper Length (mm)",
                "body_mass_g": "Body Mass (g)",
                "species": "Species",
                "bill_length_mm": "Bill Length (mm)",
                "island": "Island"
            },
            title="Penguin Species Measurements",
            size_max=12
        )

# --------------------------------------------------------
# Reactive calculations and effects
# --------------------------------------------------------

# Add a reactive calculation to filter the data
# By decorating the function with @reactive, we can use the function to filter the data
# The function will be called whenever an input functions used to generate that output changes.
# Any output that depends on the reactive function (e.g., filtered_data()) will be updated when the data changes.

@reactive.calc
def filtered_data():
    selected_species = input.selected_species_list()  # Get the list of selected species
    filtered_df = penguins_df[penguins_df['species'].isin(selected_species)]  # Filter the DataFrame
    return filtered_df



