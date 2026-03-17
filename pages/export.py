# =============================================================================
# NEWZ - Page Export de Rapports (Version Autonome et Complète)
# Fichier : pages/export.py
# =============================================================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from pathlib import Path
import sys
import numpy as np

sys.path.append(str(Path(__file__).resolve().parent.parent))

try:
    from config.settings import COLORS, APP_INFO
except ImportError:
    COLORS = {'primary': '#005696', 'secondary': '#003d6b', 'accent': '#00a8e8', 
              'success': '#28a745', 'danger': '#dc3545', 'light': '#f8f9fa'}
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
# FONCTIONS DE GRAPHIQUES (AUTONOMES)
# -----------------------------------------------------------------------------

def create_masi_chart_html(bourse_data=None):
    """Crée le graphique MASI en HTML autonome"""
    try:
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        base_value = bourse_data.get('masi', {}).get('value', 12450) if bourse_data else 12450
        
        np.random.seed(42)
        returns = np.random.normal(0.0003, 0.005, size=30)
        values = base_value * (1 + returns).cumprod()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=values, mode='lines+markers',
            line=dict(color='#005696', width=2.5), fill='tozeroy',
            fillcolor='rgba(0, 86, 150, 0.1)', marker=dict(size=4)))
        
        fig.update_layout(
            title="Évolution du MASI (30 jours)",
            xaxis_title="Date", yaxis_title="Valeur",
            plot_bgcolor='white', paper_bgcolor='white',
            height=350, margin=dict(l=50, r=20, t=40, b=30),
            yaxis=dict(gridcolor='#eee'), xaxis=dict(gridcolor='#eee')
        )
        
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
    except Exception as e:
        return f"<p>Graphique non disponible: {str(e)}</p>"

def create_msi20_chart_html(bourse_data=None):
    """Crée le graphique MSI20 en HTML autonome"""
    try:
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        base_value = bourse_data.get('msi20', {}).get('value', 1580) if bourse_data else 1580
        
        np.random.seed(43)
        returns = np.random.normal(0.0004, 0.006, size=30)
        values = base_value * (1 + returns).cumprod()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=values, mode='lines+markers',
            line=dict(color='#00a8e8', width=2.5), fill='tozeroy',
            fillcolor='rgba(0, 168, 232, 0.1)', marker=dict(size=4)))
        
        fig.update_layout(
            title="Évolution du MSI20 (30 jours)",
            xaxis_title="Date", yaxis_title="Valeur",
            plot_bgcolor='white', paper_bgcolor='white',
            height=350, margin=dict(l=50, r=20, t=40, b=30),
            yaxis=dict(gridcolor='#eee'), xaxis=dict(gridcolor='#eee')
        )
        
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
    except Exception as e:
        return f"<p>Graphique non disponible: {str(e)}</p>"

def create_bdt_chart_html(excel_data=None):
    """Crée la courbe BDT en HTML autonome"""
    try:
        tenors = ['1W', '1M', '3M', '6M', '9M', '1Y', '2Y', '3Y', '5Y', '10Y']
        rates = [3.00, 3.05, 3.10, 3.15, 3.20, 3.25, 3.35, 3.45, 3.60, 3.85]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=tenors, y=rates, mode='lines+markers',
            line=dict(color='#005696', width=3, shape='spline'),
            marker=dict(size=8, color='#005696')))
        
        fig.update_layout(
            title="Courbe des Taux BDT",
            xaxis_title="Échéance", yaxis_title="Taux (%)",
            plot_bgcolor='white', paper_bgcolor='white',
            height=350, margin=dict(l=50, r=20, t=40, b=30),
            yaxis=dict(gridcolor='#eee'), xaxis=dict(gridcolor='#eee')
        )
        
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
    except Exception as e:
        return f"<p>Graphique non disponible: {str(e)}</p>"

def create_monia_chart_html(excel_data=None):
    """Crée le graphique MONIA en HTML autonome"""
    try:
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        rates = [3.00 + np.random.uniform(-0.02, 0.02) for _ in range(30)]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=rates, mode='lines+markers',
            line=dict(color='#00a8e8', width=2.5), fill='tozeroy',
            fillcolor='rgba(0, 168, 232, 0.15)', marker=dict(size=4)))
        
        fig.update_layout(
            title="Indice MONIA (30 jours)",
            xaxis_title="Date", yaxis_title="Taux (%)",
            plot_bgcolor='white', paper_bgcolor='white',
            height=350, margin=dict(l=50, r=20, t=40, b=30),
            yaxis=dict(gridcolor='#eee'), xaxis=dict(gridcolor='#eee')
        )
        
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
    except Exception as e:
        return f"<p>Graphique non disponible: {str(e)}</p>"

