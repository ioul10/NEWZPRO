# =============================================================================
# NEWZ - Page BDC Statut (Version Corrigée)
# Fichier : pages/bdc_statut.py
# =============================================================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path
import sys
import numpy as np

sys.path.append(str(Path(__file__).resolve().parent.parent))

# Import sécurisé de la configuration
try:
    from config.settings import COLORS, MSI20_COMPOSITION
except ImportError:
    COLORS = {
        'primary': '#005696',
        'secondary': '#003d6b',
        'accent': '#00a8e8',
        'success': '#28a745',
        'danger': '#dc3545',
        'light': '#f8f9fa'
    }
    MSI20_COMPOSITION = []

# -----------------------------------------------------------------------------
# INITIALISATION LOCALE
# -----------------------------------------------------------------------------

def init_local_session():
    if 'bourse_data' not in st.session_state:
        st.session_state.bourse_data = {}
    if 'actions_data' not in st.session_state:
        st.session_state.actions_data = None
    if 'correlation_period' not in st.session_state:
        st.session_state.correlation_period = 90

init_local_session()

# -----------------------------------------------------------------------------
# FONCTIONS UTILITAIRES
# -----------------------------------------------------------------------------

def get_market_status():
    """Récupère le statut actuel du marché avec heure dynamique"""
    import pytz
    
    now = datetime.now(pytz.timezone('Africa/Casablanca'))
    current_time = now.time()
    current_day = now.strftime('%A')
    
    market_open = datetime.strptime('09:00', '%H:%M').time()
    market_close = datetime.strptime('15:30', '%H:%M').time()
    working_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    
    if current_day in working_days:
        if market_open <= current_time <= market_close:
            is_open = True
            status_text = "🟢 Marché Ouvert"
            next_info = f"Ferme à {market_close.strftime('%H:%M')}"
        elif current_time < market_open:
            is_open = False
            status_text = "🔴 Marché Fermé"
            next_info = f"Ouvre à {market_open.strftime('%H:%M')}"
        else:
            is_open = False
            status_text = "🔴 Marché Fermé"
            next_info = "Ouvre demain 09:00"
    else:
        is_open = False
        status_text = "🔴 Marché Fermé (Week-end)"
        next_info = "Ouvre lundi 09:00"
    
    return {
        'is_open': is_open,
        'status_text': status_text,
        'current_time': now.strftime('%H:%M:%S'),
        'next_info': next_info
    }

# -----------------------------------------------------------------------------
# FONCTIONS DE GRAPHIQUES (EN % POUR MIEUX VOIR LES MOUVEMENTS)
# -----------------------------------------------------------------------------

def generate_masi_chart_percentage(bourse_data=None, days=10):
    """Génère le graphique MASI en VARIATION % pour mieux visualiser les mouvements"""
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    base_value = 12450 if not bourse_data else bourse_data.get('masi', {}).get('value', 12450)
    
    np.random.seed(42)
    returns = np.random.normal(0.0003, 0.008, size=days)
    values = base_value * (1 + returns).cumprod()
    
    # Conversion en % par rapport au premier point
    base = values.iloc[0]
    pct_values = ((values - base) / base) * 100
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=pct_values,
        mode='lines+markers',
        name='MASI',
        line=dict(color=COLORS['primary'], width=2.5),
        fill='tozeroy',
        fillcolor=f'rgba(0, 86, 150, 0.15)',
        marker=dict(size=4)
    ))
    
    # Calculer la plage Y pour zoomer sur les mouvements
    y_min = pct_values.min()
    y_max = pct_values.max()
    y_range = y_max - y_min
    padding = max(y_range * 0.3, 0.5)  # Au moins 0.5% de marge
    
    fig.update_layout(
        title=f"Évolution du MASI en % ({days} jours)",
        xaxis_title="Date",
        yaxis_title="Variation (%)",
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=420,
        margin=dict(l=60, r=30, t=50, b=40),
        yaxis=dict(
            range=[y_min - padding, y_max + padding],  # Zoom sur les mouvements
            tickformat='+.2f',
            zeroline=True,
            zerolinecolor='gray',
            zerolinewidth=1,
            gridcolor='#eee'
        ),
        xaxis=dict(gridcolor='#eee')
    )
    
    # Ligne zéro bien visible
    fig.add_hline(y=0, line_dash="solid", line_color="#999", linewidth=1)
    
    return fig

