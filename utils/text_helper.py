from shiny.ui import modal_show, modal, modal_button
from htmltools import TagList, tags

about_text = TagList(
    tags.p(
        """
        Explore hippocampal hyperemia signal change, activation elicit by 
        an autobiographical memory task and other MR parameter projected 
        on a folded or unfolded surface. Data includes 
        two example subjects as well as group
        average across all subjects.
        """,
        style="""
        text-align: justify;
        word-break:break-word;
        hyphens: auto;
        """,
    ),
)



about_line_text = TagList(
    tags.p(
        """
        View subfield-wise laminar profiles.
        Multiple subjects can be loaded to explore 
        simultaneously. The average is highlighted, if selected. 
        You can zoom, pan, etc. using the bottons in the top-right corner.
        To highlight individual subfields, doubleclick on the subfield 
        in the legend. Doubleclick inside the graph automatically rescales 
        the y-axis.
        """,
        style="""
        text-align: justify;
        word-break:break-word;
        hyphens: auto;
        """,
    ),
)

subject_text_plot = tags.p(
    """
    Please select the subject you want to inspect
    """,
    style="""
    text-align: justify;
    word-break:break-word;
    hyphens: auto;
    """,
)

about_line = tags.p(
    """
    Dummy
    """,
    style="""
    text-align: justify;
    word-break:break-word;
    hyphens: auto;
    """,
    )

extra_notes = tags.p(
    """
    Toggle 'Unfolded' on/off to switch
    between native (folded) and unfolded space. You can
    change the color range by adjusting the colorbar slider.
    """,
    style="""
    font-size: 14px;
    text-align: justify;
    word-break:break-word;
    hyphens: auto;
    """,
)

def info_modal():
    modal_show(
        modal(
            tags.strong(tags.h3("Hippocampal Data Explorer")),
            tags.p(
                """
                Explore several hippocampal properties including venous vessel distribution, 
                venous bias in GRE-BOLD, activity during autobiographical memory, tSNR, T2* 
                """
            ),
            tags.hr(),
            tags.strong(tags.h4("Aim")),
            tags.p(
            """
            This application supports the manuscript 'Laminar fMRI of the human hippocampus: Insights into vascular bias
            and autobiographical memory'.
            """,
                style="""
            text-align: justify;
            word-break:break-word;
            hyphens: auto;
            """,
            ),
            tags.br(),
            tags.hr(),
            about_text,
            tags.hr(),
            extra_notes,
            size="l",
            easy_close=True,
            footer=modal_button("Close"),
        )
    )
