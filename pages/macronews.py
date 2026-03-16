# =============================================================================
# NEWZ - Page Macronews (Actualités & Inflation)
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
def generate_inflation_gauge(value=-0.8, target_min=2.0, target_max=3.0):
    """Génère la jauge d'inflation"""
    
    # Déterminer la couleur selon la position
    if target_min - 0.5 <= value <= target_max + 0.5:
        color = COLORS['success']  # Vert - dans la cible
        status = "Dans la cible"
        status_color = "#28a745"
    elif value < target_min:
        color = COLORS['warning']  # Jaune - en dessous
        status = "En-dessous"
        status_color = "#ffc107"
    else:
        color = COLORS['danger']  # Rouge - au-dessus
        status = "Au-dessus"
        status_color = "#dc3545"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={
            'text': f"Inflation (IPC)<br><span style='font-size: 12px; color: {status_color}'>{status}</span>",
            'font': {'size': 16, 'color': COLORS['primary']}
        },
        number={'font': {'size': 32, 'color': color}},
        delta={'reference': target_min, 'increasing': {'color': COLORS['danger']}, 'decreasing': {'color': COLORS['success']}},
        gauge={
            'axis': {'range': [-2, 8], 'tickwidth': 2, 'tickcolor': "#333"},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#333",
            'steps': [
                {'range': [-2, 2], 'color': '#e8f5e9'},
                {'range': [2, 3], 'color': '#c8e6c9'},
                {'range': [3, 8], 'color': '#ffebee'}
            ],
            'threshold': {
                'line': {'color': COLORS['danger'], 'width': 4},
                'thickness': 0.75,
                'value': target_max + 0.5
            }
        }
    ))
    
    fig.update_layout(height=350, margin=dict(l=30, r=30, t=60, b=30))
    return fig

def generate_inflation_history():
    """Génère l'historique de l'inflation"""
    
    # Données simulées (à remplacer par des données réelles)
    months = pd.date_range(end=datetime.now(), periods=12, freq='M')
    inflation_values = [-0.8, -0.5, 0.2, 0.8, 1.2, 1.5, 1.8, 2.1, 2.3, 1.9, 1.2, -0.8]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=months,
        y=inflation_values,
        mode='lines+markers',
        line=dict(color=COLORS['primary'], width=3),
        marker=dict(size=8, color=COLORS['primary']),
        name='Inflation IPC',
        fill='tozeroy',
        fillcolor=f'rgba(0, 86, 150, 0.1)'
    ))
    
    # Ligne cible BAM
    fig.add_hline(
        y=2.5,
        line_dash="dash",
        line_color=COLORS['success'],
        annotation_text="Cible BAM (2-3%)",
        annotation_position="right"
    )
    
    # Zone cible
    fig.add_hrect(
        y0=2.0, y1=3.0,
        fillcolor="rgba(40, 167, 69, 0.1)",
        line_width=0,
        annotation_text="Zone cible",
        annotation_position="right"
    )
    
    fig.update_layout(
        height=350,
        margin=dict(l=60, r=40, t=40, b=60),
        xaxis_title='Mois',
        yaxis_title='Inflation (%)',
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(showgrid=True, gridcolor='#f0f0f0'),
        yaxis=dict(showgrid=True, gridcolor='#f0f0f0')
    )
    
    return fig

