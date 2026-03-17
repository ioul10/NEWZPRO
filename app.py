# =============================================================================
# NEWZ - Market Data Platform
# Application Principale
# Fichier : app.py
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
    from config.settings import COLORS, APP_INFO, MSI20_COMPOSITION, get_last_update_timestamp
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
    APP_INFO = {'name': 'Newz', 'version': '2.0.0'}

# -----------------------------------------------------------------------------
# CSS PERSONNALISÉ
# -----------------------------------------------------------------------------

st.markdown(f"""
<style>
    /* Header principal */
    .main-header {{
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%);
        color: white;
        padding: 40px;
        border-radius: 15px;
        margin-bottom: 30px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }}
    .main-header h1 {{
        margin: 0;
        font-size: 42px;
        font-weight: 700;
    }}
    .main-header p {{
        margin: 10px 0 0 0;
        opacity: 0.9;
        font-size: 16px;
    }}
    
    /* Sidebar */
    .stSidebar {{
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }}
    .stSidebar .stRadio {{
        padding: 10px;
    }}
    
    /* Cartes KPI */
    .kpi-card {{
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 25px;
        border-radius: 10px;
        text-align: center;
        border-left: 5px solid {COLORS['primary']};
        margin: 10px 0;
    }}
    .kpi-card h4 {{
        color: #666;
        font-size: 14px;
        margin-bottom: 10px;
        text-transform: uppercase;
    }}
    .kpi-card .value {{
        font-size: 32px;
        font-weight: bold;
        color: {COLORS['primary']};
    }}
    .kpi-card .positive {{ color: {COLORS['success']}; }}
    .kpi-card .negative {{ color: {COLORS['danger']}; }}
    
    /* Sections */
    .section {{
        background: white;
        padding: 30px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 30px;
        border-left: 5px solid {COLORS['primary']};
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
    
    /* Boutons */
    .stButton > button {{
        border-radius: 8px;
        font-weight: 600;
    }}
    
    /* Alertes */
    .stAlert {{
        border-radius: 8px;
    }}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# INITIALISATION DE L'ÉTAT DE SESSION
# -----------------------------------------------------------------------------

def init_session_state():
    """Initialise toutes les variables de session"""
    
    # Data Ingestion
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
    
    # Export
    if 'export_selected_sections' not in st.session_state:
        st.session_state.export_selected_sections = ['summary', 'bdc', 'bam', 'inflation']
    if 'report_html' not in st.session_state:
        st.session_state.report_html = None

init_session_state()

# -----------------------------------------------------------------------------
# HEADER PRINCIPAL
# -----------------------------------------------------------------------------

st.markdown(f"""
<div class="main-header">
    <h1>NEWZ</h1>
    <p><b>{APP_INFO['name']}</b> — Market Data Platform v{APP_INFO['version']}</p>
    <p style="font-size: 12px; opacity: 0.7;">{APP_INFO['copyright']} | {APP_INFO['confidentiality']}</p>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# MENU DE NAVIGATION
# -----------------------------------------------------------------------------

menu = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Accueil",
        "📥 Data Ingestion",
        "📊 BDC Statut",
        "🏦 BAM",
        "📰 Macronews",
        "📤 Export"
    ],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.markdown(f"""
**📊 État des Données**
""")

# Afficher l'état des données
if st.session_state.last_update:
    st.sidebar.success(f"✅ MAJ: {st.session_state.last_update.strftime('%H:%M')}")
else:
    st.sidebar.caption("⚪ Aucune donnée chargée")

st.sidebar.markdown("---")
st.sidebar.caption(f"{APP_INFO['copyright']}\n{APP_INFO['confidentiality']}")

# -----------------------------------------------------------------------------
# ROUTAGE DES PAGES
# -----------------------------------------------------------------------------

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
        from pages.export import render as render_export
        render_export()

except ImportError as e:
    st.error(f"❌ Erreur d'import : {str(e)}")
    st.info("""
    **Pages manquantes :**
    
    Assurez-vous que tous les fichiers suivants existent dans le dossier `pages/` :
    - home.py
    - data_ingestion.py
    - bdc_statut.py
    - bam.py
    - macronews.py
    - export.py
    """)
    st.exception(e)

except Exception as e:
    st.error(f"❌ Erreur de chargement : {str(e)}")
    st.exception(e)

# -----------------------------------------------------------------------------
# FOOTER
# -----------------------------------------------------------------------------

st.markdown(f"""
<div class="footer">
    <p><b>{APP_INFO['name']} v{APP_INFO['version']}</b> | {APP_INFO['author']}</p>
    <p>Dernière mise à jour : {get_last_update_timestamp()}</p>
    <p>Données : Bourse de Casablanca | Bank Al-Maghrib | HCP | Ilboursa</p>
</div>
""", unsafe_allow_html=True)
