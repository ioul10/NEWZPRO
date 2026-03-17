# =============================================================================
# NEWZ - Page Export de Rapports (Professionnel)
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
# GRAPHIQUES
# -----------------------------------------------------------------------------

def create_masi_chart(bourse_data=None, actions_data=None):
    """Graphique MASI"""
    try:
        if actions_data is not None and not actions_data.empty:
            df = actions_data.copy()
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'])
                df = df.sort_values('Date').tail(30)
                if 'MASI' in df.columns:
                    dates, values = df['Date'], df['MASI']
                else:
                    numeric_cols = df.select_dtypes(include=[np.number]).columns
                    dates = df['Date']
                    values = df[numeric_cols].mean(axis=1) if len(numeric_cols) > 0 else pd.Series([12450]*30)
            else:
                raise ValueError("Pas de colonne Date")
        else:
            dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
            base = bourse_data.get('masi', {}).get('value', 12450) if bourse_data else 12450
            np.random.seed(42)
            values = base * (1 + np.random.normal(0.0003, 0.008, size=30)).cumprod()
            values = values * (base / values.iloc[-1])
        
        fig = go.Figure(go.Scatter(x=dates, y=values, mode='lines',
            line=dict(color='#005696', width=2.5), fill='tozeroy'))
        fig.update_layout(title="MASI", height=250, margin=dict(l=50, r=20, t=35, b=35),
            plot_bgcolor='white', paper_bgcolor='white',
            xaxis=dict(showgrid=False, tickformat='%d/%m'),
            yaxis=dict(showgrid=True, gridcolor='#eee', tickformat=',.0f'))
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
    except:
        return "<p>Graphique non disponible</p>"

def create_msi20_chart(bourse_data=None, actions_data=None):
    """Graphique MSI20"""
    try:
        if actions_data is not None and not actions_data.empty:
            df = actions_data.copy()
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'])
                df = df.sort_values('Date').tail(30)
                if 'MSI20' in df.columns:
                    dates, values = df['Date'], df['MSI20']
                else:
                    numeric_cols = df.select_dtypes(include=[np.number]).columns[:5]
                    dates = df['Date']
                    values = df[numeric_cols].mean(axis=1) * 10 if len(numeric_cols) > 0 else pd.Series([1580]*30)
            else:
                raise ValueError("Pas de colonne Date")
        else:
            dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
            base = bourse_data.get('msi20', {}).get('value', 1580) if bourse_data else 1580
            np.random.seed(43)
            values = base * (1 + np.random.normal(0.0004, 0.009, size=30)).cumprod()
            values = values * (base / values.iloc[-1])
        
        fig = go.Figure(go.Scatter(x=dates, y=values, mode='lines',
            line=dict(color='#00a8e8', width=2.5), fill='tozeroy'))
        fig.update_layout(title="MSI20", height=250, margin=dict(l=50, r=20, t=35, b=35),
            plot_bgcolor='white', paper_bgcolor='white',
            xaxis=dict(showgrid=False, tickformat='%d/%m'),
            yaxis=dict(showgrid=True, gridcolor='#eee', tickformat=',.0f'))
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
    except:
        return "<p>Graphique non disponible</p>"

