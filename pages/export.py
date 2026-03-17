# =============================================================================
# NEWZ - Page Export de Rapports
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
    APP_INFO = {'name': 'Newz', 'version': '2.0.0'}

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
    """Génère le rapport HTML"""
    
    # Récupérer DONNÉES
    bourse_data = st.session_state.get('bourse_data', {})
    excel_data = st.session_state.get('excel_data', {})
    news_data = st.session_state.get('news_data', [])
    inflation_rate = st.session_state.get('inflation_rate')
    selected = st.session_state.get('export_selected_sections', ['synthese', 'graphiques'])
    
    # === DONNÉES BDC STATUT ===
    masi_val = bourse_data.get('masi', {}).get('value')
    masi_chg = bourse_data.get('masi', {}).get('change')
    msi20_val = bourse_data.get('msi20', {}).get('value')
    msi20_chg = bourse_data.get('msi20', {}).get('change')
    
    # === DONNÉES BAM ===
    taux_directeur = 3.00
    
    # MONIA
    monia_val = None
    if 'MONIA' in excel_data and not excel_data['MONIA'].empty:
        df = excel_data['MONIA']
        if 'rate' in df.columns:
            valid = df.dropna(subset=['rate'])
            if not valid.empty:
                monia_val = float(valid['rate'].iloc[-1])
    
    # EUR/MAD
    eur_mad = None
    eur_chg = None
    if 'EUR_MAD' in excel_data and not excel_data['EUR_MAD'].empty:
        df = excel_data['EUR_MAD']
        if 'Mid' in df.columns:
            valid = df.dropna(subset=['Mid'])
            valid = valid[valid['Mid'] > 0]
            if len(valid) >= 2:
                valid = valid.sort_values(df.columns[0] if len(df.columns) > 0 else 0)
                eur_mad = float(valid['Mid'].iloc[-1])
                eur_prev = float(valid['Mid'].iloc[-2])
                eur_chg = ((eur_mad - eur_prev) / eur_prev) * 100
            elif len(valid) == 1:
                eur_mad = float(valid['Mid'].iloc[-1])
                eur_chg = 0.0
    
    # USD/MAD
    usd_mad = None
    usd_chg = None
    if 'USD_MAD' in excel_data and not excel_data['USD_MAD'].empty:
        df = excel_data['USD_MAD']
        if 'Mid' in df.columns:
            valid = df.dropna(subset=['Mid'])
            valid = valid[valid['Mid'] > 0]
            if len(valid) >= 2:
                valid = valid.sort_values(df.columns[0] if len(df.columns) > 0 else 0)
                usd_mad = float(valid['Mid'].iloc[-1])
                usd_prev = float(valid['Mid'].iloc[-2])
                usd_chg = ((usd_mad - usd_prev) / usd_prev) * 100
            elif len(valid) == 1:
                usd_mad = float(valid['Mid'].iloc[-1])
                usd_chg = 0.0
    
    # === CRÉER GRAPHIQUES ===
    charts = {}
    
    # MASI
    if masi_val is not None:
        try:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=[datetime.now()], y=[masi_val], mode='markers+text',
                marker=dict(size=15, color='#005696'), text=[f"{masi_val:,.0f}"]))
            fig.update_layout(title="Indice MASI", height=350, plot_bgcolor='white',
                xaxis=dict(showgrid=False, showticklabels=False),
                yaxis=dict(showgrid=True, gridcolor='#eee'))
            charts['masi'] = fig.to_html(full_html=False, include_plotlyjs='cdn')
        except:
            charts['masi'] = None
    
    # MSI20
    if msi20_val is not None:
        try:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=[datetime.now()], y=[msi20_val], mode='markers+text',
                marker=dict(size=15, color='#00a8e8'), text=[f"{msi20_val:,.0f}"]))
            fig.update_layout(title="Indice MSI20", height=350, plot_bgcolor='white',
                xaxis=dict(showgrid=False, showticklabels=False),
                yaxis=dict(showgrid=True, gridcolor='#eee'))
            charts['msi20'] = fig.to_html(full_html=False, include_plotlyjs='cdn')
        except:
            charts['msi20'] = None
    
    # Taux
    try:
        dates = pd.date_range(end=datetime.now(), periods=6, freq='M')
        rates = [3.00] * 6
        fig = go.Figure(go.Scatter(x=dates, y=rates, mode='lines+markers'))
        fig.update_layout(title="Taux Directeur BAM", height=350, plot_bgcolor='white')
        charts['taux'] = fig.to_html(full_html=False, include_plotlyjs='cdn')
    except:
        charts['taux'] = None
    
    # MONIA
    if monia_val is not None:
        try:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=[datetime.now()], y=[monia_val], mode='markers+text',
                marker=dict(size=15, color='#00a8e8'), text=[f"{monia_val:.3f}"]))
            fig.update_layout(title="Indice MONIA", height=350, plot_bgcolor='white',
                xaxis=dict(showgrid=False, showticklabels=False),
                yaxis=dict(showgrid=True, gridcolor='#eee'))
            charts['monia'] = fig.to_html(full_html=False, include_plotlyjs='cdn')
        except:
            charts['monia'] = None
    
    # EUR/MAD
    if eur_mad is not None:
        try:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=[datetime.now()], y=[eur_mad], mode='markers+text',
                marker=dict(size=15, color='#28a745'), text=[f"{eur_mad:.4f}"]))
            fig.update_layout(title="EUR/MAD", height=350, plot_bgcolor='white',
                xaxis=dict(showgrid=False, showticklabels=False),
                yaxis=dict(showgrid=True, gridcolor='#eee'))
            charts['eur'] = fig.to_html(full_html=False, include_plotlyjs='cdn')
        except:
            charts['eur'] = None
    
    # USD/MAD
    if usd_mad is not None:
        try:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=[datetime.now()], y=[usd_mad], mode='markers+text',
                marker=dict(size=15, color='#28a745'), text=[f"{usd_mad:.4f}"]))
            fig.update_layout(title="USD/MAD", height=350, plot_bgcolor='white',
                xaxis=dict(showgrid=False, showticklabels=False),
                yaxis=dict(showgrid=True, gridcolor='#eee'))
            charts['usd'] = fig.to_html(full_html=False, include_plotlyjs='cdn')
        except:
            charts['usd'] = None
    
    # Inflation
    if inflation_rate is not None:
        try:
            fig = go.Figure(go.Indicator(mode="gauge+number", value=inflation_rate,
                title={'text': "Inflation"},
                gauge={'axis': {'range': [-2, 6]}, 'bar': {'color': '#dc3545' if inflation_rate < 2 else '#28a745'}}))
            fig.update_layout(height=350, paper_bgcolor='white')
            charts['inflation'] = fig.to_html(full_html=False, include_plotlyjs='cdn')
        except:
            charts['inflation'] = None
    
    # === CONSTRUIRE HTML ===
    today = datetime.now().strftime('%d/%m/%Y')
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>NEWZ Report - {today}</title>
        <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
        <style>
            body {{ font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px; }}
            .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 50px; }}
            .header {{ background: linear-gradient(135deg, #005696, #003d6b); color: white; padding: 50px; text-align: center; margin-bottom: 50px; }}
            .header h1 {{ font-size: 48px; margin-bottom: 15px; }}
            .header h2 {{ font-size: 24px; margin-bottom: 15px; }}
            .section {{ margin-bottom: 50px; padding: 40px; border-left: 6px solid #005696; background: #fafafa; }}
            .section h2 {{ color: #005696; font-size: 32px; margin-bottom: 30px; }}
            .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 20px; margin: 25px 0; }}
            .kpi-card {{ background: white; padding: 25px; text-align: center; box-shadow: 0 3px 10px rgba(0,0,0,0.1); }}
            .kpi-card h4 {{ color: #666; font-size: 13px; margin-bottom: 12px; }}
            .kpi-card .value {{ font-size: 28px; font-weight: bold; color: #005696; margin-bottom: 8px; }}
            .chart-box {{ margin: 30px 0; background: white; padding: 25px; }}
            .no-data {{ padding: 30px; background: #fff3cd; text-align: center; }}
            .footer {{ margin-top: 60px; padding: 40px; background: linear-gradient(135deg, #005696, #003d6b); color: white; text-align: center; }}
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
    
    # SYNTHÈSE
    if 'synthese' in selected:
        html += '<div class="section"><h2>📊 Synthèse</h2><div class="kpi-grid">'
        
        if masi_val is not None:
            html += f'<div class="kpi-card"><h4>Indice MASI</h4><div class="value">{masi_val:,.0f}</div><div style="color:{"#28a745" if masi_chg and masi_chg >= 0 else "#dc3545"}">{masi_chg:+.2f}%</div></div>'
        else:
            html += '<div class="kpi-card"><h4>Indice MASI</h4><div class="no-data">Non disponible</div></div>'
        
        if msi20_val is not None:
            html += f'<div class="kpi-card"><h4>Indice MSI20</h4><div class="value">{msi20_val:,.0f}</div><div style="color:{"#28a745" if msi20_chg and msi20_chg >= 0 else "#dc3545"}">{msi20_chg:+.2f}%</div></div>'
        else:
            html += '<div class="kpi-card"><h4>Indice MSI20</h4><div class="no-data">Non disponible</div></div>'
        
        html += f'<div class="kpi-card"><h4>Taux Directeur</h4><div class="value">{taux_directeur:.2f}%</div></div>'
        
        if monia_val is not None:
            html += f'<div class="kpi-card"><h4>Indice MONIA</h4><div class="value">{monia_val:.3f}%</div></div>'
        else:
            html += '<div class="kpi-card"><h4>Indice MONIA</h4><div class="no-data">Non disponible</div></div>'
        
        if eur_mad is not None:
            html += f'<div class="kpi-card"><h4>EUR/MAD</h4><div class="value">{eur_mad:.4f}</div><div style="color:{"#28a745" if eur_chg and eur_chg >= 0 else "#dc3545"}">{eur_chg:+.2f}%</div></div>'
        else:
            html += '<div class="kpi-card"><h4>EUR/MAD</h4><div class="no-data">Non disponible</div></div>'
        
        if usd_mad is not None:
            html += f'<div class="kpi-card"><h4>USD/MAD</h4><div class="value">{usd_mad:.4f}</div><div style="color:{"#28a745" if usd_chg and usd_chg >= 0 else "#dc3545"}">{usd_chg:+.2f}%</div></div>'
        else:
            html += '<div class="kpi-card"><h4>USD/MAD</h4><div class="no-data">Non disponible</div></div>'
        
        if inflation_rate is not None:
            html += f'<div class="kpi-card"><h4>Inflation</h4><div class="value">{inflation_rate:.2f}%</div></div>'
        else:
            html += '<div class="kpi-card"><h4>Inflation</h4><div class="no-data">Non disponible</div></div>'
        
        html += '</div></div>'
    
    # GRAPHIQUES
    if 'graphiques' in selected:
        html += '<div class="section"><h2>📈 Graphiques</h2>'
        
        html += '<div class="chart-box">'
        html += charts.get('masi', '<div class="no-data">MASI non disponible</div>')
        html += '</div>'
        
        html += '<div class="chart-box">'
        html += charts.get('msi20', '<div class="no-data">MSI20 non disponible</div>')
        html += '</div>'
        
        html += '<div class="chart-box">'
        html += charts.get('taux', '<div class="no-data">Taux non disponible</div>')
        html += '</div>'
        
        html += '<div class="chart-box">'
        html += charts.get('monia', '<div class="no-data">MONIA non disponible</div>')
        html += '</div>'
        
        html += '<div class="chart-box">'
        html += charts.get('eur', '<div class="no-data">EUR/MAD non disponible</div>')
        html += '</div>'
        
        html += '<div class="chart-box">'
        html += charts.get('usd', '<div class="no-data">USD/MAD non disponible</div>')
        html += '</div>'
        
        html += '<div class="chart-box">'
        html += charts.get('inflation', '<div class="no-data">Inflation non disponible</div>')
        html += '</div>'
        
        html += '</div>'
    
    html += f"""
            <div class="footer">
                <p><b>CDG Capital - Market Data Team</b></p>
                <p>{APP_INFO.get('name','NEWZ')} v{APP_INFO.get('version','2.0.0')} | Document confidentiel</p>
                <p>Généré le : {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}</p>
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
    
    st.markdown("### 📤 Export de Rapport")
    
    # DEBUG
    st.markdown("### 🔍 État des données")
    
    bourse_data = st.session_state.get('bourse_data', {})
    excel_data = st.session_state.get('excel_data', {})
    inflation_rate = st.session_state.get('inflation_rate')
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        has_masi = bourse_data.get('masi', {}).get('value') is not None
        st.metric("MASI", "✅" if has_masi else "❌")
        if has_masi:
            st.write(f"Valeur: {bourse_data['masi']['value']:,.0f}")
    
    with col2:
        has_msi20 = bourse_data.get('msi20', {}).get('value') is not None
        st.metric("MSI20", "✅" if has_msi20 else "❌")
        if has_msi20:
            st.write(f"Valeur: {bourse_data['msi20']['value']:,.0f}")
    
    with col3:
        has_excel = len(excel_data) > 0
        st.metric("Excel", f"✅ {len(excel_data)}" if has_excel else "❌")
        if has_excel:
            st.write(f"Feuilles: {list(excel_data.keys())}")
    
    with col4:
        st.metric("Inflation", "✅" if inflation_rate else "❌")
        if inflation_rate:
            st.write(f"{inflation_rate:.2f}%")
    
    # Vérifier
    if not any([bourse_data.get('masi', {}).get('value'), bourse_data.get('msi20', {}).get('value'), len(excel_data), inflation_rate]):
        st.error("""
        ⚠️ **AUCUNE DONNÉE !**
        
        Collectez d'abord les données :
        1. **Data Ingestion** → Actualiser Bourse
        2. **Data Ingestion** → Upload Excel
        3. **Macronews** → Actualiser Inflation
        """)
    
    st.markdown("---")
    
    # Sélections
    st.markdown("### Sections")
    sections = {'synthese': '📊 Synthèse', 'graphiques': '📈 Graphiques'}
    for key, label in sections.items():
        st.checkbox(label, value=True, key=f"chk_{key}")
    
    st.markdown("---")
    
    # Génération
    if st.button("🚀 Générer", type="primary", use_container_width=True):
        with st.spinner("Génération..."):
            try:
                html = generate_report_html()
                st.session_state.report_html = html
                st.success("✅ Rapport généré")
            except Exception as e:
                st.error(f"❌ Erreur: {str(e)}")
                st.exception(e)
    
    # Aperçu
    if st.session_state.report_html:
        st.markdown("---")
        st.markdown("### Aperçu")
        st.components.v1.html(st.session_state.report_html, height=800, scrolling=True)
        
        st.download_button("📥 Télécharger", st.session_state.report_html,
            f"NEWZ_{datetime.now().strftime('%Y%m%d')}.html", "text/html")

# =============================================================================
render()
