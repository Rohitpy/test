import streamlit as st
import requests
import json
import time

API_URL = "http://localhost:7002"
DEFAULT_USER_INPUT = """Define a table named 'customers' with columns: customer_id (integer, primary key), name (varchar 100), email (varchar 100), segment (varchar 20), total_spend (decimal 10,2)."""

custom_css = """
<style>
    /* Theme-aware colors */
    :root {
        --primary-color: #0072B2;
        --primary-light: rgba(0, 114, 178, 0.2);
        --text-color: rgba(250, 250, 250, 0.95);
        --text-secondary: rgba(250, 250, 250, 0.7);
        --bg-card: rgba(30, 30, 30, 0.6);
        --bg-panel: rgba(40, 40, 40, 0.6);
        --border-light: rgba(255, 255, 255, 0.2);
        
        --success-color: #28a745;
        --warning-color: #ffc107;
        --danger-color: #dc3545;
        --info-color: #0d6efd;
        
        --success-bg: rgba(40, 167, 69, 0.2);
        --warning-bg: rgba(255, 193, 7, 0.2);
        --danger-bg: rgba(220, 53, 69, 0.2);
        --info-bg: rgba(13, 110, 253, 0.2);
    }
    
    /* Improved headers */
    .main-header {
        color: var(--primary-color);
        font-weight: 600;
        margin-bottom: 20px;
    }
    
    /* Card styling for dark theme */
    .card {
        border-radius: 5px;
        padding: 20px;
        background-color: var(--bg-card);
        margin-bottom: 20px;
        border-left: 5px solid var(--primary-color);
        color: var(--text-color);
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 15px;
        color: var(--primary-color);
        border-bottom: 1px solid var(--border-light);
        padding-bottom: 5px;
    }
    
    /* Info panels */
    .info-panel {
        background-color: var(--info-bg);
        border-radius: 5px;
        padding: 10px 15px;
        margin-bottom: 15px;
        color: var(--text-color);
        border: 1px solid rgba(13, 110, 253, 0.3);
    }
    
    /* Warning panels */
    .warning-panel {
        background-color: var(--warning-bg);
        border-radius: 5px;
        padding: 10px 15px;
        margin-bottom: 15px;
        color: var(--text-color);
        border: 1px solid rgba(255, 193, 7, 0.4);
    }
    
    /* Badges */
    .badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 10px;
        font-size: 0.8rem;
        font-weight: 500;
        margin-right: 5px;
    }
    
    .badge-green {
        background-color: var(--success-bg);
        color: var(--success-color);
    }
    
    .badge-orange {
        background-color: var(--warning-bg);
        color: var(--warning-color);
    }
    
    .badge-red {
        background-color: var(--danger-bg);
        color: var(--danger-color);
    }
    
    /* Features styling */
    .feature-item {
        margin-bottom: 10px;
        padding-left: 10px;
        border-left: 3px solid var(--primary-color);
        color: var(--text-color);
    }
    
    /* Function mapping styling */
    .function-map {
        background-color: var(--bg-panel);
        padding: 5px 10px;
        border-radius: 4px;
        margin-bottom: 5px;
        font-family: monospace;
        color: var(--text-color);
    }
    
    /* Button styling */
    .primary-button {
        background-color: var(--primary-color);
        color: white;
        padding: 8px 16px;
        border-radius: 4px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: var(--bg-panel);
        border-radius: 4px 4px 0 0;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--primary-color) !important;
        color: white !important;
    }

    /* Icon styling */
    .icon {
        margin-right: 5px;
        vertical-align: middle;
    }
    
    /* Teradata logo styling */
    .teradata-text {
        font-weight: bold;
        font-size: 1.5rem;
        color: var(--primary-color);
        letter-spacing: 1px;
    }
    
    /* Dark-theme specific overrides */
    .dark-card {
        background-color: var(--bg-card);
        color: var(--text-color);
        border: 1px solid var(--border-light);
    }
    
    .dark-text {
        color: var(--text-color) !important;
    }
    
    .dark-secondary {
        color: var(--text-secondary) !important;
    }
    
    /* Warning item in dark theme */
    .warning-item {
        background-color: var(--bg-panel);
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 10px;
        border-left: 4px solid;
    }
    
    .warning-high {
        border-color: var(--danger-color);
    }
    
    .warning-medium {
        border-color: var(--warning-color);
    }
    
    .warning-low {
        border-color: var(--info-color);
    }
    
    /* Alert text colors */
    .text-success {
        color: var(--success-color) !important;
    }
    
    .text-warning {
        color: var(--warning-color) !important;
    }
    
    .text-danger {
        color: var(--danger-color) !important;
    }
    
    .text-info {
        color: var(--info-color) !important;
    }
</style>
"""

st.set_page_config(
    page_title="DDL Statement Generator",
    page_icon="🗄️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown(custom_css, unsafe_allow_html=True)

def generate_ddl(user_input: str) -> dict:
    """Call the API to generate DDL statement"""
    try:
        response = requests.post(
            f"{API_URL}/generate_ddl",
            json={"user_input": user_input},
            timeout=600
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error calling DDL API: {str(e)}")
        return {
            "ddl_statement": f"Error: {str(e)}",
            "execution_time": 0
        }

def render_header():
    """Render the app header"""
    st.markdown('<h1 class="main-header">DDL Statement Generator</h1>', unsafe_allow_html=True)
    st.markdown("""
    <div class="info-panel">
        <span style="font-size: 1.2em;">🗄️</span> <span class="dark-text">
        Generate database DDL statements (CREATE TABLE, ALTER TABLE, etc.) from your requirements using AI.
        </span>
    </div>
    """, unsafe_allow_html=True)

def render_input_section():
    """Render the requirements input section"""
    st.markdown('<div class="section-header">📝 Input Requirements</div>', unsafe_allow_html=True)
    user_input = st.text_area(
        "Describe your table or DDL requirements:",
        value=DEFAULT_USER_INPUT,
        height=200
    )
    st.markdown('</div>', unsafe_allow_html=True)
    return user_input

def render_ddl_results(result):
    """Render DDL statement results"""
    if not result:
        return

    st.markdown('<div class="section-header">✅ DDL Statement Result</div>', unsafe_allow_html=True)
    ddl_statement = result.get("ddl_statement", "")
    st.markdown(f"""```sql
{ddl_statement}
```""")
    execution_time = result.get("execution_time", 0)
    st.caption(f"⏱️ Generated in {execution_time:.2f} seconds")

def main():
    render_header()
    user_input = render_input_section()
    generate_button = st.button("✨ Generate DDL Statement", type="primary", use_container_width=True)
    if generate_button:
        with st.spinner("Generating DDL statement..."):
            ddl_result = generate_ddl(user_input)
            render_ddl_results(ddl_result)

if __name__ == "__main__":
    main()
