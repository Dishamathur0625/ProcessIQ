import streamlit as st
from streamlit_option_menu import option_menu


def sidebar():

    with st.sidebar:

        st.markdown(
            """
            <div class='sidebar-title'>
            ProcessIQ
            </div>

            <div class='sidebar-sub'>
            Intelligent Industrial<br>
            Data Analytics Platform
            </div>
            """,
            unsafe_allow_html=True
        )

        page = option_menu(

            menu_title=None,

            options=[

                "Dashboard",

                "Upload Data",

                "Data Overview",

                "Statistics",

                "Correlation Analysis",

                "Predictive Analysis",

                "Reports",

                "Download Center",

                "Settings"

            ],

            icons=[

                "house",

                "cloud-upload",

                "table",

                "bar-chart",

                "diagram-3",

                "graph-up",

                "file-earmark-text",

                "download",

                "gear"

            ],

            default_index=0,

            styles={

                "container":{

                    "padding":"0",

                    "background-color":"#081529"

                },

                "icon":{

                    "color":"white",

                    "font-size":"18px"

                },

                "nav-link":{

                    "font-size":"17px",

                    "text-align":"left",

                    "margin":"5px",

                    "padding":"12px",

                    "--hover-color":"#17365D",

                    "color":"white"

                },

                "nav-link-selected":{

                    "background-color":"#2F6BFF"

                }

            }

        )

        st.markdown(
            "<div class='sidebar-divider'></div>",
            unsafe_allow_html=True
        )

        st.info(
            "Need Help?\n\nDocumentation and user guide will appear here."
        )

    return page