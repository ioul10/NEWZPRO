# =============================================================================
# NEWZ - Page Export de Rapport (VERSION COMPLÈTE)
# =============================================================================

import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
import sys
import base64

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config.settings import COLORS

# -----------------------------------------------------------------------------
# INITIALISATION DU SESSION_STATE (DÈS LE DÉBUT)
# -----------------------------------------------------------------------------
if 'export_selected_sections' not in st.session_state:
    st.session_state.export_selected_sections = ['summary', 'bdc', 'bam', 'inflation']
if 'report_html' not in st.session_state:
    st.session_state.report_html = None

# -----------------------------------------------------------------------------
# FONCTIONS DE GÉNÉRATION DE GRAPHIQUES HTML
# -----------------------------------------------------------------------------
def get_masi_chart_html():
    try:
        from pages.bdc_statut import generate_masi_chart
        bourse_data = st.session_state.get('bourse_data', {})
        fig = generate_masi_chart(bourse_data)
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
    except Exception as e:
        return f"<p style='color:red'>Graphique MASI: {str(e)}</p>"

def get_msi20_chart_html():
    try:
        from pages.bdc_statut import generate_msi20_chart
        bourse_data = st.session_state.get('bourse_data', {})
        fig = generate_msi20_chart(bourse_data)
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
    except Exception as e:
        return f"<p style='color:red'>Graphique MSI20: {str(e)}</p>"

def get_bdt_chart_html():
    try:
        from pages.bam import generate_bdt_curve_chart
        excel_data = st.session_state.get('excel_data', {})
        fig = generate_bdt_curve_chart(excel_data)
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
    except Exception as e:
        return f"<p style='color:red'>Graphique BDT: {str(e)}</p>"

def get_monias_chart_html():
    try:
        from pages.bam import generate_monia_chart
        excel_data = st.session_state.get('excel_data', {})
        fig = generate_monia_chart(excel_data)
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
    except Exception as e:
        return f"<p style='color:red'>Graphique MONIA: {str(e)}</p>"

def get_eur_mad_chart_html():
    try:
        from pages.bam import generate_fx_chart
        excel_data = st.session_state.get('excel_data', {})
        fig, _, _ = generate_fx_chart(excel_data, 'EUR/MAD')
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
    except Exception as e:
        return f"<p style='color:red'>Graphique EUR/MAD: {str(e)}</p>"

def get_usd_mad_chart_html():
    try:
        from pages.bam import generate_fx_chart
        excel_data = st.session_state.get('excel_data', {})
        fig, _, _ = generate_fx_chart(excel_data, 'USD/MAD')
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
    except Exception as e:
        return f"<p style='color:red'>Graphique USD/MAD: {str(e)}</p>"

def get_inflation_gauge_html():
    try:
        from pages.macronews import generate_inflation_gauge
        fig = generate_inflation_gauge(-0.8, 2.0, 3.0)
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
    except Exception as e:
        return f"<p style='color:red'>Jauge Inflation: {str(e)}</p>"

