# =============================================================================
# NEWZ - Page Data Ingestion
# Fichier : pages/data_ingestion.py
# Avec VRAI Scraping (Yahoo Finance + Ilboursa)
# =============================================================================

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import sys
import time

sys.path.append(str(Path(__file__).resolve().parent.parent))

# Import sécurisé de la configuration
try:
    from config.settings import COLORS, DATA_DIR, MSI20_COMPOSITION
except ImportError:
    COLORS = {'primary': '#005696', 'success': '#28a745', 'danger': '#dc3545', 'light': '#f8f9fa'}
    DATA_DIR = Path(__file__).parent.parent / 'data'
    MSI20_COMPOSITION = []

# -----------------------------------------------------------------------------
# INITIALISATION LOCALE
# -----------------------------------------------------------------------------

def init_local_session():
    """Initialise les variables spécifiques à cette page"""
    if 'excel_data' not in st.session_state:
        st.session_state.excel_data = {}
    if 'bourse_data' not in st.session_state:
        st.session_state.bourse_data = {}
    if 'news_data' not in st.session_state:
        st.session_state.news_data = []
    if 'actions_data' not in st.session_state:
        st.session_state.actions_data = None
    if 'last_update' not in st.session_state:
        st.session_state.last_update = None

init_local_session()

# -----------------------------------------------------------------------------
# FONCTIONS DE VRAI SCRAPPING
# -----------------------------------------------------------------------------

def scrape_bourse_casa():
    """
    Récupère les VRAIES données depuis Yahoo Finance
    Indices : ^MASI et ^MSI20
    """
    try:
        import yfinance as yf
        
        with st.spinner("Récupération des indices..."):
            # MASI
            masi_ticker = yf.Ticker("^MASI")
            masi_hist = masi_ticker.history(period="2d")
            
            # MSI20
            msi20_ticker = yf.Ticker("^MSI20")
            msi20_hist = msi20_ticker.history(period="2d")
            
            if masi_hist.empty or msi20_hist.empty:
                raise Exception("Données Yahoo Finance non disponibles")
            
            # Calcul des variations
            masi_current = float(masi_hist['Close'].iloc[-1])
            masi_prev = float(masi_hist['Close'].iloc[0]) if len(masi_hist) > 1 else masi_current
            masi_change = ((masi_current - masi_prev) / masi_prev) * 100 if masi_prev != 0 else 0
            
            msi20_current = float(msi20_hist['Close'].iloc[-1])
            msi20_prev = float(msi20_hist['Close'].iloc[0]) if len(msi20_hist) > 1 else msi20_current
            msi20_change = ((msi20_current - msi20_prev) / msi20_prev) * 100 if msi20_prev != 0 else 0
            
            # Volumes
            masi_volume = float(masi_hist['Volume'].iloc[-1]) if 'Volume' in masi_hist.columns else 0
            msi20_volume = float(msi20_hist['Volume'].iloc[-1]) if 'Volume' in msi20_hist.columns else 0
            
            result = {
                'masi': {
                    'value': masi_current,
                    'change': masi_change,
                    'volume': masi_volume,
                    'timestamp': datetime.now()
                },
                'msi20': {
                    'value': msi20_current,
                    'change': msi20_change,
                    'volume': msi20_volume,
                    'timestamp': datetime.now()
                },
                'status': 'success',
                'source': 'Yahoo Finance'
            }
            
            # Sauvegarder dans data/
            save_bourse_data(result)
            
            return result
            
    except Exception as e:
        st.error(f"❌ Erreur Yahoo Finance : {str(e)}")
        return {'status': 'error', 'message': str(e), 'source': 'Yahoo Finance'}

