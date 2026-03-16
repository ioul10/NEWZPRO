# =============================================================================
# NEWZ - Application Principale (VERSION CORRIGÉE)
# =============================================================================

import streamlit as st
from pathlib import Path
import sys

# Configuration de la page (DOIT ÊTRE LA PREMIÈRE COMMANDE)
st.set_page_config(
    page_title="Newz | Market Data",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ajout du chemin pour les imports
sys.path.append(str(Path(__file__).resolve().parent))

# Import de la config
try:
    from config.settings import COLORS, APP_VERSION
except:
    COLORS = {
        'primary': '#005696',
        'secondary': '#003d6b',
        'accent': '#00a8e8',
        'success': '#28a745',
        'warning': '#ffc107',
        'danger': '#dc3545',
        'light': '#f8f9fa'
    }
    APP_VERSION = "2.0.0"

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
    .stSidebar {{
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown(f"""
<div class="main-header">
    <h1>🏦 CDG Capital</h1>
    <p><b>Newz</b> — Market Data Platform v{APP_VERSION}</p>
</div>
""", unsafe_allow_html=True)

# Menu de navigation
menu = st.sidebar.radio(
    "Navigation",
    ["🏠 Accueil", "📥 Data Ingestion", "📊 BDC Statut", "🏦 BAM", "📰 Macronews", "📤 Export"],
    index=0
)

# Initialisation de l'état de session
if 'current_page' not in st.session_state:
    st.session_state.current_page = "home"

# Routage des pages
try:
    if menu == "🏠 Accueil":
        from pages.home import render as render_home
        render_home()
    
    elif menu == "📥 Data Ingestion":
        from pages.data_ingestion import render as render_ingestion
        render_ingestion()
    
    elif menu == "📊 BDC Statut":
        from pages.bdc_statut import render as render_bdc
        render_bdc()
    
    elif menu == "🏦 BAM":
        from pages.bam import render as render_bam
        render_bam()
    
    elif menu == "📰 Macronews":
        from pages.macronews import render as render_macronews
        render_macronews()
    
    elif menu == "📤 Export":
        st.info("📤 Page Export - En cours de développement")
        st.markdown("""
        Cette page permettra de :
        - Générer des rapports HTML/PDF
        - Exporter les graphiques
        - Télécharger les données
        """)

except Exception as e:
    st.error(f"❌ Erreur de chargement de la page : {str(e)}")
    st.exception(e)

# Footer
st.sidebar.markdown("---")
st.sidebar.caption(f"© 2025 CDG Capital\nUsage interne uniquement")