def create_bdt_chart(excel_data=None):
    """Courbe des taux BDT"""
    try:
        if excel_data and 'MADBDT_52W' in excel_data and not excel_data['MADBDT_52W'].empty:
            df = excel_data['MADBDT_52W']
            if 'tenor_mat' in df.columns and 'zero_rate' in df.columns:
                tenors = df['tenor_mat'].tolist()
                rates = df['zero_rate'].tolist()
            else:
                tenors = ['1W', '1M', '3M', '6M', '9M', '1Y', '2Y', '3Y', '5Y', '10Y']
                rates = [3.00, 3.05, 3.10, 3.15, 3.20, 3.25, 3.35, 3.45, 3.60, 3.85]
        else:
            tenors = ['1W', '1M', '3M', '6M', '9M', '1Y', '2Y', '3Y', '5Y', '10Y']
            rates = [3.00, 3.05, 3.10, 3.15, 3.20, 3.25, 3.35, 3.45, 3.60, 3.85]
        
        fig = go.Figure(go.Scatter(x=tenors, y=rates, mode='lines+markers',
            line=dict(color='#005696', width=3, shape='spline'), marker=dict(size=8)))
        fig.update_layout(title="Courbe des Taux BDT", height=250,
            margin=dict(l=50, r=20, t=35, b=35), plot_bgcolor='white', paper_bgcolor='white',
            xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#eee', tickformat='.2f'))
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
    except:
        return "<p>Graphique non disponible</p>"

def create_monia_chart(excel_data=None):
    """Graphique MONIA"""
    try:
        if excel_data and 'MONIA' in excel_data and not excel_data['MONIA'].empty:
            df = excel_data['MONIA']
            if 'quote_date' in df.columns and 'rate' in df.columns:
                df = df.dropna(subset=['quote_date', 'rate'])
                df['quote_date'] = pd.to_datetime(df['quote_date'])
                df = df.sort_values('quote_date').tail(30)
                dates, rates = df['quote_date'], df['rate']
            else:
                raise ValueError("Colonnes manquantes")
        else:
            dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
            rates = [3.00 + np.random.uniform(-0.02, 0.02) for _ in range(30)]
        
        fig = go.Figure(go.Scatter(x=dates, y=rates, mode='lines',
            line=dict(color='#00a8e8', width=2.5), fill='tozeroy'))
        fig.update_layout(title="Indice MONIA", height=250,
            margin=dict(l=50, r=20, t=35, b=35), plot_bgcolor='white', paper_bgcolor='white',
            xaxis=dict(showgrid=False, tickformat='%d/%m'),
            yaxis=dict(showgrid=True, gridcolor='#eee', tickformat='.3f'))
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
    except:
        return "<p>Graphique non disponible</p>"

def create_fx_chart(pair='EUR/MAD', excel_data=None, current_rate=None):
    """Graphique FX"""
    try:
        sheet_name = 'EUR_MAD' if 'EUR' in pair else 'USD_MAD'
        
        if excel_data and sheet_name in excel_data and not excel_data[sheet_name].empty:
            df = excel_data[sheet_name].copy()
            if 'quote_date' in df.columns and 'Mid' in df.columns:
                df = df.dropna(subset=['quote_date', 'Mid'])
                df = df[df['Mid'] > 0]
                if not df.empty:
                    df['quote_date'] = pd.to_datetime(df['quote_date'])
                    df = df.sort_values('quote_date').tail(30)
                    dates, rates = df['quote_date'], df['Mid']
                    current_rate = rates.iloc[-1]
                else:
                    raise ValueError("Pas de données")
            else:
                raise ValueError("Colonnes manquantes")
        else:
            dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
            base = current_rate if current_rate else (10.75 if 'EUR' in pair else 9.85)
            rates = base + np.random.uniform(-0.05, 0.05, size=30).cumsum()
        
        fig = go.Figure(go.Scatter(x=dates, y=rates, mode='lines',
            line=dict(color='#28a745', width=2.5), fill='tozeroy'))
        fig.update_layout(title=pair, height=250,
            margin=dict(l=50, r=20, t=35, b=35), plot_bgcolor='white', paper_bgcolor='white',
            xaxis=dict(showgrid=False, tickformat='%d/%m'),
            yaxis=dict(showgrid=True, gridcolor='#eee', tickformat='.4f'))
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
    except:
        return "<p>Graphique non disponible</p>"

def create_inflation_gauge(rate=-0.8):
    """Jauge inflation"""
    try:
        target_min, target_max = 2.0, 3.0
        color = '#dc3545' if rate < target_min or rate > target_max else '#28a745'
        
        fig = go.Figure(go.Indicator(mode="gauge+number", value=rate,
            title={'text': "Inflation", 'font': {'size': 14}},
            gauge={'axis': {'range': [-2, 6]}, 'bar': {'color': color},
                'bgcolor': "#f5f5f5", 'steps': [
                    {'range': [-2, target_min], 'color': '#ffebee'},
                    {'range': [target_min, target_max], 'color': '#e8f5e9'},
                    {'range': [target_max, 6], 'color': '#ffebee'}
                ]}))
        fig.update_layout(height=250, margin=dict(l=20, r=20, t=35, b=20), paper_bgcolor='white')
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
    except:
        return "<p>Graphique non disponible</p>"

def create_taux_directeur_chart():
    """Taux directeur"""
    try:
        dates = pd.to_datetime(['2024-10-01', '2024-12-01', '2025-01-01', '2025-02-01', '2025-03-01'])
        rates = [3.00, 3.00, 3.00, 3.00, 3.00]
        
        fig = go.Figure(go.Scatter(x=dates, y=rates, mode='lines+markers',
            line=dict(color='#005696', width=3), marker=dict(size=8)))
        fig.update_layout(title="Taux Directeur BAM", height=250,
            margin=dict(l=50, r=20, t=35, b=35), plot_bgcolor='white', paper_bgcolor='white',
            xaxis=dict(showgrid=False, tickformat='%b %Y'),
            yaxis=dict(showgrid=True, gridcolor='#eee', range=[2.5, 3.5], tickformat='.2f'))
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
    except:
        return "<p>Graphique non disponible</p>"

# -----------------------------------------------------------------------------
# GÉNÉRATEUR DE RAPPORT
# -----------------------------------------------------------------------------

def generate_report_html():
    """Génère le rapport HTML"""
    
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
    
    # Graphiques
    masi_html = create_masi_chart(bourse_data, actions_data)
    msi20_html = create_msi20_chart(bourse_data, actions_data)
    bdt_html = create_bdt_chart(excel_data)
    mon_html = create_monia_chart(excel_data)
    eur_html = create_fx_chart('EUR/MAD', excel_data, eur_mad)
    usd_html = create_fx_chart('USD/MAD', excel_data, usd_mad)
    inflation_html = create_inflation_gauge(inflation_rate)
    taux_html = create_taux_directeur_chart()
    
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
            .section h2 {{ color: #005696; font-size: 24px; margin-bottom: 20px; border-bottom: 2px solid #005696; padding-bottom: 10px; }}
            .charts-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin: 20px 0; }}
            .chart-box {{ background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
            .kpi-grid {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 15px; margin: 20px 0; }}
            .kpi-card {{ background: white; padding: 15px; border-radius: 8px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
            .kpi-card h4 {{ color: #666; font-size: 11px; margin-bottom: 8px; }}
            .kpi-card .value {{ font-size: 24px; font-weight: bold; color: #005696; }}
            .positive {{ color: #28a745; }}
            .negative {{ color: #dc3545; }}
            .news-item {{ background: white; padding: 12px; margin: 8px 0; border-radius: 6px; border-left: 3px solid #005696; font-size: 13px; }}
            .footer {{ margin-top: 50px; padding: 30px; background: linear-gradient(135deg, #005696 0%, #003d6b 100%); color: white; text-align: center; border-radius: 15px; }}
            @media print {{ body {{ background: white; }} .container {{ box-shadow: none; }} .chart-box {{ page-break-inside: avoid; }} }}
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
    
    if 'bdc' in selected:
        html += f"""
            <div class="section">
                <h2>📈 Indices Boursiers</h2>
                <div class="charts-grid">
                    <div class="chart-box">{masi_html}</div>
                    <div class="chart-box">{msi20_html}</div>
                </div>
            </div>
        """
    
    if 'bam' in selected:
        html += f"""
            <div class="section">
                <h2>🏦 Bank Al-Maghrib</h2>
                <div class="charts-grid">
                    <div class="chart-box">{taux_html}</div>
                    <div class="chart-box">{inflation_html}</div>
                    <div class="chart-box">{bdt_html}</div>
                    <div class="chart-box">{mon_html}</div>
                    <div class="chart-box">{eur_html}</div>
                    <div class="chart-box">{usd_html}</div>
                </div>
            </div>
        """
    
    if 'news' in selected and news_data:
        html += """<div class="section"><h2>📰 Actualités</h2>"""
        for news in news_data[:8]:
            html += f"""<div class="news-item"><b>{news.get('title', 'N/A')}</b><br>{news.get('summary', '')[:150]}</div>"""
        html += "</div>"
    
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
        'bam': '🏦 BAM (Taux + BDT + MONIA + FX + Inflation)',
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
