# =============================================================================
# NEWZ - Application Principale
# =============================================================================

import streamlit as st
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent))
from config.settings import APP_TITLE, APP_VERSION, COLORS

# Configuration de la page
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Personnalisé
st.markdown(f"""
<style>
    .main-header {{
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%);
        color: white;
        padding: 30px;
        border-radius: 15px;
        margin-bottom: 30px;
        text-align: center;
    }}
    .main-header h1 {{ margin: 0; font-size: 36px; }}
    .main-header p {{ margin: 10px 0 0 0; opacity: 0.9; }}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown(f"""
<div class="main-header">
    <h1>NEWZ</h1>
    <p><b>Newz</b> — Market Data Platform v{APP_VERSION}</p>
</div>
""", unsafe_allow_html=True)

# Menu de navigation
menu = st.sidebar.radio(
    "Navigation",
    ["🏠 Accueil", "📥 Data Ingestion", "📊 BDC Statut", "🏦 BAM", "📰 Macronews", "📤 Export"],
    index=0
)

# Routage des pages
if menu == "🏠 Accueil":
    from pages.home import render
    render()
elif menu == "📥 Data Ingestion":
    from pages.data_ingestion import render
    render()
elif menu == "📊 BDC Statut":
    st.info("Page en cours de développement...")
elif menu == "🏦 BAM":
    st.info("Page en cours de développement...")
elif menu == "📰 Macronews":
    st.info("Page en cours de développement...")
elif menu == "📤 Export":
    st.info("Page en cours de développement...")

# Footer
st.sidebar.markdown("---")
st.sidebar.caption(f"© 2025 CDG Capital\nUsage interne uniquement")