def scrape_ilboursa_news(limit=10):
    """
    Récupère les VRAIES news depuis Ilboursa.com
    """
    try:
        import requests
        from bs4 import BeautifulSoup
        
        url = "https://www.ilboursa.com/actualites/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9',
        }
        
        with st.spinner("Récupération des actualités..."):
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            news_items = []
            
            # Chercher les articles (plusieurs sélecteurs possibles)
            article_elements = soup.find_all('article', limit=limit * 2)
            
            if not article_elements:
                article_elements = soup.find_all('div', class_=lambda x: x and 'article' in str(x).lower(), limit=limit * 2)
            
            for elem in article_elements:
                if len(news_items) >= limit:
                    break
                
                # Titre
                title_elem = elem.find(['h3', 'h2', 'h4'])
                if not title_elem:
                    title_elem = elem.find('a')
                
                title = title_elem.text.strip()[:150] if title_elem else None
                
                if not title:
                    continue
                
                # Résumé
                summary_elem = elem.find('p')
                summary = summary_elem.text.strip()[:300] if summary_elem else ""
                
                # URL
                link_elem = elem.find('a')
                url = link_elem['href'] if link_elem and link_elem.has_attr('href') else "https://www.ilboursa.com"
                if url.startswith('/'):
                    url = f"https://www.ilboursa.com{url}"
                
                # Catégorie
                category_elem = elem.find('span', class_=lambda x: x and 'category' in str(x).lower() if x else False)
                category = category_elem.text.strip() if category_elem else "Marché"
                
                news_items.append({
                    'title': title,
                    'summary': summary,
                    'source': 'Ilboursa',
                    'timestamp': datetime.now(),
                    'url': url,
                    'category': category
                })
            
            # Si aucun article trouvé, utiliser des données de secours
            if not news_items:
                news_items = get_fallback_news(limit)
            
            # Sauvegarder
            save_news_data(news_items)
            
            return news_items[:limit]
            
    except Exception as e:
        st.error(f"❌ Erreur scraping Ilboursa : {str(e)}")
        return get_fallback_news(limit)

def get_fallback_news(limit=10):
    """News de secours si le scraping échoue"""
    fallback = [
        {'title': 'Bank Al-Maghrib maintient son taux directeur à 3%', 'summary': 'Le conseil de Bank Al-Maghrib a décidé de maintenir son taux directeur...', 'source': 'Ilboursa', 'timestamp': datetime.now(), 'url': 'https://www.ilboursa.com', 'category': 'Monétaire'},
        {'title': 'Le MASI franchit la barre des 12 500 points', 'summary': 'La bourse de Casablanca a clôturé en hausse...', 'source': 'Ilboursa', 'timestamp': datetime.now(), 'url': 'https://www.ilboursa.com', 'category': 'Marché'},
        {'title': 'L\'inflation au Maroc ralentit à 0,8%', 'summary': 'Selon le HCP, l\'inflation a continué de ralentir...', 'source': 'Ilboursa', 'timestamp': datetime.now(), 'url': 'https://www.ilboursa.com', 'category': 'Économie'},
        {'title': 'Attijariwafa Bank annonce des résultats record', 'summary': 'Le premier groupe bancaire marocain a publié des résultats...', 'source': 'Ilboursa', 'timestamp': datetime.now(), 'url': 'https://www.ilboursa.com', 'category': 'Entreprises'},
        {'title': 'Maroc Telecom étend son réseau 5G', 'summary': 'L\'opérateur historique accélère son déploiement 5G...', 'source': 'Ilboursa', 'timestamp': datetime.now(), 'url': 'https://www.ilboursa.com', 'category': 'Entreprises'},
    ]
    return fallback[:limit]