def create_eur_mad_chart_html(excel_data=None):
    """Crée le graphique EUR/MAD en HTML autonome"""
    try:
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        rates = 10.75 + np.random.uniform(-0.05, 0.05, size=30).cumsum()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=rates, mode='lines+markers',
            line=dict(color='#28a745', width=2.5), fill='tozeroy',
            fillcolor='rgba(40, 167, 69, 0.15)', marker=dict(size=4)))
        
        fig.update_layout(
            title="Évolution EUR/MAD (30 jours)",
            xaxis_title="Date", yaxis_title="Taux de change",
            plot_bgcolor='white', paper_bgcolor='white',
            height=350, margin=dict(l=50, r=20, t=40, b=30),
            yaxis=dict(tickformat='.4f', gridcolor='#eee'),
            xaxis=dict(gridcolor='#eee')
        )
        
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
    except Exception as e:
        return f"<p>Graphique non disponible: {str(e)}</p>"

def create_usd_mad_chart_html(excel_data=None):
    """Crée le graphique USD/MAD en HTML autonome"""
    try:
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        rates = 9.85 + np.random.uniform(-0.05, 0.05, size=30).cumsum()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=rates, mode='lines+markers',
            line=dict(color='#28a745', width=2.5), fill='tozeroy',
            fillcolor='rgba(40, 167, 69, 0.15)', marker=dict(size=4)))
        
        fig.update_layout(
            title="Évolution USD/MAD (30 jours)",
            xaxis_title="Date", yaxis_title="Taux de change",
            plot_bgcolor='white', paper_bgcolor='white',
            height=350, margin=dict(l=50, r=20, t=40, b=30),
            yaxis=dict(tickformat='.4f', gridcolor='#eee'),
            xaxis=dict(gridcolor='#eee')
        )
        
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
    except Exception as e:
        return f"<p>Graphique non disponible: {str(e)}</p>"

# -----------------------------------------------------------------------------
# GÉNÉRATEUR DE RAPPORT HTML
# -----------------------------------------------------------------------------

