import os
import numpy as np
from shiny import ui, module, reactive, render
from shinywidgets import (
    output_widget,
    render_widget
)
from utils.plot_helper import create_line_plot
from utils.text_helper import (
    about_line_text
)

import unicodeit

from data.data_loader import depth_data

all_subjects    = list(np.unique(depth_data.index.get_level_values(0)))
subject_choices = all_subjects
overlay_choices = [
    "T2*","hyperemia \u0394S","weighted hyperemia \u0394S",
    "tSNR",unicodeit.replace("\\beta")
    ]

contrast_choices = ["breath-hold","memory vs. math","construction vs. elaboration"]

Overlay_to_show = {"T2*":"T2s",unicodeit.replace("\\beta"):"beta","tSNR":"tSNR",
                  "hyperemia \u0394S":"dSbreathhold","weighted hyperemia \u0394S":"dSbreathhold_weighted",
                  }

contrast_to_show = {"breath-hold":"breathhold","memory vs. math":"memory_vs_math","construction vs. elaboration":"pre_vs_post"}

@module.ui
def depth_ui():
    gui = ui.layout_sidebar(
        ui.panel_sidebar(
            about_line_text,
            ui.tags.hr(),
            ui.input_selectize(
                id="subject_multiselect",
                label="Select subject",
                choices=all_subjects,
                selected="avg",
                multiple=True
            ),

            ui.tags.hr(),
            ui.input_selectize(
                id="contrast_select",
                label="Select contrast",
                choices=contrast_choices,
                selected=contrast_choices[0],
                multiple=False
            ),
            
            ui.tags.hr(),
            ui.input_selectize(
                id="overlay_select",
                label="Select overlay",
                choices=overlay_choices,
                selected=overlay_choices[0],
                multiple=False
            ),
            ui.row(
                ui.column(5,
                    ui.input_checkbox(
                        id="show_all",
                        label="Show all",
                        value=False
                    )
                ),
                ui.column(7,
                    ui.input_checkbox(
                        id="vessel_masked",
                        label="Show vessel masked",
                        value=True
                        )
                )
            ),
            ui.row(
                ui.tags.hr(),
                ui.download_button(
                    "download_depth_data",
                    label="Download data",
                    class_="btn-primary"
                ),
            ),
            class_="card text-white bg-primary mb-3"
        ),
        ui.panel_main(
            output_widget("line_plot")
        )
    )
    return gui

@module.server
def depth_server(input, output, session):

    @reactive.effect
    def remove_missing_subject():
        all_subjects = list(np.unique(depth_data.index.get_level_values(0)))
        if input.contrast_select() == "breath-hold":
            all_subjects = [s for s in all_subjects if s != "7491"]
        else:
            all_subjects
        ui.update_selectize("subject_multiselect",choices=all_subjects,selected="avg")
        
    @reactive.effect
    def load_all():
        all_subjects = list(np.unique(depth_data.index.get_level_values(0))) 
        if input.contrast_select() == "breath-hold":
            all_subjects = [s for s in all_subjects if s != "7491"]
        else:
            all_subjects
        if input.show_all():
            ui.update_selectize("subject_multiselect",choices=all_subjects,selected=all_subjects)
        else:
            ui.update_selectize("subject_multiselect",choices=all_subjects,selected="avg")

    @reactive.effect
    def change_overlay():
        overlay_choices = [
            "T2*","hyperemia \u0394S","weighted hyperemia \u0394S",
            "tSNR",unicodeit.replace("\\beta")
            ]
        inp = overlay_choices[0:3] if input.contrast_select() == "breath-hold" else overlay_choices[3:]
        
        ui.update_selectize("overlay_select",choices=inp,selected=inp[0])
    
    @reactive.Calc
    def line_fig():
        return create_line_plot(
            depth_data=depth_data,
            subject=input.subject_multiselect(),
            Overlay=Overlay_to_show[input.overlay_select()],
            contrast=contrast_to_show[input.contrast_select()],
            vessel_masked=input.vessel_masked()
        ) 
    

    @output(suspend_when_hidden=True)
    @render_widget
    def line_plot():
        return line_fig()
    
    @render.download()
    def download_depth_data():
        path = os.path.join(os.path.dirname(__file__), "../data/depth_data.pkl")
        return path