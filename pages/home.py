# =============================================================================
# NEWZ - Page d'Accueil
# Fichier : pages/home.py
# Compatible avec st.navigation() dans app.py
# =============================================================================

import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
import sys

# Ajout du chemin pour les imports
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Import sécurisé de la configuration
try:
    from config.settings import COLORS, APP_INFO, MSI20_COMPOSITION
except ImportError:
    # Fallback si config non chargée
    COLORS = {
        'primary': '#005696',
        'secondary': '#003d6b',
        'accent': '#00a8e8',
        'success': '#28a745',
        'warning': '#ffc107',
        'danger': '#dc3545',
        'light': '#f8f9fa'
    }
    APP_INFO = {'name': 'Newz', 'version': '2.0.0', 'author': 'CDG Capital'}
    MSI20_COMPOSITION = []

# -----------------------------------------------------------------------------
# FONCTION PRINCIPALE
# -----------------------------------------------------------------------------

def render():
    """
    Fonction principale de la page d'accueil
    Appelée automatiquement par st.navigation() dans app.py
    """
    
    # ---------------------------------------------------------------------
    # SECTION 1 : BIENVENUE
    # ---------------------------------------------------------------------
    
    st.markdown(f"""
    <div style="background: white; padding: 40px; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); margin-bottom: 30px;">
        <h2 style="color: {COLORS['primary']}; margin-bottom: 20px;">👋 Bienvenue sur Newz</h2>
        <p style="font-size: 16px; line-height: 1.8; color: #555;">
            Plateforme de market data pour <b>CDG Capital</b>. Cette application vous permet de centraliser, 
            analyser et exporter les données financières marocaines en temps réel.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # ---------------------------------------------------------------------
    # SECTION 2 : FONCTIONNALITÉS PRINCIPALES
    # ---------------------------------------------------------------------
    
    st.markdown("### 🚀 Fonctionnalités Principales")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style="background: {COLORS['light']}; padding: 25px; border-radius: 10px; border-left: 4px solid {COLORS['primary']};">
            <h4 style="color: {COLORS['primary']}; margin-top: 0;">📥 Data Ingestion</h4>
            <ul style="color: #555; margin: 0; padding-left: 20px;">
                <li>Upload fichiers Excel</li>
                <li>Scraping Bourse de Casa</li>
                <li>Actualités Ilboursa</li>
                <li>Données Bank Al-Maghrib</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: {COLORS['light']}; padding: 25px; border-radius: 10px; border-left: 4px solid {COLORS['accent']};">
            <h4 style="color: {COLORS['accent']}; margin-top: 0;">📊 Analyse & Visualisation</h4>
            <ul style="color: #555; margin: 0; padding-left: 20px;">
                <li>Indices MASI / MSI20</li>
                <li>Courbes des taux BDT</li>
                <li>Devises EUR/MAD, USD/MAD</li>
                <li>Matrice de corrélations</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="background: {COLORS['light']}; padding: 25px; border-radius: 10px; border-left: 4px solid {COLORS['success']};">
            <h4 style="color: {COLORS['success']}; margin-top: 0;">📤 Export de Rapports</h4>
            <ul style="color: #555; margin: 0; padding-left: 20px;">
                <li>Rapports HTML pro</li>
                <li>Export PDF facile</li>
                <li>Graphiques interactifs</li>
                <li>Charte CDG Capital</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ---------------------------------------------------------------------
    # SECTION 3 : COMPOSITION DU MSI20
    # ---------------------------------------------------------------------
    
    st.markdown("### 📈 Composition du MSI20")
    
    if MSI20_COMPOSITION:
        st.info(f"**{len(MSI20_COMPOSITION)} actions** composent l'indice MSI20. Liste révisée trimestriellement.")
        
        df_msi20 = pd.DataFrame(MSI20_COMPOSITION)
        
        st.dataframe(
            df_msi20,
            use_container_width=True,
            hide_index=True,
            column_config={
                "nom": st.column_config.TextColumn("Action", width="large"),
                "ticker": st.column_config.TextColumn("Ticker", width="small"),
                "secteur": st.column_config.TextColumn("Secteur", width="medium")
            }
        )
    else:
        st.warning("⚠️ Composition MSI20 non disponible")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ---------------------------------------------------------------------
    # SECTION 4 : ÉTAT DES DONNÉES (Lecture seule)
    # ---------------------------------------------------------------------
    
    st.markdown("### 📊 État des Données")
    
    # Lecture sécurisée des variables de session (initialisées dans app.py)
    has_excel = bool(st.session_state.get('excel_data', {}))
    has_bourse = bool(st.session_state.get('bourse_data', {}))
    has_news = bool(st.session_state.get('news_data', []))
    has_actions = st.session_state.get('actions_data') is not None
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if has_excel:
            st.success("✅ Excel")
        else:
            st.caption("⚪ Excel")
    
    with col2:
        if has_bourse:
            st.success("✅ Bourse")
        else:
            st.caption("⚪ Bourse")
    
    with col3:
        if has_news:
            st.success(f"✅ News")
        else:
            st.caption("⚪ News")
    
    with col4:
        if has_actions:
            st.success("✅ Actions")
        else:
            st.caption("⚪ Actions")
    
    last_update = st.session_state.get('last_update')
    if last_update:
        st.caption(f"Dernière MAJ : {last_update.strftime('%d/%m/%Y %H:%M')}")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ---------------------------------------------------------------------
    # SECTION 5 : SOURCES DE DONNÉES
    # ---------------------------------------------------------------------
    
    st.markdown("### 🔗 Sources de Données")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🏛️ Institutions Officielles**
        - [Bourse de Casablanca](https://www.casablanca-bourse.com)
        - [Bank Al-Maghrib](https://www.bkam.ma)
        - [HCP](https://www.hcp.ma)
        """)
    
    with col2:
        st.markdown("""
        **📰 Médias Financiers**
        - [Ilboursa](https://www.ilboursa.com)
        - [Leconomiste](https://www.leconomiste.com)
        - [Medias24](https://www.medias24.com)
        """)
    
    with col3:
        st.markdown("""
        **📊 International**
        - [Yahoo Finance](https://finance.yahoo.com)
        - [Bloomberg](https://www.bloomberg.com)
        - [Reuters](https://www.reuters.com)
        """)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ---------------------------------------------------------------------
    # SECTION 6 : INFORMATIONS
    # ---------------------------------------------------------------------
    
    st.markdown("### ℹ️ Informations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        **📋 À Propos**
        - **Version :** {APP_INFO.get('version', 'N/A')}
        - **Développeur :** {APP_INFO.get('author', 'CDG Capital')}
        - **Confidentialité :** Usage interne uniquement
        
        **🕐 Horaires Bourse**
        - Ouverture : 09h00
        - Clôture : 15h30
        - Jours : Lun-Ven
        """)
    
    with col2:
        st.markdown("""
        **💡 Bonnes Pratiques**
        1. Mettre à jour avant analyse
        2. Vérifier la cohérence des données
        3. Exporter en fin de journée
        4. Sauvegarder les rapports
        
        **📞 Support**
        - Vérifiez les logs d'erreur
        - Contactez l'équipe Market Data
        """)
# Appel de la fonction render
render()
# =============================================================================
# NOTE IMPORTANTE :
# Avec st.navigation(), cette fonction render() est appelée automatiquement.
# Le bloc if __name__ == "__main__" n'est PAS nécessaire ici.
# =============================================================================
