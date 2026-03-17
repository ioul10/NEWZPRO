# =============================================================================
# NEWZ - Page d'Accueil
# Fichier : pages/home.py
# =============================================================================

import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config.settings import COLORS, APP_INFO, MSI20_COMPOSITION

def render():
    """Fonction principale de la page d'accueil"""
    
    # SECTION 1 : BIENVENUE
    st.markdown(f"""
    <div style="background: white; padding: 40px; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); margin-bottom: 30px;">
        <h2 style="color: {COLORS['primary']}; margin-bottom: 20px;">👋 Bienvenue sur Newz</h2>
        <p style="font-size: 16px; line-height: 1.8; color: #555;">
            Plateforme de market data pour <b>CDG Capital</b>. Cette application vous permet de centraliser, 
            analyser et exporter les données financières marocaines en temps réel.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # SECTION 2 : FONCTIONNALITÉS
    st.markdown("### 🚀 Fonctionnalités Principales")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("**📥 Data Ingestion**\n\n- Upload Excel\n- Scraping Bourse\n- Actualités\n- Données BAM")
    
    with col2:
        st.info("**📊 Analyse**\n\n- Indices MASI/MSI20\n- Courbes des taux\n- Devises\n- Corrélations")
    
    with col3:
        st.info("**📤 Export**\n\n- Rapports HTML\n- Conversion PDF\n- Graphiques\n- Design CDG")
    
    # SECTION 3 : MSI20
    st.markdown("### 📈 Composition du MSI20")
    st.info(f"**{len(MSI20_COMPOSITION)} actions** composent l'indice MSI20.")
    
    df_msi20 = pd.DataFrame(MSI20_COMPOSITION)
    st.dataframe(df_msi20, use_container_width=True, hide_index=True)
    
    # SECTION 4 : ÉTAT DES DONNÉES
    st.markdown("### 📊 État des Données")
    
    has_excel = bool(st.session_state.get('excel_data', {}))
    has_bourse = bool(st.session_state.get('bourse_data', {}))
    has_news = bool(st.session_state.get('news_data', []))
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.success("✅ Excel chargé" if has_excel else "⚪ Excel")
    
    with col2:
        st.success("✅ Bourse" if has_bourse else "⚪ Bourse")
    
    with col3:
        st.success(f"✅ News ({len(st.session_state.news_data)})" if has_news else "⚪ News")
    
    if st.session_state.get('last_update'):
        st.caption(f"Dernière MAJ : {st.session_state.last_update.strftime('%d/%m/%Y %H:%M')}")

# Point d'entrée
if __name__ == "__main__":
    render()
