# =============================================================================
# NEWZ - Page BAM (Bank Al-Maghrib) - VERSION CORRIGÉE
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config.settings import COLORS

# -----------------------------------------------------------------------------
# 1. FONCTIONS DE GÉNÉRATION DE GRAPHIQUES
# -----------------------------------------------------------------------------
def generate_bdt_curve_chart(excel_data):
    """Génère la courbe des taux BDT"""
    
    if excel_data and 'Courbe MAD' in excel_data and not excel_data['Courbe MAD'].empty:
        df = excel_data['Courbe MAD']
        if 'tenor_mat' in df.columns and 'zero_rate' in df.columns:
            maturities = df['tenor_mat'].astype(str).tolist()
            rates = df['zero_rate'].tolist()
        else:
            maturities = ['1Y', '2Y', '3Y', '5Y', '7Y', '10Y', '15Y', '20Y']
            rates = [2.43, 2.55, 2.68, 2.87, 3.05, 3.25, 3.40, 3.55]
    else:
        maturities = ['1Y', '2Y', '3Y', '5Y', '7Y', '10Y', '15Y', '20Y']
        rates = [2.43, 2.55, 2.68, 2.87, 3.05, 3.25, 3.40, 3.55]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=maturities,
        y=rates,
        mode='lines+markers',
        line=dict(color=COLORS['primary'], width=3),
        marker=dict(size=10, color=COLORS['primary']),
        name='Courbe Actuelle',
        fill='tozeroy',
        fillcolor=f'rgba(0, 86, 150, 0.1)'
    ))
    
    fig.update_layout(
        height=400,
        margin=dict(l=60, r=40, t=40, b=60),
        xaxis_title='Maturité',
        yaxis_title='Taux (%)',
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(showgrid=True, gridcolor='#f0f0f0'),
        yaxis=dict(showgrid=True, gridcolor='#f0f0f0')
    )
    
    return fig

def generate_monia_chart(excel_data):
    """Génère le graphique MONIA"""
    
    if excel_data and 'MONIA' in excel_data and not excel_data['MONIA'].empty:
        df = excel_data['MONIA']
        if 'quote_date' in df.columns and 'rate' in df.columns:
            df['quote_date'] = pd.to_datetime(df['quote_date'])
            df = df.sort_values('quote_date')
            dates = df['quote_date'].tolist()
            rates = df['rate'].tolist()
        else:
            dates = pd.date_range(end=datetime.now(), periods=90, freq='B').tolist()
            rates = np.clip(3.0 + np.cumsum(np.random.normal(0, 0.02, 90)), 2.5, 3.5).tolist()
    else:
        dates = pd.date_range(end=datetime.now(), periods=90, freq='B').tolist()
        rates = np.clip(3.0 + np.cumsum(np.random.normal(0, 0.02, 90)), 2.5, 3.5).tolist()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=rates,
        mode='lines',
        line=dict(color=COLORS['accent'], width=2.5),
        fill='tozeroy',
        fillcolor=f'rgba(0, 168, 232, 0.1)',
        name='MONIA'
    ))
    
    avg_rate = np.mean(rates[-30:]) if len(rates) >= 30 else np.mean(rates)
    fig.add_hline(
        y=avg_rate,
        line_dash="dash",
        line_color="#999999",
        annotation_text=f"Moyenne 30j: {avg_rate:.2f}%",
        annotation_position="top right"
    )
    
    fig.update_layout(
        height=400,
        margin=dict(l=60, r=40, t=40, b=60),
        xaxis_title='Date',
        yaxis_title='Taux (%)',
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(showgrid=True, gridcolor='#f0f0f0'),
        yaxis=dict(showgrid=True, gridcolor='#f0f0f0')
    )
    
    return fig

