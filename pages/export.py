# =============================================================================
# NEWZ - Page Export de Rapport (VERSION ULTRA-SIMPLIFIÉE)
# =============================================================================

import streamlit as st
from datetime import datetime
import base64

# Initialisation IMMÉDIATE (avant toute utilisation)
if 'export_selected_sections' not in st.session_state:
    st.session_state.export_selected_sections = ['summary', 'bdc', 'bam', 'inflation']
if 'report_html' not in st.session_state:
    st.session_state.report_html = None

def render():
    """Fonction principale"""
    
    st.markdown("## 📤 Export de Rapport")
    
    # Sélection des sections
    st.markdown("### Étape 1 : Sélection du Contenu")
    
    sections = {
        'summary': '📊 Synthèse Executive',
        'bdc': '📈 BDC Statut',
        'bam': '🏦 Bank Al-Maghrib',
        'inflation': '💹 Inflation',
        'news': '📰 Actualités'
    }
    
    for key, label in sections.items():
        if key not in st.session_state.export_selected_sections:
            st.session_state.export_selected_sections.append(key)
        
        st.checkbox(label, value=True, key=f"chk_{key}")
    
    # Génération
    st.markdown("### Étape 2 : Génération")
    
    if st.button("🚀 Générer le Rapport", type="primary"):
        html = """
        <html>
        <head><title>Newz Report</title></head>
        <body>
        <h1>CDG Capital - Rapport</h1>
        <p>Rapport généré avec succès !</p>
        <p>Date: """ + datetime.now().strftime('%d/%m/%Y') + """</p>
        </body>
        </html>
        """
        st.session_state.report_html = html
        st.success("✅ Rapport généré !")
    
    # Téléchargement
    if st.session_state.report_html:
        st.download_button(
            label="📥 Télécharger",
            data=st.session_state.report_html,
            file_name="report.html",
            mime="text/html"
        )

if __name__ == "__main__":
    render()