# -----------------------------------------------------------------------------
# GÉNÉRATEUR DE RAPPORT HTML
# -----------------------------------------------------------------------------
def generate_report_html():
    """Génère le rapport HTML complet"""
    
    bourse_data = st.session_state.get('bourse_data', {})
    excel_data = st.session_state.get('excel_data', {})
    news_data = st.session_state.get('news_data', [])
    selected_sections = st.session_state.get('export_selected_sections', [])
    
    # Données
    masi_value = bourse_data.get('masi', {}).get('value', 12450.50)
    masi_change = bourse_data.get('masi', {}).get('change', 0.85)
    msi20_value = bourse_data.get('msi20', {}).get('value', 1580.30)
    msi20_change = bourse_data.get('msi20', {}).get('change', 1.20)
    
    # USD/MAD
    usd_mad_df = excel_data.get('USD_MAD', pd.DataFrame())
    if not usd_mad_df.empty and 'Mid' in usd_mad_df.columns:
        usd_mad_rate = float(usd_mad_df['Mid'].iloc[-1])
    else:
        usd_mad_rate = 9.85
    
    # Construction HTML
    html = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <title>Newz Report - {datetime.now().strftime('%d/%m/%Y')}</title>
        <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; background: #f5f5f5; padding: 20px; }}
            .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 40px; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #005696 0%, #003d6b 100%); color: white; padding: 40px; text-align: center; border-radius: 15px; margin-bottom: 40px; }}
            .header h1 {{ font-size: 42px; margin-bottom: 10px; }}
            .section {{ margin-bottom: 40px; padding: 30px; background: white; border-radius: 10px; border-left: 5px solid #005696; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }}
            .section h2 {{ color: #005696; font-size: 28px; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 3px solid #005696; }}
            .section h3 {{ color: #003d6b; font-size: 22px; margin: 20px 0 15px 0; }}
            .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
            .kpi-card {{ background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); padding: 25px; border-radius: 10px; text-align: center; border-left: 5px solid #005696; }}
            .kpi-card h4 {{ color: #666; font-size: 14px; margin-bottom: 10px; text-transform: uppercase; }}
            .kpi-card .value {{ font-size: 32px; font-weight: bold; color: #005696; }}
            .positive {{ color: #28a745; }}
            .negative {{ color: #dc3545; }}
            .chart-container {{ margin: 30px 0; padding: 20px; background: white; border-radius: 10px; border: 1px solid #e0e0e0; }}
            .footer {{ margin-top: 50px; padding: 30px; background: linear-gradient(135deg, #005696 0%, #003d6b 100%); color: white; text-align: center; border-radius: 15px; }}
            .stamp {{ display: inline-block; border: 4px solid #dc3545; color: #dc3545; padding: 15px 40px; font-weight: bold; font-size: 24px; transform: rotate(-3deg); margin-top: 20px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background: #005696; color: white; font-weight: bold; }}
            tr:nth-child(even) {{ background: #f8f9fa; }}
            @media print {{ body {{ background: white; padding: 0; }} .container {{ box-shadow: none; padding: 20px; }} .no-print {{ display: none; }} }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏦 CDG CAPITAL</h1>
                <p><b>Newz — Market Data Platform</b></p>
                <p>Rapport Hebdomadaire | {datetime.now().strftime('%d/%m/%Y')}</p>
            </div>
    """
    
    # SECTION 1 : SYNTHÈSE
    if 'summary' in selected_sections:
        html += f"""
            <div class="section">
                <h2>📊 Synthèse Executive</h2>
                <div class="kpi-grid">
                    <div class="kpi-card"><h4>MASI</h4><div class="value">{masi_value:,.0f}</div><div class="{'positive' if masi_change >= 0 else 'negative'}">{masi_change:+.2f}%</div></div>
                    <div class="kpi-card"><h4>MSI20</h4><div class="value">{msi20_value:,.0f}</div><div class="{'positive' if msi20_change >= 0 else 'negative'}">{msi20_change:+.2f}%</div></div>
                    <div class="kpi-card"><h4>EUR/MAD</h4><div class="value">10.75</div><div class="positive">+0.10%</div></div>
                    <div class="kpi-card"><h4>USD/MAD</h4><div class="value">{usd_mad_rate:.4f}</div><div class="negative">-0.15%</div></div>
                    <div class="kpi-card"><h4>Inflation</h4><div class="value">-0.80%</div><div class="negative">Hors cible</div></div>
                </div>
            </div>
        """
    
    # SECTION 2 : BDC STATUT
    if 'bdc' in selected_sections:
        html += f"""
            <div class="section">
                <h2>📈 BDC Statut - Bourse de Casablanca</h2>
                <h3>Évolution du MASI</h3>
                <div class="chart-container">{get_masi_chart_html()}</div>
                <h3>Évolution du MSI20</h3>
                <div class="chart-container">{get_msi20_chart_html()}</div>
            </div>
        """
    
    # SECTION 3 : BAM
    if 'bam' in selected_sections:
        html += f"""
            <div class="section">
                <h2>🏦 Bank Al-Maghrib</h2>
                <h3>Courbe des Taux BDT</h3>
                <div class="chart-container">{get_bdt_chart_html()}</div>
                <h3>Indice MONIA</h3>
                <div class="chart-container">{get_monias_chart_html()}</div>
                <h3>Devises - EUR/MAD</h3>
                <div class="chart-container">{get_eur_mad_chart_html()}</div>
                <h3>Devises - USD/MAD</h3>
                <div class="chart-container">{get_usd_mad_chart_html()}</div>
            </div>
        """
    
    # SECTION 4 : INFLATION
    if 'inflation' in selected_sections:
        html += f"""
            <div class="section">
                <h2>💹 Inflation & Macroéconomie</h2>
                <div class="chart-container">{get_inflation_gauge_html()}</div>
                <p><b>Analyse :</b> L'inflation est actuellement en-dessous de la cible de Bank Al-Maghrib (2-3%).</p>
            </div>
        """
    
    # SECTION 5 : NEWS
    if 'news' in selected_sections and news_data:
        html += """
            <div class="section">
                <h2>📰 Actualités Marquantes</h2>
        """
        for news in news_data[:5]:
            html += f"""
                <div style="background:#f8f9fa; padding:15px; margin:10px 0; border-radius:8px; border-left:4px solid #005696;">
                    <h4 style="color:#005696; margin-bottom:5px;">{news['title']}</h4>
                    <p style="font-size:14px; color:#666;">{news['summary']}</p>
                </div>
            """
        html += "</div>"
    
    # Footer
    html += f"""
            <div class="footer">
                <p><b>CDG Capital — Market Data Team</b></p>
                <p>Newz v2.0.0 | Usage interne uniquement</p>
                <div class="stamp">ADMIN<br/>CONFIDENTIEL</div>
            </div>
        </div>
        <div class="no-print" style="background:#fff3cd; padding:20px; margin:20px auto; max-width:1200px; border-radius:10px; text-align:center;">
            <p><strong>💡 Pour PDF :</strong> Ctrl+P → Enregistrer au format PDF</p>
        </div>
    </body>
    </html>
    """
    
    return html

# -----------------------------------------------------------------------------
# PAGE PRINCIPALE
# -----------------------------------------------------------------------------
def render():
    """Fonction principale de la page Export"""
    
    # Initialisation SÉCURISÉE
    if 'export_selected_sections' not in st.session_state:
        st.session_state.export_selected_sections = ['summary', 'bdc', 'bam', 'inflation']
    if 'report_html' not in st.session_state:
        st.session_state.report_html = None
    
    st.markdown("## 📤 Export de Rapport Professionnel")
    
    # Étape 1 : Sélection
    st.markdown("### Étape 1 : Sélection du Contenu")
    
    sections = {
        'summary': '📊 Synthèse Executive',
        'bdc': '📈 BDC Statut (MASI + MSI20)',
        'bam': '🏦 BAM (BDT + MONIA + Devises)',
        'inflation': '💹 Inflation',
        'news': '📰 Actualités'
    }
    
    for key, label in sections.items():
        if key not in st.session_state.export_selected_sections:
            st.session_state.export_selected_sections.append(key)
        st.checkbox(label, value=True, key=f"chk_{key}")
    
    st.markdown("---")
    
    # Étape 2 : Génération
    st.markdown("### Étape 2 : Génération")
    
    if st.button("🚀 Générer le Rapport", type="primary", use_container_width=True):
        with st.spinner("Génération en cours..."):
            try:
                html_content = generate_report_html()
                st.session_state.report_html = html_content
                st.success("✅ Rapport généré avec succès !")
                st.balloons()
            except Exception as e:
                st.error(f"❌ Erreur : {str(e)}")
                st.exception(e)
    
    # Étape 3 : Téléchargement
    if st.session_state.report_html:
        st.markdown("---")
        st.markdown("### Étape 3 : Téléchargement")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.download_button(
                label="📥 Télécharger le Rapport (HTML)",
                data=st.session_state.report_html,
                file_name=f"newz_report_{datetime.now().strftime('%Y%m%d')}.html",
                mime="text/html",
                use_container_width=True,
                type="primary"
            )
        
        with col2:
            if st.button("👁️ Aperçu", use_container_width=True):
                st.components.v1.html(st.session_state.report_html, height=800, scrolling=True)
        
        st.info("💡 **Pour convertir en PDF :** Téléchargez le fichier HTML, ouvrez-le dans votre navigateur, puis Ctrl+P → Enregistrer au format PDF")

# Point d'entrée
if __name__ == "__main__":
    render()
