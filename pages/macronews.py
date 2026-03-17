# =============================================================================
# NEWZ - Page Macronews
# Fichier : pages/macronews.py
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
        'warning': '#ffc107',
        'danger': '#dc3545',
        'light': '#f8f9fa'
    }

# -----------------------------------------------------------------------------
# INITIALISATION
# -----------------------------------------------------------------------------

def init_local_session():
    if 'news_data' not in st.session_state:
        st.session_state.news_data = []
    if 'inflation_data' not in st.session_state:
        st.session_state.inflation_data = None

init_local_session()

# -----------------------------------------------------------------------------
# FONCTIONS DE GRAPHIQUES
# -----------------------------------------------------------------------------

def generate_inflation_gauge(current_inflation=-0.8, target_min=2.0, target_max=3.0):
    """
    Génère une jauge d'inflation style BAM
    
    Parameters:
        current_inflation: Taux d'inflation actuel (%)
        target_min: Cible minimale BAM (%)
        target_max: Cible maximale BAM (%)
    """
    
    # Déterminer la couleur selon la position
    if current_inflation < target_min:
        color = COLORS['danger']  # En-dessous de la cible
        status = "En-dessous de la cible"
    elif current_inflation > target_max:
        color = COLORS['danger']  # Au-dessus de la cible
        status = "Au-dessus de la cible"
    else:
        color = COLORS['success']  # Dans la cible
        status = "Dans la cible"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=current_inflation,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={
            'text': f"Taux d'Inflation (Cible BAM: {target_min}-{target_max}%)",
            'font': {'size': 16, 'color': COLORS['primary']}
        },
        delta={
            'reference': target_min,
            'increasing': {'color': COLORS['danger']},
            'decreasing': {'color': COLORS['success']}
        },
        gauge={
            'axis': {
                'range': [-2, 6],
                'tickwidth': 1,
                'tickcolor': "#333",
                'tickfont': {'size': 12}
            },
            'bar': {
                'color': color,
                'thickness': 0.3
            },
            'bgcolor': COLORS['light'],
            'borderwidth': 2,
            'bordercolor': "#333",
            'steps': [
                {'range': [-2, target_min], 'color': '#ffebee'},
                {'range': [target_min, target_max], 'color': '#e8f5e9'},
                {'range': [target_max, 6], 'color': '#ffebee'}
            ],
            'threshold': {
                'line': {'color': COLORS['danger'], 'width': 4},
                'thickness': 0.75,
                'value': target_max
            }
        }
    ))
    
    fig.update_layout(
        height=350,
        margin=dict(l=30, r=30, t=60, b=30),
        paper_bgcolor='white',
        plot_bgcolor='white'
    )
    
    # Ajouter une annotation avec le statut
    fig.add_annotation(
        text=status,
        xref="paper", yref="paper",
        x=0.5, y=-0.15,
        showarrow=False,
        font=dict(size=14, color=color, weight="bold")
    )
    
    return fig

def generate_inflation_history():
    """Génère l'historique de l'inflation au Maroc"""
    
    # Données simulées (à remplacer par données réelles HCP)
    months = pd.date_range(end=datetime.now(), periods=12, freq='M')
    inflation_rates = [1.2, 1.4, 1.1, 0.9, 0.7, 0.5, 0.3, 0.1, -0.2, -0.5, -0.8, -0.8]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=months,
        y=inflation_rates,
        mode='lines+markers',
        name='Inflation',
        line=dict(color=COLORS['primary'], width=3),
        marker=dict(size=8),
        fill='tozeroy',
        fillcolor=f'rgba(0, 86, 150, 0.1)'
    ))
    
    # Lignes de cible BAM
    fig.add_hline(y=2.0, line_dash="dash", line_color=COLORS['success'], 
                  annotation_text="Cible Min (2%)", annotation_position="right")
    fig.add_hline(y=3.0, line_dash="dash", line_color=COLORS['success'],
                  annotation_text="Cible Max (3%)", annotation_position="right")
    
    fig.update_layout(
        title="Historique de l'Inflation (12 mois)",
        xaxis_title="Mois",
        yaxis_title="Inflation (%)",
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=400,
        margin=dict(l=60, r=30, t=50, b=40),
        yaxis=dict(gridcolor='#eee', zeroline=True, zerolinecolor='#999'),
        xaxis=dict(gridcolor='#eee')
    )
    
    return fig

