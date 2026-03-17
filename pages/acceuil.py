# =============================================================================
# NEWZ - Page d'Accueil
# Fichier : pages/home.py
# =============================================================================

import streamlit as st
from datetime import datetime
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config.settings import COLORS, APP_INFO, MSI20_COMPOSITION

# -----------------------------------------------------------------------------
# FONCTION PRINCIPALE
# -----------------------------------------------------------------------------

def render():
    """Fonction principale de la page d'accueil"""
    
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
        <div style="background: linear-gradient(135deg, {COLORS['light']} 0%, #ffffff 100%); 
                    padding: 30px; border-radius: 12px; border-left: 5px solid {COLORS['primary']};
                    height: 100%;">
            <h3 style="color: {COLORS['primary']}; margin-top: 0;">📥 Data Ingestion</h3>
            <ul style="color: #555; line-height: 2;">
                <li>Upload de fichiers Excel</li>
                <li>Scraping Bourse de Casablanca</li>
                <li>Actualités Ilboursa</li>
                <li>Données BAM (taux, devises)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {COLORS['light']} 0%, #ffffff 100%); 
                    padding: 30px; border-radius: 12px; border-left: 5px solid {COLORS['accent']};
                    height: 100%;">
            <h3 style="color: {COLORS['accent']}; margin-top: 0;">📊 Analyse & Visualisation</h3>
            <ul style="color: #555; line-height: 2;">
                <li>Indices MASI / MSI20</li>
                <li>Courbes des taux BDT</li>
                <li>Devises (EUR/MAD, USD/MAD)</li>
                <li>Matrice de corrélations</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {COLORS['light']} 0%, #ffffff 100%); 
                    padding: 30px; border-radius: 12px; border-left: 5px solid {COLORS['success']};
                    height: 100%;">
            <h3 style="color: {COLORS['success']}; margin-top: 0;">📤 Export de Rapports</h3>
            <ul style="color: #555; line-height: 2;">
                <li>Rapports HTML professionnels</li>
                <li>Conversion PDF facile</li>
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
    
    st.info(f"""
    **{len(MSI20_COMPOSITION)} actions** composent l'indice MSI20 (Moroccan Most Active Shares Index).
    La liste est révisée trimestriellement par la Bourse de Casablanca.
    """)
    
    # Afficher les actions sous forme de tableau
    import pandas as pd
    df_msi20 = pd.DataFrame(MSI20_COMPOSITION)
    
    # Formater le tableau avec des couleurs par secteur
    st.dataframe(
        df_msi20,
        use_container_width=True,
        hide_index=True,
        column_config={
            "nom": "Action",
            "ticker": "Ticker",
            "secteur": "Secteur"
        }
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ---------------------------------------------------------------------
    # SECTION 4 : ACCÈS RAPIDE
    # ---------------------------------------------------------------------
    
    st.markdown("### ⚡ Accès Rapide")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.link_button(
            label="📥 Data Ingestion",
            url="/data_ingestion",
            use_container_width=True,
            type="primary"
        )
    
    with col2:
        st.link_button(
            label="📊 BDC Statut",
            url="/bdc_statut",
            use_container_width=True
        )
    
    with col3:
        st.link_button(
            label="🏦 BAM",
            url="/bam",
            use_container_width=True
        )
    
    with col4:
        st.link_button(
            label="📤 Export",
            url="/export",
            use_container_width=True
        )
    
    # ---------------------------------------------------------------------
    # SECTION 5 : ÉTAT DES DONNÉES
    # ---------------------------------------------------------------------
    
    st.markdown("### 📊 État des Données")
    
    # Vérifier les données disponibles
    has_excel = bool(st.session_state.get('excel_data', {}))
    has_bourse = bool(st.session_state.get('bourse_data', {}))
    has_news = bool(st.session_state.get('news_data', []))
    has_actions = st.session_state.get('actions_data') is not None
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if has_excel:
            st.success("✅ Excel chargé")
        else:
            st.caption("⚪ Excel")
    
    with col2:
        if has_bourse:
            st.success("✅ Bourse de Casa")
        else:
            st.caption("⚪ Bourse de Casa")
    
    with col3:
        if has_news:
            st.success(f"✅ News ({len(st.session_state.news_data)})")
        else:
            st.caption("⚪ News")
    
    with col4:
        if has_actions:
            st.success("✅ Actions MSI20")
        else:
            st.caption("⚪ Actions MSI20")
    
    if st.session_state.get('last_update'):
        st.caption(f"Dernière mise à jour : {st.session_state.last_update.strftime('%d/%m/%Y %H:%M:%S')}")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ---------------------------------------------------------------------
    # SECTION 6 : SOURCES DE DONNÉES
    # ---------------------------------------------------------------------
    
    st.markdown("### 🔗 Sources de Données")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        **🏛️ Institutions Officielles**
        - [Bourse de Casablanca](https://www.casablanca-bourse.com)
        - [Bank Al-Maghrib](https://www.bkam.ma)
        - [HCP](https://www.hcp.ma)
        """)
    
    with col2:
        st.markdown(f"""
        **📰 Médias Financiers**
        - [Ilboursa](https://www.ilboursa.com)
        - [Leconomiste](https://www.leconomiste.com)
        - [Medias24](https://www.medias24.com)
        """)
    
    with col3:
        st.markdown(f"""
        **📊 Données Internationales**
        - [Yahoo Finance](https://finance.yahoo.com)
        - [Bloomberg](https://www.bloomberg.com)
        - [Reuters](https://www.reuters.com)
        """)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ---------------------------------------------------------------------
    # SECTION 7 : INFORMATIONS
    # ---------------------------------------------------------------------
    
    st.markdown("### ℹ️ Informations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        **📋 À Propos de Newz**
        
        - **Version :** {APP_INFO['version']}
        - **Développeur :** {APP_INFO['author']}
        - **Copyright :** {APP_INFO['copyright']}
        - **Confidentialité :** {APP_INFO['confidentiality']}
        
        ** Horaires de la Bourse**
        
        - Ouverture : 09h00
        - Clôture : 15h30
        - Jours : Lundi - Vendredi
        """)
    
    with col2:
        st.markdown(f"""
        **💡 Bonnes Pratiques**
        
        1. Mettre à jour les données avant chaque analyse
        2. Vérifier la cohérence des données Excel
        3. Exporter les rapports en fin de journée
        4. Sauvegarder les rapports importants
        
        **📞 Support**
        
        Pour toute question ou problème :
        - Vérifiez les logs d'erreur
        - Consultez la documentation
        """)
