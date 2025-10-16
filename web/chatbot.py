import streamlit as st
from streamlit.components.v1 import html

def chat_message(role, message):
    """Render chat messages with modern styling"""
    if role == "user":
        bg_color = "#daf0ef"
        color = "black"
        align = "right"
        border_radius = "20px 20px 0 20px"
    else:
        bg_color = "#333"
        color="white"
        align = "left"
        border_radius = "20px 20px 20px 0"



    st.markdown(
        f"""
        <div style="
            display: flex;
            justify-content: {align};
            margin: 10px 0;
        ">
            <div style="
                background-color: {bg_color};
                color: {color};
                padding: 10px 15px;
                border-radius: {border_radius};
                max-width: 75%;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                word-wrap: break-word;
                font-size: 15px;
                line-height: 1.5;
            ">
                {message}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def add_scroll_style():
    """Add global CSS for chat area scroll + modern theme"""
    st.markdown(
        """
        <style>
        body {
            background-color: #7ea5f2;
        }
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
        }
        [data-testid="stChatMessage"] {
            padding: 0 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