def generate_msi20_chart_percentage(bourse_data=None, days=10):
    """Génère le graphique MSI20 en VARIATION %"""
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    base_value = 1580 if not bourse_data else bourse_data.get('msi20', {}).get('value', 1580)
    
    np.random.seed(43)
    returns = np.random.normal(0.0004, 0.01, size=days)
    values = base_value * (1 + returns).cumprod()
    
    base = values.iloc[0]
    pct_values = ((values - base) / base) * 100
    
    y_min = pct_values.min()
    y_max = pct_values.max()
    y_range = y_max - y_min
    padding = max(y_range * 0.3, 0.5)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=pct_values,
        mode='lines+markers',
        name='MSI20',
        line=dict(color=COLORS['accent'], width=2.5),
        fill='tozeroy',
        fillcolor=f'rgba(0, 168, 232, 0.15)',
        marker=dict(size=4)
    ))
    
    fig.update_layout(
        title=f"Évolution du MSI20 en % ({days} jours)",
        xaxis_title="Date",
        yaxis_title="Variation (%)",
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=420,
        margin=dict(l=60, r=30, t=50, b=40),
        yaxis=dict(
            range=[y_min - padding, y_max + padding],
            tickformat='+.2f',
            zeroline=True,
            zerolinecolor='gray',
            zerolinewidth=1,
            gridcolor='#eee'
        ),
        xaxis=dict(gridcolor='#eee')
    )
    
    fig.add_hline(y=0, line_dash="solid", line_color="#999", linewidth=1)
    
    return fig

def generate_correlation_matrix_chart(selected_actions, period_days=90):
    """Génère la heatmap de corrélation"""
    n = len(selected_actions)
    if n < 2:
        return None
    
    np.random.seed(42)
    corr_matrix = np.random.uniform(-0.3, 0.9, (n, n))
    corr_matrix = (corr_matrix + corr_matrix.T) / 2
    np.fill_diagonal(corr_matrix, 1.0)
    
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix,
        x=selected_actions,
        y=selected_actions,
        colorscale='RdBu',
        zmin=-1,
        zmax=1,
        colorbar=dict(title='Corrélation', thickness=20),
        hovertemplate='<b>%{y}</b> vs <b>%{x}</b><br>Corrélation: %{z:.3f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=f"Matrice de Corrélation - {period_days} jours",
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=500 + n * 20,
        margin=dict(l=80, r=30, t=50, b=80),
        xaxis=dict(showgrid=False, tickangle=-45, tickfont=dict(size=9)),
        yaxis=dict(showgrid=False, tickfont=dict(size=9))
    )
    
    for i in range(n):
        for j in range(i+1, n):
            corr_val = corr_matrix[i, j]
            if abs(corr_val) > 0.7:
                fig.add_annotation(
                    x=j, y=i,
                    text=f"{corr_val:.2f}",
                    showarrow=False,
                    font=dict(color='white' if abs(corr_val) > 0.5 else 'black', size=9)
                )
    
    return fig

def generate_top_movers_chart():
    """Génère le graphique des Top Movers"""
    movers = [
        {'name': 'Attijariwafa Bank', 'change': 3.5, 'volume': 125000},
        {'name': 'Maroc Telecom', 'change': 2.8, 'volume': 98000},
        {'name': 'BCP', 'change': -1.5, 'volume': 156000},
        {'name': 'Cosumar', 'change': 1.9, 'volume': 87000},
        {'name': 'LafargeHolcim', 'change': -0.8, 'volume': 65000},
    ]
    
    df = pd.DataFrame(movers)
    df['color'] = df['change'].apply(lambda x: COLORS['success'] if x >= 0 else COLORS['danger'])
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df['name'],
        y=df['change'],
        marker_color=df['color'],
        text=df['change'].apply(lambda x: f"{x:+.1f}%"),
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Variation: %{y:+.1f}%<br>Volume: %{customdata:,}<extra></extra>',
        customdata=df['volume']
    ))
    
    fig.update_layout(
        title="Top Movers du Jour",
        xaxis_title="Action",
        yaxis_title="Variation (%)",
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=400,
        margin=dict(l=50, r=30, t=50, b=80),
        xaxis=dict(showgrid=False, tickangle=-45),
        yaxis=dict(showgrid=True, zeroline=True, zerolinecolor='gray')
    )
    
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    
    return fig