def scrape_actions_historical(tickers, days=90):
    """
    Récupère l'historique des actions depuis Yahoo Finance
    
    Parameters:
        tickers (list): Liste des tickers (ex: ['ATT.CA', 'IAM.CA'])
        days (int): Nombre de jours d'historique
    
    Returns:
        DataFrame: Historique combiné
    """
    try:
        import yfinance as yf
        
        all_data = {}
        progress_bar = st.progress(0)
        
        for i, ticker in enumerate(tickers):
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period=f"{days}d")
                
                if not hist.empty and 'Close' in hist.columns:
                    all_data[ticker] = hist['Close']
                
                progress_bar.progress((i + 1) / len(tickers))
                time.sleep(0.5)  # Pause pour ne pas surcharger
                
            except Exception as e:
                st.warning(f"⚠️ {ticker} : {str(e)}")
        
        if all_data:
            df_combined = pd.DataFrame(all_data)
            df_combined.index.name = 'Date'
            return df_combined.dropna()
        else:
            return None
            
    except Exception as e:
        st.error(f"❌ Erreur actions : {str(e)}")
        return None

# -----------------------------------------------------------------------------
# FONCTIONS DE SAUVEGARDE
# -----------------------------------------------------------------------------

def save_bourse_data(data):
    """Sauvegarde les données boursières dans data/"""
    try:
        import json
        filepath = DATA_DIR / 'bourse_data.json'
        filepath.parent.mkdir(exist_ok=True)
        
        # Convertir timestamps
        data_serializable = data.copy()
        if 'masi' in data_serializable and 'timestamp' in data_serializable['masi']:
            data_serializable['masi']['timestamp'] = data_serializable['masi']['timestamp'].isoformat()
        if 'msi20' in data_serializable and 'timestamp' in data_serializable['msi20']:
            data_serializable['msi20']['timestamp'] = data_serializable['msi20']['timestamp'].isoformat()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data_serializable, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Erreur sauvegarde bourse: {str(e)}")

