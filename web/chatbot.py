import streamlit as st
from streamlit.components.v1 import html


import streamlit as st

st.set_page_config(page_title="Product Manual Assistant", layout="centered")




def chat_message(role, message):
    """Render chat messages with modern styling"""
    if role == "user":
        bg_color = "#6ed994"
        color = "white"
        align = "right"
        border_radius = "20px 20px 0 20px"
    else:
        bg_color = "#3f9092"
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
    """Add global CSS for full-page background and chat area"""
    st.markdown(
        """
        <style>
        /* ✅ Full background across entire Streamlit app */
        # [data-testid="stAppScrollToBottomContainer"] {
        #     background-color: #181b65;  /* Deep blue background */
        #     background-size: cover;
        # }

         [data-testid="stHeadingWithActionElements"] {
            background-color: #181b65;  /* Deep blue background */
            background-size: cover;
        }
  [data-testid="stSidebarCollapseButton"] {
            background-color: #6ed994;  /* Deep blue background */
            background-size: cover;
        }
        
        

        /* ✅ Also color the sidebar */
        [data-testid="stSidebar"] {
            background-color: #151854;
        }

        /* Chat area padding adjustments */
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
        }

        /* Remove unwanted padding around chat messages */
        [data-testid="stChatMessage"] {
            padding: 0 !important;
        }

        /* Optional: make scrollbars match theme */
        ::-webkit-scrollbar {
            width: 8px;
        }
        ::-webkit-scrollbar-thumb {
            background-color: rgba(255, 255, 255, 0.3);
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background-color: rgba(255, 255, 255, 0.5);
        }

        /* Optional: set global font and text color */
        body {
            color: white;
            font-family: "Inter", sans-serif;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# def add_scroll_style():
#     """Add global CSS for chat area scroll + modern theme"""
#     st.markdown(
#         """
#         <style>
#         body {
#             background-color: #181b65;
#         }
#         .block-container {
#             padding-top: 1rem;
#             padding-bottom: 0rem;
#         }
#         [data-testid="stChatMessage"] {
#             padding: 0 !important;
#         }
#         </style>
#         """,
#         unsafe_allow_html=True,
#     )
