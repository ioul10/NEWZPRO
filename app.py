# =============================================================================
# NEWZ - Market Data Platform
# Fichier Principal - app.py
# Navigation Multi-Pages
# =============================================================================

import streamlit as st
from pathlib import Path
import sys
from datetime import datetime

# Configuration de la page (DOIT ÊTRE LA PREMIÈRE COMMANDE)
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
        'danger': '#dc3545',
        'light': '#f8f9fa'
    }
    APP_INFO = {'name': 'Newz', 'version': '2.0.0', 'author': 'CDG Capital'}

# -----------------------------------------------------------------------------
# INITIALISATION SESSION STATE
# -----------------------------------------------------------------------------

def init_session_state():
    """Initialise toutes les variables de session"""
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
    if 'top_movers' not in st.session_state:
        st.session_state.top_movers = None
    if 'correlation_period' not in st.session_state:
        st.session_state.correlation_period = 90

init_session_state()

# -----------------------------------------------------------------------------
# CSS PERSONNALISÉ
# -----------------------------------------------------------------------------

st.markdown(f"""
<style>
    /* Header principal */
    .main-header {{
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%);
        color: white;
        padding: 30px;
        border-radius: 10px;
        margin-bottom: 20px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }}
    .main-header h1 {{
        margin: 0;
        font-size: 36px;
        font-weight: 700;
    }}
    .main-header p {{
        margin: 10px 0 0 0;
        opacity: 0.9;
        font-size: 14px;
    }}
    
    /* Sidebar */
    .stSidebar {{
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }}
    
    /* Footer */
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
# HEADER
# -----------------------------------------------------------------------------

st.markdown(f"""
<div class="main-header">
    <h1>NEWZ</h1>
    <p> Market Data Platform v{APP_INFO.get('version', '2.0.0')}</p>
    <p style="font-size: 11px; opacity: 0.7;">{APP_INFO.get('copyright', '© 2025 CDG Capital')} | {APP_INFO.get('confidentiality', 'Usage interne uniquement')}</p>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# NAVIGATION MULTI-PAGES
# -----------------------------------------------------------------------------

# Définir les pages de l'application
pages = [
    st.Page("pages/home.py", title="Accueil", icon="🏠"),
    st.Page("pages/data_ingestion.py", title="Data Ingestion", icon="📥"),
    st.Page("pages/bdc_statut.py", title="BDC Statut", icon="📊"),
    st.Page("pages/bam.py", title="BAM", icon="🏦"),
    st.Page("pages/macronews.py", title="Macronews", icon="📰"),
    st.Page("pages/export.py", title="Export", icon="📤"),
]

# Créer la navigation (affichage automatique dans la sidebar)
pg = st.navigation(pages)

# Exécuter la page sélectionnée
pg.run()

# -----------------------------------------------------------------------------
# FOOTER
# -----------------------------------------------------------------------------

st.markdown(f"""
<div class="footer">
    <p><b>{APP_INFO.get('name', 'Newz')} v{APP_INFO.get('version', '2.0.0')}</b> | {APP_INFO.get('author', 'CDG Capital - OULMADANI Ilyas & ATANANE Oussama')}</p>
    <p>Dernière mise à jour : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
    <p>Données : Bourse de Casablanca | Bank Al-Maghrib | HCP | Ilboursa</p>
</div>
""", unsafe_allow_html=True)
