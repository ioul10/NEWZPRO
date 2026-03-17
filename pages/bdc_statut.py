# =============================================================================
# NEWZ - Page BDC Statut
# Fichier : pages/bdc_statut.py
# =============================================================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
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
# FONCTIONS UTILITAIRES
# -----------------------------------------------------------------------------

def get_market_status():
    """
    Récupère le statut actuel du marché (ouvert/fermé)
    Returns: dict avec status, message, next_open
    """
    import pytz
    
    now = datetime.now(pytz.timezone('Africa/Casablanca'))
    current_time = now.time()
    current_day = now.strftime('%A')
    
    # Horaires de la bourse
    market_open = datetime.strptime('09:00', '%H:%M').time()
    market_close = datetime.strptime('15:30', '%H:%M').time()
    
    # Jours ouvrés
    working_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    
    is_open = False
    status_text = ""
    next_open = None
    
    if current_day in working_days:
        if market_open <= current_time <= market_close:
            is_open = True
            status_text = "🟢 Marché Ouvert"
        elif current_time < market_open:
            status_text = f"🔴 Marché Fermé (Ouvre à {market_open.strftime('%H:%M')})"
            next_open = now.replace(hour=market_open.hour, minute=market_open.minute)
        else:
            status_text = f"🔴 Marché Fermé (Fermé à {market_close.strftime('%H:%M')})"
            next_open = (now + timedelta(days=1)).replace(hour=market_open.hour, minute=market_open.minute)
    else:
        status_text = "🔴 Marché Fermé (Week-end)"
        # Trouver le prochain lundi
        days_until_monday = (7 - now.weekday()) % 7 or 7
        next_open = (now + timedelta(days=days_until_monday)).replace(hour=market_open.hour, minute=market_open.minute)
    
    return {
        'is_open': is_open,
        'status_text': status_text,
        'current_time': now.strftime('%H:%M:%S'),
        'next_open': next_open
    }



# -----------------------------------------------------------------------------
# INITIALISATION LOCALE
# -----------------------------------------------------------------------------

def init_local_session():
    """Initialise les variables spécifiques à cette page"""
    if 'bourse_data' not in st.session_state:
        st.session_state.bourse_data = {}
    if 'actions_data' not in st.session_state:
        st.session_state.actions_data = None
    if 'correlation_period' not in st.session_state:
        st.session_state.correlation_period = 90

init_local_session()

def generate_masi_chart(bourse_data=None, days=10):
    """Génère le graphique d'évolution du MASI"""
    # Données simulées pour l'exemple (à remplacer par vraies données)
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    base_value = 12450 if not bourse_data else bourse_data.get('masi', {}).get('value', 12450)
    
    # Génération de données réalistes avec plus de volatilité pour les courtes périodes
    np.random.seed(42)
    returns = np.random.normal(0.0003, 0.01, size=days)
    values = base_value * (1 + returns).cumprod()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=values,
        mode='lines',
        name='MASI',
        line=dict(color=COLORS['primary'], width=2),
        fill='tozeroy',
        fillcolor=f'rgba(0, 86, 150, 0.1)'
    ))
    
    fig.update_layout(
        title=f"Évolution du MASI ({days} jours)",
        xaxis_title="Date",
        yaxis_title="Valeur",
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=400,
        margin=dict(l=50, r=30, t=50, b=30),
        xaxis=dict(
            rangeslider=dict(visible=True),  # Slider pour zoomer
            type="date"
        )
    )
    
    return fig

def generate_msi20_chart(bourse_data=None, days=10):
    """Génère le graphique d'évolution du MSI20"""
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    base_value = 1580 if not bourse_data else bourse_data.get('msi20', {}).get('value', 1580)
    
    np.random.seed(43)
    returns = np.random.normal(0.0004, 0.012, size=days)
    values = base_value * (1 + returns).cumprod()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=values,
        mode='lines',
        name='MSI20',
        line=dict(color=COLORS['accent'], width=2),
        fill='tozeroy',
        fillcolor=f'rgba(0, 168, 232, 0.1)'
    ))
    
    fig.update_layout(
        title=f"Évolution du MSI20 ({days} jours)",
        xaxis_title="Date",
        yaxis_title="Valeur",
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=400,
        margin=dict(l=50, r=30, t=50, b=30),
        xaxis=dict(
            rangeslider=dict(visible=True),  # Slider pour zoomer
            type="date"
        )
    )
    
    return fig

