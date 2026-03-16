# =============================================================================
# NEWZ - Page BDC Statut (Bourse de Casa)
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
def generate_masi_chart(data_bourse):
    """Génère le graphique MASI"""
    
    # Si on a des données réelles, les utiliser
    if data_bourse and 'masi' in data_bourse:
        # Créer un historique simulé basé sur la valeur actuelle
        current_value = data_bourse['masi']['value']
        dates = pd.date_range(end=datetime.now(), periods=90, freq='B')
        np.random.seed(42)
        returns = np.random.normal(0.0005, 0.012, 90)
        values = current_value / np.prod(1 + returns[-10:]) * np.cumprod(1 + returns)
    else:
        # Données par défaut
        dates = pd.date_range(end=datetime.now(), periods=90, freq='B')
        values = 12000 + np.cumsum(np.random.normal(10, 50, 90))
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=values,
        mode='lines',
        line=dict(color=COLORS['primary'], width=2.5),
        fill='tozeroy',
        fillcolor=f'rgba(0, 86, 150, 0.1)',
        name='MASI'
    ))
    
    fig.update_layout(
        height=350,
        margin=dict(l=50, r=30, t=30, b=50),
        xaxis_title='Date',
        yaxis_title='Indice MASI',
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=False,
        xaxis=dict(showgrid=True, gridcolor='#f0f0f0'),
        yaxis=dict(showgrid=True, gridcolor='#f0f0f0')
    )
    
    return fig

def generate_msi20_chart(data_bourse):
    """Génère le graphique MSI20"""
    
    if data_bourse and 'msi20' in data_bourse:
        current_value = data_bourse['msi20']['value']
        dates = pd.date_range(end=datetime.now(), periods=90, freq='B')
        np.random.seed(43)
        returns = np.random.normal(0.0008, 0.015, 90)
        values = current_value / np.prod(1 + returns[-10:]) * np.cumprod(1 + returns)
    else:
        dates = pd.date_range(end=datetime.now(), periods=90, freq='B')
        values = 1500 + np.cumsum(np.random.normal(5, 20, 90))
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=values,
        mode='lines',
        line=dict(color=COLORS['accent'], width=2.5),
        fill='tozeroy',
        fillcolor=f'rgba(0, 168, 232, 0.1)',
        name='MSI20'
    ))
    
    fig.update_layout(
        height=350,
        margin=dict(l=50, r=30, t=30, b=50),
        xaxis_title='Date',
        yaxis_title='Indice MSI20',
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=False,
        xaxis=dict(showgrid=True, gridcolor='#f0f0f0'),
        yaxis=dict(showgrid=True, gridcolor='#f0f0f0')
    )
    
    return fig

def generate_volume_chart():
    """Génère le graphique des volumes"""
    dates = pd.date_range(end=datetime.now(), periods=30, freq='B')
    volumes = np.random.randint(30000000, 70000000, 30)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=dates,
        y=volumes,
        marker_color=COLORS['primary'],
        name='Volume'
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=50, r=30, t=30, b=50),
        xaxis_title='Date',
        yaxis_title='Volume (MAD)',
        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=False,
        xaxis=dict(showgrid=True, gridcolor='#f0f0f0'),
        yaxis=dict(showgrid=True, gridcolor='#f0f0f0')
    )
    
    return fig

