# =============================================================================
# NEWZ - Page Export de Rapport (VERSION FINALE)
# =============================================================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from pathlib import Path
import sys
import base64

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config.settings import COLORS

# -----------------------------------------------------------------------------
# 1. FONCTIONS DE GÉNÉRATION DE GRAPHIQUES
# -----------------------------------------------------------------------------
def get_masi_chart_html():
    """Génère le graphique MASI en HTML"""
    try:
        from pages.bdc_statut import generate_masi_chart
        bourse_data = st.session_state.get('bourse_data', {})
        fig = generate_masi_chart(bourse_data)
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
    except:
        return "<p>Graphique MASI non disponible</p>"

def get_msi20_chart_html():
    """Génère le graphique MSI20 en HTML"""
    try:
        from pages.bdc_statut import generate_msi20_chart
        bourse_data = st.session_state.get('bourse_data', {})
        fig = generate_msi20_chart(bourse_data)
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
    except:
        return "<p>Graphique MSI20 non disponible</p>"

def get_monias_chart_html():
    """Génère le graphique MONIA en HTML"""
    try:
        from pages.bam import generate_monia_chart
        excel_data = st.session_state.get('excel_data', {})
        fig = generate_monia_chart(excel_data)
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
    except:
        return "<p>Graphique MONIA non disponible</p>"

def get_bdt_chart_html():
    """Génère la courbe BDT en HTML"""
    try:
        from pages.bam import generate_bdt_curve_chart
        excel_data = st.session_state.get('excel_data', {})
        fig = generate_bdt_curve_chart(excel_data)
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
    except:
        return "<p>Graphique BDT non disponible</p>"

def get_eur_mad_chart_html():
    """Génère le graphique EUR/MAD en HTML"""
    try:
        from pages.bam import generate_fx_chart
        excel_data = st.session_state.get('excel_data', {})
        fig, _, _ = generate_fx_chart(excel_data, 'EUR/MAD')
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
    except:
        return "<p>Graphique EUR/MAD non disponible</p>"

def get_usd_mad_chart_html():
    """Génère le graphique USD/MAD en HTML"""
    try:
        from pages.bam import generate_fx_chart
        excel_data = st.session_state.get('excel_data', {})
        fig, _, _ = generate_fx_chart(excel_data, 'USD/MAD')
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
    except:
        return "<p>Graphique USD/MAD non disponible</p>"

def get_inflation_gauge_html():
    """Génère la jauge d'inflation en HTML"""
    try:
        from pages.macronews import generate_inflation_gauge
        fig = generate_inflation_gauge(-0.8, 2.0, 3.0)
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
    except:
        return "<p>Graphique inflation non disponible</p>"

# -----------------------------------------------------------------------------
# 2. INITIALISATION DE L'ÉTAT DE SESSION
# -----------------------------------------------------------------------------
def init_export_session():
    """Initialise les variables de session pour l'export"""
    if 'export_selected_sections' not in st.session_state:
        st.session_state.export_selected_sections = ['summary', 'bdc', 'bam', 'inflation']
    if 'report_html' not in st.session_state:
        st.session_state.report_html = None

init_export_session()

