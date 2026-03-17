# =============================================================================
# NEWZ - Page Export de Rapports
# Fichier : pages/export.py
# =============================================================================

import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
import sys
import json

sys.path.append(str(Path(__file__).resolve().parent.parent))

try:
    from config.settings import COLORS, APP_INFO
except ImportError:
    COLORS = {
        'primary': '#005696',
        'secondary': '#003d6b',
        'accent': '#00a8e8',
        'success': '#28a745',
        'danger': '#dc3545',
        'light': '#f8f9fa'
    }
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
# GÉNÉRATEUR DE RAPPORT HTML
# -----------------------------------------------------------------------------

def generate_report_html():
    """Génère le rapport HTML complet avec graphiques"""
    
    bourse_data = st.session_state.get('bourse_data', {})
    excel_data = st.session_state.get('excel_data', {})
    news_data = st.session_state.get('news_data', [])
    selected = st.session_state.get('export_selected_sections', [])
    
    # Données MASI/MSI20
    masi_val = bourse_data.get('masi', {}).get('value', 12450)
    masi_chg = bourse_data.get('masi', {}).get('change', 0.85)
    msi20_val = bourse_data.get('msi20', {}).get('value', 1580)
    msi20_chg = bourse_data.get('msi20', {}).get('change', 1.20)
    
    # USD/MAD depuis Excel
    usd_mad = 9.85
    if 'USD_MAD' in excel_data and not excel_data['USD_MAD'].empty:
        if 'Mid' in excel_data['USD_MAD'].columns:
            usd_mad = float(excel_data['USD_MAD']['Mid'].iloc[-1])
    
    # EUR/MAD depuis Excel
    eur_mad = 10.75
    if 'EUR_MAD' in excel_data and not excel_data['EUR_MAD'].empty:
        if 'Mid' in excel_data['EUR_MAD'].columns:
            eur_mad = float(excel_data['EUR_MAD']['Mid'].iloc[-1])
    
    # Inflation
    inflation = -0.8
    
    # Générer les graphiques Plotly
    try:
        from pages.bdc_statut import generate_masi_chart_real, generate_msi20_chart_real
        from pages.bam import generate_bdt_curve_chart, generate_monia_chart, generate_fx_chart
        
        # MASI
        fig_masi = generate_masi_chart_real(bourse_data, days=30)
        masi_html = fig_masi.to_html(full_html=False, include_plotlyjs='cdn')
        
        # MSI20
        fig_msi20 = generate_msi20_chart_real(bourse_data, days=30)
        msi20_html = fig_msi20.to_html(full_html=False, include_plotlyjs='cdn')
        
        # BDT
        fig_bdt = generate_bdt_curve_chart(excel_data)
        bdt_html = fig_bdt.to_html(full_html=False, include_plotlyjs='cdn')
        
        # MONIA
        fig_mon = generate_monia_chart(excel_data)
        mon_html = fig_mon.to_html(full_html=False, include_plotlyjs='cdn')
        
        # EUR/MAD
        fig_eur, _, _ = generate_fx_chart(excel_data, 'EUR/MAD')
        eur_html = fig_eur.to_html(full_html=False, include_plotlyjs='cdn')
        
        # USD/MAD
        fig_usd, _, _ = generate_fx_chart(excel_data, 'USD/MAD')
        usd_html = fig_usd.to_html(full_html=False, include_plotlyjs='cdn')
        
    except Exception as e:
        st.warning(f"⚠️ Graphiques non disponibles : {str(e)}")
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
            body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; background: #f5f5f5; padding: 20px; }}
            .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 40px; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #005696 0%, #003d6b 100%); color: white; padding: 40px; text-align: center; border-radius: 15px; margin-bottom: 40px; }}
            .header h1 {{ font-size: 42px; margin-bottom: 10px; }}
            .header h2 {{ font-size: 24px; font-weight: 300; opacity: 0.9; }}
            .header p {{ margin-top: 10px; font-size: 14px; opacity: 0.8; }}
            .section {{ margin-bottom: 40px; padding: 30px; background: white; border-radius: 10px; border-left: 5px solid #005696; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }}
            .section h2 {{ color: #005696; font-size: 28px; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 3px solid #005696; }}
            .section h3 {{ color: #003d6b; font-size: 20px; margin: 20px 0 15px 0; }}
            .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
            .kpi-card {{ background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); padding: 25px; border-radius: 10px; text-align: center; border-left: 5px solid #005696; }}
            .kpi-card h4 {{ color: #666; font-size: 13px; margin-bottom: 10px; text-transform: uppercase; }}
            .kpi-card .value {{ font-size: 32px; font-weight: bold; color: #005696; margin: 10px 0; }}
            .kpi-card .change {{ font-size: 14px; padding: 5px 15px; border-radius: 20px; display: inline-block; }}
            .positive {{ color: #28a745; background: #d4edda; }}
            .negative {{ color: #dc3545; background: #f8d7da; }}
            .chart-container {{ margin: 30px 0; padding: 20px; background: white; border: 2px solid #e0e0e0; border-radius: 10px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background: #005696; color: white; font-weight: bold; }}
            tr:nth-child(even) {{ background: #f8f9fa; }}
            .news-item {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #005696; }}
            .news-item h4 {{ color: #005696; margin-bottom: 8px; }}
            .news-item p {{ color: #666; font-size: 14px; }}
            .footer {{ margin-top: 50px; padding: 30px; background: linear-gradient(135deg, #005696 0%, #003d6b 100%); color: white; text-align: center; border-radius: 15px; }}
            .stamp {{ display: inline-block; border: 4px solid #dc3545; color: #dc3545; padding: 15px 40px; font-weight: bold; font-size: 24px; transform: rotate(-3deg); margin-top: 20px; background: white; }}
            @media print {{ body {{ background: white; padding: 0; }} .container {{ box-shadow: none; padding: 20px; }} .no-print {{ display: none; }} .chart-container {{ page-break-inside: avoid; }} }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏦 CDG CAPITAL</h1>
                <h2>Newz — Market Data Platform</h2>
                <p>Rapport Hebdomadaire | {datetime.now().strftime('%d/%m/%Y')}</p>
                <p>Semaine {datetime.now().strftime('%V, %Y')}</p>
            </div>
    """
    
    # SECTION 1 : SYNTHÈSE
    if 'summary' in selected:
        html += f"""
            <div class="section">
                <h2>📊 Synthèse Executive</h2>
                <div class="kpi-grid">
                    <div class="kpi-card">
                        <h4>MASI</h4>
                        <div class="value">{masi_val:,.0f}</div>
                        <div class="{'positive' if masi_chg >= 0 else 'negative'}">{masi_chg:+.2f}%</div>
                    </div>
                    <div class="kpi-card">
                        <h4>MSI20</h4>
                        <div class="value">{msi20_val:,.0f}</div>
                        <div class="{'positive' if msi20_chg >= 0 else 'negative'}">{msi20_chg:+.2f}%</div>
                    </div>
                    <div class="kpi-card">
                        <h4>EUR/MAD</h4>
                        <div class="value">{eur_mad:.4f}</div>
                        <div class="positive">+0.10%</div>
                    </div>
                    <div class="kpi-card">
                        <h4>USD/MAD</h4>
                        <div class="value">{usd_mad:.4f}</div>
                        <div class="negative">-0.15%</div>
                    </div>
                    <div class="kpi-card">
                        <h4>Inflation</h4>
                        <div class="value">{inflation:.2f}%</div>
                        <div class="negative">Hors cible</div>
                    </div>
                </div>
            </div>
        """
    
    # SECTION 2 : INDICES BOURSIERS (GRAPHIQUES)
    if 'bdc' in selected:
        html += f"""
            <div class="section">
                <h2>📈 Indices Boursiers</h2>
                <h3>Évolution du MASI (30 jours)</h3>
                <div class="chart-container">{masi_html}</div>
                <h3>Évolution du MSI20 (30 jours)</h3>
                <div class="chart-container">{msi20_html}</div>
            </div>
        """
    
    # SECTION 3 : BANK AL-MAGHRIB (GRAPHIQUES)
    if 'bam' in selected:
        html += f"""
            <div class="section">
                <h2>🏦 Bank Al-Maghrib</h2>
                <h3>Courbe des Taux BDT</h3>
                <div class="chart-container">{bdt_html}</div>
                <h3>Indice MONIA</h3>
                <div class="chart-container">{mon_html}</div>
                <h3>Taux de Change</h3>
                <h4>EUR/MAD</h4>
                <div class="chart-container">{eur_html}</div>
                <h4>USD/MAD</h4>
                <div class="chart-container">{usd_html}</div>
            </div>
        """
    
    # SECTION 4 : INFLATION
    if 'inflation' in selected:
        html += f"""
            <div class="section">
                <h2>💹 Inflation & Macroéconomie</h2>
                <h3>Taux d'Inflation Actuel</h3>
                <p>L'inflation est actuellement à <b>{inflation:.2f}%</b>, en-dessous de la cible de Bank Al-Maghrib (2-3%).</p>
                <h3>Analyse</h3>
                <p>Cette situation indique :</p>
                <ul>
                    <li>Une faible demande intérieure</li>
                    <li>Une baisse des prix des produits alimentaires</li>
                    <li>Un espace pour une politique monétaire accommodante</li>
                </ul>
            </div>
        """
    
    # SECTION 5 : NEWS
    if 'news' in selected and news_data:
        html += """
            <div class="section">
                <h2>📰 Actualités Marquantes</h2>
        """
        for news in news_data[:10]:
            title = news.get('title', 'N/A')
            summary = news.get('summary', '')[:300]
            source = news.get('source', 'N/A')
            category = news.get('category', 'Général')
            
            html += f"""
                <div class="news-item">
                    <h4>{title}</h4>
                    <p><b>Source:</b> {source} | <b>Catégorie:</b> {category}</p>
                    <p>{summary}</p>
                </div>
            """
        html += "</div>"
    
    # Footer
    html += f"""
            <div class="footer">
                <p><b>CDG Capital — Market Data Team</b></p>
                <p>{APP_INFO.get('name', 'Newz')} v{APP_INFO.get('version', '2.0.0')} | Usage interne uniquement | Document confidentiel</p>
                <p>Sources : Bourse de Casablanca | Bank Al-Maghrib | HCP | Ilboursa</p>
                <p>Généré le : {datetime.now().strftime('%d/%m/%Y à %H:%M')}</p>
                <div class="stamp">ADMIN<br/>CONFIDENTIEL</div>
            </div>
        </div>
        
        <div class="no-print" style="background:#fff3cd; padding:20px; margin:20px auto; max-width:1200px; border-radius:10px; text-align:center;">
            <p style="margin:0; font-size:16px;"><strong>💡 Pour sauvegarder en PDF :</strong> Ctrl+P → Destination: "Enregistrer au format PDF" → Marges: "Aucune"</p>
        </div>
    </body>
    </html>
    """
    
    return html

# -----------------------------------------------------------------------------
# FONCTION PRINCIPALE
# -----------------------------------------------------------------------------

def render():
    """Fonction principale"""
    
    # HEADER
    st.markdown(f"""
    <div style="background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 25px;">
        <h2 style="color: {COLORS['primary']}; margin: 0;">📤 Export de Rapport</h2>
        <p style="margin: 10px 0 0 0; color: #666;">Générez des rapports professionnels HTML/PDF</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ---------------------------------------------------------------------
    # ÉTAPE 1 : SÉLECTION
    # ---------------------------------------------------------------------
    st.markdown("### Étape 1 : Sélection du Contenu")
    
    sections = {
        'summary': '📊 Synthèse Executive (KPIs)',
        'bdc': '📈 BDC Statut (Bourse)',
        'bam': '🏦 Bank Al-Maghrib (Taux & Devises)',
        'inflation': '💹 Inflation & Macro',
        'news': '📰 Actualités'
    }
    
    for key, label in sections.items():
        if key not in st.session_state.export_selected_sections:
            st.session_state.export_selected_sections.append(key)
        st.checkbox(label, value=True, key=f"chk_{key}")
    
    st.markdown("---")
    
    # ---------------------------------------------------------------------
    # ÉTAPE 2 : GÉNÉRATION
    # ---------------------------------------------------------------------
    st.markdown("### Étape 2 : Génération")
    
    if st.button("🚀 Générer le Rapport", type="primary", use_container_width=True):
        with st.spinner("Génération du rapport en cours..."):
            try:
                html_content = generate_report_html()
                st.session_state.report_html = html_content
                st.success("✅ Rapport généré avec succès !")
                st.balloons()
            except Exception as e:
                st.error(f"❌ Erreur : {str(e)}")
                st.exception(e)
    
    # ---------------------------------------------------------------------
    # ÉTAPE 3 : TÉLÉCHARGEMENT
    # ---------------------------------------------------------------------
    if st.session_state.report_html:
        st.markdown("---")
        st.markdown("### Étape 3 : Téléchargement")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.download_button(
                label="📥 Télécharger le Rapport (HTML)",
                data=st.session_state.report_html,
                file_name=f"newz_report_{datetime.now().strftime('%Y%m%d_%H%M')}.html",
                mime="text/html",
                use_container_width=True,
                type="primary"
            )
        
        with col2:
            if st.button("👁️ Aperçu du Rapport", use_container_width=True):
                st.components.v1.html(st.session_state.report_html, height=800, scrolling=True)
        
        st.info("""
        **💡 Instructions pour convertir en PDF :**
        
        1. **Téléchargez** le fichier HTML ci-dessus
        2. **Ouvrez-le** dans Google Chrome (recommandé) ou Firefox
        3. **Appuyez sur Ctrl+P** (ou Cmd+P sur Mac)
        4. **Destination :** Choisissez "Enregistrer au format PDF"
        5. **Marges :** Sélectionnez "Aucune" pour un rendu optimal
        6. **Options :** Cochez "Graphiques d'arrière-plan"
        7. **Cliquez sur Enregistrer**
        
        **Alternative :** Utilisez l'aperçu ci-dessus et faites Ctrl+P directement
        """)
    
    # ---------------------------------------------------------------------
    # RÉSUMÉ
    # ---------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### 📊 Résumé des Données Disponibles")
    
    bourse_data = st.session_state.get('bourse_data', {})
    excel_data = st.session_state.get('excel_data', {})
    news_data = st.session_state.get('news_data', [])
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status = "✅" if bourse_data.get('status') == 'success' else "⚪"
        st.metric("Bourse", status)
    
    with col2:
        sheets = len([s for s in excel_data.values() if not s.empty]) if excel_data else 0
        st.metric("Feuilles Excel", f"{sheets}/6")
    
    with col3:
        st.metric("News", f"{len(news_data)}")
    
    with col4:
        st.metric("Rapport", "✅ Généré" if st.session_state.report_html else "⚪ Non généré")
    
    if st.session_state.get('last_update'):
        st.caption(f"Dernière MAJ : {st.session_state.last_update.strftime('%d/%m/%Y %H:%M:%S')}")

# =============================================================================
# APPEL
# =============================================================================
render()