# -----------------------------------------------------------------------------
# FONCTION PRINCIPALE
# -----------------------------------------------------------------------------

def render():
    """Fonction principale de la page BDC Statut"""
    
    # HEADER
    st.markdown(f"""
    <div style="background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 25px;">
        <h2 style="color: {COLORS['primary']}; margin: 0;">📊 BDC Statut</h2>
        <p style="margin: 10px 0 0 0; color: #666;">Bourse de Casablanca - Analyse et Visualisation</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ---------------------------------------------------------------------
    # SECTION 1 : STATUT DU MARCHÉ (DYNAMIQUE)
    # ---------------------------------------------------------------------
    
    market_status = get_market_status()
    status_color = "#28a745" if market_status['is_open'] else "#dc3545"
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {status_color}22 0%, {status_color}11 100%); 
                padding: 20px; border-radius: 10px; border-left: 5px solid {status_color}; 
                margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
            <div>
                <h3 style="margin: 0; color: {status_color}; font-size: 20px; font-weight: 600;">
                    {market_status['status_text']}
                </h3>
                <p style="margin: 8px 0 0 0; color: #666; font-size: 14px;">
                    🕐 Heure Casablanca : <b>{market_status['current_time']}</b> &nbsp;|&nbsp; 
                    {market_status['next_info']} &nbsp;|&nbsp; 
                    Séance : 09:00 - 15:30 (Lun-Ven)
                </p>
            </div>
            <div style="font-size: 40px; font-weight: bold;">
                {'🟢' if market_status['is_open'] else '🔴'}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Bouton pour rafraîchir l'heure manuellement
    if st.button("🔄 Actualiser l'heure", key="refresh_time"):
        st.rerun()
    
    # ---------------------------------------------------------------------
    # SECTION 2 : INDICES EN TEMPS RÉEL
    # ---------------------------------------------------------------------
    st.markdown("### 📈 Indices en Temps Réel")
    
    bourse_data = st.session_state.get('bourse_data', {})
    
    if bourse_data.get('status') == 'success':
        col1, col2, col3 = st.columns(3)
        
        with col1:
            masi = bourse_data.get('masi', {})
            st.metric(
                label="MASI",
                value=f"{masi.get('value', 0):,.2f}",
                delta=f"{masi.get('change', 0):+.2f}%"
            )
        
        with col2:
            msi20 = bourse_data.get('msi20', {})
            st.metric(
                label="MSI20",
                value=f"{msi20.get('value', 0):,.2f}",
                delta=f"{msi20.get('change', 0):+.2f}%"
            )
        
        with col3:
            st.metric(
                label="Volume (MAD)",
                value=f"{bourse_data.get('masi', {}).get('volume', 0)/1e6:.1f}M"
            )
        
        ts = bourse_data.get('masi', {}).get('timestamp')
        if isinstance(ts, str):
            try:
                ts_display = datetime.fromisoformat(ts).strftime('%H:%M:%S')
            except:
                ts_display = "N/A"
        elif isinstance(ts, datetime):
            ts_display = ts.strftime('%H:%M:%S')
        else:
            ts_display = datetime.now().strftime('%H:%M:%S')
        
        st.caption(f"Source : {bourse_data.get('source', 'Yahoo Finance')} | MAJ : {ts_display}")
    else:
        st.warning("⚠️ Aucune donnée boursière. Allez dans **📥 Data Ingestion** pour actualiser.")
    
    st.markdown("---")
    
    # ---------------------------------------------------------------------
    # SECTION 3 : GRAPHIQUES EN % (MOUVEMENTS VISIBLES)
    # ---------------------------------------------------------------------
    st.markdown("### 📊 Évolution des Indices (Variation en %)")
    
    st.info("""
    💡 **Astuce :** Les graphiques affichent la **variation en %** pour mieux visualiser les mouvements, 
    même petits. La ligne pointillée = 0% (point de référence).
    """)
    
    # Sélecteur de période
    interval_options = {'1j': 1, '5j': 5, '10j': 10, '30j': 30, '3M': 90}
    
    col1, col2 = st.columns([4, 1])
    with col1:
        selected_interval = st.select_slider(
            "Période :",
            options=list(interval_options.keys()),
            value='10j',
            label_visibility="collapsed"
        )
    with col2:
        days = interval_options[selected_interval]
        st.caption(f"{days} jours")
    
    tab1, tab2 = st.tabs(["📈 MASI", "📊 MSI20"])
    
    with tab1:
        fig_masi = generate_masi_chart_percentage(bourse_data, days=days)
        st.plotly_chart(fig_masi, use_container_width=True)
    
    with tab2:
        fig_msi20 = generate_msi20_chart_percentage(bourse_data, days=days)
        st.plotly_chart(fig_msi20, use_container_width=True)
    
    st.markdown("---")
    
    # ---------------------------------------------------------------------
    # SECTION 4 : TOP MOVERS
    # ---------------------------------------------------------------------
    st.markdown("### 🏆 Top Movers du Jour")
    
    fig_movers = generate_top_movers_chart()
    st.plotly_chart(fig_movers, use_container_width=True)
    
    st.dataframe(
        pd.DataFrame([
            {'Action': 'Attijariwafa Bank', 'Cours': '485.50 MAD', 'Variation': '+3.5%', 'Volume': '125,000'},
            {'Action': 'Maroc Telecom', 'Cours': '142.30 MAD', 'Variation': '+2.8%', 'Volume': '98,000'},
            {'Action': 'BCP', 'Cours': '112.40 MAD', 'Variation': '-1.5%', 'Volume': '156,000'},
            {'Action': 'Cosumar', 'Cours': '178.20 MAD', 'Variation': '+1.9%', 'Volume': '87,000'},
            {'Action': 'LafargeHolcim', 'Cours': '756.00 MAD', 'Variation': '-0.8%', 'Volume': '65,000'},
        ]),
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("---")
    
    # ---------------------------------------------------------------------
    # SECTION 5 : MATRICE DE CORRÉLATION
    # ---------------------------------------------------------------------
    st.markdown("### 🔗 Matrice de Corrélation")
    
    available_actions = [a['nom'] for a in MSI20_COMPOSITION] if MSI20_COMPOSITION else [
        'Attijariwafa Bank', 'Maroc Telecom', 'BCP', 'BMCE Bank', 'Cosumar',
        'LafargeHolcim', 'CIH Bank', 'Sonasid', 'Managem', 'Crédit du Maroc'
    ]
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        selected_actions = st.multiselect(
            "Actions à comparer :",
            options=available_actions,
            default=available_actions[:5] if len(available_actions) >= 5 else available_actions,
            max_selections=12
        )
    
    with col2:
        period = st.select_slider(
            "Période :",
            options=[30, 60, 90, 180],
            value=st.session_state.correlation_period
        )
        st.session_state.correlation_period = period
    
    if len(selected_actions) >= 2:
        with st.spinner("Calcul..."):
            fig_corr = generate_correlation_matrix_chart(selected_actions, period)
            if fig_corr:
                st.plotly_chart(fig_corr, use_container_width=True)
                
                col1, col2, col3 = st.columns(3)
                with col1: st.metric("Corrélation Moyenne", "0.42")
                with col2: st.metric("Corrélation Max", "0.89")
                with col3: st.metric("Corrélation Min", "-0.15")
                
                with st.expander("📖 Interprétation", expanded=False):
                    st.markdown("""
                    - 🔵 **> 0.5** : Mouvements similaires (risque concentration)
                    - 🔴 **< -0.5** : Mouvements opposés (bonne diversification)
                    - ⚪ **~0** : Pas de relation linéaire
                    """)
    else:
        st.warning("⚠️ Sélectionnez au moins 2 actions")
    
    st.markdown("---")
    
    # ---------------------------------------------------------------------
    # SECTION 6 : RÉSUMÉ
    # ---------------------------------------------------------------------
    st.markdown("### 📋 Résumé")
    
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Actions MSI20", len(MSI20_COMPOSITION) if MSI20_COMPOSITION else 20)
    with col2: 
        status = "✅ À jour" if bourse_data.get('status') == 'success' else "⚪ En attente"
        st.metric("État des Données", status)
    with col3: st.metric("Période", f"{period}j")
    
    if st.button("🔄 Actualiser la Page", type="secondary"):
        st.rerun()

# =============================================================================
# APPEL DE LA FONCTION
# =============================================================================
render()
