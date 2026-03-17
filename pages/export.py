# =============================================================================
# NEWZ - Page Export de Rapports
# Utilise les DONNÉES COLLECTÉES dans les autres pages
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
    COLORS = {'primary': '#005696', 'secondary': '#003d6b'}
    APP_INFO = {'name': 'Newz', 'version': '2.0.0'}

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
# GÉNÉRATEUR DE RAPPORT (Données réelles collectées)
# -----------------------------------------------------------------------------

def generate_report_html():
    """Génère le rapport avec les DONNÉES RÉELLES collectées"""
    
    # Récupérer les DONNÉES COLLECTÉES
    bourse_data = st.session_state.get('bourse_data', {})
    excel_data = st.session_state.get('excel_data', {})
    news_data = st.session_state.get('news_data', [])
    inflation_rate = st.session_state.get('inflation_rate', None)
    selected = st.session_state.get('export_selected_sections', [])
    
    # Données MASI/MSI20 (collectées dans Data Ingestion)
    masi_val = bourse_data.get('masi', {}).get('value')
    masi_chg = bourse_data.get('masi', {}).get('change')
    msi20_val = bourse_data.get('msi20', {}).get('value')
    msi20_chg = bourse_data.get('msi20', {}).get('change')
    
    # USD/MAD et EUR/MAD (collectés dans Data Ingestion - Excel)
    usd_mad = None
    eur_mad = None
    
    if 'USD_MAD' in excel_data and not excel_data['USD_MAD'].empty:
        df = excel_data['USD_MAD']
        if 'Mid' in df.columns:
            valid = df.dropna(subset=['Mid'])
            valid = valid[valid['Mid'] > 0]
            if not valid.empty:
                usd_mad = float(valid['Mid'].iloc[-1])
    
    if 'EUR_MAD' in excel_data and not excel_data['EUR_MAD'].empty:
        df = excel_data['EUR_MAD']
        if 'Mid' in df.columns:
            valid = df.dropna(subset=['Mid'])
            valid = valid[valid['Mid'] > 0]
            if not valid.empty:
                eur_mad = float(valid['Mid'].iloc[-1])
    
    # Créer les graphiques UNIQUEMENT si on a des données
    html_graphs = {}
    
    # Graphique MASI (seulement si données disponibles)
    if masi_val is not None:
        try:
            # Créer un graphique simple avec la valeur actuelle
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=[datetime.now()],
                y=[masi_val],
                mode='markers+text',
                marker=dict(size=20, color='#005696'),
                text=[f"{masi_val:,.0f}"],
                textposition="top center",
                textfont=dict(size=20, color='#005696')
            ))
            fig.update_layout(
                title=f"MASI - {datetime.now().strftime('%d/%m/%Y')}",
                height=300,
                xaxis=dict(showgrid=False, showticklabels=False),
                yaxis=dict(showgrid=True, gridcolor='#eee', range=[masi_val*0.99, masi_val*1.01]),
                plot_bgcolor='white'
            )
            html_graphs['masi'] = fig.to_html(full_html=False, include_plotlyjs='cdn')
        except:
            html_graphs['masi'] = None
    else:
        html_graphs['masi'] = None
    
    # Graphique MSI20
    if msi20_val is not None:
        try:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=[datetime.now()],
                y=[msi20_val],
                mode='markers+text',
                marker=dict(size=20, color='#00a8e8'),
                text=[f"{msi20_val:,.0f}"],
                textposition="top center"
            ))
            fig.update_layout(
                title=f"MSI20 - {datetime.now().strftime('%d/%m/%Y')}",
                height=300,
                xaxis=dict(showgrid=False, showticklabels=False),
                yaxis=dict(showgrid=True, gridcolor='#eee', range=[msi20_val*0.99, msi20_val*1.01]),
                plot_bgcolor='white'
            )
            html_graphs['msi20'] = fig.to_html(full_html=False, include_plotlyjs='cdn')
        except:
            html_graphs['msi20'] = None
    else:
        html_graphs['msi20'] = None
    
    # Courbe BDT (si données Excel disponibles)
    if 'MADBDT_52W' in excel_data and not excel_data['MADBDT_52W'].empty:
        try:
            df = excel_data['MADBDT_52W']
            if 'tenor_mat' in df.columns and 'zero_rate' in df.columns:
                tenors = df['tenor_mat'].tolist()
                rates = df['zero_rate'].tolist()
                
                fig = go.Figure(go.Scatter(x=tenors, y=rates, mode='lines+markers',
                    line=dict(color='#005696', width=3), marker=dict(size=8)))
                fig.update_layout(title="Courbe des Taux BDT", height=300,
                    plot_bgcolor='white', xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=True, gridcolor='#eee'))
                html_graphs['bdt'] = fig.to_html(full_html=False, include_plotlyjs='cdn')
            else:
                html_graphs['bdt'] = None
        except:
            html_graphs['bdt'] = None
    else:
        html_graphs['bdt'] = None
    
    # MONIA (si données Excel disponibles)
    if 'MONIA' in excel_data and not excel_data['MONIA'].empty:
        try:
            df = excel_data['MONIA']
            if 'quote_date' in df.columns and 'rate' in df.columns:
                df = df.dropna(subset=['quote_date', 'rate'])
                df['quote_date'] = pd.to_datetime(df['quote_date'])
                df = df.sort_values('quote_date').tail(30)
                
                fig = go.Figure(go.Scatter(x=df['quote_date'], y=df['rate'], mode='lines',
                    line=dict(color='#00a8e8', width=2.5)))
                fig.update_layout(title="Indice MONIA", height=300,
                    plot_bgcolor='white', xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=True, gridcolor='#eee'))
                html_graphs['monia'] = fig.to_html(full_html=False, include_plotlyjs='cdn')
            else:
                html_graphs['monia'] = None
        except:
            html_graphs['monia'] = None
    else:
        html_graphs['monia'] = None
    
    # EUR/MAD (si données disponibles)
    if eur_mad is not None:
        try:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=[datetime.now()], y=[eur_mad], mode='markers+text',
                marker=dict(size=20, color='#28a745'), text=[f"{eur_mad:.4f}"]))
            fig.update_layout(title="EUR/MAD", height=300, plot_bgcolor='white',
                xaxis=dict(showgrid=False, showticklabels=False),
                yaxis=dict(showgrid=True, gridcolor='#eee'))
            html_graphs['eur'] = fig.to_html(full_html=False, include_plotlyjs='cdn')
        except:
            html_graphs['eur'] = None
    else:
        html_graphs['eur'] = None
    
    # USD/MAD (si données disponibles)
    if usd_mad is not None:
        try:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=[datetime.now()], y=[usd_mad], mode='markers+text',
                marker=dict(size=20, color='#28a745'), text=[f"{usd_mad:.4f}"]))
            fig.update_layout(title="USD/MAD", height=300, plot_bgcolor='white',
                xaxis=dict(showgrid=False, showticklabels=False),
                yaxis=dict(showgrid=True, gridcolor='#eee'))
            html_graphs['usd'] = fig.to_html(full_html=False, include_plotlyjs='cdn')
        except:
            html_graphs['usd'] = None
    else:
        html_graphs['usd'] = None
    
    # Construire le HTML
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
            .no-data {{ padding: 20px; background: #fff3cd; border-radius: 8px; text-align: center; color: #856404; }}
            .footer {{ margin-top: 50px; padding: 30px; background: linear-gradient(135deg, #005696, #003d6b); color: white; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏦 CDG CAPITAL</h1>
                <h2>Newz - Market Data Platform</h2>
                <p>Rapport - {datetime.now().strftime('%d/%m/%Y')}</p>
            </div>
    """
    
    # SECTION 1 : SYNTHÈSE (uniquement si données disponibles)
    if 'summary' in selected:
        html += '<div class="section"><h2>📊 Synthèse</h2>'
        
        if masi_val is not None or msi20_val is not None or eur_mad is not None or usd_mad is not None or inflation_rate is not None:
            html += '<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:15px;margin:20px 0;">'
            
            if masi_val is not None:
                html += f'<div style="background:white;padding:15px;text-align:center;box-shadow:0 2px 5px rgba(0,0,0,0.1);"><h4 style="margin:0 0 10px 0;color:#666;font-size:12px;">MASI</h4><div style="font-size:24px;font-weight:bold;color:#005696">{masi_val:,.0f}</div><div style="color:{"#28a745" if masi_chg and masi_chg >= 0 else "#dc3545"}">{masi_chg:+.2f}%</div></div>'
            
            if msi20_val is not None:
                html += f'<div style="background:white;padding:15px;text-align:center;"><h4 style="margin:0 0 10px 0;color:#666;font-size:12px;">MSI20</h4><div style="font-size:24px;font-weight:bold;color:#005696">{msi20_val:,.0f}</div><div style="color:{"#28a745" if msi20_chg and msi20_chg >= 0 else "#dc3545"}">{msi20_chg:+.2f}%</div></div>'
            
            if eur_mad is not None:
                html += f'<div style="background:white;padding:15px;text-align:center;"><h4 style="margin:0 0 10px 0;color:#666;font-size:12px;">EUR/MAD</h4><div style="font-size:24px;font-weight:bold;color:#005696">{eur_mad:.4f}</div></div>'
            
            if usd_mad is not None:
                html += f'<div style="background:white;padding:15px;text-align:center;"><h4 style="margin:0 0 10px 0;color:#666;font-size:12px;">USD/MAD</h4><div style="font-size:24px;font-weight:bold;color:#005696">{usd_mad:.4f}</div></div>'
            
            if inflation_rate is not None:
                html += f'<div style="background:white;padding:15px;text-align:center;"><h4 style="margin:0 0 10px 0;color:#666;font-size:12px;">Inflation</h4><div style="font-size:24px;font-weight:bold;color:#005696">{inflation_rate:.2f}%</div></div>'
            
            html += '</div>'
        else:
            html += '<div class="no-data">⚠️ Aucune donnée disponible. Allez dans <b>Data Ingestion</b> pour collecter les données.</div>'
        
        html += '</div>'
    
    # SECTION 2 : INDICES BOURSIERS
    if 'bdc' in selected:
        html += '<div class="section"><h2>📈 Indices Boursiers</h2>'
        
        if html_graphs.get('masi'):
            html += f'<div class="chart-box">{html_graphs["masi"]}</div>'
        else:
            html += '<div class="no-data">⚠️ MASI : Aucune donnée disponible</div>'
        
        if html_graphs.get('msi20'):
            html += f'<div class="chart-box">{html_graphs["msi20"]}</div>'
        else:
            html += '<div class="no-data">⚠️ MSI20 : Aucune donnée disponible</div>'
        
        html += '</div>'
    
    # SECTION 3 : BANK AL-MAGHRIB
    if 'bam' in selected:
        html += '<div class="section"><h2>🏦 Bank Al-Maghrib</h2>'
        
        if html_graphs.get('bdt'):
            html += '<h3 style="color:#003d6b;margin:20px 0 15px 0;">Courbe BDT</h3>'
            html += f'<div class="chart-box">{html_graphs["bdt"]}</div>'
        else:
            html += '<div class="no-data">⚠️ Courbe BDT : Aucune donnée Excel disponible</div>'
        
        if html_graphs.get('monia'):
            html += '<h3 style="color:#003d6b;margin:20px 0 15px 0;">MONIA</h3>'
            html += f'<div class="chart-box">{html_graphs["monia"]}</div>'
        else:
            html += '<div class="no-data">⚠️ MONIA : Aucune donnée Excel disponible</div>'
        
        if html_graphs.get('eur'):
            html += '<h3 style="color:#003d6b;margin:20px 0 15px 0;">EUR/MAD</h3>'
            html += f'<div class="chart-box">{html_graphs["eur"]}</div>'
        else:
            html += '<div class="no-data">⚠️ EUR/MAD : Aucune donnée disponible</div>'
        
        if html_graphs.get('usd'):
            html += '<h3 style="color:#003d6b;margin:20px 0 15px 0;">USD/MAD</h3>'
            html += f'<div class="chart-box">{html_graphs["usd"]}</div>'
        else:
            html += '<div class="no-data">⚠️ USD/MAD : Aucune donnée disponible</div>'
        
        html += '</div>'
    
    # SECTION 4 : NEWS
    if 'news' in selected and news_data:
        html += '<div class="section"><h2>📰 Actualités</h2>'
        for news in news_data[:10]:
            title = news.get('title', 'N/A')
            summary = news.get('summary', '')[:200]
            source = news.get('source', 'N/A')
            html += f'<div style="margin:10px 0;padding:15px;background:white;border-left:3px solid #005696;border-radius:5px;"><b style="color:#005696">{title}</b><br><span style="color:#666;font-size:13px">{source}</span><br><p style="margin:10px 0 0 0;color:#333">{summary}</p></div>'
        html += '</div>'
    elif 'news' in selected:
        html += '<div class="section"><h2>📰 Actualités</h2><div class="no-data">⚠️ Aucune actualité disponible. Allez dans <b>Data Ingestion</b> pour collecter les news.</div></div>'
    
    # Footer
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

# -----------------------------------------------------------------------------
# FONCTION PRINCIPALE
# -----------------------------------------------------------------------------

def render():
    """Fonction principale"""
    
    st.markdown(f"""
    <div style="background:white;padding:25px;border-radius:10px;margin-bottom:25px;">
        <h2 style="color:{COLORS['primary']};margin:0;">📤 Export de Rapport</h2>
        <p style="margin:10px 0 0 0;color:#666;">Générez un rapport basé sur les données collectées</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("💡 **Important :** Ce rapport utilise UNIQUEMENT les données que vous avez collectées dans **Data Ingestion**. Assurez-vous d'avoir actualisé les données avant de générer le rapport.")
    
    st.markdown("### Sections à inclure")
    sections = {
        'summary': '📊 Synthèse',
        'bdc': '📈 Indices Boursiers',
        'bam': '🏦 Bank Al-Maghrib',
        'news': '📰 Actualités'
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
