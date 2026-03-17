# =============================================================================
# NEWZ - Page Bank Al-Maghrib
# Fichier : pages/bam.py
# =============================================================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path
import sys
import numpy as np

sys.path.append(str(Path(__file__).resolve().parent.parent))

try:
    from config.settings import COLORS
except ImportError:
    COLORS = {
        'primary': '#005696',
        'secondary': '#003d6b',
        'accent': '#00a8e8',
        'success': '#28a745',
        'danger': '#dc3545',
        'light': '#f8f9fa'
    }

# -----------------------------------------------------------------------------
# INITIALISATION
# -----------------------------------------------------------------------------

def init_local_session():
    if 'excel_data' not in st.session_state:
        st.session_state.excel_data = {}

init_local_session()

# -----------------------------------------------------------------------------
# FONCTIONS DE GRAPHIQUES
# -----------------------------------------------------------------------------

def generate_bdt_curve_chart(excel_data=None):
    """Génère la courbe des taux BDT (Bank Al-Maghrib)"""
    
    # Données simulées si pas de données Excel
    if excel_data is None or 'MADBDT_52W' not in excel_data or excel_data['MADBDT_52W'].empty:
        tenors = ['1W', '1M', '3M', '6M', '9M', '1Y', '2Y', '3Y', '5Y', '10Y']
        rates = [3.00, 3.05, 3.10, 3.15, 3.20, 3.25, 3.35, 3.45, 3.60, 3.85]
    else:
        df = excel_data['MADBDT_52W']
        if 'tenor' in df.columns and 'rate' in df.columns:
            tenors = df['tenor'].tolist()
            rates = df['rate'].tolist()
        else:
            tenors = ['1W', '1M', '3M', '6M', '9M', '1Y', '2Y', '3Y', '5Y', '10Y']
            rates = [3.00, 3.05, 3.10, 3.15, 3.20, 3.25, 3.35, 3.45, 3.60, 3.85]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=tenors,
        y=rates,
        mode='lines+markers',
        name='Courbe BDT',
        line=dict(color=COLORS['primary'], width=3, shape='spline'),
        marker=dict(size=8, color=COLORS['primary'])
    ))
    
    fig.update_layout(
        title="Courbe des Taux BDT (Bank Al-Maghrib)",
        xaxis_title="Échéance",
        yaxis_title="Taux (%)",
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=450,
        margin=dict(l=60, r=30, t=50, b=40),
        yaxis=dict(
            tickformat='.2f',
            range=[min(rates) - 0.2, max(rates) + 0.3],
            gridcolor='#eee'
        ),
        xaxis=dict(gridcolor='#eee')
    )
    
    return fig

def generate_monia_chart(excel_data=None):
    """Génère le graphique MONIA avec échelle zoomée"""
    
    if excel_data is None or 'MONIA' not in excel_data or excel_data['MONIA'].empty:
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        rates = [3.00 + np.random.uniform(-0.02, 0.02) for _ in range(30)]
    else:
        df = excel_data['MONIA']
        if 'quote_date' in df.columns and 'rate' in df.columns:
            dates = pd.to_datetime(df['quote_date'])
            rates = df['rate']
            # Filtrer les valeurs nulles
            mask = rates.notna()
            dates = dates[mask]
            rates = rates[mask]
        else:
            dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
            rates = [3.00 + np.random.uniform(-0.02, 0.02) for _ in range(30)]
    
    if len(rates) == 0:
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        rates = [3.00 + np.random.uniform(-0.02, 0.02) for _ in range(30)]
    
    rates_series = pd.Series(rates) if not isinstance(rates, pd.Series) else rates
    
    # Calculer la plage pour zoomer
    min_val = rates_series.min()
    max_val = rates_series.max()
    range_val = max_val - min_val
    padding = max(range_val * 0.3, 0.005)  # Au moins 0.005 de marge
    y_min = min_val - padding
    y_max = max_val + padding
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dates,
        y=rates_series,
        mode='lines+markers',
        name='MONIA',
        line=dict(color=COLORS['accent'], width=2.5),
        fill='tozeroy',
        fillcolor=f'rgba(0, 168, 232, 0.15)',
        marker=dict(size=4)
    ))
    
    fig.update_layout(
        title="Indice MONIA (30 jours)",
        xaxis_title="Date",
        yaxis_title="Taux (%)",
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=420,
        margin=dict(l=60, r=30, t=50, b=40),
        yaxis=dict(
            tickformat='.3f',
            range=[y_min, y_max],  # AXE Y ZOOMÉ
            gridcolor='#eee'
        ),
        xaxis=dict(gridcolor='#eee')
    )
    
    return fig