def generate_correlation_matrix():
    """Génère une matrice de corrélation simulée"""
    # Simuler 10 valeurs du MSI20
    np.random.seed(42)
    n_stocks = 10
    correlations = np.random.uniform(-0.3, 0.9, (n_stocks, n_stocks))
    correlations = (correlations + correlations.T) / 2
    np.fill_diagonal(correlations, 1.0)
    
    stocks = [f'Valeur {i+1}' for i in range(n_stocks)]
    
    fig = go.Figure(data=go.Heatmap(
        z=correlations,
        x=stocks,
        y=stocks,
        colorscale='RdBu',
        zmin=-1,
        zmax=1,
        colorbar=dict(title='Corrélation')
    ))
    
    fig.update_layout(
        height=400,
        margin=dict(l=50, r=30, t=30, b=50),
        xaxis_title='Actions',
        yaxis_title='Actions',
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig

# -----------------------------------------------------------------------------
# 2. DONNÉES SIMULÉES POUR LES TOP MOVERS
# -----------------------------------------------------------------------------
def get_top_movers():
    """Retourne les top gainers et losers"""
    gainers = [
        {'name': 'Attijariwafa Bank', 'price': 485.50, 'change': 3.5, 'volume': 125000},
        {'name': 'Maroc Telecom', 'price': 142.30, 'change': 2.8, 'volume': 98000},
        {'name': 'LafargeHolcim', 'price': 756.00, 'change': 2.1, 'volume': 45000},
        {'name': 'Cosumar', 'price': 178.20, 'change': 1.9, 'volume': 67000},
        {'name': 'BMCE Bank', 'price': 245.80, 'change': 1.6, 'volume': 89000}
    ]
    
    losers = [
        {'name': 'BCP', 'price': 112.40, 'change': -1.5, 'volume': 156000},
        {'name': 'Sonasid', 'price': 895.00, 'change': -1.2, 'volume': 23000},
        {'name': 'Managem', 'price': 1245.00, 'change': -0.9, 'volume': 34000},
        {'name': 'CIH Bank', 'price': 234.50, 'change': -0.7, 'volume': 78000},
        {'name': 'Crédit du Maroc', 'price': 456.00, 'change': -0.5, 'volume': 45000}
    ]
    
    return gainers, losers

# -----------------------------------------------------------------------------
# 3. PAGE PRINCIPALE
# -----------------------------------------------------------------------------
def render():
    """Fonction principale de la page BDC Statut"""
    
    st.markdown(f"""
    <div style="background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 25px;">
        <h2 style="color: {COLORS['primary']}; margin: 0;">📊 BDC Statut</h2>
        <p style="margin: 10px 0 0 0; color: #666;">Bourse de Casablanca - Visualisation et Statistiques</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Récupérer les données de la session (CORRECTION ICI)
    bourse_data = st.session_state.get('bourse_data', {})
    
    # Vérifier si des données sont disponibles
    if not bourse_data or bourse_data.get('status') != 'success':
        st.warning("""
        ⚠️ **Aucune donnée boursière disponible**
        
        Pour afficher les données :
        1. Allez dans la page **📥 Data Ingestion**
        2. Cliquez sur **"🔄 Lancer le scraping"** dans la section Bourse de Casablanca
        3. Revenez sur cette page
        """)
        
        if st.button("📥 Aller à Data Ingestion"):
            st.session_state.current_page = "data_ingestion"
            st.rerun()
        
        # Afficher quand même des données simulées pour le test
        st.info("💡 Affichage de données de démonstration...")
        bourse_data = {
            'masi': {'value': 12450.50, 'change': 0.85, 'volume': 45000000},
            'msi20': {'value': 1580.30, 'change': 1.20, 'volume': 38000000},
            'status': 'demo'
        }

    
    # ---------------------------------------------------------------------
    # SECTION 1 : KPIs PRINCIPAUX
    # ---------------------------------------------------------------------
    st.markdown("### 📈 Indices Principaux")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        masi_value = bourse_data.get('masi', {}).get('value', 12450.50)
        masi_change = bourse_data.get('masi', {}).get('change', 0.85)
        st.metric(
            label="MASI",
            value=f"{masi_value:,.2f}",
            delta=f"{masi_change:+.2f}%"
        )
    
    with col2:
        msi20_value = bourse_data.get('msi20', {}).get('value', 1580.30)
        msi20_change = bourse_data.get('msi20', {}).get('change', 1.20)
        st.metric(
            label="MSI20",
            value=f"{msi20_value:,.2f}",
            delta=f"{msi20_change:+.2f}%"
        )
    
    with col3:
        volume = bourse_data.get('masi', {}).get('volume', 45000000)
        st.metric(
            label="Volume (MAD)",
            value=f"{volume/1e6:.1f}M"
        )
    
    with col4:
        nb_transactions = np.random.randint(5000, 15000)
        st.metric(
            label="Transactions",
            value=f"{nb_transactions:,}"
        )
    
    st.markdown("---")
    
    # ---------------------------------------------------------------------
    # SECTION 2 : GRAPHIQUES DES INDICES
    # ---------------------------------------------------------------------
    st.markdown("### 📊 Évolution des Indices")
    
    # Onglets pour MASI et MSI20
    tab1, tab2 = st.tabs(["📈 MASI", "📈 MSI20"])
    
    with tab1:
        fig_masi = generate_masi_chart(bourse_data)
        st.plotly_chart(fig_masi, use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Plus haut (90j)", f"{masi_value * 1.05:,.2f}")
        with col2:
            st.metric("Plus bas (90j)", f"{masi_value * 0.95:,.2f}")
        with col3:
            st.metric("Volatilité (30j)", "1.2%")
    
    with tab2:
        fig_msi20 = generate_msi20_chart(bourse_data)
        st.plotly_chart(fig_msi20, use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Plus haut (90j)", f"{msi20_value * 1.06:,.2f}")
        with col2:
            st.metric("Plus bas (90j)", f"{msi20_value * 0.94:,.2f}")
        with col3:
            st.metric("Volatilité (30j)", "1.5%")
    
    st.markdown("---")
    
    # ---------------------------------------------------------------------
    # SECTION 3 : TOP MOVERS
    # ---------------------------------------------------------------------
    st.markdown("### 🏆 Top Movers de la Séance")
    
    gainers, losers = get_top_movers()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div style="background: #e8f5e9; padding: 20px; border-radius: 10px; border-left: 5px solid {COLORS['success']};">
            <h3 style="color: {COLORS['success']}; margin: 0 0 15px 0;">🟢 Top Gainers</h3>
        </div>
        """, unsafe_allow_html=True)
        
        for gainer in gainers:
            st.markdown(f"""
            <div style="background: white; padding: 12px; margin: 8px 0; border-radius: 8px; display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <b style="font-size: 14px;">{gainer['name']}</b>
                    <br><small style="color: #666;">Vol: {gainer['volume']:,}</small>
                </div>
                <div style="text-align: right;">
                    <div style="color: {COLORS['success']}; font-weight: bold; font-size: 16px;">{gainer['change']:+.1f}%</div>
                    <div style="color: #666; font-size: 12px;">{gainer['price']:.2f} MAD</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: #ffebee; padding: 20px; border-radius: 10px; border-left: 5px solid {COLORS['danger']};">
            <h3 style="color: {COLORS['danger']}; margin: 0 0 15px 0;">🔴 Top Losers</h3>
        </div>
        """, unsafe_allow_html=True)
        
        for loser in losers:
            st.markdown(f"""
            <div style="background: white; padding: 12px; margin: 8px 0; border-radius: 8px; display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <b style="font-size: 14px;">{loser['name']}</b>
                    <br><small style="color: #666;">Vol: {loser['volume']:,}</small>
                </div>
                <div style="text-align: right;">
                    <div style="color: {COLORS['danger']}; font-weight: bold; font-size: 16px;">{loser['change']:+.1f}%</div>
                    <div style="color: #666; font-size: 12px;">{loser['price']:.2f} MAD</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ---------------------------------------------------------------------
    # SECTION 4 : STATISTIQUES AVANCÉES
    # ---------------------------------------------------------------------
    st.markdown("### 📊 Statistiques de Marché")
    
    tab_stats1, tab_stats2 = st.tabs(["📈 Volumes", "🔗 Corrélations"])
    
    with tab_stats1:
        fig_volume = generate_volume_chart()
        st.plotly_chart(fig_volume, use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Volume Moyen (30j)", "52.3M MAD")
        with col2:
            st.metric("Pic de Volume", "78.5M MAD")
        with col3:
            st.metric("Liquidité", "Élevée")
    
    with tab_stats2:
        st.info("💡 Matrice de corrélation entre les principales valeurs du MSI20")
        fig_corr = generate_correlation_matrix()
        st.plotly_chart(fig_corr, use_container_width=True)
        
        st.markdown("""
        **Interprétation :**
        - 🔴 Corrélation forte (> 0.7) : Les valeurs évoluent ensemble
        - 🟡 Corrélation modérée (0.3-0.7) : Relation moyenne
        - 🟢 Corrélation faible (< 0.3) : Indépendance relative
        """)
    
    st.markdown("---")
    
    # ---------------------------------------------------------------------
    # SECTION 5 : TABLEAU DE DONNÉES DÉTAILLÉES
    # ---------------------------------------------------------------------
    st.markdown("### 📋 Données Détaillées")
    
    # Créer un DataFrame avec les données principales
    df_details = pd.DataFrame({
        'Indice': ['MASI', 'MSI20'],
        'Valeur': [masi_value, msi20_value],
        'Variation (%)': [masi_change, msi20_change],
        'Volume (MAD)': [f"{volume/1e6:.2f}M", f"{volume*0.85/1e6:.2f}M"],
        'Date MAJ': [datetime.now().strftime('%d/%m/%Y %H:%M')] * 2
    })
    
    st.dataframe(
        df_details,
        use_container_width=True,
        hide_index=True
    )
    
    # Bouton d'export
    col1, col2 = st.columns(2)
    
    with col1:
        csv = df_details.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Télécharger en CSV",
            data=csv,
            file_name=f"bdc_statut_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        if st.button("🔄 Actualiser les données", use_container_width=True):
            st.session_state.bourse_data = {}
            st.success("Données réinitialisées. Retournez à Data Ingestion pour recharger.")
            st.rerun()
