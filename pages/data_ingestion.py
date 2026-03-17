# =============================================================================
# NEWZ - Page Data Ingestion
# Fichier : pages/data_ingestion.py
# =============================================================================

import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))

# Import sécurisé de la configuration
try:
    from config.settings import COLORS, DATA_DIR, MSI20_COMPOSITION
except ImportError:
    COLORS = {'primary': '#005696', 'success': '#28a745', 'danger': '#dc3545'}
    DATA_DIR = Path(__file__).parent.parent / 'data'
    MSI20_COMPOSITION = []

# -----------------------------------------------------------------------------
# INITIALISATION LOCALE
# -----------------------------------------------------------------------------

def init_local_session():
    """Initialise les variables spécifiques à cette page"""
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

init_local_session()

# -----------------------------------------------------------------------------
# FONCTIONS DE TRAITEMENT
# -----------------------------------------------------------------------------

def process_excel_file(uploaded_file):
    """Traite un fichier Excel uploadé"""
    try:
        excel_data = pd.read_excel(uploaded_file, sheet_name=None)
        processed = {}
        
        expected_sheets = ['Courbe MAD', 'Courbe_EUR', 'MONIA', 'MADBDT_52W', 'USD_MAD', 'EUR_MAD']
        
        for sheet in expected_sheets:
            if sheet in excel_data:
                df = excel_data[sheet].dropna(how='all')
                processed[sheet] = df
            else:
                processed[sheet] = pd.DataFrame()
        
        return processed
    except Exception as e:
        st.error(f"Erreur lecture Excel : {str(e)}")
        return None

def scrape_bourse_casa():
    """Scraping simulé de la Bourse de Casablanca"""
    try:
        return {
            'masi': {'value': 12450.50, 'change': 0.85, 'volume': 45000000, 'timestamp': datetime.now()},
            'msi20': {'value': 1580.30, 'change': 1.20, 'volume': 38000000, 'timestamp': datetime.now()},
            'status': 'success'
        }
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def scrape_ilboursa_news(limit=10):
    """Scraping simulé des news Ilboursa"""
    try:
        news_items = [
            {'title': 'Bank Al-Maghrib maintient son taux directeur à 3%', 'summary': 'Le conseil de BAM a décidé de maintenir son taux...', 'source': 'Ilboursa', 'timestamp': datetime.now(), 'url': 'https://www.ilboursa.com', 'category': 'Monétaire'},
            {'title': 'Le MASI franchit la barre des 12 500 points', 'summary': 'La bourse de Casablanca a clôturé en hausse...', 'source': 'Ilboursa', 'timestamp': datetime.now(), 'url': 'https://www.ilboursa.com', 'category': 'Marché'},
            {'title': 'L\'inflation au Maroc ralentit à 0,8%', 'summary': 'Selon le HCP, l\'inflation a continué de ralentir...', 'source': 'Ilboursa', 'timestamp': datetime.now(), 'url': 'https://www.ilboursa.com', 'category': 'Économie'}
        ]
        return news_items[:limit]
    except:
        return []

# -----------------------------------------------------------------------------
# FONCTION PRINCIPALE
# -----------------------------------------------------------------------------

