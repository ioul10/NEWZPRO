# =============================================================================
# NEWZ - Page Export (Utilise données des pages)
# Fichier : pages/export.py
# =============================================================================

import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))

try:
    from config.settings import COLORS, APP_INFO
except ImportError:
    COLORS = {'primary': '#005696', 'secondary': '#003d6b'}
    APP_INFO = {'name': 'Newz', 'version': '2.0.0'}

# -----------------------------------------------------------------------------
# INITIALISATION
# -----------------------------------------------------------------------------

def init_local_session():
    if 'export_selected_sections' not in st.session_state:
        st.session_state.export_selected_sections = ['summary', 'bdc', 'bam', 'inflation']
    if 'report_html' not in st.session_state:
        st.session_state.report_html = None

init_local_session()

# -----------------------------------------------------------------------------
# GÉNÉRATEUR DE RAPPORT (Utilise données session_state)
# -----------------------------------------------------------------------------

def generate_report_html():
    """Génère le rapport avec les DONNÉES EXISTANTES des pages"""
    
    # Récupérer les données DÉJÀ DISPONIBLES
    bourse_data = st.session_state.get('bourse_data', {})
    excel_data = st.session_state.get('excel_data', {})
    news_data = st.session_state.get('news_data', [])
    inflation_rate = st.session_state.get('inflation_rate', -0.8)
    selected = st.session_state.get('export_selected_sections', [])
    
    # Données MASI/MSI20
    masi_val = bourse_data.get('masi', {}).get('value', 12450)
    masi_chg = bourse_data.get('masi', {}).get('change', 0.85)
    msi20_val = bourse_data.get('msi20', {}).get('value', 1580)
    msi20_chg = bourse_data.get('msi20', {}).get('change', 1.20)
    
    # USD/MAD et EUR/MAD (dernières valeurs)
    usd_mad = 9.85
    if 'USD_MAD' in excel_data and not excel_data['USD_MAD'].empty:
        df = excel_data['USD_MAD']
        if 'Mid' in df.columns:
            valid = df.dropna(subset=['Mid'])
            valid = valid[valid['Mid'] > 0]
            if not valid.empty:
                usd_mad = float(valid['Mid'].iloc[-1])
    
    eur_mad = 10.75
    if 'EUR_MAD' in excel_data and not excel_data['EUR_MAD'].empty:
        df = excel_data['EUR_MAD']
        if 'Mid' in df.columns:
            valid = df.dropna(subset=['Mid'])
            valid = valid[valid['Mid'] > 0]
            if not valid.empty:
                eur_mad = float(valid['Mid'].iloc[-1])
    
    # HTML simple et professionnel
    html = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <title>Newz Report - {datetime.now().strftime('%d/%m/%Y')}</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f5f5f5; padding: 20px; }}
            .container {{ max-width: 1000px; margin: 0 auto; background: white; padding: 40px; border-radius: 15px; }}
            .header {{ background: linear-gradient(135deg, #005696 0%, #003d6b 100%); color: white; padding: 40px; text-align: center; border-radius: 15px; margin-bottom: 40px; }}
            .header h1 {{ font-size: 42px; margin-bottom: 10px; }}
            .section {{ margin-bottom: 40px; padding: 30px; border-left: 5px solid #005696; background: #fafafa; border-radius: 8px; }}
            .section h2 {{ color: #005696; font-size: 28px; margin-bottom: 20px; border-bottom: 3px solid #005696; padding-bottom: 10px; }}
            .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 15px; margin: 20px 0; }}
            .kpi-card {{ background: white; padding: 20px; border-radius: 8px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
            .kpi-card h4 {{ color: #666; font-size: 12px; margin-bottom: 10px; }}
            .kpi-card .value {{ font-size: 28px; font-weight: bold; color: #005696; }}
            .positive {{ color: #28a745; }}
            .negative {{ color: #dc3545; }}
            .news-item {{ background: white; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #005696; }}
            .footer {{ margin-top: 50px; padding: 30px; background: linear-gradient(135deg, #005696 0%, #003d6b 100%); color: white; text-align: center; border-radius: 15px; }}
            @media print {{ body {{ background: white; }} .container {{ box-shadow: none; }} }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏦 CDG CAPITAL</h1>
                <h2>Newz — Market Data Platform</h2>
                <p>Rapport Hebdomadaire | {datetime.now().strftime('%d/%m/%Y')}</p>
            </div>
    """
    
    # SECTION 1 : SYNTHÈSE
    if 'summary' in selected:
        html += f"""
            <div class="section">
                <h2>📊 Synthèse Executive</h2>
                <div class="kpi-grid">
                    <div class="kpi-card"><h4>MASI</h4><div class="value">{masi_val:,.0f}</div>
                    <div class="{'positive' if masi_chg >= 0 else 'negative'}">{masi_chg:+.2f}%</div></div>
                    <div class="kpi-card"><h4>MSI20</h4><div class="value">{msi20_val:,.0f}</div>
                    <div class="{'positive' if msi20_chg >= 0 else 'negative'}">{msi20_chg:+.2f}%</div></div>
                    <div class="kpi-card"><h4>EUR/MAD</h4><div class="value">{eur_mad:.4f}</div></div>
                    <div class="kpi-card"><h4>USD/MAD</h4><div class="value">{usd_mad:.4f}</div></div>
                    <div class="kpi-card"><h4>Inflation</h4><div class="value">{inflation_rate:.2f}%</div></div>
                </div>
            </div>
        """
    
    # SECTION 2 : BDC STATUT
    if 'bdc' in selected:
        html += f"""
            <div class="section">
                <h2>📈 BDC Statut</h2>
                <p><b>MASI :</b> {masi_val:,.2f} ({masi_chg:+.2f}%)</p>
                <p><b>MSI20 :</b> {msi20_val:,.2f} ({msi20_chg:+.2f}%)</p>
                <p><b>Volume :</b> {bourse_data.get('masi', {}).get('volume', 0)/1e6:.1f}M MAD</p>
            </div>
        """
    
    # SECTION 3 : BAM
    if 'bam' in selected:
        html += f"""
            <div class="section">
                <h2>🏦 Bank Al-Maghrib</h2>
                <p><b>Taux Directeur :</b> 3.00%</p>
                <p><b>EUR/MAD :</b> {eur_mad:.4f}</p>
                <p><b>USD/MAD :</b> {usd_mad:.4f}</p>
            </div>
        """
    
    # SECTION 4 : INFLATION
    if 'inflation' in selected:
        html += f"""
            <div class="section">
                <h2>💹 Inflation (HCP)</h2>
                <p><b>Taux actuel :</b> {inflation_rate:.2f}%</p>
                <p><b>Cible BAM :</b> 2-3%</p>
                <p><b>Statut :</b> {'Dans la cible' if 2 <= inflation_rate <= 3 else 'Hors cible'}</p>
            </div>
        """
    
    # SECTION 5 : NEWS
    if 'news' in selected and news_data:
        html += """<div class="section"><h2>📰 Actualités</h2>"""
        for news in news_data[:10]:
            html += f"""<div class="news-item"><h4>{news.get('title', 'N/A')}</h4>
                <p><b>Source:</b> {news.get('source', 'N/A')} | {news.get('summary', '')[:200]}</p></div>"""
        html += "</div>"
    
    # Footer
    html += f"""
            <div class="footer">
                <p><b>CDG Capital — Market Data Team</b></p>
                <p>{APP_INFO.get('name', 'Newz')} v{APP_INFO.get('version', '2.0.0')} | Document confidentiel</p>
                <p>Généré le : {datetime.now().strftime('%d/%m/%Y à %H:%M')}</p>
            </div>
        </div>
    </body></html>
    """
    
    return html

# -----------------------------------------------------------------------------
# FONCTION PRINCIPALE
# -----------------------------------------------------------------------------

def render():
    """Fonction principale"""
    
    st.markdown(f"""
    <div style="background: white; padding: 25px; border-radius: 10px; margin-bottom: 25px;">
        <h2 style="color: {COLORS['primary']}; margin: 0;">📤 Export de Rapport</h2>
        <p style="margin: 10px 0 0 0; color: #666;">Générez des rapports basés sur les données collectées</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ÉTAPE 1 : SÉLECTION
    st.markdown("### Étape 1 : Sélection du Contenu")
    
    sections = {
        'summary': '📊 Synthèse Executive',
        'bdc': '📈 BDC Statut',
        'bam': '🏦 Bank Al-Maghrib',
        'inflation': '💹 Inflation (HCP)',
        'news': '📰 Actualités'
    }
    
    for key, label in sections.items():
        st.checkbox(label, value=True, key=f"chk_{key}")
    
    st.markdown("---")
    
    # ÉTAPE 2 : GÉNÉRATION
    st.markdown("### Étape 2 : Génération")
    
    if st.button("🚀 Générer le Rapport", type="primary", use_container_width=True):
        with st.spinner("Génération en cours..."):
            try:
                html_content = generate_report_html()
                st.session_state.report_html = html_content
                st.success("✅ Rapport généré !")
                st.balloons()
            except Exception as e:
                st.error(f"❌ Erreur : {str(e)}")
                st.exception(e)
    
    # ÉTAPE 3 : TÉLÉCHARGEMENT
    if st.session_state.report_html:
        st.markdown("---")
        st.markdown("### Étape 3 : Téléchargement")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.download_button(
                label="📥 Télécharger (HTML)",
                data=st.session_state.report_html,
                file_name=f"newz_report_{datetime.now().strftime('%Y%m%d_%H%M')}.html",
                mime="text/html",
                use_container_width=True,
                type="primary"
            )
        
        with col2:
            if st.button("👁️ Aperçu", use_container_width=True):
                st.components.v1.html(st.session_state.report_html, height=800, scrolling=True)

# =============================================================================
# APPEL
# =============================================================================
render()
