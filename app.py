from pathlib import Path
from shiny import App, Session, reactive, ui
from modules import surface, depth
from utils.text_helper import (
    info_modal
)


page_dependencies = ui.tags.head(
    ui.tags.link(rel="stylesheet", href="bootstrap.css"),
    ui.tags.link(rel="stylesheet", href="layout.css"),
    ui.tags.script(src="index.js"),
    ui.tags.meta(name="description", content="Hippocampal Data Explorer"),
)

page_header = ui.tags.div(
    ui.tags.div(
        ui.tags.div(
            ui.input_action_button(
                id="tab_surface",
                label="View surface data",
                class_="btn-danger"
            ),
            id="div-navbar-surface",
        ),
        ui.tags.div(
            ui.input_action_button(
                id="tab_depth",
                label="View depth data",
                class_="btn-primary"
            ),
            id="div-navbar-depth",
        )
    ),
    class_="navbar-top page-header"
)

surface_ui = ui.tags.div(
    surface.surface_ui("surface"),
    id="surface-container",
    class_="page-main main-visible",
)

depth_ui = ui.tags.div(
     depth.depth_ui("depth"),
     id="depth-container",
     class_="page-main",
)


page_layout = ui.tags.div(
    page_header,
    surface_ui,
    depth_ui,
    class_ = "page-layout"
)

app_ui = ui.page_fluid(
    page_dependencies,
    page_layout,
    title="Hippocampal Data Explorer",
)

def server(input, output, session: Session):
    
    @reactive.Effect
    @reactive.event(input.info_icon)
    def _():
        info_modal()

    surface.surface_server("surface")
    depth.depth_server("depth")

    @reactive.Effect
    @reactive.event(input.tab_surface)
    async def _():
        await session.send_custom_message(
            "toggleActiveTab", {"activeTab": "surface"}
        )

    @reactive.Effect
    @reactive.event(input.tab_depth)
    async def _():
        await session.send_custom_message(
            "toggleActiveTab", {"activeTab": "depth"}
        )

www_dir = Path(__file__).parent / "www"
app = App(app_ui, server, static_assets=www_dir)