# =============================================================================
# NEWZ - Page Data Ingestion
# =============================================================================

import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config.settings import COLORS, DATA_DIR

# -----------------------------------------------------------------------------
# 1. INITIALISATION DE L'ÉTAT DE SESSION
# -----------------------------------------------------------------------------
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'excel_data' not in st.session_state:
    st.session_state.excel_data = {}
if 'bourse_data' not in st.session_state:
    st.session_state.bourse_data = {}
if 'news_data' not in st.session_state:
    st.session_state.news_data = []
if 'last_update' not in st.session_state:
    st.session_state.last_update = None

# -----------------------------------------------------------------------------
# 2. FONCTIONS DE SCRAPING (SIMPLIFIÉES)
# -----------------------------------------------------------------------------
def scrape_bourse_casa():
    """
    Scraping simplifié de la Bourse de Casablanca
    Note: Pour production, utiliser une API officielle
    """
    try:
        # Données simulées pour le développement
        # À remplacer par le vrai scraping quand l'API est disponible
        return {
            'masi': {
                'value': 12450.50,
                'change': 0.85,
                'volume': 45000000,
                'timestamp': datetime.now()
            },
            'msi20': {
                'value': 1580.30,
                'change': 1.20,
                'volume': 38000000,
                'timestamp': datetime.now()
            },
            'status': 'success'
        }
    except Exception as e:
        st.error(f"Erreur scraping Bourse : {str(e)}")
        return {'status': 'error', 'message': str(e)}

def scrape_ilboursa_news(limit=10):
    """
    Scraping des news depuis ilboursa.com
    """
    try:
        # Données simulées pour le développement
        news_items = [
            {
                'title': 'Bank Al-Maghrib maintient son taux directeur à 3%',
                'summary': 'Le conseil de Bank Al-Maghrib a décidé de maintenir son taux directeur...',
                'source': 'Ilboursa',
                'timestamp': datetime.now(),
                'url': 'https://www.ilboursa.com',
                'category': 'Monétaire'
            },
            {
                'title': 'Le MASI franchit la barre des 12 500 points',
                'summary': 'La bourse de Casablanca a clôturé en hausse de 0.85%...',
                'source': 'Ilboursa',
                'timestamp': datetime.now(),
                'url': 'https://www.ilboursa.com',
                'category': 'Marché'
            },
            {
                'title': 'L\'inflation au Maroc ralentit à 0,8% en glissement annuel',
                'summary': 'Selon le HCP, l\'inflation a continué de ralentir...',
                'source': 'Ilboursa',
                'timestamp': datetime.now(),
                'url': 'https://www.ilboursa.com',
                'category': 'Économie'
            }
        ]
        return news_items[:limit]
    except Exception as e:
        st.error(f"Erreur scraping News : {str(e)}")
        return []

# -----------------------------------------------------------------------------
# 3. FONCTIONS DE TRAITEMENT EXCEL
# -----------------------------------------------------------------------------
def process_excel_file(uploaded_file):
    """
    Traite le fichier Excel uploadé et extrait les feuilles
    """
    try:
        # Lire toutes les feuilles du fichier Excel
        excel_data = pd.read_excel(uploaded_file, sheet_name=None)
        
        processed = {}
        
        # Traiter chaque feuille attendue
        expected_sheets = [
            'Courbe MAD', 'Courbe_EUR', 'MONIA', 
            'MADBDT_52W', 'USD_MAD', 'EUR_MAD'
        ]
        
        for sheet in expected_sheets:
            if sheet in excel_data:
                df = excel_data[sheet]
                # Nettoyage basique
                df = df.dropna(how='all')
                processed[sheet] = df
                
                # Afficher un résumé
                st.success(f"✅ Feuille '{sheet}' chargée : {len(df)} lignes")
            else:
                st.warning(f"⚠️ Feuille '{sheet}' non trouvée dans le fichier")
                processed[sheet] = pd.DataFrame()
        
        return processed
    
    except Exception as e:
        st.error(f"Erreur de lecture Excel : {str(e)}")
        return None