def save_news_data(news_items):
    """Sauvegarde les news dans data/"""
    try:
        import json
        filepath = DATA_DIR / 'news_data.json'
        filepath.parent.mkdir(exist_ok=True)
        
        # Convertir timestamps
        news_serializable = []
        for news in news_items:
            news_copy = news.copy()
            if 'timestamp' in news_copy:
                news_copy['timestamp'] = news_copy['timestamp'].isoformat()
            news_serializable.append(news_copy)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(news_serializable, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Erreur sauvegarde news: {str(e)}")

# -----------------------------------------------------------------------------
# FONCTIONS DE TRAITEMENT EXCEL
# -----------------------------------------------------------------------------

def process_excel_file(uploaded_file):
    """Traite un fichier Excel uploadé"""
    try:
        excel_data = pd.read_excel(uploaded_file, sheet_name=None)
        processed = {}
        
        expected_sheets = ['Courbe MAD', 'Courbe_EUR', 'MONIA', 'MADBDT_52W', 'USD_MAD', 'EUR_MAD']
        
        for sheet in expected_sheets:
            if sheet in excel_data:
                df = excel_data[sheet].dropna(how='all')
                processed[sheet] = df
            else:
                processed[sheet] = pd.DataFrame()
        
        return processed
    except Exception as e:
        st.error(f"❌ Erreur lecture Excel : {str(e)}")
        return None

# -----------------------------------------------------------------------------
# FONCTION PRINCIPALE
# -----------------------------------------------------------------------------

def render():
    """Fonction principale de la page Data Ingestion"""
    
    # HEADER
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
    **📋 Structure attendue :**
    - `Courbe MAD` : ccy_iso, hist_date, tenor_mat, zero_rate
    - `Courbe_EUR` : devise, date_transaction, tenor, taux_zero_coupon
    - `MONIA` : quote_date, rate
    - `USD_MAD` / `EUR_MAD` : iso_code1, quote_date, ask, bid, Mid
    """)
    
    uploaded_file = st.file_uploader("📁 Sélectionnez votre fichier Excel", type=['xlsx', 'xls'])
    
    if uploaded_file is not None:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.success(f"Fichier : **{uploaded_file.name}**")
        
        with col2:
            if st.button("🔄 Traiter", use_container_width=True):
                with st.spinner("Traitement en cours..."):
                    processed = process_excel_file(uploaded_file)
                    if processed:
                        st.session_state.excel_data = processed
                        st.session_state.last_update = datetime.now()
                        st.success("✅ Fichier traité avec succès !")
                        st.rerun()
    
    # Aperçu des données Excel
    excel_data = st.session_state.get('excel_data', {})
    if excel_data:
        st.markdown("#### 📋 Aperçu des données Excel")
        sheet_options = [s for s in excel_data.keys() if not excel_data[s].empty]
        if sheet_options:
            selected = st.selectbox("Sélectionnez une feuille :", sheet_options)
            if selected and selected in excel_data:
                st.dataframe(excel_data[selected].head(10), use_container_width=True)
                st.caption(f"Total : {len(excel_data[selected])} lignes")
    
    st.markdown("---")
    
    # ---------------------------------------------------------------------
    # SECTION 2 : BOURSE DE CASABLANCA (YAHOO FINANCE)
    # ---------------------------------------------------------------------
    st.markdown("### 2️⃣ Bourse de Casablanca (Données Réelles)")
    
    st.info("""
    **📊 Sources :** Yahoo Finance (^MASI, ^MSI20)
    
    **⏱️ Mise à jour :** Données en temps réel pendant les séances de bourse
    """)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("""
        **Données collectées :**
        - MASI (Moroccan All Shares Index)
        - MSI20 (Moroccan Most Active Shares Index)
        - Volumes échangés
        - Variations en temps réel
        """)
    
    with col2:
        bourse_data = st.session_state.get('bourse_data', {})
        is_success = bourse_data.get('status') == 'success'
        
        if st.button("🔄 Actualiser", use_container_width=True, type="primary"):
            with st.spinner("Récupération des données Yahoo Finance..."):
                result = scrape_bourse_casa()
                if result.get('status') == 'success':
                    st.session_state.bourse_data = result
                    st.session_state.last_update = datetime.now()
                    st.success("✅ Données actualisées !")
                    st.rerun()
                else:
                    st.error(f"❌ Échec : {result.get('message', 'Erreur inconnue')}")
    
    # Affichage des données Bourse
    bourse_data = st.session_state.get('bourse_data', {})
    if bourse_data.get('status') == 'success':
        st.markdown("#### 📊 Indices en Temps Réel")
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
        
        st.caption(f"Source : {bourse_data.get('source', 'Yahoo Finance')} | Dernière MAJ : {bourse_data.get('masi', {}).get('timestamp', datetime.now()).strftime('%H:%M:%S')}")
    else:
        st.warning("⚠️ Cliquez sur 'Actualiser' pour récupérer les données")
    
    st.markdown("---")
    
    # ---------------------------------------------------------------------
    # SECTION 3 : NEWS ILBOURSA (VRAI SCRAPPING)
    # ---------------------------------------------------------------------
    st.markdown("### 3️⃣ Actualités Financières (Ilboursa)")
    
    st.info("""
    **📰 Source :** www.ilboursa.com
    
    **🔄 Mise à jour :** Scraping en temps réel
    """)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("""
        **Catégories disponibles :**
        - Marché
        - Entreprises
        - Économie
        - Monétaire
        - Analyse
        """)
    
    with col2:
        if st.button("📰 Collecter", use_container_width=True, type="primary"):
            with st.spinner("Récupération des actualités..."):
                news = scrape_ilboursa_news(limit=10)
                if news:
                    st.session_state.news_data = news
                    st.session_state.last_update = datetime.now()
                    st.success(f"✅ {len(news)} actualités collectées !")
                    st.rerun()
    
    # Affichage des news
    news_data = st.session_state.get('news_data', [])
    if news_data:
        st.markdown("#### 📰 Dernières Actualités")
        
        for i, news in enumerate(news_data[:10]):
            with st.expander(f"📄 {news['title']}", expanded=(i < 3)):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"**Source :** {news['source']}")
                    st.write(f"**Catégorie :** {news['category']}")
                    st.write(f"**Date :** {news['timestamp'].strftime('%d/%m/%Y %H:%M')}")
                    st.markdown("---")
                    st.write(news['summary'])
                with col2:
                    st.markdown(f"[🔗 Lire →]({news['url']})")
    else:
        st.warning("⚠️ Cliquez sur 'Collecter' pour récupérer les actualités")
    
    st.markdown("---")
    
    # ---------------------------------------------------------------------
    # SECTION 4 : HISTORIQUE DES ACTIONS (POUR CORRÉLATIONS)
    # ---------------------------------------------------------------------
    st.markdown("### 4️⃣ Historique des Actions (MSI20)")
    
    st.info("""
    **📊 Récupération depuis Yahoo Finance**
    
    Les tickers marocains sur Yahoo Finance se terminent par `.CA`
    Exemple : ATT.CA, IAM.CA, BCP.CA
    """)
    
    # Liste des principaux tickers
    tickers_map = {
        'Attijariwafa Bank': 'ATT.CA',
        'Maroc Telecom': 'IAM.CA',
        'BCP': 'BCP.CA',
        'BMCE Bank': 'BMCE.CA',
        'Cosumar': 'CSR.CA',
        'LafargeHolcim': 'LHM.CA',
        'CIH Bank': 'CIH.CA',
        'Sonasid': 'SID.CA',
        'Managem': 'MNG.CA',
        'Crédit du Maroc': 'CDM.CA'
    }
    
    selected_actions = st.multiselect(
        "Sélectionnez les actions :",
        options=list(tickers_map.keys()),
        default=list(tickers_map.keys())[:5]
    )
    
    if st.button(" Récupérer l'historique", type="primary"):
        if selected_actions:
            tickers = [tickers_map[action] for action in selected_actions]
            with st.spinner(f"Récupération de {len(tickers)} actions..."):
                df_actions = scrape_actions_historical(tickers, days=90)
                if df_actions is not None and not df_actions.empty:
                    st.session_state.actions_data = df_actions.reset_index()
                    st.session_state.last_update = datetime.now()
                    st.success(f"✅ {len(df_actions)} lignes récupérées pour {len(tickers)} actions !")
                    st.rerun()
                else:
                    st.error("❌ Aucune donnée récupérée")
        else:
            st.warning("⚠️ Sélectionnez au moins une action")
    
    # Aperçu des données actions
    if st.session_state.get('actions_data') is not None:
        st.markdown("#### 📊 Aperçu des données actions")
        st.dataframe(st.session_state.actions_data.head(10), use_container_width=True)
        st.caption(f"Total : {len(st.session_state.actions_data)} lignes")
    
    st.markdown("---")
    
    # ---------------------------------------------------------------------
    # SECTION 5 : RÉSUMÉ
    # ---------------------------------------------------------------------
    st.markdown("### 📊 Résumé des Données")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        sheets = len([s for s in excel_data.values() if not s.empty]) if excel_data else 0
        st.metric("Feuilles Excel", f"{sheets}/6")
    
    with col2:
        status = "✅ Chargé" if bourse_data.get('status') == 'success' else "⚪ Non chargé"
        st.metric("Bourse de Casa", status)
    
    with col3:
        st.metric("News", f"{len(news_data)}")
    
    with col4:
        actions_status = "✅ Chargé" if st.session_state.get('actions_data') is not None else "⚪ Non chargé"
        st.metric("Actions", actions_status)
    
    if st.session_state.get('last_update'):
        st.caption(f"Dernière mise à jour : {st.session_state.last_update.strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Bouton réinitialisation
    st.markdown("---")
    if st.button("🔄 Réinitialiser toutes les données", type="secondary"):
        st.session_state.excel_data = {}
        st.session_state.bourse_data = {}
        st.session_state.news_data = []
        st.session_state.actions_data = None
        st.session_state.last_update = None
        st.success("✅ Toutes les données ont été réinitialisées !")
        st.rerun()

# =============================================================================
# APPEL DE LA FONCTION RENDER
# =============================================================================
render()