# -----------------------------------------------------------------------------
# 2. CALENDRIER ÉCONOMIQUE
# -----------------------------------------------------------------------------
def get_economic_calendar():
    """Retourne le calendrier économique"""
    
    # Données simulées
    events = [
        {
            'date': (datetime.now() + timedelta(days=1)).strftime('%d/%m/%Y'),
            'time': '10:00',
            'event': 'Inflation (Glissement Annuel)',
            'country': 'Maroc',
            'impact': '🔴 Haute',
            'forecast': '-0.5%',
            'previous': '-0.8%'
        },
        {
            'date': (datetime.now() + timedelta(days=3)).strftime('%d/%m/%Y'),
            'time': '14:30',
            'event': 'Décision Taux Directeur BAM',
            'country': 'Maroc',
            'impact': '🔴 Haute',
            'forecast': '3.00%',
            'previous': '3.00%'
        },
        {
            'date': (datetime.now() + timedelta(days=5)).strftime('%d/%m/%Y'),
            'time': '09:00',
            'event': 'PIB Trimestriel',
            'country': 'Maroc',
            'impact': '🟡 Moyenne',
            'forecast': '2.8%',
            'previous': '2.5%'
        },
        {
            'date': (datetime.now() + timedelta(days=7)).strftime('%d/%m/%Y'),
            'time': '11:00',
            'event': 'Balance Commerciale',
            'country': 'Maroc',
            'impact': '🟡 Moyenne',
            'forecast': '-45 MMD',
            'previous': '-48 MMD'
        },
        {
            'date': (datetime.now() + timedelta(days=10)).strftime('%d/%m/%Y'),
            'time': '10:00',
            'event': 'Indice de Production Industrielle',
            'country': 'Maroc',
            'impact': '🟢 Faible',
            'forecast': '1.5%',
            'previous': '1.2%'
        }
    ]
    
    return events

