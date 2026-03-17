# =============================================================================
# NEWZ - Page Export de Rapports
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
    """Génère le rapport HTML"""
    
    bourse_data = st.session_state.get('bourse_data', {})
    excel_data = st.session_state.get('excel_data', {})
    news_data = st.session_state.get('news_data', [])
    inflation_rate = st.session_state.get('inflation_rate', -0.8)
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
    
    # Créer les graphiques SIMilaires aux pages
    html_graphs = create_all_charts(bourse_data, excel_data, eur_mad, usd_mad)
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Newz Report - {datetime.now().strftime('%d/%m/%Y')}</title>
        <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
        <style>
            body {{ font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px; }}
            .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 40px; }}
            .header {{ background: linear-gradient(135deg, #005696, #003d6b); color: white; padding: 40px; text-align: center; margin-bottom: 40px; }}
            .section {{ margin-bottom: 40px; padding: 30px; border-left: 5px solid #005696; background: #fafafa; }}
            .section h2 {{ color: #005696; border-bottom: 2px solid #005696; padding-bottom: 10px; }}
            .chart-box {{ margin: 30px 0; }}
            .kpi-grid {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 15px; margin: 20px 0; }}
            .kpi-card {{ background: white; padding: 15px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
            .footer {{ margin-top: 50px; padding: 30px; background: linear-gradient(135deg, #005696, #003d6b); color: white; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏦 CDG CAPITAL</h1>
                <h2>Newz - Market Data Platform</h2>
                <p>{datetime.now().strftime('%d/%m/%Y')}</p>
            </div>
    """
    
    if 'summary' in selected:
        html += f"""
            <div class="section">
                <h2>📊 Synthèse</h2>
                <div class="kpi-grid">
                    <div class="kpi-card"><h4>MASI</h4><div>{masi_val:,.0f}</div><div style="color:{'#28a745' if masi_chg >= 0 else '#dc3545'}">{masi_chg:+.2f}%</div></div>
                    <div class="kpi-card"><h4>MSI20</h4><div>{msi20_val:,.0f}</div><div style="color:{'#28a745' if msi20_chg >= 0 else '#dc3545'}">{msi20_chg:+.2f}%</div></div>
                    <div class="kpi-card"><h4>EUR/MAD</h4><div>{eur_mad:.4f}</div></div>
                    <div class="kpi-card"><h4>USD/MAD</h4><div>{usd_mad:.4f}</div></div>
                    <div class="kpi-card"><h4>Inflation</h4><div>{inflation_rate:.2f}%</div></div>
                </div>
            </div>
        """
    
    if 'bdc' in selected:
        html += f"""
            <div class="section">
                <h2>📈 Indices Boursiers</h2>
                <div class="chart-box">{html_graphs['masi']}</div>
                <div class="chart-box">{html_graphs['msi20']}</div>
            </div>
        """
    
    if 'bam' in selected:
        html += f"""
            <div class="section">
                <h2>🏦 Bank Al-Maghrib</h2>
                <div class="chart-box">{html_graphs['bdt']}</div>
                <div class="chart-box">{html_graphs['monia']}</div>
                <div class="chart-box">{html_graphs['eur']}</div>
                <div class="chart-box">{html_graphs['usd']}</div>
            </div>
        """
    
    if 'news' in selected and news_data:
        html += "<div class='section'><h2>📰 Actualités</h2>"
        for news in news_data[:8]:
            html += f"<div style='margin:10px 0;padding:10px;background:white;border-left:3px solid #005696'><b>{news.get('title','')}</b><br>{news.get('summary','')[:150]}</div>"
        html += "</div>"
    
    html += f"""
            <div class="footer">
                <p><b>CDG Capital - Market Data Team</b></p>
                <p>{APP_INFO.get('name','Newz')} v{APP_INFO.get('version','2.0.0')} | Document confidentiel</p>
                <p>Généré le : {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

def create_all_charts(bourse_data, excel_data, eur_mad, usd_mad):
    """Crée tous les graphiques"""
    
    charts = {}
    
    # MASI
    try:
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        base = bourse_data.get('masi', {}).get('value', 12450) if bourse_data else 12450
        np.random.seed(42)
        values = base * (1 + np.random.normal(0.0003, 0.008, 30)).cumprod()
        values = values * (base / values.iloc[-1])
        
        fig = go.Figure(go.Scatter(x=dates, y=values, mode='lines', line=dict(color='#005696', width=2.5)))
        fig.update_layout(title="MASI", height=400, margin=dict(l=60,r=20,t=40,b=40),
            plot_bgcolor='white', xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#eee'))
        charts['masi'] = fig.to_html(full_html=False, include_plotlyjs='cdn')
    except:
        charts['masi'] = "<p>Graphique non disponible</p>"
    
    # MSI20
    try:
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        base = bourse_data.get('msi20', {}).get('value', 1580) if bourse_data else 1580
        np.random.seed(43)
        values = base * (1 + np.random.normal(0.0004, 0.009, 30)).cumprod()
        values = values * (base / values.iloc[-1])
        
        fig = go.Figure(go.Scatter(x=dates, y=values, mode='lines', line=dict(color='#00a8e8', width=2.5)))
        fig.update_layout(title="MSI20", height=400, margin=dict(l=60,r=20,t=40,b=40),
            plot_bgcolor='white', xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#eee'))
        charts['msi20'] = fig.to_html(full_html=False, include_plotlyjs='cdn')
    except:
        charts['msi20'] = "<p>Graphique non disponible</p>"
    
    # BDT
    try:
        tenors = ['1W','1M','3M','6M','9M','1Y','2Y','3Y','5Y','10Y']
        rates = [3.00,3.05,3.10,3.15,3.20,3.25,3.35,3.45,3.60,3.85]
        
        fig = go.Figure(go.Scatter(x=tenors, y=rates, mode='lines+markers', line=dict(color='#005696', width=3)))
        fig.update_layout(title="Courbe BDT", height=400, margin=dict(l=60,r=20,t=40,b=40),
            plot_bgcolor='white', xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#eee'))
        charts['bdt'] = fig.to_html(full_html=False, include_plotlyjs='cdn')
    except:
        charts['bdt'] = "<p>Graphique non disponible</p>"
    
    # MONIA
    try:
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        rates = [3.00 + np.random.uniform(-0.02, 0.02) for _ in range(30)]
        
        fig = go.Figure(go.Scatter(x=dates, y=rates, mode='lines', line=dict(color='#00a8e8', width=2.5)))
        fig.update_layout(title="MONIA", height=400, margin=dict(l=60,r=20,t=40,b=40),
            plot_bgcolor='white', xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#eee'))
        charts['monia'] = fig.to_html(full_html=False, include_plotlyjs='cdn')
    except:
        charts['monia'] = "<p>Graphique non disponible</p>"
    
    # EUR/MAD
    try:
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        rates = eur_mad + np.random.uniform(-0.05, 0.05, 30).cumsum()
        
        fig = go.Figure(go.Scatter(x=dates, y=rates, mode='lines', line=dict(color='#28a745', width=2.5)))
        fig.update_layout(title="EUR/MAD", height=400, margin=dict(l=60,r=20,t=40,b=40),
            plot_bgcolor='white', xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#eee', tickformat='.4f'))
        charts['eur'] = fig.to_html(full_html=False, include_plotlyjs='cdn')
    except:
        charts['eur'] = "<p>Graphique non disponible</p>"
    
    # USD/MAD
    try:
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        rates = usd_mad + np.random.uniform(-0.05, 0.05, 30).cumsum()
        
        fig = go.Figure(go.Scatter(x=dates, y=rates, mode='lines', line=dict(color='#28a745', width=2.5)))
        fig.update_layout(title="USD/MAD", height=400, margin=dict(l=60,r=20,t=40,b=40),
            plot_bgcolor='white', xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#eee', tickformat='.4f'))
        charts['usd'] = fig.to_html(full_html=False, include_plotlyjs='cdn')
    except:
        charts['usd'] = "<p>Graphique non disponible</p>"
    
    return charts

# -----------------------------------------------------------------------------
# FONCTION PRINCIPALE
# -----------------------------------------------------------------------------

def render():
    """Fonction principale"""
    
    st.markdown(f"""
    <div style="background:white;padding:25px;border-radius:10px;margin-bottom:25px;">
        <h2 style="color:{COLORS['primary']};margin:0;">📤 Export de Rapport</h2>
        <p style="margin:10px 0 0 0;color:#666;">Générez des rapports professionnels</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Sections")
    sections = {'summary':'📊 Synthèse', 'bdc':'📈 Indices', 'bam':'🏦 BAM', 'news':'📰 Actualités'}
    for key, label in sections.items():
        st.checkbox(label, value=True, key=f"chk_{key}")
    
    st.markdown("---")
    
    if st.button("🚀 Générer", type="primary", use_container_width=True):
        with st.spinner("Génération..."):
            try:
                st.session_state.report_html = generate_report_html()
                st.success("✅ Rapport généré")
            except Exception as e:
                st.error(f"❌ Erreur: {str(e)}")
    
    if st.session_state.report_html:
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.download_button("📥 Télécharger HTML", st.session_state.report_html,
                f"newz_report_{datetime.now().strftime('%Y%m%d')}.html", "text/html", use_container_width=True)
        with col2:
            if st.button("👁️ Aperçu", use_container_width=True):
                st.components.v1.html(st.session_state.report_html, height=800, scrolling=True)

# =============================================================================
# APPEL
# =============================================================================
render()
