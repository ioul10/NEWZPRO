# =============================================================================
# NEWZ - Page d'Accueil
# =============================================================================

import streamlit as st
from config.settings import COLORS

def render():
    st.markdown(f"""
    <div style="background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
        <h2 style="color: {COLORS['primary']};">👋 Bienvenue sur Newz</h2>
        <p style="font-size: 16px; line-height: 1.6;">
            Plateforme de market data pour CDG Capital.
        </p>
        <p style="font-size: 16px; line-height: 1.6;">
            Cette application vous permet de :
        </p>
        <ul style="font-size: 16px; line-height: 1.8;">
            <li>📥 <b>Importer</b> des données depuis Excel (BDT, FX, MONIA)</li>
            <li>📊 <b>Visualiser</b> les indices boursiers (MASI, MSI20)</li>
            <li>🏦 <b>Analyser</b> les courbes de taux et devises</li>
            <li>📰 <b>Suivre</b> l'actualité financière marocaine</li>
            <li>📤 <b>Générer</b> des rapports professionnels</li>
        </ul>
    </div>
    
    <div style="margin-top: 30px; display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px;">
        <div style="background: {COLORS['light']}; padding: 20px; border-radius: 10px; border-left: 5px solid {COLORS['primary']};">
            <h3 style="margin: 0; color: {COLORS['primary']};">📥 Données</h3>
            <p style="margin: 10px 0 0 0; font-size: 14px;">Import Excel + Scraping automatique</p>
        </div>
        <div style="background: {COLORS['light']}; padding: 20px; border-radius: 10px; border-left: 5px solid {COLORS['accent']};">
            <h3 style="margin: 0; color: {COLORS['accent']};">📊 Analyse</h3>
            <p style="margin: 10px 0 0 0; font-size: 14px;">Graphiques interactifs et statistiques</p>
        </div>
        <div style="background: {COLORS['light']}; padding: 20px; border-radius: 10px; border-left: 5px solid {COLORS['success']};">
            <h3 style="margin: 0; color: {COLORS['success']};">📤 Rapports</h3>
            <p style="margin: 10px 0 0 0; font-size: 14px;">Export HTML/PDF professionnel</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🚀 Commencer →", type="primary", use_container_width=True):
        st.session_state.current_page = "data_ingestion"
        st.rerun()
