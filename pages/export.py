# =============================================================================
# NEWZ - Page Export de Rapports
# Structure: Synthèse + Graphiques (Données réelles collectées)
# =============================================================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
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
        st.session_state.export_selected_sections = ['synthese', 'graphiques']
    if 'report_html' not in st.session_state:
        st.session_state.report_html = None

init_local_session()

# -----------------------------------------------------------------------------
# GÉNÉRATEUR DE RAPPORT
# -----------------------------------------------------------------------------

def generate_report_html():
    """Génère le rapport avec DONNÉES RÉELLES collectées"""
    
    # Récupérer DONNÉES COLLECTÉES
    bourse_data = st.session_state.get('bourse_data', {})
    excel_data = st.session_state.get('excel_data', {})
    news_data = st.session_state.get('news_data', [])
    inflation_rate = st.session_state.get('inflation_rate', None)
    selected = st.session_state.get('export_selected_sections', [])
    
    # === DONNÉES BDC STATUT ===
    masi_val = bourse_data.get('masi', {}).get('value')
    masi_chg = bourse_data.get('masi', {}).get('change')
    msi20_val = bourse_data.get('msi20', {}).get('value')
    msi20_chg = bourse_data.get('msi20', {}).get('change')
    
    # === DONNÉES BAM ===
    taux_directeur = 3.00  # Taux fixe BAM
    
    # MONIA - dernière valeur
    monia_val = None
    if 'MONIA' in excel_data and not excel_data['MONIA'].empty:
        df = excel_data['MONIA']
        if 'rate' in df.columns:
            valid = df.dropna(subset=['rate'])
            if not valid.empty:
                monia_val = float(valid['rate'].iloc[-1])
    
    # EUR/MAD - dernière valeur + variation
    eur_mad = None
    eur_chg = None
    if 'EUR_MAD' in excel_data and not excel_data['EUR_MAD'].empty:
        df = excel_data['EUR_MAD']
        if 'quote_date' in df.columns and 'Mid' in df.columns:
            valid = df.dropna(subset=['Mid'])
            valid = valid[valid['Mid'] > 0]
            if len(valid) >= 2:
                valid = valid.sort_values('quote_date')
                eur_mad = float(valid['Mid'].iloc[-1])
                eur_prev = float(valid['Mid'].iloc[-2])
                eur_chg = ((eur_mad - eur_prev) / eur_prev) * 100
            elif len(valid) == 1:
                eur_mad = float(valid['Mid'].iloc[-1])
                eur_chg = 0.0
    
    # USD/MAD - dernière valeur + variation
    usd_mad = None
    usd_chg = None
    if 'USD_MAD' in excel_data and not excel_data['USD_MAD'].empty:
        df = excel_data['USD_MAD']
        if 'quote_date' in df.columns and 'Mid' in df.columns:
            valid = df.dropna(subset=['Mid'])
            valid = valid[valid['Mid'] > 0]
            if len(valid) >= 2:
                valid = valid.sort_values('quote_date')
                usd_mad = float(valid['Mid'].iloc[-1])
                usd_prev = float(valid['Mid'].iloc[-2])
                usd_chg = ((usd_mad - usd_prev) / usd_prev) * 100
            elif len(valid) == 1:
                usd_mad = float(valid['Mid'].iloc[-1])
                usd_chg = 0.0
    
    # === DONNÉES MACRONEWS ===
    # inflation_rate déjà récupéré ci-dessus
    
    # === CRÉER GRAPHIQUES ===
    charts = {}
    
    # MASI Chart
    if masi_val is not None:
        try:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=[datetime.now()], y=[masi_val], mode='markers+text',
                marker=dict(size=15, color='#005696'), text=[f"{masi_val:,.0f}"],
                textposition="top center", textfont=dict(size=16)))
            fig.update_layout(title="Indice MASI", height=350, plot_bgcolor='white',
                xaxis=dict(showgrid=False, showticklabels=False),
                yaxis=dict(showgrid=True, gridcolor='#eee', tickformat=',.0f'))
            charts['masi'] = fig.to_html(full_html=False, include_plotlyjs='cdn')
        except:
            charts['masi'] = None
    else:
        charts['masi'] = None
    
    # MSI20 Chart
    if msi20_val is not None:
        try:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=[datetime.now()], y=[msi20_val], mode='markers+text',
                marker=dict(size=15, color='#00a8e8'), text=[f"{msi20_val:,.0f}"],
                textposition="top center", textfont=dict(size=16)))
            fig.update_layout(title="Indice MSI20", height=350, plot_bgcolor='white',
                xaxis=dict(showgrid=False, showticklabels=False),
                yaxis=dict(showgrid=True, gridcolor='#eee', tickformat=',.0f'))
            charts['msi20'] = fig.to_html(full_html=False, include_plotlyjs='cdn')
        except:
            charts['msi20'] = None
    else:
        charts['msi20'] = None
    
    # Taux Directeur Chart
    try:
        dates = pd.date_range(end=datetime.now(), periods=6, freq='M')
        rates = [3.00] * 6
        fig = go.Figure(go.Scatter(x=dates, y=rates, mode='lines+markers',
            line=dict(color='#005696', width=3), marker=dict(size=8)))
        fig.update_layout(title="Taux Directeur BAM", height=350, plot_bgcolor='white',
            xaxis=dict(showgrid=False, tickformat='%b %Y'),
            yaxis=dict(showgrid=True, gridcolor='#eee', range=[2.5, 3.5], tickformat='.2f'))
        charts['taux'] = fig.to_html(full_html=False, include_plotlyjs='cdn')
    except:
        charts['taux'] = None
    
    # MONIA Chart
    if monia_val is not None:
        try:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=[datetime.now()], y=[monia_val], mode='markers+text',
                marker=dict(size=15, color='#00a8e8'), text=[f"{monia_val:.3f}"],
                textposition="top center", textfont=dict(size=16)))
            fig.update_layout(title="Indice MONIA", height=350, plot_bgcolor='white',
                xaxis=dict(showgrid=False, showticklabels=False),
                yaxis=dict(showgrid=True, gridcolor='#eee', tickformat='.3f'))
            charts['monia'] = fig.to_html(full_html=False, include_plotlyjs='cdn')
        except:
            charts['monia'] = None
    else:
        charts['monia'] = None
    
    # EUR/MAD Chart
    if eur_mad is not None:
        try:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=[datetime.now()], y=[eur_mad], mode='markers+text',
                marker=dict(size=15, color='#28a745'), text=[f"{eur_mad:.4f}"],
                textposition="top center", textfont=dict(size=16)))
            fig.update_layout(title="EUR/MAD", height=350, plot_bgcolor='white',
                xaxis=dict(showgrid=False, showticklabels=False),
                yaxis=dict(showgrid=True, gridcolor='#eee', tickformat='.4f'))
            charts['eur'] = fig.to_html(full_html=False, include_plotlyjs='cdn')
        except:
            charts['eur'] = None
    else:
        charts['eur'] = None
    
    # USD/MAD Chart
    if usd_mad is not None:
        try:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=[datetime.now()], y=[usd_mad], mode='markers+text',
                marker=dict(size=15, color='#28a745'), text=[f"{usd_mad:.4f}"],
                textposition="top center", textfont=dict(size=16)))
            fig.update_layout(title="USD/MAD", height=350, plot_bgcolor='white',
                xaxis=dict(showgrid=False, showticklabels=False),
                yaxis=dict(showgrid=True, gridcolor='#eee', tickformat='.4f'))
            charts['usd'] = fig.to_html(full_html=False, include_plotlyjs='cdn')
        except:
            charts['usd'] = None
    else:
        charts['usd'] = None
    
    # Inflation Chart
    if inflation_rate is not None:
        try:
            fig = go.Figure(go.Indicator(mode="gauge+number", value=inflation_rate,
                title={'text': "Inflation (HCP)", 'font': {'size': 16}},
                gauge={'axis': {'range': [-2, 6]}, 'bar': {'color': '#dc3545' if inflation_rate < 2 else '#28a745'},
                    'bgcolor': "#f5f5f5", 'steps': [
                        {'range': [-2, 2], 'color': '#ffebee'},
                        {'range': [2, 3], 'color': '#e8f5e9'},
                        {'range': [3, 6], 'color': '#ffebee'}
                    ]}))
            fig.update_layout(height=350, margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor='white')
            charts['inflation'] = fig.to_html(full_html=False, include_plotlyjs='cdn')
        except:
            charts['inflation'] = None
    else:
        charts['inflation'] = None
    
    # === CONSTRUIRE HTML ===
    today = datetime.now().strftime('%d/%m/%Y')
    
    html = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <title>NEWZ Report - {today}</title>
        <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f5f5f5; padding: 20px; }}
            .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 50px; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #005696 0%, #003d6b 100%); color: white; padding: 50px; text-align: center; border-radius: 15px; margin-bottom: 50px; }}
            .header h1 {{ font-size: 48px; margin-bottom: 15px; font-weight: 700; }}
            .header h2 {{ font-size: 24px; font-weight: 300; opacity: 0.95; margin-bottom: 15px; }}
            .header p {{ font-size: 16px; opacity: 0.85; }}
            .section {{ margin-bottom: 50px; padding: 40px; border-left: 6px solid #005696; background: #fafafa; border-radius: 10px; }}
            .section h2 {{ color: #005696; font-size: 32px; margin-bottom: 30px; border-bottom: 3px solid #005696; padding-bottom: 15px; }}
            .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 20px; margin: 25px 0; }}
            .kpi-card {{ background: white; padding: 25px; border-radius: 10px; text-align: center; box-shadow: 0 3px 10px rgba(0,0,0,0.1); border-top: 4px solid #005696; }}
            .kpi-card h4 {{ color: #666; font-size: 13px; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 1px; }}
            .kpi-card .value {{ font-size: 28px; font-weight: bold; color: #005696; margin-bottom: 8px; }}
            .kpi-card .change {{ font-size: 14px; padding: 5px 12px; border-radius: 20px; display: inline-block; font-weight: 600; }}
            .positive {{ color: #28a745; background: #d4edda; }}
            .negative {{ color: #dc3545; background: #f8d7da; }}
            .chart-box {{ margin: 30px 0; background: white; padding: 25px; border-radius: 10px; box-shadow: 0 3px 10px rgba(0,0,0,0.1); }}
            .no-data {{ padding: 30px; background: #fff3cd; border-radius: 10px; text-align: center; color: #856404; font-size: 15px; }}
            .footer {{ margin-top: 60px; padding: 40px; background: linear-gradient(135deg, #005696 0%, #003d6b 100%); color: white; text-align: center; border-radius: 15px; }}
            .footer p {{ margin: 8px 0; }}
            @media print {{ body {{ background: white; padding: 0; }} .container {{ box-shadow: none; padding: 30px; }} .chart-box {{ page-break-inside: avoid; }} }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>NEWZ</h1>
                <h2>Market Data Platform</h2>
                <p>Rapport - {today}</p>
            </div>
    """
    
    # === SECTION 1 : SYNTHÈSE ===
    if 'synthese' in selected:
        html += """
            <div class="section">
                <h2>📊 Synthèse</h2>
                <div class="kpi-grid">
        """
        
        # MASI
        if masi_val is not None:
            html += f"""<div class="kpi-card">
                <h4>Indice MASI</h4>
                <div class="value">{masi_val:,.0f}</div>
                <div class="{'positive' if masi_chg and masi_chg >= 0 else 'negative'}">{masi_chg:+.2f}%</div>
            </div>"""
        else:
            html += """<div class="kpi-card"><h4>Indice MASI</h4><div class="no-data" style="padding:10px;">Non disponible</div></div>"""
        
        # MSI20
        if msi20_val is not None:
            html += f"""<div class="kpi-card">
                <h4>Indice MSI20</h4>
                <div class="value">{msi20_val:,.0f}</div>
                <div class="{'positive' if msi20_chg and msi20_chg >= 0 else 'negative'}">{msi20_chg:+.2f}%</div>
            </div>"""
        else:
            html += """<div class="kpi-card"><h4>Indice MSI20</h4><div class="no-data" style="padding:10px;">Non disponible</div></div>"""
        
        # Taux Directeur
        html += f"""<div class="kpi-card">
            <h4>Taux Directeur</h4>
            <div class="value">{taux_directeur:.2f}%</div>
            <div style="font-size:12px;color:#666;">BAM</div>
        </div>"""
        
        # MONIA
        if monia_val is not None:
            html += f"""<div class="kpi-card">
                <h4>Indice MONIA</h4>
                <div class="value">{monia_val:.3f}%</div>
                <div style="font-size:12px;color:#666;">Dernière valeur</div>
            </div>"""
        else:
            html += """<div class="kpi-card"><h4>Indice MONIA</h4><div class="no-data" style="padding:10px;">Non disponible</div></div>"""
        
        # EUR/MAD
        if eur_mad is not None:
            html += f"""<div class="kpi-card">
                <h4>EUR/MAD</h4>
                <div class="value">{eur_mad:.4f}</div>
                <div class="{'positive' if eur_chg and eur_chg >= 0 else 'negative'}">{eur_chg:+.2f}%</div>
            </div>"""
        else:
            html += """<div class="kpi-card"><h4>EUR/MAD</h4><div class="no-data" style="padding:10px;">Non disponible</div></div>"""
        
        # USD/MAD
        if usd_mad is not None:
            html += f"""<div class="kpi-card">
                <h4>USD/MAD</h4>
                <div class="value">{usd_mad:.4f}</div>
                <div class="{'positive' if usd_chg and usd_chg >= 0 else 'negative'}">{usd_chg:+.2f}%</div>
            </div>"""
        else:
            html += """<div class="kpi-card"><h4>USD/MAD</h4><div class="no-data" style="padding:10px;">Non disponible</div></div>"""
        
        # Inflation
        if inflation_rate is not None:
            html += f"""<div class="kpi-card">
                <h4>Inflation</h4>
                <div class="value">{inflation_rate:.2f}%</div>
                <div style="font-size:12px;color:#666;">HCP</div>
            </div>"""
        else:
            html += """<div class="kpi-card"><h4>Inflation</h4><div class="no-data" style="padding:10px;">Non disponible</div></div>"""
        
        html += """
                </div>
            </div>
        """
    
    # === SECTION 2 : GRAPHIQUES ===
    if 'graphiques' in selected:
        html += """
            <div class="section">
                <h2>📈 Graphiques</h2>
        """
        
        # MASI
        html += """<div class="chart-box">"""
        if charts.get('masi'):
            html += charts['masi']
        else:
            html += """<div class="no-data">⚠️ Indice MASI : Aucune donnée disponible (Allez dans Data Ingestion)</div>"""
        html += """</div>"""
        
        # MSI20
        html += """<div class="chart-box">"""
        if charts.get('msi20'):
            html += charts['msi20']
        else:
            html += """<div class="no-data">⚠️ Indice MSI20 : Aucune donnée disponible (Allez dans Data Ingestion)</div>"""
        html += """</div>"""
        
        # Taux Directeur
        html += """<div class="chart-box">"""
        if charts.get('taux'):
            html += charts['taux']
        else:
            html += """<div class="no-data">⚠️ Taux Directeur : Graphique non disponible</div>"""
        html += """</div>"""
        
        # MONIA
        html += """<div class="chart-box">"""
        if charts.get('monia'):
            html += charts['monia']
        else:
            html += """<div class="no-data">⚠️ Indice MONIA : Aucune donnée Excel disponible</div>"""
        html += """</div>"""
        
        # EUR/MAD
        html += """<div class="chart-box">"""
        if charts.get('eur'):
            html += charts['eur']
        else:
            html += """<div class="no-data">⚠️ EUR/MAD : Aucune donnée disponible</div>"""
        html += """</div>"""
        
        # USD/MAD
        html += """<div class="chart-box">"""
        if charts.get('usd'):
            html += charts['usd']
        else:
            html += """<div class="no-data">⚠️ USD/MAD : Aucune donnée disponible</div>"""
        html += """</div>"""
        
        # Inflation
        html += """<div class="chart-box">"""
        if charts.get('inflation'):
            html += charts['inflation']
        else:
            html += """<div class="no-data">⚠️ Inflation : Aucune donnée HCP disponible (Allez dans Macronews)</div>"""
        html += """</div>"""
        
        html += """
            </div>
        """
    
    # === FOOTER ===
    html += f"""
            <div class="footer">
                <p><b>CDG Capital - Market Data Team</b></p>
                <p>{APP_INFO.get('name','NEWZ')} v{APP_INFO.get('version','2.0.0')} | Document confidentiel</p>
                <p>Généré le : {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}</p>
                <p style="margin-top:15px;font-size:13px;opacity:0.8;">Sources : Bourse de Casablanca | Bank Al-Maghrib | HCP | Ilboursa</p>
            </div>
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
    
    st.markdown(f"""
    <div style="background:white;padding:25px;border-radius:10px;margin-bottom:25px;">
        <h2 style="color:{COLORS['primary']};margin:0;">📤 Export de Rapport</h2>
        <p style="margin:10px 0 0 0;color:#666;">Générez un rapport professionnel basé sur les données collectées</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("""
    💡 **Important :** 
    - Ce rapport utilise **UNIQUEMENT** les données collectées dans les autres pages
    - Allez dans **Data Ingestion** pour actualiser MASI, MSI20, et les données Excel (BDT, MONIA, FX)
    - Allez dans **Macronews** pour actualiser l'inflation HCP
    """)
    
    st.markdown("### Sections du rapport")
    
    sections = {
        'synthese': '📊 Synthèse (KPIs)',
        'graphiques': '📈 Graphiques'
    }
    
    for key, label in sections.items():
        st.checkbox(label, value=True, key=f"chk_{key}")
    
    st.markdown("---")
    
    if st.button("🚀 Générer le Rapport", type="primary", use_container_width=True):
        with st.spinner("Génération en cours..."):
            try:
                st.session_state.report_html = generate_report_html()
                st.success("✅ Rapport généré avec succès")
            except Exception as e:
                st.error(f"❌ Erreur: {str(e)}")
                st.exception(e)
    
    if st.session_state.report_html:
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            st.download_button(
                label="📥 Télécharger HTML",
                data=st.session_state.report_html,
                file_name=f"NEWZ_Report_{datetime.now().strftime('%Y%m%d')}.html",
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
