from shiny import ui, module, reactive, render
from shinywidgets import (
    output_widget,
    render_widget
)
from utils.plot_helper import create_surface_plot,create_colormaps,create_overlay_file
from utils.text_helper import (
    about_text, extra_notes
)

import unicodeit
import numpy as np

from data.data_loader import surface_data

subject_choices = list(np.unique(surface_data.index.get_level_values(0))) #["7218", "7495"] + ['avg']
overlay_choices = [
    "T2*","angio","hyperemia \u0394S","weighted hyperemia \u0394S",
    "tSNR","vessel masked tSNR"
    ]

Overlay_to_show = {"Subfields":"Subfields","angio":"angio","T2*":"T2s",
                  "hyperemia \u0394S":"dSbreathhold","weighted hyperemia \u0394S":"dSbreathhold_weighted",
                  "tSNR":"tSNR","vessel masked tSNR":"tSNR_vessel_masked",unicodeit.replace("\\beta"):"beta"}


colormaps = create_colormaps()

@module.ui
def surface_ui():
    surface_gui = ui.layout_sidebar(
        ui.panel_sidebar(
            about_text,
            ui.tags.hr(),
            ui.input_selectize(
                id="subject_select",
                label="Select subject",
                choices=subject_choices,
                selected='avg',
                multiple=False
            ),
            ui.tags.hr(),
            ui.input_selectize(
                id="layer_select",
                label="Select surface",
                choices=["inner","outer"],
                selected="inner",
                multiple=False
            ),
            ui.tags.hr(),
            ui.input_selectize(
                id="overlay_select",
                label="Select surface overlay",
                choices=overlay_choices,
                selected="T2*",
                multiple=False
            ),
            ui.tags.hr(),
            ui.input_slider(
                "colorrange","Color Range",0,100,[0, 70],
            ),
            ui.row(
                ui.column(5,
                    ui.input_checkbox(
                        id="unfolded_select",
                        label="Unfolded",
                        value=False
                    )
                ),
                ui.column(7,
                    ui.input_checkbox(
                        id="borders_select",
                        label="Show borders",
                        value=True
                        )
                )
            ),
            ui.tags.hr(),
            extra_notes,
            ui.tags.hr(),
            
            ui.download_button(
                "download_surface_data",
                label="Download map",
                class_="btn-danger"
            ),            
            class_="card text-white bg-danger mb-3"
        ),
        ui.panel_main(
            output_widget("surface_plot")
        )
    )
    return surface_gui

@module.server
def surface_server(input, output, session):    

    @reactive.effect
    def remove_missing_subject():
        all_subjects = list(np.unique(surface_data.index.get_level_values(0)))
        if input.overlay_select() not in ["tSNR","vessel masked tSNR"]:
            all_subjects = [s for s in all_subjects if s != "7491"]
        else:
            all_subjects
        
        selected = "avg" if input.subject_select() == "7491" else input.subject_select()
        ui.update_selectize("subject_select",choices=all_subjects,selected=selected)

    @reactive.effect
    def _():
        mymin = colormaps[Overlay_to_show[input.overlay_select()]][2]-10
        mymax = colormaps[Overlay_to_show[input.overlay_select()]][3]+10
        myvalue = [mymin+10, mymax-10]
        ui.update_slider("colorrange",
                         min=mymin,
                         max=mymax,
                         value=myvalue
                         )
    
    @reactive.Calc
    def surface_fig():        
        return create_surface_plot(
            surface_data=surface_data,
            subject=input.subject_select(),
            Overlay=Overlay_to_show[input.overlay_select()],
            Layer=input.layer_select(),
            unfolded=input.unfolded_select(),
            show_borders=input.borders_select(),
            colorrange=input.colorrange(),
        ) 

    @output(suspend_when_hidden=True)
    @render_widget
    def surface_plot():
        return surface_fig()
    
    

    @render.download()
    def download_surface_data():
        return create_overlay_file(
            data=surface_data,
            subject=input.subject_select(),
            Layer=input.layer_select(),
            Overlay=Overlay_to_show[input.overlay_select()]
        )    

