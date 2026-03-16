# NEWZ - Export de Rapport Professionnel
import streamlit as st
import pandas as pd
from datetime import datetime
import base64

if 'export_selected_sections' not in st.session_state:
    st.session_state.export_selected_sections = ['summary', 'bdc', 'bam', 'inflation']
if 'report_html' not in st.session_state:
    st.session_state.report_html = None

def get_chart_html(chart_func, chart_name):
    """Récupère le HTML d'un graphique Plotly"""
    try:
        fig = chart_func()
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
    except:
        return f"<div style='padding:20px; background:#f0f0f0; text-align:center;'>{chart_name} non disponible</div>"

def generate_report_html():
    """Génère le rapport HTML complet avec graphiques"""
    
    bourse_data = st.session_state.get('bourse_data', {})
    excel_data = st.session_state.get('excel_data', {})
    news_data = st.session_state.get('news_data', [])
    selected = st.session_state.get('export_selected_sections', [])
    
    # Données
    masi_val = bourse_data.get('masi', {}).get('value', 12450)
    masi_chg = bourse_data.get('masi', {}).get('change', 0.85)
    msi20_val = bourse_data.get('msi20', {}).get('value', 1580)
    msi20_chg = bourse_data.get('msi20', {}).get('change', 1.20)
    
    # USD/MAD depuis Excel
    usd_mad = 9.85
    if 'USD_MAD' in excel_data and not excel_data['USD_MAD'].empty:
        if 'Mid' in excel_data['USD_MAD'].columns:
            usd_mad = excel_data['USD_MAD']['Mid'].iloc[-1]
    
    # EUR/MAD
    eur_mad = 10.75
    if 'EUR_MAD' in excel_data and not excel_data['EUR_MAD'].empty:
        if 'Mid' in excel_data['EUR_MAD'].columns:
            eur_mad = excel_data['EUR_MAD']['Mid'].iloc[-1]
    
    # Inflation
    inflation = -0.8
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Newz Report - {datetime.now().strftime('%d/%m/%Y')}</title>
        <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ 
                font-family: 'Segoe UI', Arial, sans-serif; 
                background: #f5f5f5; 
                padding: 20px;
                line-height: 1.6;
            }}
            .container {{ 
                max-width: 1200px; 
                margin: 0 auto; 
                background: white; 
                padding: 50px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            }}
            .header {{ 
                background: linear-gradient(135deg, #005696 0%, #003d6b 100%);
                color: white; 
                padding: 40px; 
                text-align: center;
                border-radius: 10px;
                margin-bottom: 40px;
            }}
            .header h1 {{ font-size: 48px; margin-bottom: 10px; }}
            .header h2 {{ font-size: 24px; font-weight: 300; opacity: 0.9; }}
            .header p {{ margin-top: 10px; font-size: 14px; opacity: 0.8; }}
            
            .section {{ 
                margin-bottom: 50px; 
                padding: 30px;
                background: white;
                border-radius: 10px;
                border-left: 6px solid #005696;
                box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            }}
            .section h2 {{ 
                color: #005696; 
                font-size: 28px; 
                margin-bottom: 25px;
                padding-bottom: 15px;
                border-bottom: 3px solid #005696;
            }}
            .section h3 {{ 
                color: #003d6b; 
                font-size: 20px; 
                margin: 25px 0 15px 0;
            }}
            
            .kpi-grid {{ 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); 
                gap: 20px; 
                margin: 20px 0;
            }}
            .kpi-card {{ 
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                padding: 25px; 
                border-radius: 10px; 
                text-align: center;
                border-left: 5px solid #005696;
                transition: transform 0.3s;
            }}
            .kpi-card:hover {{ transform: translateY(-5px); }}
            .kpi-card h4 {{ 
                color: #666; 
                font-size: 13px; 
                margin-bottom: 15px;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            .kpi-card .value {{ 
                font-size: 36px; 
                font-weight: bold; 
                color: #005696;
                margin: 10px 0;
            }}
            .kpi-card .change {{ 
                font-size: 16px;
                padding: 5px 15px;
                border-radius: 20px;
                display: inline-block;
                margin-top: 10px;
            }}
            .positive {{ color: #28a745; background: #d4edda; }}
            .negative {{ color: #dc3545; background: #f8d7da; }}
            
            .chart-box {{ 
                margin: 30px 0; 
                padding: 20px;
                background: white;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
            }}
            
            table {{ 
                width: 100%; 
                border-collapse: collapse; 
                margin: 20px 0;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            th, td {{ 
                padding: 15px; 
                text-align: left; 
                border-bottom: 1px solid #ddd;
            }}
            th {{ 
                background: #005696; 
                color: white; 
                font-weight: bold;
                text-transform: uppercase;
                font-size: 12px;
            }}
            tr:nth-child(even) {{ background: #f8f9fa; }}
            tr:hover {{ background: #e3f2fd; }}
            
            .news-item {{
                background: #f8f9fa;
                padding: 20px;
                margin: 15px 0;
                border-radius: 8px;
                border-left: 5px solid #005696;
            }}
            .news-item h4 {{ color: #005696; margin-bottom: 10px; }}
            .news-item p {{ color: #666; font-size: 14px; }}
            
            .footer {{ 
                margin-top: 60px;
                padding: 40px;
                background: linear-gradient(135deg, #005696 0%, #003d6b 100%);
                color: white;
                text-align: center;
                border-radius: 10px;
            }}
            .footer p {{ margin: 10px 0; opacity: 0.9; }}
            .stamp {{ 
                display: inline-block;
                border: 4px solid #dc3545;
                color: #dc3545;
                padding: 20px 50px;
                font-weight: bold;
                font-size: 28px;
                transform: rotate(-5deg);
                margin-top: 30px;
                opacity: 0.9;
                background: white;
            }}
            
            @media print {{
                body {{ background: white; padding: 0; }}
                .container {{ box-shadow: none; padding: 30px; }}
                .no-print {{ display: none; }}
                .section {{ break-inside: avoid; }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏦 CDG CAPITAL</h1>
                <h2>Newz — Market Data Platform</h2>
                <p>Rapport Hebdomadaire | {datetime.now().strftime('%d/%m/%Y à %H:%M')}</p>
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
    
    # SECTION 2 : BDC STATUT
    if 'bdc' in selected:
        try:
            from pages.bdc_statut import generate_masi_chart, generate_msi20_chart
            
            masi_fig = generate_masi_chart(bourse_data)
            msi20_fig = generate_msi20_chart(bourse_data)
            
            html += f"""
                <div class="section">
                    <h2>📈 BDC Statut - Bourse de Casablanca</h2>
                    <h3>Évolution du MASI</h3>
                    <div class="chart-box">{masi_fig.to_html(full_html=False, include_plotlyjs='cdn')}</div>
                    <h3>Évolution du MSI20</h3>
                    <div class="chart-box">{msi20_fig.to_html(full_html=False, include_plotlyjs='cdn')}</div>
                    <h3>Top Movers</h3>
                    <table>
                        <tr><th>Valeur</th><th>Cours</th><th>Variation</th><th>Volume</th></tr>
                        <tr><td>Attijariwafa Bank</td><td>485.50 MAD</td><td style='color:#28a745'>+3.5%</td><td>125,000</td></tr>
                        <tr><td>Maroc Telecom</td><td>142.30 MAD</td><td style='color:#28a745'>+2.8%</td><td>98,000</td></tr>
                        <tr><td>BCP</td><td>112.40 MAD</td><td style='color:#dc3545'>-1.5%</td><td>156,000</td></tr>
                    </table>
                </div>
            """
        except Exception as e:
            html += f"<div class='section'><h2>📈 BDC Statut</h2><p>Graphiques: {str(e)}</p></div>"
    
    # SECTION 3 : BAM
    if 'bam' in selected:
        try:
            from pages.bam import generate_bdt_curve_chart, generate_monia_chart, generate_fx_chart
            
            bdt_fig = generate_bdt_curve_chart(excel_data)
            monia_fig = generate_monia_chart(excel_data)
            eur_fig, _, _ = generate_fx_chart(excel_data, 'EUR/MAD')
            usd_fig, _, _ = generate_fx_chart(excel_data, 'USD/MAD')
            
            html += f"""
                <div class="section">
                    <h2>🏦 Bank Al-Maghrib</h2>
                    <h3>Courbe des Taux BDT</h3>
                    <div class="chart-box">{bdt_fig.to_html(full_html=False, include_plotlyjs='cdn')}</div>
                    <h3>Indice MONIA</h3>
                    <div class="chart-box">{monia_fig.to_html(full_html=False, include_plotlyjs='cdn')}</div>
                    <h3>EUR/MAD</h3>
                    <div class="chart-box">{eur_fig.to_html(full_html=False, include_plotlyjs='cdn')}</div>
                    <h3>USD/MAD</h3>
                    <div class="chart-box">{usd_fig.to_html(full_html=False, include_plotlyjs='cdn')}</div>
                </div>
            """
        except Exception as e:
            html += f"<div class='section'><h2>🏦 BAM</h2><p>Graphiques: {str(e)}</p></div>"
    
    # SECTION 4 : INFLATION
    if 'inflation' in selected:
        try:
            from pages.macronews import generate_inflation_gauge
            inflation_fig = generate_inflation_gauge(inflation, 2.0, 3.0)
            
            html += f"""
                <div class="section">
                    <h2>💹 Inflation & Macroéconomie</h2>
                    <div class="chart-box">{inflation_fig.to_html(full_html=False, include_plotlyjs='cdn')}</div>
                    <p><b>Analyse :</b> L'inflation est actuellement à {inflation:.2f}%, en-dessous de la cible de Bank Al-Maghrib (2-3%). 
                    Cela indique une faible demande intérieure et un espace pour une politique monétaire accommodante.</p>
                </div>
            """
        except Exception as e:
            html += f"<div class='section'><h2>💹 Inflation</h2><p>Graphique: {str(e)}</p></div>"
    
    # SECTION 5 : NEWS
    if 'news' in selected and news_data:
        html += """
            <div class="section">
                <h2>📰 Actualités Marquantes</h2>
        """
        for news in news_data[:5]:
            html += f"""
                <div class="news-item">
                    <h4>{news['title']}</h4>
                    <p><b>Source:</b> {news['source']} | <b>Catégorie:</b> {news['category']}</p>
                    <p>{news['summary']}</p>
                </div>
            """
        html += "</div>"
    
    # Footer
    html += f"""
            <div class="footer">
                <p><b>CDG Capital — Market Data Team</b></p>
                <p>Newz v2.0.0 | Usage interne uniquement | Document confidentiel</p>
                <p>Sources : Bourse de Casablanca | Bank Al-Maghrib | HCP | Ilboursa</p>
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

def render():
    """Fonction principale"""
    
    if 'export_selected_sections' not in st.session_state:
        st.session_state.export_selected_sections = ['summary', 'bdc', 'bam', 'inflation']
    if 'report_html' not in st.session_state:
        st.session_state.report_html = None
    
    st.markdown("## 📤 Export de Rapport Professionnel")
    
    st.markdown("### Étape 1 : Sélection des Sections")
    
    sections = {
        'summary': '📊 Synthèse Executive',
        'bdc': '📈 BDC Statut (Graphiques MASI + MSI20)',
        'bam': '🏦 BAM (BDT + MONIA + Devises)',
        'inflation': '💹 Inflation (Jauge)',
        'news': '📰 Actualités'
    }
    
    for key, label in sections.items():
        if key not in st.session_state.export_selected_sections:
            st.session_state.export_selected_sections.append(key)
        st.checkbox(label, value=True, key=f"chk_{key}")
    
    st.markdown("---")
    st.markdown("### Étape 2 : Génération du Rapport")
    
    if st.button("🚀 Générer le Rapport Complet", type="primary", use_container_width=True):
        with st.spinner("Génération du rapport avec tous les graphiques..."):
            try:
                html_content = generate_report_html()
                st.session_state.report_html = html_content
                st.success("✅ Rapport généré avec succès !")
                st.balloons()
            except Exception as e:
                st.error(f"❌ Erreur: {str(e)}")
                st.exception(e)
    
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
                st.components.v1.html(st.session_state.report_html, height=900, scrolling=True)
        
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

if __name__ == "__main__":
    render()
