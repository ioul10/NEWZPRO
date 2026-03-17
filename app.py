# =============================================================================
# NEWZ - Market Data Platform
# Navigation Unifiée
# Fichier : app.py
# =============================================================================

import streamlit as st
from pathlib import Path
import sys
from datetime import datetime

# Configuration de la page
st.set_page_config(
    page_title="Newz | Market Data Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ajout du chemin pour les imports
sys.path.append(str(Path(__file__).resolve().parent))

# Import de la configuration
try:
    from config.settings import COLORS, APP_INFO
except ImportError:
    COLORS = {
        'primary': '#005696',
        'secondary': '#003d6b',
        'accent': '#00a8e8',
        'success': '#28a745',
        'warning': '#ffc107',
        'danger': '#dc3545'
    }
    APP_INFO = {'name': 'Newz', 'version': '2.0.0'}

# -----------------------------------------------------------------------------
# CSS PERSONNALISÉ
# -----------------------------------------------------------------------------

st.markdown(f"""
<style>
    .main-header {{
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%);
        color: white;
        padding: 40px;
        border-radius: 15px;
        margin-bottom: 30px;
        text-align: center;
    }}
    .main-header h1 {{ margin: 0; font-size: 42px; }}
    .main-header p {{ margin: 10px 0 0 0; opacity: 0.9; }}
    
    .footer {{
        margin-top: 50px;
        padding: 20px;
        text-align: center;
        color: #666;
        font-size: 12px;
        border-top: 1px solid #e0e0e0;
    }}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# INITIALISATION
# -----------------------------------------------------------------------------

def init_session_state():
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    if 'excel_data' not in st.session_state:
        st.session_state.excel_data = {}
    if 'bourse_data' not in st.session_state:
        st.session_state.bourse_data = {}
    if 'news_data' not in st.session_state:
        st.session_state.news_data = []
    if 'actions_data' not in st.session_state:
        st.session_state.actions_data = None
    if 'last_update' not in st.session_state:
        st.session_state.last_update = None
    if 'export_selected_sections' not in st.session_state:
        st.session_state.export_selected_sections = ['summary', 'bdc', 'bam', 'inflation']
    if 'report_html' not in st.session_state:
        st.session_state.report_html = None

init_session_state()

# -----------------------------------------------------------------------------
# HEADER
# -----------------------------------------------------------------------------

st.markdown(f"""
<div class="main-header">
    <h1>🏦 CDG Capital</h1>
    <p><b>{APP_INFO['name']}</b> — Market Data Platform v{APP_INFO['version']}</p>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# NAVIGATION AVEC st.navigation()
# -----------------------------------------------------------------------------

# Définir les pages
pages = [
    st.Page("pages/home.py", title="Accueil", icon="🏠"),
    st.Page("pages/data_ingestion.py", title="Data Ingestion", icon="📥"),
    st.Page("pages/bdc_statut.py", title="BDC Statut", icon="📊"),
    st.Page("pages/bam.py", title="BAM", icon="🏦"),
    st.Page("pages/macronews.py", title="Macronews", icon="📰"),
    st.Page("pages/export.py", title="Export", icon="📤"),
]

# Créer la navigation
pg = st.navigation(pages)

# Exécuter la page sélectionnée
pg.run()

# -----------------------------------------------------------------------------
# FOOTER
# -----------------------------------------------------------------------------

st.markdown(f"""
<div class="footer">
    <p><b>{APP_INFO['name']} v{APP_INFO['version']}</b> | {APP_INFO.get('author', 'CDG Capital')}</p>
    <p>© 2025 CDG Capital | Usage interne uniquement</p>
</div>
""", unsafe_allow_html=True)