# -----------------------------------------------------------------------------
# 3. GÉNÉRATEUR DE RAPPORT HTML
# -----------------------------------------------------------------------------
def generate_report_html():
    """Génère le rapport HTML complet"""
    
    bourse_data = st.session_state.get('bourse_data', {})
    excel_data = st.session_state.get('excel_data', {})
    news_data = st.session_state.get('news_data', [])
    selected_sections = st.session_state.get('export_selected_sections', [])
    
    masi_value = bourse_data.get('masi', {}).get('value', 12450.50)
    masi_change = bourse_data.get('masi', {}).get('change', 0.85)
    msi20_value = bourse_data.get('msi20', {}).get('value', 1580.30)
    msi20_change = bourse_data.get('msi20', {}).get('change', 1.20)
    
    html = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Newz Report - {datetime.now().strftime('%d/%m/%Y')}</title>
        <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; background: #f5f5f5; padding: 20px; }}
            .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 40px; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #005696 0%, #003d6b 100%); color: white; padding: 40px; text-align: center; border-radius: 15px; margin-bottom: 40px; }}
            .header h1 {{ font-size: 42px; margin-bottom: 10px; }}
            .header p {{ font-size: 18px; opacity: 0.9; }}
            .report-info {{ background: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 30px; display: flex; justify-content: space-between; align-items: center; }}
            .section {{ margin-bottom: 40px; padding: 30px; background: white; border-radius: 10px; border-left: 5px solid #005696; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }}
            .section h2 {{ color: #005696; font-size: 28px; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 3px solid #005696; }}
            .section h3 {{ color: #003d6b; font-size: 22px; margin: 20px 0 15px 0; }}
            .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0; }}
            .kpi-card {{ background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); padding: 25px; border-radius: 10px; text-align: center; border-left: 5px solid #005696; }}
            .kpi-card h4 {{ color: #666; font-size: 14px; margin-bottom: 10px; text-transform: uppercase; }}
            .kpi-card .value {{ font-size: 32px; font-weight: bold; color: #005696; }}
            .kpi-card .change {{ font-size: 16px; margin-top: 5px; }}
            .positive {{ color: #28a745; }}
            .negative {{ color: #dc3545; }}
            .chart-container {{ margin: 30px 0; padding: 20px; background: white; border-radius: 10px; border: 1px solid #e0e0e0; }}
            .news-item {{ background: #f8f9fa; padding: 20px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #005696; }}
            .news-item h4 {{ color: #005696; margin-bottom: 10px; }}
            .news-item p {{ color: #666; font-size: 14px; }}
            .footer {{ margin-top: 50px; padding: 30px; background: linear-gradient(135deg, #005696 0%, #003d6b 100%); color: white; text-align: center; border-radius: 15px; }}
            .footer p {{ margin: 10px 0; opacity: 0.9; }}
            .stamp {{ display: inline-block; border: 4px solid #dc3545; color: #dc3545; padding: 15px 40px; font-weight: bold; font-size: 24px; transform: rotate(-3deg); margin-top: 20px; opacity: 0.8; }}
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
            <div class="report-info">
                <div>
                    <p><b>Généré le :</b> {datetime.now().strftime('%d/%m/%Y à %H:%M')}</p>
                    <p><b>Période :</b> Semaine {datetime.now().strftime('%V, %Y')}</p>
                </div>
                <div>
                    <p><b>Version :</b> Newz v2.0.0</p>
                    <p><b>Confidentialité :</b> Usage interne uniquement</p>
                </div>
            </div>
    """
    
    # SECTION 1 : SYNTHÈSE
    if 'summary' in selected_sections:
        html += f"""
            <div class="section">
                <h2>📊 Synthèse Executive</h2>
                <div class="kpi-grid">
                    <div class="kpi-card"><h4>MASI</h4><div class="value">{masi_value:,.0f}</div><div class="change {'positive' if masi_change >= 0 else 'negative'}">{masi_change:+.2f}%</div></div>
                    <div class="kpi-card"><h4>MSI20</h4><div class="value">{msi20_value:,.0f}</div><div class="change {'positive' if msi20_change >= 0 else 'negative'}">{msi20_change:+.2f}%</div></div>
                    <div class="kpi-card"><h4>EUR/MAD</h4><div class="value">10.75</div><div class="change">+0.10%</div></div>
                    <div class="kpi-card"><h4>Inflation</h4><div class="value">-0.80%</div><div class="change negative">Hors cible</div></div>
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
                <h3>Top Movers</h3>
                <table>
                    <tr><th>Valeur</th><th>Cours</th><th>Variation</th><th>Volume</th></tr>
                    <tr><td>Attijariwafa Bank</td><td>485.50 MAD</td><td class="positive">+3.5%</td><td>125,000</td></tr>
                    <tr><td>Maroc Telecom</td><td>142.30 MAD</td><td class="positive">+2.8%</td><td>98,000</td></tr>
                    <tr><td>BCP</td><td>112.40 MAD</td><td class="negative">-1.5%</td><td>156,000</td></tr>
                </table>
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
                <p><b>Analyse :</b> L'inflation est actuellement en-dessous de la cible de Bank Al-Maghrib (2-3%). 
                Cela indique une faible demande intérieure et un espace pour une politique monétaire accommodante.</p>
            </div>
        """
    
    # SECTION 5 : NEWS
    if 'news' in selected_sections and news_
        html += """
            <div class="section">
                <h2>📰 Actualités Marquantes</h2>
        """
        for news in news_data[:5]:
            html += f"""
                <div class="news-item">
                    <h4>{news['title']}</h4>
                    <p><b>Source :</b> {news['source']} | <b>Catégorie :</b> {news['category']}</p>
                    <p>{news['summary']}</p>
                </div>
            """
        html += """
            </div>
        """
    
    # Footer
    html += f"""
            <div class="footer">
                <p><b>CDG Capital — Market Data Team</b></p>
                <p>Newz v2.0.0 | Usage interne uniquement | Document confidentiel</p>
                <p>Sources : Bourse de Casablanca | Bank Al-Maghrib | HCP | Ilboursa</p>
                <div class="stamp">ADMIN<br/>CONFIDENTIEL</div>
            </div>
        </div>
        <div class="no-print" style="background: #fff3cd; padding: 20px; margin: 20px auto; max-width: 1200px; border-radius: 10px; text-align: center;">
            <p style="margin: 0; font-size: 16px;"><strong>💡 Pour sauvegarder en PDF :</strong> Appuyez sur <kbd>Ctrl+P</kbd> (ou Cmd+P) puis sélectionnez "Enregistrer au format PDF"</p>
        </div>
    </body>
    </html>
    """
    
    return html

# -----------------------------------------------------------------------------
# 4. PAGE PRINCIPALE
# -----------------------------------------------------------------------------
def render():
    """Fonction principale de la page Export"""
    
    st.markdown(f"""
    <div style="background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 25px;">
        <h2 style="color: {COLORS['primary']}; margin: 0;">📤 Export de Rapport</h2>
        <p style="margin: 10px 0 0 0; color: #666;">Génération de rapports professionnels HTML/PDF</p>
    </div>
    """, unsafe_allow_html=True)
    
    # SECTION 1 : SÉLECTION DU CONTENU
    st.markdown("### Étape 1 : Sélection du Contenu")
    st.info("📋 Cochez les sections à inclure dans le rapport")
    
    sections = {
        'summary': {'label': '📊 Synthèse Executive', 'desc': 'KPIs principaux'},
        'bdc': {'label': '📈 BDC Statut', 'desc': 'Bourse de Casablanca + Graphiques'},
        'bam': {'label': '🏦 Bank Al-Maghrib', 'desc': 'Courbe BDT + MONIA'},
        'inflation': {'label': '💹 Inflation', 'desc': 'Jauge + Analyse'},
        'news': {'label': '📰 Actualités', 'desc': 'Top 5 news de la semaine'}
    }
    
    for key, section in sections.items():
        is_selected = st.checkbox(
            f"**{section['label']}**",
            value=key in st.session_state.export_selected_sections,
            help=section['desc']
        )
        if is_selected and key not in st.session_state.export_selected_sections:
            st.session_state.export_selected_sections.append(key)
        elif not is_selected and key in st.session_state.export_selected_sections:
            st.session_state.export_selected_sections.remove(key)
    
    st.markdown("---")
    
    # SECTION 2 : GÉNÉRATION DU RAPPORT
    st.markdown("### Étape 2 : Génération")
    
    if st.button("🚀 Générer le Rapport", type="primary", use_container_width=True):
        with st.spinner("Génération du rapport en cours..."):
            try:
                html_content = generate_report_html()
                st.session_state.report_html = html_content
                st.success("✅ Rapport généré avec succès !")
            except Exception as e:
                st.error(f"❌ Erreur de génération : {str(e)}")
                st.exception(e)
    
    # SECTION 3 : TÉLÉCHARGEMENT
    if st.session_state.get('report_html'):
        st.markdown("---")
        st.markdown("### Étape 3 : Téléchargement")
        
        html_content = st.session_state.report_html
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.download_button(
                label="📥 Télécharger le Rapport (HTML)",
                data=html_content,
                file_name=f"newz_report_{datetime.now().strftime('%Y%m%d')}.html",
                mime="text/html",
                use_container_width=True,
                type="primary"
            )
        
        with col2:
            if st.button("👁️ Aperçu du Rapport", use_container_width=True):
                st.components.v1.html(html_content, height=800, scrolling=True)
        
        st.info("""
        **💡 Comment convertir en PDF :**
        1. Téléchargez le fichier HTML
        2. Ouvrez-le dans votre navigateur
        3. Appuyez sur **Ctrl+P** (ou Cmd+P sur Mac)
        4. Sélectionnez **"Enregistrer au format PDF"**
        5. Cliquez sur **Enregistrer**
        """)
    
    # SECTION 4 : INFORMATIONS
    st.markdown("---")
    st.markdown("### ℹ️ Informations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **📊 Sections disponibles :**
        - Synthèse Executive : KPIs clés
        - BDC Statut : Indices boursiers
        - BAM : Taux et courbes
        - Inflation : Analyse macro
        - Actualités : News marquantes
        """)
    
    with col2:
        st.markdown("""
        **📄 Format du rapport :**
        - Format : HTML interactif
        - Conversion : PDF via navigateur
        - Graphiques : Plotly interactifs
        - Charte : CDG Capital
        """)
    
    st.markdown("---")
    st.caption(f"📤 Export | Newz v2.0.0 | Généré le {datetime.now().strftime('%d/%m/%Y %H:%M')}")