def generate_correlation_matrix_chart(selected_actions, period_days=90):
    """
    Génère la heatmap de corrélation pour les actions sélectionnées
    
    Parameters:
        selected_actions: Liste des noms d'actions
        period_days: Période en jours pour le calcul
    """
    # Données simulées pour l'exemple
    n = len(selected_actions)
    if n < 2:
        return None
    
    # Générer une matrice de corrélation réaliste
    np.random.seed(42)
    corr_matrix = np.random.uniform(-0.3, 0.9, (n, n))
    corr_matrix = (corr_matrix + corr_matrix.T) / 2  # Symétrique
    np.fill_diagonal(corr_matrix, 1.0)
    
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix,
        x=selected_actions,
        y=selected_actions,
        colorscale='RdBu',
        zmin=-1,
        zmax=1,
        colorbar=dict(title='Corrélation', thickness=20),
        hoverongaps=False,
        hovertemplate='<b>%{y}</b> vs <b>%{x}</b><br>Corrélation: %{z:.3f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=f"Matrice de Corrélation - Période: {period_days} jours",
        xaxis_title="Actions",
        yaxis_title="Actions",
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=500 + n * 20,
        margin=dict(l=80, r=30, t=50, b=80),
        xaxis=dict(showgrid=False, tickangle=-45, tickfont=dict(size=9)),
        yaxis=dict(showgrid=False, tickfont=dict(size=9))
    )
    
    # Ajouter annotations pour fortes corrélations
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
    # Données simulées
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
    
    # Ligne zéro
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
    # SECTION 1 : INDICES EN TEMPS RÉEL
    # ---------------------------------------------------------------------
        # Statut du marché
    market_status = get_market_status()
    
    # Badge de statut
    status_color = "#28a745" if market_status['is_open'] else "#dc3545"
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {status_color}22 0%, {status_color}11 100%); 
                padding: 20px; border-radius: 10px; border-left: 5px solid {status_color}; 
                margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h3 style="margin: 0; color: {status_color}; font-size: 20px;">
                    {market_status['status_text']}
                </h3>
                <p style="margin: 5px 0 0 0; color: #666; font-size: 14px;">
                    🕐 Heure locale : <b>{market_status['current_time']}</b> | 
                    Horaires : 09:00 - 15:30 (Lun-Ven)
                </p>
            </div>
            <div style="font-size: 48px;">
                {'🟢' if market_status['is_open'] else '🔴'}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
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
        st.warning("⚠️ Aucune donnée boursière disponible. Allez dans **📥 Data Ingestion** pour actualiser.")
    
    st.markdown("---")
    
    # ---------------------------------------------------------------------
    # SECTION 2 : GRAPHIQUES DES INDICES (AVEC SÉLECTEUR D'INTERVALLE)
    # ---------------------------------------------------------------------
    st.markdown("### 📊 Évolution des Indices")
    
    # Sélecteur d'intervalle
    interval_options = {
        '1 jour': 1,
        '5 jours': 5,
        '10 jours': 10,
        '30 jours': 30,
        '3 mois': 90
    }
    
    selected_interval = st.select_slider(
        "🔍 Intervalle d'affichage :",
        options=list(interval_options.keys()),
        value='10 jours',
        help="Sélectionnez la période à afficher sur les graphiques"
    )
    
    days = interval_options[selected_interval]
    
    tab1, tab2 = st.tabs(["📈 MASI", "📊 MSI20"])
    
    with tab1:
        fig_masi = generate_masi_chart(bourse_data, days=days)
        st.plotly_chart(fig_masi, use_container_width=True)
    
    with tab2:
        fig_msi20 = generate_msi20_chart(bourse_data, days=days)
        st.plotly_chart(fig_msi20, use_container_width=True)
    
    st.markdown("---")
    
    # ---------------------------------------------------------------------
    # SECTION 3 : TOP MOVERS
    # ---------------------------------------------------------------------
    st.markdown("### 🏆 Top Movers du Jour")
    
    fig_movers = generate_top_movers_chart()
    st.plotly_chart(fig_movers, use_container_width=True)
    
    # Tableau des top movers
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
    # SECTION 4 : MATRICE DE CORRÉLATION
    # ---------------------------------------------------------------------
    st.markdown("### 🔗 Matrice de Corrélation")
    
    st.info("""
    **📋 Sélectionnez les actions à analyser**
    
    La matrice montre les corrélations de Pearson entre les rendements quotidiens.
    - 🔴 Corrélation négative : mouvements opposés
    - 🔵 Corrélation positive : mouvements similaires
    - ⚪ Proche de 0 : pas de relation linéaire
    """)
    
    # Sélection des actions
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
            value=st.session_state.correlation_period,
            help="Période pour le calcul des corrélations"
        )
        st.session_state.correlation_period = period
    
    # Génération de la heatmap
    if len(selected_actions) >= 2:
        with st.spinner("Calcul des corrélations..."):
            fig_corr = generate_correlation_matrix_chart(selected_actions, period)
            
            if fig_corr:
                st.plotly_chart(fig_corr, use_container_width=True)
                
                # Statistiques
                col1, col2, col3 = st.columns(3)
                
                # Simuler des stats pour l'exemple
                avg_corr = 0.42
                max_corr = 0.89
                min_corr = -0.15
                
                with col1:
                    st.metric("Corrélation Moyenne", f"{avg_corr:.3f}")
                with col2:
                    st.metric("Corrélation Max", f"{max_corr:.3f}")
                with col3:
                    st.metric("Corrélation Min", f"{min_corr:.3f}")
                
                # Interprétation
                with st.expander("📖 Interprétation des corrélations", expanded=False):
                    st.markdown("""
                    **🔵 Corrélation Positive (> 0.5) :**
                    - Les actions évoluent dans le même sens
                    - Risque de concentration élevé
                    - Exemple: Deux banques du même secteur
                    
                    **🔴 Corrélation Négative (< -0.5) :**
                    - Les actions évoluent en sens opposé
                    - Bonne pour la diversification du portefeuille
                    
                    **⚪ Corrélation Proche de 0 :**
                    - Pas de relation linéaire significative
                    - Les mouvements sont indépendants
                    """)
            else:
                st.warning("⚠️ Impossible de générer la matrice")
    else:
        st.warning("⚠️ Sélectionnez au moins 2 actions pour calculer les corrélations")
    
    st.markdown("---")
    
    # ---------------------------------------------------------------------
    # SECTION 5 : RÉSUMÉ
    # ---------------------------------------------------------------------
    st.markdown("### 📋 Résumé")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Actions MSI20", len(MSI20_COMPOSITION) if MSI20_COMPOSITION else 20)
    
    with col2:
        status = "✅ Données à jour" if bourse_data.get('status') == 'success' else "⚪ En attente"
        st.metric("État des Données", status)
    
    with col3:
        st.metric("Période Corrélation", f"{period} jours")
    
    # Bouton d'actualisation
    if st.button("🔄 Actualiser les Graphiques", type="secondary"):
        st.rerun()

# =============================================================================
# APPEL DE LA FONCTION RENDER
# =============================================================================
render()
