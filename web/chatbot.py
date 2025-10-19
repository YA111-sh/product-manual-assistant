import streamlit as st
from streamlit.components.v1 import html
import base64
import os
import streamlit as st

st.set_page_config(page_title="Product Manual Assistant", layout="wide")

# --- Load and Encode Image ---
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

img_base64 = get_base64_image("web/assets/6.jpg")

def chat_message(role, message):
    """Render chat messages with modern styling"""
    if role == "user":
        bg_color = "rgb(230, 234, 241)"
        color = "black"
        align = "right"
        border_radius = "20px 20px 0 20px"
        icon= "👤"
    else:
        bg_color = "rgb(240, 242, 246)"
        color="black"
        align = "left"
        border_radius = "20px 20px 20px 0"
        icon = "🧑‍💻"



    st.markdown(
        f"""
      
        <div style="
            display: flex;
            justify-content: {align};
            margin: 10px 0;
        ">
          <div style="margin-top: 10px;">{icon}</div>
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
    f"""
    <style>

  [data-testid="stAppDeployButton"]{{
        display:none;
    }}
    
    [data-testid="stMainMenu"]{{
        display:none;
    }}
    
    </style>
    """,
    unsafe_allow_html=True
)
