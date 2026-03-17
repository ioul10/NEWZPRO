# =============================================================================
# NEWZ - Page Data Ingestion (Version Simplifiée)
# =============================================================================

import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))

try:
    from config.settings import COLORS
except:
    COLORS = {'primary': '#005696', 'success': '#28a745', 'danger': '#dc3545'}

# Initialisation session
if 'excel_data' not in st.session_state:
    st.session_state.excel_data = {}
if 'bourse_data' not in st.session_state:
    st.session_state.bourse_data = {}
if 'news_data' not in st.session_state:
    st.session_state.news_data = []
if 'last_update' not in st.session_state:
    st.session_state.last_update = None

def render():
    """Fonction principale"""
    
    # Header
    st.markdown(f"""
    <div style="background: white; padding: 25px; border-radius: 10px; margin-bottom: 25px;">
        <h2 style="color: {COLORS['primary']}; margin: 0;">📥 Data Ingestion</h2>
        <p style="margin: 10px 0 0 0; color: #666;">Import des données</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Section 1: Excel
    st.markdown("### 1️⃣ Import Excel")
    
    uploaded_file = st.file_uploader("Choisissez un fichier Excel", type=['xlsx'])
    
    if uploaded_file is not None:
        if st.button("Traiter"):
            try:
                excel_data = pd.read_excel(uploaded_file, sheet_name=None)
                st.session_state.excel_data = excel_data
                st.session_state.last_update = datetime.now()
                st.success("Fichier traité !")
                st.rerun()
            except Exception as e:
                st.error(f"Erreur: {e}")
    
    if st.session_state.excel_
        st.write(f"Feuilles chargées: {list(st.session_state.excel_data.keys())}")
    
    st.markdown("---")
    
    # Section 2: Bourse (Simulée pour l'instant)
    st.markdown("### 2️⃣ Bourse de Casablanca")
    
    if st.button("Actualiser les données"):
        with st.spinner("Chargement..."):
            # Données simulées
            st.session_state.bourse_data = {
                'masi': {'value': 12450.50, 'change': 0.85},
                'msi20': {'value': 1580.30, 'change': 1.20},
                'status': 'success'
            }
            st.session_state.last_update = datetime.now()
            st.success("Données actualisées !")
            st.rerun()
    
    if st.session_state.bourse_data.get('status') == 'success':
        col1, col2 = st.columns(2)
        with col1:
            st.metric("MASI", f"{st.session_state.bourse_data['masi']['value']:,.2f}", 
                     f"{st.session_state.bourse_data['masi']['change']:+.2f}%")
        with col2:
            st.metric("MSI20", f"{st.session_state.bourse_data['msi20']['value']:,.2f}",
                     f"{st.session_state.bourse_data['msi20']['change']:+.2f}%")
    
    st.markdown("---")
    
    # Section 3: News
    st.markdown("### 3️⃣ Actualités")
    
    if st.button("Collecter les news"):
        st.session_state.news_data = [
            {'title': 'News 1', 'summary': 'Résumé 1', 'category': 'Marché', 
             'timestamp': datetime.now(), 'url': 'https://www.ilboursa.com'},
            {'title': 'News 2', 'summary': 'Résumé 2', 'category': 'Économie',
             'timestamp': datetime.now(), 'url': 'https://www.ilboursa.com'}
        ]
        st.session_state.last_update = datetime.now()
        st.success(f"{len(st.session_state.news_data)} news collectées !")
        st.rerun()
    
    if st.session_state.news_
        for news in st.session_state.news_data:
            st.expander(news['title']).write(news['summary'])
    
    st.markdown("---")
    
    # Résumé
    st.markdown("### 📊 Résumé")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Excel", "✅" if st.session_state.excel_data else "⚪")
    with col2:
        st.metric("Bourse", "✅" if st.session_state.bourse_data.get('status') == 'success' else "⚪")
    with col3:
        st.metric("News", len(st.session_state.news_data))
    
    if st.session_state.last_update:
        st.caption(f"Dernière MAJ: {st.session_state.last_update.strftime('%H:%M:%S')}")

# Appel de render
render()