def generate_economic_calendar():
    """Génère le calendrier économique"""
    
    # Données simulées (à remplacer par scraping ou API)
    events = [
        {'date': datetime.now() + timedelta(days=1), 'event': 'Indice des Prix à la Consommation', 'country': 'Maroc', 'impact': 'High', 'forecast': '-0.5%', 'previous': '-0.8%'},
        {'date': datetime.now() + timedelta(days=3), 'event': 'Taux de Chômage', 'country': 'Maroc', 'impact': 'High', 'forecast': '12.5%', 'previous': '12.9%'},
        {'date': datetime.now() + timedelta(days=5), 'event': 'Décision Taux Directeur BAM', 'country': 'Maroc', 'impact': 'High', 'forecast': '3.00%', 'previous': '3.00%'},
        {'date': datetime.now() + timedelta(days=7), 'event': 'Balance Commerciale', 'country': 'Maroc', 'impact': 'Medium', 'forecast': '-15M MAD', 'previous': '-18M MAD'},
        {'date': datetime.now() + timedelta(days=10), 'event': 'PIB Trimestriel', 'country': 'Maroc', 'impact': 'High', 'forecast': '3.2%', 'previous': '3.0%'},
        {'date': datetime.now() + timedelta(days=12), 'event': 'Réserves de Change', 'country': 'Maroc', 'impact': 'Medium', 'forecast': '320B MAD', 'previous': '315B MAD'},
        {'date': datetime.now() + timedelta(days=15), 'event': 'Production Industrielle', 'country': 'Maroc', 'impact': 'Medium', 'forecast': '2.5%', 'previous': '2.1%'},
    ]
    
    df = pd.DataFrame(events)
    
    # Colorer par impact
    df['impact_color'] = df['impact'].apply(lambda x: COLORS['danger'] if x == 'High' else COLORS['warning'])
    
    return df

# -----------------------------------------------------------------------------
# FONCTION PRINCIPALE
# -----------------------------------------------------------------------------