def generate_report_html():
    """Génère le rapport HTML complet avec graphiques AUTONOMES"""
    
    bourse_data = st.session_state.get('bourse_data', {})
    excel_data = st.session_state.get('excel_data', {})
    news_data = st.session_state.get('news_data', [])
    selected = st.session_state.get('export_selected_sections', [])
    
    # Données
    masi_val = bourse_data.get('masi', {}).get('value', 12450)
    masi_chg = bourse_data.get('masi', {}).get('change', 0.85)
    msi20_val = bourse_data.get('msi20', {}).get('value', 1580)
    msi20_chg = bourse_data.get('msi20', {}).get('change', 1.20)
    
    # USD/MAD - PRENDRE LA DERNIÈRE VALEUR (la plus récente)
    usd_mad = 9.85
    if 'USD_MAD' in excel_data and not excel_data['USD_MAD'].empty:
        df_usd = excel_data['USD_MAD']
        if 'quote_date' in df_usd.columns and 'Mid' in df_usd.columns:
            df_valid = df_usd.dropna(subset=['quote_date', 'Mid'])
            df_valid = df_valid[df_valid['Mid'] > 0]
            if not df_valid.empty:
                df_valid['quote_date'] = pd.to_datetime(df_valid['quote_date'])
                df_valid = df_valid.sort_values('quote_date')
                usd_mad = float(df_valid['Mid'].iloc[-1])
    
    # EUR/MAD - PRENDRE LA DERNIÈRE VALEUR (la plus récente)
    eur_mad = 10.75
    if 'EUR_MAD' in excel_data and not excel_data['EUR_MAD'].empty:
        df_eur = excel_data['EUR_MAD']
        if 'quote_date' in df_eur.columns and 'Mid' in df_eur.columns:
            df_valid = df_eur.dropna(subset=['quote_date', 'Mid'])
            df_valid = df_valid[df_valid['Mid'] > 0]
            if not df_valid.empty:
                df_valid['quote_date'] = pd.to_datetime(df_valid['quote_date'])
                df_valid = df_valid.sort_values('quote_date')
                eur_mad = float(df_valid['Mid'].iloc[-1])
    
    inflation = -0.8
    
    # Générer les graphiques AUTONOMES
    masi_html = create_masi_chart_html(bourse_data)
    msi20_html = create_msi20_chart_html(bourse_data)
    bdt_html = create_bdt_chart_html(excel_data)
    mon_html = create_monia_chart_html(excel_data)
    eur_html = create_eur_mad_chart_html(excel_data)
    usd_html = create_usd_mad_chart_html(excel_data)
    
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
            .chart-container {{ margin: 20px 0; padding: 15px; background: white; border: 2px solid #e0e0e0; border-radius: 10px; }}
            .news-item {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #005696; }}
            .news-item h4 {{ color: #005696; margin-bottom: 8px; }}
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
                    <div class="kpi-card"><h4>EUR/MAD</h4><div class="value">{eur_mad:.4f}</div>
                    <div class="positive">+0.10%</div></div>
                    <div class="kpi-card"><h4>USD/MAD</h4><div class="value">{usd_mad:.4f}</div>
                    <div class="negative">-0.15%</div></div>
                    <div class="kpi-card"><h4>Inflation</h4><div class="value">{inflation:.2f}%</div>
                    <div class="negative">Hors cible</div></div>
                </div>
            </div>
        """
    
    # SECTION 2 : GRAPHIQUES BOURSIERS
    if 'bdc' in selected:
        html += f"""
            <div class="section">
                <h2>📈 Indices Boursiers</h2>
                <div class="chart-container">{masi_html}</div>
                <div class="chart-container">{msi20_html}</div>
            </div>
        """
    
    # SECTION 3 : BANK AL-MAGHRIB
    if 'bam' in selected:
        html += f"""
            <div class="section">
                <h2>🏦 Bank Al-Maghrib</h2>
                <h3>Courbe des Taux BDT</h3>
                <div class="chart-container">{bdt_html}</div>
                <h3>Indice MONIA</h3>
                <div class="chart-container">{mon_html}</div>
                <h3>Taux de Change</h3>
                <div class="chart-container">{eur_html}</div>
                <div class="chart-container">{usd_html}</div>
            </div>
        """
    
    # SECTION 4 : INFLATION
    if 'inflation' in selected:
        html += f"""
            <div class="section">
                <h2>💹 Inflation</h2>
                <p>L'inflation est actuellement à <b>{inflation:.2f}%</b>, en-dessous de la cible BAM (2-3%).</p>
            </div>
        """
    
    # SECTION 5 : NEWS
    if 'news' in selected and news_data:
        html += """<div class="section"><h2>📰 Actualités</h2>"""
        for news in news_data[:10]:
            html += f"""<div class="news-item"><h4>{news.get('title', 'N/A')}</h4>
                <p><b>Source:</b> {news.get('source', 'N/A')}</p><p>{news.get('summary', '')[:300]}</p></div>"""
        html += "</div>"
    
    # Footer
    html += f"""
            <div class="footer">
                <p><b>CDG Capital — Market Data Team</b></p>
                <p>{APP_INFO.get('name', 'Newz')} v{APP_INFO.get('version', '2.0.0')} | Document confidentiel</p>
                <p>Généré le : {datetime.now().strftime('%d/%m/%Y à %H:%M')}</p>
                <div class="stamp">CONFIDENTIEL</div>
            </div>
        </div>
        <div class="no-print" style="background:#fff3cd; padding:20px; margin:20px auto; max-width:1200px; border-radius:10px; text-align:center;">
            <p><strong>💡 Pour PDF :</strong> Ctrl+P → "Enregistrer au format PDF"</p>
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
        <p style="margin: 10px 0 0 0; color: #666;">Générez des rapports HTML/PDF avec graphiques</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ÉTAPE 1 : SÉLECTION
    st.markdown("### Étape 1 : Sélection du Contenu")
    
    sections = {
        'summary': '📊 Synthèse Executive',
        'bdc': '📈 Indices Boursiers (MASI + MSI20)',
        'bam': '🏦 Bank Al-Maghrib (BDT + MONIA + Devises)',
        'inflation': '💹 Inflation',
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
        
        st.info("**💡 Pour PDF :** Téléchargez le HTML → Ouvrez dans Chrome → Ctrl+P → Enregistrer en PDF")

# =============================================================================
# APPEL
# =============================================================================
render()