def render():
    """Fonction principale de la page Data Ingestion"""
    
    # HEADER
    st.markdown(f"""
    <div style="background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 25px;">
        <h2 style="color: {COLORS['primary']}; margin: 0;">📥 Data Ingestion</h2>
        <p style="margin: 10px 0 0 0; color: #666;">Import des données et collecte automatique</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ---------------------------------------------------------------------
    # SECTION 1 : UPLOAD EXCEL
    # ---------------------------------------------------------------------
    st.markdown("### 1️⃣ Import des Données Structurées (Excel)")
    
    st.info("""
    **📋 Structure attendue :**
    - `Courbe MAD` : ccy_iso, hist_date, tenor_mat, zero_rate
    - `Courbe_EUR` : devise, date_transaction, tenor, taux_zero_coupon
    - `MONIA` : quote_date, rate
    - `USD_MAD` / `EUR_MAD` : iso_code1, quote_date, ask, bid, Mid
    """)
    
    uploaded_file = st.file_uploader("📁 Sélectionnez votre fichier Excel", type=['xlsx', 'xls'])
    
    if uploaded_file is not None:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.success(f"Fichier : **{uploaded_file.name}**")
        
        with col2:
            if st.button("🔄 Traiter", use_container_width=True):
                with st.spinner("Traitement..."):
                    processed = process_excel_file(uploaded_file)
                    if processed:
                        st.session_state.excel_data = processed
                        st.session_state.last_update = datetime.now()
                        st.success("✅ Fichier traité !")
                        st.rerun()
    
    # Aperçu des données Excel
    excel_data = st.session_state.get('excel_data', {})
    if excel_data:
        st.markdown("#### 📋 Aperçu")
        sheet_options = [s for s in excel_data.keys() if not excel_data[s].empty]
        if sheet_options:
            selected = st.selectbox("Feuille :", sheet_options)
            if selected:
                st.dataframe(excel_data[selected].head(10), use_container_width=True)
                st.caption(f"Total : {len(excel_data[selected])} lignes")
    
    st.markdown("---")
    
    # ---------------------------------------------------------------------
    # SECTION 2 : BOURSE DE CASABLANCA
    # ---------------------------------------------------------------------
    st.markdown("### 2️⃣ Bourse de Casablanca")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("""
        **Données collectées :**
        - MASI (indice général)
        - MSI20 (20 valeurs liquides)
        - Volumes échangés
        """)
    
    with col2:
        bourse_data = st.session_state.get('bourse_data', {})
        is_success = bourse_data.get('status') == 'success'
        
        if st.button("🔄 Scraper", use_container_width=True, disabled=is_success):
            with st.spinner("Collecte..."):
                result = scrape_bourse_casa()
                if result.get('status') == 'success':
                    st.session_state.bourse_data = result
                    st.session_state.last_update = datetime.now()
                    st.success("✅ Données collectées !")
                    st.rerun()
                else:
                    st.error("❌ Échec")
    
    # Affichage des données Bourse
    bourse_data = st.session_state.get('bourse_data', {})
    if bourse_data.get('status') == 'success':
        col1, col2, col3 = st.columns(3)
        with col1:
            masi = bourse_data.get('masi', {})
            st.metric("MASI", f"{masi.get('value', 0):,.2f}", f"{masi.get('change', 0):+.2f}%")
        with col2:
            msi20 = bourse_data.get('msi20', {})
            st.metric("MSI20", f"{msi20.get('value', 0):,.2f}", f"{msi20.get('change', 0):+.2f}%")
        with col3:
            st.metric("Volume", f"{bourse_data.get('masi', {}).get('volume', 0)/1e6:.1f}M MAD")
    
    st.markdown("---")
    
    # ---------------------------------------------------------------------
    # SECTION 3 : NEWS ILBOURSA
    # ---------------------------------------------------------------------
    st.markdown("### 3️⃣ Actualités Financières")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("**Source :** www.ilboursa.com")
    
    with col2:
        if st.button("📰 Collecter", use_container_width=True):
            with st.spinner("Collecte..."):
                news = scrape_ilboursa_news(limit=10)
                if news:
                    st.session_state.news_data = news
                    st.session_state.last_update = datetime.now()
                    st.success(f"✅ {len(news)} news collectées !")
                    st.rerun()
    
    # Affichage des news
    news_data = st.session_state.get('news_data', [])
    if news_data:
        for i, news in enumerate(news_data[:5]):
            with st.expander(f"📄 {news['title']}", expanded=(i==0)):
                st.write(f"**Source :** {news['source']} | **Catégorie :** {news['category']}")
                st.write(f"**Date :** {news['timestamp'].strftime('%d/%m/%Y %H:%M')}")
                st.write(news['summary'])
    
    st.markdown("---")
    
    # ---------------------------------------------------------------------
    # SECTION 4 : RÉSUMÉ
    # ---------------------------------------------------------------------
    st.markdown("### 📊 Résumé")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sheets = len([s for s in excel_data.values() if not s.empty]) if excel_data else 0
        st.metric("Feuilles Excel", f"{sheets}/6")
    
    with col2:
        status = "✅ Chargé" if bourse_data.get('status') == 'success' else "⚪ Non chargé"
        st.metric("Bourse de Casa", status)
    
    with col3:
        st.metric("News", f"{len(news_data)}")
    
    if st.session_state.get('last_update'):
        st.caption(f"Dernière MAJ : {st.session_state.last_update.strftime('%d/%m/%Y %H:%M')}")
    
    # Bouton réinitialisation
    if st.button("🔄 Réinitialiser", type="secondary"):
        st.session_state.excel_data = {}
        st.session_state.bourse_data = {}
        st.session_state.news_data = []
        st.session_state.last_update = None
        st.success("Données réinitialisées !")
        st.rerun()

# =============================================================================
# APPEL DE LA FONCTION RENDER
# =============================================================================
render()