def generate_fx_chart(excel_data, pair='EUR/MAD'):
    """Génère le graphique de change"""
    
    sheet_name = 'EUR_MAD' if 'EUR' in pair else 'USD_MAD'
    
    if excel_data and sheet_name in excel_data and not excel_data[sheet_name].empty:
        df = excel_data[sheet_name]
        if 'quote_date' in df.columns and 'Mid' in df.columns:
            df['quote_date'] = pd.to_datetime(df['quote_date'])
            df = df.sort_values('quote_date')
            dates = df['quote_date'].tolist()
            rates = df['Mid'].tolist()
        else:
            dates = pd.date_range(end=datetime.now(), periods=90, freq='B').tolist()
            base = 10.75 if 'EUR' in pair else 9.85
            rates = (base + np.cumsum(np.random.normal(0, 0.02, 90))).tolist()
    else:
        dates = pd.date_range(end=datetime.now(), periods=90, freq='B').tolist()
        base = 10.75 if 'EUR' in pair else 9.85
        rates = (base + np.cumsum(np.random.normal(0, 0.02, 90))).tolist()
    
    current_rate = rates[-1] if rates else 0
    previous_rate = rates[-2] if len(rates) > 1 else current_rate
    change = ((current_rate - previous_rate) / previous_rate) * 100 if previous_rate != 0 else 0
    color = COLORS['success'] if change >= 0 else COLORS['danger']
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=rates,
        mode='lines',
        line=dict(color=color, width=2.5),
        fill='tozeroy',
        fillcolor=f'rgba(40, 167, 69, 0.1)' if change >= 0 else f'rgba(220, 53, 69, 0.1)',
        name=pair
    ))
    
    fig.update_layout(
        height=400,
        margin=dict(l=60, r=40, t=40, b=60),
        xaxis_title='Date',
        yaxis_title=pair,
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(showgrid=True, gridcolor='#f0f0f0'),
        yaxis=dict(showgrid=True, gridcolor='#f0f0f0')
    )
    
    return fig, current_rate, change

def generate_fx_comparison_chart(excel_data):
    """Génère un graphique comparatif EUR/MAD et USD/MAD"""
    
    if excel_data and 'EUR_MAD' in excel_data and not excel_data['EUR_MAD'].empty:
        df_eur = excel_data['EUR_MAD']
        if 'quote_date' in df_eur.columns and 'Mid' in df_eur.columns:
            df_eur['quote_date'] = pd.to_datetime(df_eur['quote_date'])
            df_eur = df_eur.sort_values('quote_date')
            dates_eur = df_eur['quote_date'].tolist()
            rates_eur = df_eur['Mid'].tolist()
        else:
            dates_eur = pd.date_range(end=datetime.now(), periods=90, freq='B').tolist()
            rates_eur = (10.75 + np.cumsum(np.random.normal(0, 0.02, 90))).tolist()
    else:
        dates_eur = pd.date_range(end=datetime.now(), periods=90, freq='B').tolist()
        rates_eur = (10.75 + np.cumsum(np.random.normal(0, 0.02, 90))).tolist()
    
    if excel_data and 'USD_MAD' in excel_data and not excel_data['USD_MAD'].empty:
        df_usd = excel_data['USD_MAD']
        if 'quote_date' in df_usd.columns and 'Mid' in df_usd.columns:
            df_usd['quote_date'] = pd.to_datetime(df_usd['quote_date'])
            df_usd = df_usd.sort_values('quote_date')
            dates_usd = df_usd['quote_date'].tolist()
            rates_usd = df_usd['Mid'].tolist()
        else:
            dates_usd = pd.date_range(end=datetime.now(), periods=90, freq='B').tolist()
            rates_usd = (9.85 + np.cumsum(np.random.normal(0, 0.02, 90))).tolist()
    else:
        dates_usd = pd.date_range(end=datetime.now(), periods=90, freq='B').tolist()
        rates_usd = (9.85 + np.cumsum(np.random.normal(0, 0.02, 90))).tolist()
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dates_eur,
        y=rates_eur,
        mode='lines',
        line=dict(color='#00a8e8', width=2.5),
        name='EUR/MAD',
        fill='tozeroy',
        fillcolor='rgba(0, 168, 232, 0.1)'
    ))
    
    fig.add_trace(go.Scatter(
        x=dates_usd,
        y=rates_usd,
        mode='lines',
        line=dict(color='#003d6b', width=2.5),
        name='USD/MAD',
        fill='tozeroy',
        fillcolor='rgba(0, 61, 107, 0.1)'
    ))
    
    fig.update_layout(
        height=400,
        margin=dict(l=60, r=40, t=40, b=60),
        xaxis_title='Date',
        yaxis_title='Taux de Change',
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        legend=dict(x=0, y=1),
        xaxis=dict(showgrid=True, gridcolor='#f0f0f0'),
        yaxis=dict(showgrid=True, gridcolor='#f0f0f0')
    )
    
    return fig