# -----------------------------------------------------------------------------
# 3. PAGE PRINCIPALE
# -----------------------------------------------------------------------------
def render():
    """Fonction principale de la page Macronews"""
    
    st.markdown(f"""
    <div style="background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 25px;">
        <h2 style="color: {COLORS['primary']}; margin: 0;">📰 Macronews</h2>
        <p style="margin: 10px 0 0 0; color: #666;">Actualités financières et indicateurs macroéconomiques</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Récupérer les news de la session
    news_data = st.session_state.get('news_data', [])
    
    # ---------------------------------------------------------------------
    # SECTION 1 : ACTUALITÉS FINANCIÈRES
    # ---------------------------------------------------------------------
    st.markdown("### 📰 Flux d'Actualités")
    
    if news_
        # Filtres
        col1, col2 = st.columns(2)
        
        with col1:
            filter_category = st.selectbox(
                "Filtrer par catégorie :",
                options=['Toutes'] + list(set(n['category'] for n in news_data)),
                index=0
            )
        
        with col2:
            st.caption(f"{len(news_data)} actualités disponibles")
        
        # Appliquer le filtre
        if filter_category != 'Toutes':
            filtered_news = [n for n in news_data if n['category'] == filter_category]
        else:
            filtered_news = news_data
        
        # Afficher les news
        st.markdown("#### Dernières Actualités")
        
        for i, news in enumerate(filtered_news[:10]):
            # Couleur selon la catégorie
            if news.get('category') == 'Monétaire':
                border_color = COLORS['primary']
            elif news.get('category') == 'Marché':
                border_color = COLORS['success']
            elif news.get('category') == 'Économie':
                border_color = COLORS['accent']
            else:
                border_color = '#999999'
            
            with st.expander(f"📄 {news['title']}", expanded=(i < 3)):
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.markdown(f"**Source :** {news['source']}")
                    st.markdown(f"**Catégorie :** {news['category']}")
                    st.markdown(f"**Date :** {news['timestamp'].strftime('%d/%m/%Y %H:%M')}")
                    st.markdown("---")
                    st.write(news['summary'])
                
                with col2:
                    st.markdown(f"[🔗 Lire →]({news['url']})")
        
        if len(filtered_news) == 0:
            st.info("ℹ️ Aucune actualité dans cette catégorie")
    
    else:
        st.warning("""
        ⚠️ **Aucune actualité disponible**
        
        Pour collecter les news :
        1. Allez dans la page **📥 Data Ingestion**
        2. Cliquez sur **"📰 Collecter les news"**
        3. Revenez sur cette page
        """)
        
        if st.button("📥 Aller à Data Ingestion"):
            st.session_state.current_page = "data_ingestion"
            st.rerun()
    
    st.markdown("---")
    
    # ---------------------------------------------------------------------
    # SECTION 2 : INFLATION
    # ---------------------------------------------------------------------
    st.markdown("### 💹 Indice d'Inflation")
    
    # Données actuelles (simulées)
    current_inflation = -0.8
    target_min = 2.0
    target_max = 3.0
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig_inflation = generate_inflation_history()
        st.plotly_chart(fig_inflation, use_container_width=True)
    
    with col2:
        fig_gauge = generate_inflation_gauge(current_inflation, target_min, target_max)
        st.plotly_chart(fig_gauge, use_container_width=True)
        
        # Stats
        st.markdown("#### 📊 Statistiques")
        st.metric("Inflation Actuelle", f"{current_inflation:.2f}%")
        st.metric("Cible BAM", f"{target_min}-{target_max}%")
        st.metric("Écart à la cible", f"{current_inflation - target_min:.2f} pts")
        
        # Interprétation
        st.markdown("---")
        st.info("""
        **💡 Interprétation :**
        
        L'inflation est actuellement **en-dessous** de la cible de Bank Al-Maghrib.
        
        Cela peut indiquer :
        - Une faible demande intérieure
        - Un ralentissement économique
        - Un espace pour une politique monétaire accommodante
        """)
    
    st.markdown("---")
    
    # ---------------------------------------------------------------------
    # SECTION 3 : CALENDRIER ÉCONOMIQUE
    # ---------------------------------------------------------------------
    st.markdown("### 📅 Calendrier Économique")
    
    events = get_economic_calendar()
    
    # Créer un DataFrame
    df_events = pd.DataFrame(events)
    
    # Afficher le calendrier
    st.markdown("#### 🗓️ Événements à Venir")
    
    for i, event in enumerate(events):
        col1, col2, col3 = st.columns([2, 3, 2])
        
        with col1:
            st.markdown(f"**📆 {event['date']}**")
            st.caption(f"🕐 {event['time']}")
        
        with col2:
            st.markdown(f"**{event['event']}**")
            st.caption(f"🌍 {event['country']}")
        
        with col3:
            st.markdown(f"**Impact :** {event['impact']}")
            st.caption(f"Prévision: {event['forecast']}")
        
        if i < len(events) - 1:
            st.markdown("---")
    
    # Tableau récapitulatif
    with st.expander("📋 Voir le tableau complet", expanded=False):
        st.dataframe(
            df_events,
            use_container_width=True,
            hide_index=True
        )
    
    st.markdown("---")
    
    # ---------------------------------------------------------------------
    # SECTION 4 : INDICATEURS CLÉS
    # ---------------------------------------------------------------------
    st.markdown("### 📊 Indicateurs Macroéconomiques Clés")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📈 PIB (Croissance)",
            value="2.8%",
            delta="+0.3%"
        )
    
    with col2:
        st.metric(
            label="💹 Inflation",
            value="-0.8%",
            delta="-0.3%"
        )
    
    with col3:
        st.metric(
            label="💼 Taux de Chômage",
            value="11.2%",
            delta="-0.5%"
        )
    
    with col4:
        st.metric(
            label="🏦 Réserves de Change",
            value="335 MMD",
            delta="+2.1%"
        )
    
    st.markdown("---")
    
    # ---------------------------------------------------------------------
    # SECTION 5 : SOURCES ET LIENS
    # ---------------------------------------------------------------------
    st.markdown("### 🔗 Sources et Liens Utiles")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🏛️ Institutions :**
        - [Bank Al-Maghrib](https://www.bkam.ma)
        - [Bourse de Casablanca](https://www.casablanca-bourse.com)
        - [HCP (Haut Commissariat au Plan)](https://www.hcp.ma)
        """)
    
    with col2:
        st.markdown("""
        **📰 Médias :**
        - [Ilboursa](https://www.ilboursa.com)
        - [Leconomiste](https://www.leconomiste.com)
        - [Medias24](https://www.medias24.com)
        """)
    
    with col3:
        st.markdown("""
        **📊 Données Internationales :**
        - [FMI](https://www.imf.org)
        - [Banque Mondiale](https://www.worldbank.org)
        - [Bloomberg](https://www.bloomberg.com)
        """)
    
    # Footer
    st.markdown("---")
    st.caption(f"📰 Macronews | Dernière MAJ: {datetime.now().strftime('%d/%m/%Y %H:%M')} | Sources : Ilboursa, BAM, HCP")