# -----------------------------------------------------------------------------
# 4. AFFICHAGE DES DONNÉES CHARGÉES
# -----------------------------------------------------------------------------
def display_loaded_data():
    """Affiche un résumé des données chargées"""
    
    st.markdown("### 📊 État des Données")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.session_state.excel_data:
            sheets_count = len([s for s in st.session_state.excel_data.values() if not s.empty])
            st.metric("Feuilles Excel", f"{sheets_count}/6")
        else:
            st.metric("Feuilles Excel", "0/6")
    
    with col2:
        if st.session_state.bourse_data:
            st.metric("Bourse de Casa", "✅ Chargé")
        else:
            st.metric("Bourse de Casa", "⚪ Non chargé")
    
    with col3:
        if st.session_state.news_data:
            st.metric("News", f"{len(st.session_state.news_data)}")
        else:
            st.metric("News", "0")
    
    if st.session_state.last_update:
        st.caption(f"Dernière mise à jour : {st.session_state.last_update.strftime('%d/%m/%Y %H:%M')}")

# -----------------------------------------------------------------------------
# 5. PAGE PRINCIPALE
# -----------------------------------------------------------------------------
def render():
    """Fonction principale de la page Data Ingestion"""
    
    st.markdown(f"""
    <div style="background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 25px;">
        <h2 style="color: {COLORS['primary']}; margin: 0;">📥 Data Ingestion</h2>
        <p style="margin: 10px 0 0 0; color: #666;">Import des données et collecte automatique</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ---------------------------------------------------------------------
    # SECTION 1 : UPLOAD EXCEL
    # ---------------------------------------------------------------------
    st.markdown("### 1️⃣ Import des Données Structurées (Excel)")
    
    st.info("""
    **📋 Structure du fichier Excel attendu :**
    
    Le fichier doit contenir les feuilles suivantes :
    - `Courbe MAD` : ccy_iso, hist_date, tenor_mat, zero_rate
    - `Courbe_EUR` : devise, date_transaction, tenor, date_echeance, taux_zero_coupon_euro_bond
    - `MONIA` : quote_date, rate
    - `MADBDT_52W` : ccy_iso, tenor_label, hist_date, zero_date
    - `USD_MAD` : iso_code1, quote_date, ask, bid, Mid
    - `EUR_MAD` : iso_code1, quote_date, ask, bid, Mid
    """)
    
    uploaded_file = st.file_uploader(
        "📁 Sélectionnez votre fichier Excel",
        type=['xlsx', 'xls'],
        help="Téléchargez le fichier contenant les données BDT, FX, MONIA"
    )
    
    if uploaded_file is not None:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.success(f"Fichier sélectionné : **{uploaded_file.name}**")
        
        with col2:
            if st.button("🔄 Traiter le fichier", use_container_width=True):
                with st.spinner("Traitement en cours..."):
                    processed = process_excel_file(uploaded_file)
                    
                    if processed:
                        st.session_state.excel_data = processed
                        st.session_state.data_loaded = True
                        st.session_state.last_update = datetime.now()
                        st.success("✅ Fichier traité avec succès !")
                        st.rerun()
    
    # Afficher un aperçu des données Excel si chargées
    if st.session_state.excel_data:
        st.markdown("#### 📋 Aperçu des données Excel")
        
        # Sélection de la feuille à visualiser
        sheet_options = [s for s in st.session_state.excel_data.keys() if not st.session_state.excel_data[s].empty]
        
        if sheet_options:
            selected_sheet = st.selectbox("Sélectionnez une feuille :", sheet_options)
            
            if selected_sheet:
                df = st.session_state.excel_data[selected_sheet]
                st.dataframe(df.head(10), use_container_width=True)
                st.caption(f"Total : {len(df)} lignes")
    
    st.markdown("---")
    
    # ---------------------------------------------------------------------
    # SECTION 2 : SCRAPING BOURSE DE CASABLANCA
    # ---------------------------------------------------------------------
    st.markdown("### 2️⃣ Bourse de Casablanca (Scraping)")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("""
        **Données collectées :**
        - MASI (indice général)
        - MSI20 (indice des 20 valeurs les plus liquides)
        - Volumes échangés
        - Variations en temps réel
        """)
    
    with col2:
        if st.button("🔄 Lancer le scraping", use_container_width=True, 
                     disabled=st.session_state.bourse_data.get('status') == 'success'):
            with st.spinner("Collecte en cours..."):
                result = scrape_bourse_casa()
                
                if result.get('status') == 'success':
                    st.session_state.bourse_data = result
                    st.session_state.last_update = datetime.now()
                    st.success("✅ Données collectées !")
                    st.rerun()
                else:
                    st.error("❌ Échec de la collecte")
    
    # Afficher les données Bourse si disponibles
    if st.session_state.bourse_data.get('status') == 'success':
        col1, col2, col3 = st.columns(3)
        
        with col1:
            masi = st.session_state.bourse_data['masi']
            st.metric(
                label="MASI",
                value=f"{masi['value']:,.2f}",
                delta=f"{masi['change']:+.2f}%"
            )
        
        with col2:
            msi20 = st.session_state.bourse_data['msi20']
            st.metric(
                label="MSI20",
                value=f"{msi20['value']:,.2f}",
                delta=f"{msi20['change']:+.2f}%"
            )
        
        with col3:
            st.metric(
                label="Volume (MAD)",
                value=f"{masi['volume']/1e6:.1f}M"
            )
    
    st.markdown("---")
    
    # ---------------------------------------------------------------------
    # SECTION 3 : SCRAPING NEWS ILBOURSA
    # ---------------------------------------------------------------------
    st.markdown("### 3️⃣ Actualités Financières (Ilboursa)")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("""
        **Sources :**
        - www.ilboursa.com
        - Catégories : Monétaire, Marché, Économie, Entreprises
        """)
    
    with col2:
        if st.button("📰 Collecter les news", use_container_width=True):
            with st.spinner("Collecte en cours..."):
                news = scrape_ilboursa_news(limit=10)
                
                if news:
                    st.session_state.news_data = news
                    st.session_state.last_update = datetime.now()
                    st.success(f"✅ {len(news)} news collectées !")
                    st.rerun()
    
    # Afficher les news si disponibles
    if st.session_state.news_data:
        st.markdown("#### 📰 Dernières Actualités")
        
        for i, news in enumerate(st.session_state.news_data[:5]):
            with st.expander(f"📄 {news['title']}", expanded=(i==0)):
                st.write(f"**Source :** {news['source']}")
                st.write(f"**Catégorie :** {news['category']}")
                st.write(f"**Date :** {news['timestamp'].strftime('%d/%m/%Y %H:%M')}")
                st.write(news['summary'])
                st.markdown(f"[Lire la suite →]({news['url']})")
    
    st.markdown("---")
    
    # ---------------------------------------------------------------------
    # SECTION 4 : RÉSUMÉ ET EXPORT
    # ---------------------------------------------------------------------
    display_loaded_data()
    
    # Bouton pour sauvegarder les données
    if st.session_state.data_loaded:
        st.markdown("### 💾 Sauvegarder les Données")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💾 Sauvegarder en cache", use_container_width=True):
                # Sauvegarde dans le dossier data/
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                
                for sheet_name, df in st.session_state.excel_data.items():
                    if not df.empty:
                        filepath = DATA_DIR / f"{sheet_name}_{timestamp}.csv"
                        df.to_csv(filepath, index=False)
                
                st.success(f"Données sauvegardées dans {DATA_DIR}")
        
        with col2:
            if st.button("️ Réinitialiser", use_container_width=True, type="secondary"):
                st.session_state.excel_data = {}
                st.session_state.bourse_data = {}
                st.session_state.news_data = []
                st.session_state.data_loaded = False
                st.session_state.last_update = None
                st.success("Données réinitialisées !")
                st.rerun()
    
    # Message si aucune donnée chargée
    if not st.session_state.data_loaded and not st.session_state.bourse_data and not st.session_state.news_data:
        st.warning("""
        ⚠️ **Aucune donnée chargée**
        
        Pour commencer :
        1. Uploadez un fichier Excel avec les données BDT/FX/MONIA
        2. Lancez le scraping Bourse de Casablanca
        3. Collectez les actualités Ilboursa
        """)
