GLOBAL_STYLES = """
<style>
 .stApp {
        background-color: #F9FAFB;
    }
    .custom-label {
        font-weight: 600;
        color: #1E3A8A;
    }
    .stChatMessage {
        font-size: 15px;
    }
    
/* Color variables */
:root {
    --primary-color: #1E3A8A;
    --text-color: #1E3A8A;
    --border-color: #E2E8F0;
    --bg-color: #F8F9FC;
    --white: #FFFFFF;
}

/* Base font size for the entire app */
.stApp {
    background-color: var(--bg-color);
    font-size: 1.3rem !important;
    font-weight: 600 !important;
    color: var(--text-color) !important;
}

/* Main Layout */
.main {
    padding: 1.5rem;
    max-width: 1200px;
    margin: 0 auto;
}

/* Form Containers */
.form-container {
    background-color: white;
    padding: 2rem;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    margin-bottom: 2rem;
}

/* Labels */
.custom-label {
    font-size: 1.3rem !important;  /* Increased from 0.9rem */
    font-weight: 600;
    color: #1E3A8A;
    margin-bottom: 0.5rem;
    display: block;
}

/* Input Fields */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    font-size: 1.2rem !important;  /* Increased font size */
    font-weight: 500;
    border: 1px solid #E2E8F0;
    border-radius: 6px;
    padding: 0.75rem;  /* Increased padding */
    # color: #1E3A8A;
}

/* Buttons */
.stButton > button {
    font-size: 1.2rem !important;  /* Increased font size */
    border-radius: 6px;
    padding: 0.75rem 1.25rem;  /* Increased padding */
    font-weight: 600;
    transition: all 0.2s ease;
}

.primary-btn {
    background-color: #1E3A8A !important;
    color: white !important;
}

.secondary-btn {
    background-color: #E2E8F0 !important;
    color: #1E3A8A !important;
}

/* Headers */
h1 {
    font-size: 2.5rem !important;
}

h2 {
    font-size: 2rem !important;
}

h3 {
    font-size: 1.75rem !important;
}

/* Radio buttons */
.stRadio label,
[data-testid="stRadio"] [data-testid="stMarkdownContainer"] p,
div[data-baseweb="radio"] label,
div[data-baseweb="radio"] div[data-testid="stMarkdownContainer"] {
    font-size: 1.2rem !important;
    font-weight: 600 !important;
    color: var(--text-color) !important;
}

/* Success/Info messages */
.success-msg, .info-msg {
    font-size: 1.2rem !important;
    font-weight: 600 !important;
    padding: 1.25rem;
}

/* Results section text */
.result-card {
    font-size: 1.1rem !important;
    background-color: white;
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    border-left: 4px solid #1E3A8A;
}

/* Sidebar text */
.sidebar-nav {
    font-size: 1.1rem !important;
    padding: 1rem;
}

/* File uploader text */
.stFileUploader > div > div {
    font-size: 1.1rem !important;
}

/* Captions and help text */
.stCaption {
    font-size: 1rem !important;
}

/* Sidebar styling */
# [data-testid="stSidebar"] {
#     background-color: #F8F9FC;
#     border-right: 1px solid #E2E8F1;
#     padding-top: 2rem;
# }

/* Sidebar styling - darker shades */
[data-testid="stSidebar"] {
    background-color: #E2E6F0; /* darker shade of #F8F9FC */
    border-right: 1px solid #CBD5E0; /* darker shade of #E2E8F1 */
    padding-top: 2rem;
}

[data-testid="stSidebar"] .sidebar-content {
    padding: 2rem 1rem;
}

/* Default sidebar button (unselected state) */
[data-testid="stSidebar"] button {
    background-color: #FFFFFF !important;
    color: #1E3A8A !important;
    border: 1px solid #E2E8F0 !important;
    font-size: 1.5rem !important;  /* Match label font size */
    font-weight: 600 !important;   /* Match label font weight */
    margin-bottom: 0.75rem;
    transition: all 0.2s ease;
    border-radius: 8px;
    padding: 0.75rem 1.25rem !important;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

/* Selected/Active sidebar button */
[data-testid="stSidebar"] button[kind="primary"] {
    background-color: #1E3A8A !important;
    color: white !important;
    border-color: #1E3A8A !important;
    box-shadow: 0 2px 4px rgba(30, 58, 138, 0.2);
    font-weight: 700 !important;   /* Match label font weight */
    font-size: 1.2rem !important;
}

/* Hover effect for sidebar buttons */
[data-testid="stSidebar"] button:hover:not([kind="primary"]) {
    background-color: #F0F4FF !important;
    border-color: #1E3A8A !important;
    transform: translateY(-1px);
}

/* Admin section styling */
[data-testid="stFileUploader"] {
    background-color: white;
    padding: 1rem;
    border-radius: 8px;
    border: 1px solid #E2E8F0;
}

.stMultiSelect > div {
    background-color: white;
    border-radius: 8px;
    border: 1px solid #E2E8F0;
}

/* Admin section labels */
.admin-section .custom-label {
    font-size: 1.5rem !important;
    font-weight: 600;
    color: #1E3A8A;
    margin-bottom: 1rem;
}

/* Admin section containers */
[data-testid="stContainer"] {
    background-color: white;
    padding: 1.5rem;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}


/* Responsive adjustments */
@media (max-width: 768px) {
    .custom-label {
        font-size: 1rem !important;
    }
    
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        font-size: 1.2rem !important;
    }
    
    [data-testid="stSidebar"] button {
        font-size: 1rem !important;  /* Match responsive label size */
    }
}

/* Radio button styling */
/* Target the radio button text specifically */
[data-testid="stRadio"] label[data-testid="stMarkdown"] p {
    font-size: 1.5rem !important;
    font-weight: 600 !important;
    color: #1E3A8A !important;
}

/* Radio button container */
[data-testid="stRadio"] > div {
    padding: 0.5rem !important;
}

/* Radio button group layout */
[data-testid="stRadio"] > div > div:first-child {
    gap: 2rem !important;
}

/* Individual radio option */
[data-baseweb="radio"] {
    margin: 0.5rem 1rem !important;
}

/* Remove default radio styles */
[data-testid="stRadio"] > div {
    border: none !important;
    background: transparent !important;
}

/* Selected radio button styling */
.stRadio [data-baseweb="radio"][aria-checked="true"] {
    background-color: #F0F7FF !important;
}

/* Tabs */
.stTabs [role="tablist"] {
    gap: 20px !important;
    border-bottom: 1px solid #e5e7eb;
    margin-bottom: 16px;
}

/* Style tab container */
.stTabs [role="tab"] {
    padding: 10px 14px !important;
    border-bottom: 2px solid transparent;
    transition: all 0.2s ease-in-out;
    font-weight: 600 !important;
}

/* Style tab label text */
.stTabs [role="tab"] p {
    font-size: 1.3rem !important;   /* <-- Increase font size here */
    font-weight: 600 !important;
    margin: 0 !important;
}

/* Active tab */
.stTabs [aria-selected="true"] {
    color: #1E3A8A !important;
    border-color: #1E3A8A !important;
}
.stTabs [aria-selected="true"] p {
    color: #1E3A8A !important;
}

</style>
"""