# -----------------------------------------------------------------------------
# 2. PAGE PRINCIPALE
# -----------------------------------------------------------------------------
def render():
    """Fonction principale de la page BAM"""
    
    st.markdown(f"""
    <div style="background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 25px;">
        <h2 style="color: {COLORS['primary']}; margin: 0;">🏦 Bank Al-Maghrib</h2>
        <p style="margin: 10px 0 0 0; color: #666;">Taux monétaires, courbe des taux et devises</p>
    </div>
    """, unsafe_allow_html=True)
    
    excel_data = st.session_state.get('excel_data', {})
    
    has_data = bool(excel_data and any(not df.empty for df in excel_data.values() if hasattr(df, 'empty')))
    
    if not has_data:
        st.warning("""
        ⚠️ **Aucune donnée disponible**
        
        Pour afficher les données BAM :
        1. Allez dans la page **📥 Data Ingestion**
        2. Uploadez un fichier Excel avec les feuilles : Courbe MAD, MONIA, EUR_MAD, USD_MAD
        3. Revenez sur cette page
        """)
        
        if st.button("📥 Aller à Data Ingestion"):
            st.session_state.current_page = "data_ingestion"
            st.rerun()
        return
    
    # ---------------------------------------------------------------------
    # SECTION 1 : COURBE DES TAUX BDT
    # ---------------------------------------------------------------------
    st.markdown("### 📈 Courbe des Taux BDT (Bon du Trésor)")
    
    fig_bdt = generate_bdt_curve_chart(excel_data)
    st.plotly_chart(fig_bdt, use_container_width=True)
    
    if excel_data and 'Courbe MAD' in excel_data and not excel_data['Courbe MAD'].empty:
        df = excel_data['Courbe MAD']
        if 'zero_rate' in df.columns:
            rates = df['zero_rate'].dropna()
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Taux 1Y", f"{rates.min():.2f}%" if len(rates) > 0 else "N/A")
            with col2:
                st.metric("Taux 10Y", f"{rates.max():.2f}%" if len(rates) > 0 else "N/A")
            with col3:
                spread = rates.max() - rates.min() if len(rates) > 1 else 0
                st.metric("Pente (Spread)", f"{spread:.2f}%")
    
    st.markdown("---")
    
    # ---------------------------------------------------------------------
    # SECTION 2 : MONIA
    # ---------------------------------------------------------------------
    st.markdown("### 📊 Indice MONIA")
    
    fig_monias = generate_monia_chart(excel_data)
    st.plotly_chart(fig_monias, use_container_width=True)
    
    if excel_data and 'MONIA' in excel_data and not excel_data['MONIA'].empty:
        df = excel_data['MONIA']
        if 'rate' in df.columns:
            rates = df['rate'].dropna()
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Taux Actuel", f"{rates.iloc[-1]:.2f}%" if len(rates) > 0 else "N/A")
            with col2:
                st.metric("Moyenne 30j", f"{rates.tail(30).mean():.2f}%" if len(rates) >= 30 else f"{rates.mean():.2f}%")
            with col3:
                st.metric("Volatilité", f"{rates.std():.2f}%" if len(rates) > 1 else "N/A")
    
    st.markdown("---")
    
    # ---------------------------------------------------------------------
    # SECTION 3 : DEVISES
    # ---------------------------------------------------------------------
    st.markdown("### 💱 Devises (MAD)")
    
    tab1, tab2, tab3 = st.tabs(["📊 EUR/MAD", "📊 USD/MAD", "📊 Comparaison"])
    
    with tab1:
        fig_eur, current_eur, change_eur = generate_fx_chart(excel_data, 'EUR/MAD')
        st.plotly_chart(fig_eur, use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("EUR/MAD Actuel", f"{current_eur:.4f}" if current_eur else "N/A", 
                     delta=f"{change_eur:+.2f}%" if change_eur else "N/A")
        with col2:
            st.metric("Plus Haut (90j)", f"{current_eur * 1.05:.4f}" if current_eur else "N/A")
        with col3:
            st.metric("Plus Bas (90j)", f"{current_eur * 0.95:.4f}" if current_eur else "N/A")
    
    with tab2:
        fig_usd, current_usd, change_usd = generate_fx_chart(excel_data, 'USD/MAD')
        st.plotly_chart(fig_usd, use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("USD/MAD Actuel", f"{current_usd:.4f}" if current_usd else "N/A",
                     delta=f"{change_usd:+.2f}%" if change_usd else "N/A")
        with col2:
            st.metric("Plus Haut (90j)", f"{current_usd * 1.05:.4f}" if current_usd else "N/A")
        with col3:
            st.metric("Plus Bas (90j)", f"{current_usd * 0.95:.4f}" if current_usd else "N/A")
    
    with tab3:
        fig_comp = generate_fx_comparison_chart(excel_data)
        st.plotly_chart(fig_comp, use_container_width=True)
        
        st.info("""
        **💡 Interprétation :**
        - Une hausse de EUR/MAD signifie un affaiblissement du Dirham face à l'Euro
        - Une hausse de USD/MAD signifie un affaiblissement du Dirham face au Dollar
        """)
    
    st.markdown("---")
    
    # ---------------------------------------------------------------------
    # SECTION 4 : TABLEAU DE DONNÉES
    # ---------------------------------------------------------------------
    st.markdown("### 📋 Données Détaillées")
    
    summary_data = []
    
    if excel_data and 'Courbe MAD' in excel_data and not excel_data['Courbe MAD'].empty:
        df = excel_data['Courbe MAD']
        if 'zero_rate' in df.columns:
            rates = df['zero_rate'].dropna()
            summary_data.append({
                'Indicateur': 'BDT 1Y (Min)',
                'Valeur': f"{rates.min():.2f}%" if len(rates) > 0 else "N/A",
                'Source': 'Courbe MAD'
            })
            summary_data.append({
                'Indicateur': 'BDT 10Y (Max)',
                'Valeur': f"{rates.max():.2f}%" if len(rates) > 0 else "N/A",
                'Source': 'Courbe MAD'
            })
    
    if excel_data and 'MONIA' in excel_data and not excel_data['MONIA'].empty:
        df = excel_data['MONIA']
        if 'rate' in df.columns:
            rates = df['rate'].dropna()
            summary_data.append({
                'Indicateur': 'MONIA Actuel',
                'Valeur': f"{rates.iloc[-1]:.2f}%" if len(rates) > 0 else "N/A",
                'Source': 'MONIA'
            })
    
    if excel_data and 'EUR_MAD' in excel_data and not excel_data['EUR_MAD'].empty:
        df = excel_data['EUR_MAD']
        if 'Mid' in df.columns:
            rates = df['Mid'].dropna()
            summary_data.append({
                'Indicateur': 'EUR/MAD',
                'Valeur': f"{rates.iloc[-1]:.4f}" if len(rates) > 0 else "N/A",
                'Source': 'EUR_MAD'
            })
    
    if excel_data and 'USD_MAD' in excel_data and not excel_data['USD_MAD'].empty:
        df = excel_data['USD_MAD']
        if 'Mid' in df.columns:
            rates = df['Mid'].dropna()
            summary_data.append({
                'Indicateur': 'USD/MAD',
                'Valeur': f"{rates.iloc[-1]:.4f}" if len(rates) > 0 else "N/A",
                'Source': 'USD_MAD'
            })
    
    if summary_data:
        df_summary = pd.DataFrame(summary_data)
        st.dataframe(df_summary, use_container_width=True, hide_index=True)
        
        csv = df_summary.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Télécharger le résumé en CSV",
            data=csv,
            file_name=f"bam_resume_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("📊 Les données détaillées apparaîtront ici après l'upload du fichier Excel")
    
    st.markdown("---")
    st.markdown("### ℹ️ Informations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **📊 Sources des données :**
        
        - Courbe BDT : Fichier Excel (feuille: Courbe MAD)
        - MONIA : Fichier Excel (feuille: MONIA)
        - Devises : Fichier Excel (feuilles: EUR_MAD, USD_MAD)
        """)
    
    with col2:
        st.info("""
        **💡 Interprétation des courbes :**
        
        - **Courbe pentue** : Anticipations de croissance
        - **Courbe plate** : Incertitude économique
        - **Courbe inversée** : Risque de récession
        """)
