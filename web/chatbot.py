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

img_base64 = get_base64_image("web/assets/7.png")

def chat_message(role, message):
    """Render chat messages with modern styling"""
    if role == "user":
        bg_color = "#0f1d4a"
        color = "white"
        align = "right"
        border_radius = "20px 20px 0 20px"
        icon= "👤"
    else:
        bg_color = "#3f9092"
        color="white"
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
 
 header[data-testid="stHeader"]::after {{
        content: "Product Manual Assistant";
        position: absolute;
        font-size: 2.2rem;
        font-weight: 800;
        color: #0f1d4a;
        left: 1rem;
    }}
    
    [data-testid="stSidebar"]{{
        background-color:#e6f8fa;
    }}

  [data-testid="stAppDeployButton"]{{
        display:none;
    }}
    
    [data-testid="stMainMenu"]{{
        display:none;
    }}
    .stApp {{
        background-image: url("data:image/jpeg;base64,{img_base64}");
        # background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        height: 100vh;
        width: 100vw;
    }}  
    .overlay {{
        background-color: rgba(255, 255, 255, 0.85);
        padding: 2rem;
        border-radius: 10px;
        margin: 2rem;
    }}
    
   
    
section[data-testid="stSidebar"] h2 {{
        color: #0f1d4a;
        font-size: 1.5rem;
        font-weight: 600;
        
    }}
    
    [data-testid="stMarkdownContainer"]{{
        color:#0f1d4a
          font-size: 2.2rem;
        font-weight: 400;
    }}
    
    [data-testid="stFileUploaderDropzone"]{{
         background-color:transparent;
         border:2px dashed #0f1d4a;
    }}
    
    [data-testid="stBaseButton-secondary"]{{
        background-color: #0f1d4a;
        color: white;
    }}
    
    </style>
    """,
    unsafe_allow_html=True
)