def render():
    """Fonction principale"""
    
    # HEADER
    st.markdown(f"""
    <div style="background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 25px;">
        <h2 style="color: {COLORS['primary']}; margin: 0;">📰 Macronews</h2>
        <p style="margin: 10px 0 0 0; color: #666;">Actualités Économiques et Indicateurs Macro</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ---------------------------------------------------------------------
    # SECTION 1 : ACTUALITÉS
    # ---------------------------------------------------------------------
    st.markdown("### 📰 Dernières Actualités")
    
    news_data = st.session_state.get('news_data', [])
    
    if news_
        # Afficher les 10 dernières news
        for i, news in enumerate(news_data[:10]):
            with st.expander(f"📄 {news['title']}", expanded=(i < 3)):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"**Source :** {news.get('source', 'N/A')}")
                    st.write(f"**Catégorie :** {news.get('category', 'Général')}")
                    if 'timestamp' in news:
                        if isinstance(news['timestamp'], str):
                            ts_display = news['timestamp'][:16].replace('T', ' ')
                        else:
                            ts_display = news['timestamp'].strftime('%d/%m/%Y %H:%M')
                        st.write(f"**Date :** {ts_display}")
                    st.markdown("---")
                    st.write(news.get('summary', ''))
                with col2:
                    if 'url' in news and news['url']:
                        st.markdown(f"[🔗 Lire →]({news['url']})")
    else:
        st.warning("⚠️ Aucune actualité disponible. Allez dans **📥 Data Ingestion** pour collecter les news.")
        
        # News de secours
        st.info("**📋 Actualités Récentes (Démo)**")
        demo_news = [
            {'title': 'Bank Al-Maghrib maintient son taux directeur à 3%', 'summary': 'Le conseil de Bank Al-Maghrib a décidé de maintenir son taux directeur inchangé...', 'source': 'Ilboursa', 'category': 'Monétaire'},
            {'title': 'L\'inflation au Maroc ralentit à -0,8%', 'summary': 'Selon le HCP, l\'inflation est devenue négative...', 'source': 'HCP', 'category': 'Économie'},
            {'title': 'Le MASI franchit la barre des 12 500 points', 'summary': 'La bourse de Casablanca continue sa progression...', 'source': 'Bourse de Casa', 'category': 'Marché'},
        ]
        for news in demo_news:
            with st.expander(f"📄 {news['title']}"):
                st.write(f"**Source :** {news['source']} | **Catégorie :** {news['category']}")
                st.write(news['summary'])
    
    st.markdown("---")
    
    # ---------------------------------------------------------------------
    # SECTION 2 : INFLATION
    # ---------------------------------------------------------------------
    st.markdown("### 💹 Inflation & Prix")
    
    # Jauge d'inflation
    current_inflation = -0.8  # À remplacer par donnée réelle HCP
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig_gauge = generate_inflation_gauge(current_inflation)
        st.plotly_chart(fig_gauge, use_container_width=True)
    
    with col2:
        st.markdown("#### 📊 Indicateurs Clés")
        
        st.metric("Inflation Actuelle", f"{current_inflation:.1f}%", "Hors cible")
        st.metric("Cible BAM", "2-3%", "✓")
        st.metric("Dernière MAJ", datetime.now().strftime('%d/%m/%Y'))
        
        st.info("""
        **💡 Interprétation :**
        
        Une inflation négative indique :
        - Faible demande intérieure
        - Baisse des prix des produits alimentaires
        - Espace pour politique monétaire accommodante
        """)
    
    # Historique
    fig_history = generate_inflation_history()
    st.plotly_chart(fig_history, use_container_width=True)
    
    st.markdown("---")
    
    # ---------------------------------------------------------------------
    # SECTION 3 : CALENDRIER ÉCONOMIQUE
    # ---------------------------------------------------------------------
    st.markdown("### 📅 Calendrier Économique")
    
    st.info("📋 Événements économiques à venir impactant le marché marocain")
    
    df_calendar = generate_economic_calendar()
    
    # Afficher le calendrier
    st.dataframe(
        df_calendar[['date', 'event', 'country', 'impact', 'forecast', 'previous']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "date": st.column_config.DatetimeColumn("Date", format="DD/MM/YYYY"),
            "event": st.column_config.TextColumn("Événement", width="large"),
            "country": st.column_config.TextColumn("Pays", width="small"),
            "impact": st.column_config.TextColumn("Impact", width="small"),
            "forecast": st.column_config.TextColumn("Prévision", width="small"),
            "previous": st.column_config.TextColumn("Précédent", width="small")
        }
    )
    
    # Légende impact
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"🔴 **Impact Élevé** : Peut mover le marché")
    with col2:
        st.markdown(f"🟡 **Impact Moyen** : Attention requise")
    with col3:
        st.markdown(f"🟢 **Impact Faible** : Peu d'impact")
    
    st.markdown("---")
    
    # ---------------------------------------------------------------------
    # SECTION 4 : INDICATEURS MACRO
    # ---------------------------------------------------------------------
    st.markdown("### 📊 Indicateurs Macroéconomiques")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="PIB (Croissance)",
            value="3.2%",
            delta="+0.2%",
            delta_color="normal"
        )
    
    with col2:
        st.metric(
            label="Chômage",
            value="12.9%",
            delta="-0.4%",
            delta_color="inverse"
        )
    
    with col3:
        st.metric(
            label="Réserves de Change",
            value="315 Mds MAD",
            delta="+5 Mds",
            delta_color="normal"
        )
    
    with col4:
        st.metric(
            label="Déficit Commercial",
            value="-18 Mds MAD",
            delta="-3 Mds",
            delta_color="normal"
        )
    
    st.caption("Sources : HCP, Bank Al-Maghrib, Ministère de l'Économie")
    
    st.markdown("---")
    
    # ---------------------------------------------------------------------
    # SECTION 5 : RÉSUMÉ
    # ---------------------------------------------------------------------
    st.markdown("### 📋 Résumé")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Actualités", len(news_data) if news_data else 0)
    with col2:
        st.metric("Inflation", f"{current_inflation:.1f}%", "Hors cible")
    with col3:
        st.metric("Prochains Events", len(df_calendar))
    
    # Bouton actualisation
    if st.button("🔄 Actualiser", type="secondary"):
        st.rerun()

# =============================================================================
# APPEL
# =============================================================================
render()