def generate_fx_chart(excel_data=None, pair='EUR/MAD'):
    """Génère le graphique EUR/MAD ou USD/MAD avec échelle zoomée"""
    
    sheet_name = 'EUR_MAD' if 'EUR' in pair else 'USD_MAD'
    
    if excel_data is None or sheet_name not in excel_data or excel_data[sheet_name].empty:
        # Données simulées réalistes
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        base = 10.75 if 'EUR' in pair else 9.85
        # Générer des variations réalistes autour du taux de base
        np.random.seed(42 if 'EUR' in pair else 43)
        changes = np.random.uniform(-0.02, 0.02, size=30).cumsum()
        rates = base + changes
    else:
        df = excel_data[sheet_name]
        if 'quote_date' in df.columns and 'Mid' in df.columns:
            dates = pd.to_datetime(df['quote_date'])
            rates = df['Mid']
            # Filtrer les valeurs nulles ou 0
            mask = (rates.notna()) & (rates > 0)
            dates = dates[mask]
            rates = rates[mask]
        else:
            dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
            base = 10.75 if 'EUR' in pair else 9.85
            np.random.seed(42 if 'EUR' in pair else 43)
            changes = np.random.uniform(-0.02, 0.02, size=30).cumsum()
            rates = base + changes
    
    # Vérifier qu'on a des données valides
    if len(rates) == 0 or rates.isna().all():
        # Fallback
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        base = 10.75 if 'EUR' in pair else 9.85
        rates = pd.Series([base + np.random.uniform(-0.02, 0.02) for _ in range(30)])
    
    # Calculer la plage pour zoomer l'axe Y
    min_val = rates.min()
    max_val = rates.max()
    range_val = max_val - min_val
    
    # Ajouter une marge de 20% pour voir les mouvements
    padding = max(range_val * 0.2, 0.01)  # Au moins 0.01 de marge
    y_min = min_val - padding
    y_max = max_val + padding
    
    # Valeurs actuelles et précédentes
    current_rate = rates.iloc[-1] if hasattr(rates, 'iloc') else rates[-1]
    prev_rate = rates.iloc[0] if hasattr(rates, 'iloc') else rates[0]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dates,
        y=rates,
        mode='lines+markers',
        name=pair,
        line=dict(color=COLORS['success'], width=2.5),
        fill='tozeroy',
        fillcolor=f'rgba(40, 167, 69, 0.15)',
        marker=dict(size=4)
    ))
    
    fig.update_layout(
        title=f"Évolution {pair} (30 jours)",
        xaxis_title="Date",
        yaxis_title="Taux de change",
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=420,
        margin=dict(l=60, r=30, t=50, b=40),
        yaxis=dict(
            tickformat='.4f',
            range=[y_min, y_max],  # AXE Y ZOOMÉ
            gridcolor='#eee'
        ),
        xaxis=dict(gridcolor='#eee')
    )
    
    return fig, current_rate, prev_rate
# -----------------------------------------------------------------------------
# FONCTION PRINCIPALE
# -----------------------------------------------------------------------------

def render():
    """Fonction principale"""
    
    # HEADER
    st.markdown(f"""
    <div style="background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 25px;">
        <h2 style="color: {COLORS['primary']}; margin: 0;">🏦 Bank Al-Maghrib</h2>
        <p style="margin: 10px 0 0 0; color: #666;">Taux, Courbe BDT et Devises</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ---------------------------------------------------------------------
    # SECTION 1 : TAUX DIRECTEUR
    # ---------------------------------------------------------------------
    st.markdown("### 📊 Taux Directeur")
    
    excel_data = st.session_state.get('excel_data', {})
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Taux Directeur",
            value="3.00%",
            delta="Inchangé"
        )
    
    with col2:
        st.metric(
            label="Taux d'Intervention",
            value="3.00%",
            delta="Inchangé"
        )
    
    with col3:
        st.metric(
            label="Facilité de Prêt Marginal",
            value="3.50%",
            delta="Inchangé"
        )
    
    st.caption("Dernière décision BAM : Maintien du taux directeur à 3.00%")
    
    st.markdown("---")
    
    # ---------------------------------------------------------------------
    # SECTION 2 : COURBE BDT
    # ---------------------------------------------------------------------
    st.markdown("### 📈 Courbe des Taux BDT")
    
    fig_bdt = generate_bdt_curve_chart(excel_data)
    st.plotly_chart(fig_bdt, use_container_width=True)
    
    st.info("""
    **💡 Interprétation :**
    - Courbe ascendante = anticipations de hausse des taux
    - Courbe plate = incertitude économique
    - Courbe inversée = risque de récession
    """)
    
    st.markdown("---")
    
    # ---------------------------------------------------------------------
    # SECTION 3 : MONIA
    # ---------------------------------------------------------------------
    st.markdown("### 💰 Indice MONIA")
    
    fig_mon = generate_monia_chart(excel_data)
    st.plotly_chart(fig_mon, use_container_width=True)
    
    st.caption("MONIA (Moroccan OverNight Index Average) : Taux moyen au jour le jour")
    
    st.markdown("---")
    
    # ---------------------------------------------------------------------
    # SECTION 4 : DEVISES
    # ---------------------------------------------------------------------
    st.markdown("### 💱 Devises")
    
    tab1, tab2 = st.tabs(["EUR/MAD", "USD/MAD"])
    
    with tab1:
        fig_eur, eur_current, eur_prev = generate_fx_chart(excel_data, 'EUR/MAD')
        st.plotly_chart(fig_eur, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("EUR/MAD Actuel", f"{eur_current:.4f}")
        with col2:
            change = ((eur_current - eur_prev) / eur_prev) * 100
            st.metric("Variation", f"{change:+.2f}%")
    
    with tab2:
        fig_usd, usd_current, usd_prev = generate_fx_chart(excel_data, 'USD/MAD')
        st.plotly_chart(fig_usd, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("USD/MAD Actuel", f"{usd_current:.4f}")
        with col2:
            change = ((usd_current - usd_prev) / usd_prev) * 100
            st.metric("Variation", f"{change:+.2f}%")
    
    st.markdown("---")
    
    # ---------------------------------------------------------------------
    # SECTION 5 : RÉSUMÉ
    # ---------------------------------------------------------------------
    st.markdown("### 📋 Résumé")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Taux Directeur", "3.00%", "Inchangé")
    with col2:
        st.metric("Inflation Cible", "2-3%", "✓")
    with col3:
        st.metric("Réserves de Change", "✓ Confortables")
    
    # Bouton actualisation
    if st.button("🔄 Actualiser les Données", type="secondary"):
        st.rerun()

# =============================================================================
# APPEL
# =============================================================================
render()
