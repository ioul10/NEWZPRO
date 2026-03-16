# NEWZ - Export (Version Simplifiée)
import streamlit as st
from datetime import datetime

# Initialisation
if 'export_selected_sections' not in st.session_state:
    st.session_state.export_selected_sections = ['summary', 'bdc', 'bam', 'inflation']
if 'report_html' not in st.session_state:
    st.session_state.report_html = None

def generate_report_html():
    """Génère un rapport HTML simple"""
    return f"""
    <html>
    <head><title>Newz Report</title></head>
    <body style="font-family: Arial; padding: 40px;">
        <h1 style="color: #005696;">🏦 CDG CAPITAL</h1>
        <h2>Newz — Market Data Platform</h2>
        <p><b>Date :</b> {datetime.now().strftime('%d/%m/%Y')}</p>
        <hr>
        <h3>📊 Synthèse Executive</h3>
        <p>MASI: 12,450 (+0.85%)</p>
        <p>MSI20: 1,580 (+1.20%)</p>
        <p>EUR/MAD: 10.75</p>
        <p>USD/MAD: 9.85</p>
        <p>Inflation: -0.80%</p>
        <hr>
        <p style="color: #666; font-size: 12px;">CDG Capital - Usage interne uniquement</p>
    </body>
    </html>
    """

def render():
    """Fonction principale"""
    st.markdown("## 📤 Export de Rapport")
    
    # Sélection
    st.markdown("### Étape 1 : Sélection")
    sections = {
        'summary': '📊 Synthèse',
        'bdc': '📈 BDC Statut',
        'bam': '🏦 BAM',
        'inflation': '💹 Inflation',
        'news': '📰 Actualités'
    }
    
    for key, label in sections.items():
        st.checkbox(label, value=(key in st.session_state.export_selected_sections), key=f"chk_{key}")
    
    # Génération
    st.markdown("### Étape 2 : Génération")
    
    if st.button("🚀 Générer", type="primary"):
        html = generate_report_html()
        st.session_state.report_html = html
        st.success("✅ Rapport généré !")
    
    # Téléchargement
    if st.session_state.report_html:
        st.download_button(
            label="📥 Télécharger HTML",
            data=st.session_state.report_html,
            file_name="report.html",
            mime="text/html"
        )

# Point d'entrée
if __name__ == "__main__":
    render()
