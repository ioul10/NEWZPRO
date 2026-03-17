# =============================================================================
# NEWZ - Page Export de Rapports
# Fichier : pages/export.py
# Importe les graphiques des autres pages
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
    COLORS = {'primary': '#005696', 'secondary': '#003d6b', 'accent': '#00a8e8', 
              'success': '#28a745', 'danger': '#dc3545'}
    APP_INFO = {'name': 'Newz', 'version': '2.0.0', 'author': 'CDG Capital'}

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
# GÉNÉRATEUR DE RAPPORT
# -----------------------------------------------------------------------------

def generate_report_html():
    """Génère le rapport HTML avec les graphiques des autres pages"""
    
    bourse_data = st.session_state.get('bourse_data', {})
    excel_data = st.session_state.get('excel_data', {})
    news_data = st.session_state.get('news_data', [])
    inflation_rate = st.session_state.get('inflation_rate', -0.8)
    actions_data = st.session_state.get('actions_data', None)
    selected = st.session_state.get('export_selected_sections', [])
    
    # Données
    masi_val = bourse_data.get('masi', {}).get('value', 12450)
    masi_chg = bourse_data.get('masi', {}).get('change', 0.85)
    msi20_val = bourse_data.get('msi20', {}).get('value', 1580)
    msi20_chg = bourse_data.get('msi20', {}).get('change', 1.20)
    
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
    
    # IMPORTER les fonctions de graphiques des autres pages
    try:
        from pages.bdc_statut import generate_masi_chart_percentage, generate_msi20_chart_percentage
        from pages.bam import generate_bdt_curve_chart, generate_monia_chart, generate_fx_chart
        
        # Générer les graphiques en HTML
        masi_html = generate_masi_chart_percentage(bourse_data, days=30).to_html(full_html=False, include_plotlyjs='cdn')
        msi20_html = generate_msi20_chart_percentage(bourse_data, days=30).to_html(full_html=False, include_plotlyjs='cdn')
        bdt_html = generate_bdt_curve_chart(excel_data).to_html(full_html=False, include_plotlyjs='cdn')
        mon_html = generate_monia_chart(excel_data).to_html(full_html=False, include_plotlyjs='cdn')
        eur_html = generate_fx_chart(excel_data, 'EUR/MAD')[0].to_html(full_html=False, include_plotlyjs='cdn')
        usd_html = generate_fx_chart(excel_data, 'USD/MAD')[0].to_html(full_html=False, include_plotlyjs='cdn')
        
    except Exception as e:
        st.warning(f"⚠️ Erreur import graphiques: {str(e)}")
        masi_html = msi20_html = bdt_html = mon_html = eur_html = usd_html = "<p>Graphique non disponible</p>"
    
    html = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <title>Newz Report - {datetime.now().strftime('%d/%m/%Y')}</title>
        <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f5f5f5; padding: 20px; }}
            .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 40px; border-radius: 15px; }}
            .header {{ background: linear-gradient(135deg, #005696 0%, #003d6b 100%); color: white; padding: 40px; text-align: center; border-radius: 15px; margin-bottom: 40px; }}
            .header h1 {{ font-size: 42px; margin-bottom: 10px; }}
            .section {{ margin-bottom: 40px; padding: 30px; border-left: 5px solid #005696; background: #fafafa; border-radius: 8px; }}
            .section h2 {{ color: #005696; font-size: 24px; margin-bottom: 25px; border-bottom: 2px solid #005696; padding-bottom: 10px; }}
            .chart-full-width {{ width: 100%; margin: 25px 0; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
            .kpi-grid {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 15px; margin: 20px 0; }}
            .kpi-card {{ background: white; padding: 15px; border-radius: 8px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
            .kpi-card h4 {{ color: #666; font-size: 11px; margin-bottom: 8px; }}
            .kpi-card .value {{ font-size: 24px; font-weight: bold; color: #005696; }}
            .positive {{ color: #28a745; }}
            .negative {{ color: #dc3545; }}
            .news-item {{ background: white; padding: 12px; margin: 8px 0; border-radius: 6px; border-left: 3px solid #005696; font-size: 13px; }}
            .footer {{ margin-top: 50px; padding: 30px; background: linear-gradient(135deg, #005696 0%, #003d6b 100%); color: white; text-align: center; border-radius: 15px; }}
            @media print {{ body {{ background: white; }} .container {{ box-shadow: none; }} .chart-full-width {{ page-break-inside: avoid; }} }}
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
    
    # SECTION 2 : INDICES BOURSIERS (PLEINE LARGEUR)
    if 'bdc' in selected:
        html += f"""
            <div class="section">
                <h2>📈 Indices Boursiers</h2>
                <div class="chart-full-width">{masi_html}</div>
                <div class="chart-full-width">{msi20_html}</div>
            </div>
        """
    
    # SECTION 3 : BANK AL-MAGHRIB (PLEINE LARGEUR)
    if 'bam' in selected:
        html += f"""
            <div class="section">
                <h2>🏦 Bank Al-Maghrib</h2>
                <h3 style="color:#003d6b; margin:20px 0 15px 0; font-size:18px;">Taux Directeur</h3>
                <div class="chart-full-width">{bdt_html}</div>
                <h3 style="color:#003d6b; margin:20px 0 15px 0; font-size:18px;">Indice MONIA</h3>
                <div class="chart-full-width">{mon_html}</div>
                <h3 style="color:#003d6b; margin:20px 0 15px 0; font-size:18px;">EUR/MAD</h3>
                <div class="chart-full-width">{eur_html}</div>
                <h3 style="color:#003d6b; margin:20px 0 15px 0; font-size:18px;">USD/MAD</h3>
                <div class="chart-full-width">{usd_html}</div>
            </div>
        """
    
    # SECTION 4 : NEWS
    if 'news' in selected and news_data:
        html += """<div class="section"><h2>📰 Actualités</h2>"""
        for news in news_data[:8]:
            html += f"""<div class="news-item"><b>{news.get('title', 'N/A')}</b><br>{news.get('summary', '')[:150]}</div>"""
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
        <p style="margin: 10px 0 0 0; color: #666;">Générez des rapports professionnels</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Sections à inclure")
    
    sections = {
        'summary': '📊 Synthèse',
        'bdc': '📈 Indices (MASI + MSI20)',
        'bam': '🏦 BAM (Taux + BDT + MONIA + FX)',
        'news': '📰 Actualités'
    }
    
    for key, label in sections.items():
        st.checkbox(label, value=True, key=f"chk_{key}")
    
    st.markdown("---")
    
    if st.button("🚀 Générer le Rapport", type="primary", use_container_width=True):
        with st.spinner("Génération en cours..."):
            try:
                html_content = generate_report_html()
                st.session_state.report_html = html_content
                st.success("✅ Rapport généré avec succès")
            except Exception as e:
                st.error(f"❌ Erreur : {str(e)}")
    
    if st.session_state.report_html:
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            st.download_button(
                label="📥 Télécharger HTML",
                data=st.session_state.report_html,
                file_name=f"newz_report_{datetime.now().strftime('%Y%m%d')}.html",
                mime="text/html",
                use_container_width=True
            )
        
        with col2:
            if st.button("👁️ Aperçu", use_container_width=True):
                st.components.v1.html(st.session_state.report_html, height=800, scrolling=True)

# =============================================================================
# APPEL
# =============================================================================
render()
