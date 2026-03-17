# =============================================================================
# NEWZ - Bourse de Casablanca Official Scraper
# Fichier : utils/bourse_casa_scraper.py
# =============================================================================

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import time
import json
from pathlib import Path
import sys

# Ajout du chemin pour les imports
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config.settings import SCRAPER_CONFIG, MSI20_COMPOSITION, DATA_DIR

# -----------------------------------------------------------------------------
# 1. CLASSE PRINCIPALE - BOURSE CASA SCRAPER
# -----------------------------------------------------------------------------

class BourseCasaScraper:
    """
    Scraper officiel de la Bourse de Casablanca
    
    Permet de récupérer :
    - La composition du MSI20
    - L'historique des cours des actions
    - Les indices MASI et MSI20
    - Le statut du marché
    - Les données de trading (volumes, etc.)
    """
    
    BASE_URL = "https://www.casablanca-bourse.com"
    
    def __init__(self):
        """Initialise le scraper avec une session HTTP"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': SCRAPER_CONFIG['user_agent'],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
        self.timeout = SCRAPER_CONFIG['timeout']
        self.delay = SCRAPER_CONFIG['delay_between_requests']
    
    # -------------------------------------------------------------------------
    # 2. RÉCUPÉRATION COMPOSITION MSI20
    # -------------------------------------------------------------------------
    
    def get_msi20_composition(self):
        """
        Récupère la liste officielle des 20 actions du MSI20
        
        Returns:
            list: Liste des actions avec nom, ticker, secteur, poids
        """
        try:
            url = f"{self.BASE_URL}/bourse-de-casablanca/indices/MSI20"
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            actions = []
            
            # Chercher le tableau de composition
            # Note: Les sélecteurs CSS peuvent changer, à adapter si nécessaire
            table = soup.find('table', {'class': lambda x: x and 'composition' in x.lower()})
            
            if not table:
                # Alternative: chercher par ID
                table = soup.find('table', id=lambda x: x and 'msi20' in x.lower())
            
            if table:
                rows = table.find_all('tr')[1:]  # Skip header
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 3:
                        actions.append({
                            'nom': cols[0].text.strip(),
                            'ticker': cols[1].text.strip(),
                            'secteur': cols[2].text.strip() if len(cols) > 2 else 'N/A',
                            'poids': cols[3].text.strip() if len(cols) > 3 else 'N/A'
                        })
            
            # Si scraping échoue, utiliser la liste de secours
            if not actions:
                actions = self._get_msi20_fallback()
            
            # Sauvegarder la composition
            self._save_composition(actions)
            
            time.sleep(self.delay)
            return actions
            
        except Exception as e:
            print(f"❌ Erreur récupération MSI20: {str(e)}")
            return self._get_msi20_fallback()
    
    def _get_msi20_fallback(self):
        """Liste MSI20 de secours (config/settings.py)"""
        return MSI20_COMPOSITION.copy()
    
    def _save_composition(self, actions):
        """Sauvegarde la composition dans un fichier JSON"""
        filepath = DATA_DIR / 'msi20_composition.json'
        data = {
            'last_update': datetime.now().isoformat(),
            'count': len(actions),
            'actions': actions
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    # -------------------------------------------------------------------------
    # 3. HISTORIQUE DES ACTIONS
    # -------------------------------------------------------------------------
    
    def get_action_historical(self, ticker, days=90):
        """
        Récupère l'historique des cours d'une action
        
        Parameters:
            ticker (str): Code de l'action (ex: 'ATT')
            days (int): Nombre de jours d'historique
        
        Returns:
            DataFrame: Date, Open, High, Low, Close, Volume
        """
        try:
            url = f"{self.BASE_URL}/bourse-de-casablanca/actions/{ticker.lower()}"
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            data = {
                'Date': [],
                'Open': [],
                'High': [],
                'Low': [],
                'Close': [],
                'Volume': [],
                'Variation': []
            }
            
            # Chercher le tableau d'historique
            table = soup.find('table', {'class': lambda x: x and 'historique' in x.lower()})
            
            if not table:
                table = soup.find('table', id=lambda x: x and 'historique' in x.lower())
            
            if table:
                rows = table.find_all('tr')[1:days+1]  # Skip header, limiter à days
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 6:
                        data['Date'].append(self._clean_date(cols[0].text.strip()))
                        data['Close'].append(self._clean_number(cols[1].text.strip()))
                        data['Open'].append(self._clean_number(cols[2].text.strip()))
                        data['High'].append(self._clean_number(cols[3].text.strip()))
                        data['Low'].append(self._clean_number(cols[4].text.strip()))
                        data['Volume'].append(self._clean_number(cols[5].text.strip()))
                        data['Variation'].append(self._clean_number(cols[6].text.strip()) if len(cols) > 6 else None)
            
            df = pd.DataFrame(data)
            
            if df.empty:
                return None
            
            # Nettoyage et conversion
            df = self._clean_dataframe(df)
            
            time.sleep(self.delay)
            return df
            
        except Exception as e:
            print(f"❌ Erreur scraping {ticker}: {str(e)}")
            return None
    
    def get_all_msi20_historical(self, days=90):
        """
        Récupère l'historique de toutes les actions du MSI20
        
        Parameters:
            days (int): Nombre de jours d'historique
        
        Returns:
            DataFrame: DataFrame combiné avec toutes les actions (colonnes = tickers)
        """
        actions = self.get_msi20_composition()
        all_data = {}
        
        progress_callback = None  # Peut être utilisé pour afficher une barre de progression
        
        for i, action in enumerate(actions):
            ticker = action['ticker']
            print(f"  📊 [{i+1}/{len(actions)}] {action['nom']} ({ticker})...")
            
            df = self.get_action_historical(ticker, days)
            
            if df is not None and not df.empty:
                all_data[ticker] = df.set_index('Date')['Close']
            
            # Pause pour ne pas surcharger le serveur
            time.sleep(self.delay)
        
        if all_data:
            # Combiner tous les DataFrames
            df_combined = pd.DataFrame(all_data)
            df_combined = df_combined.dropna()
            df_combined.index.name = 'Date'
            return df_combined
        else:
            return None
    
    # -------------------------------------------------------------------------
    # 4. INDICES (MASI, MSI20)
    # -------------------------------------------------------------------------
    
    def get_index_historical(self, index_name, days=90):
        """
        Récupère l'historique d'un indice (MASI ou MSI20)
        
        Parameters:
            index_name (str): Nom de l'indice ('MASI' ou 'MSI20')
            days (int): Nombre de jours d'historique
        
        Returns:
            DataFrame: Date, Value, Variation, Volume
        """
        try:
            url = f"{self.BASE_URL}/bourse-de-casablanca/indices/{index_name}"
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            data = {
                'Date': [],
                'Value': [],
                'Variation': [],
                'Volume': []
            }
            
            table = soup.find('table', {'class': lambda x: x and 'historique' in x.lower()})
            
            if table:
                rows = table.find_all('tr')[1:days+1]
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 4:
                        data['Date'].append(self._clean_date(cols[0].text.strip()))
                        data['Value'].append(self._clean_number(cols[1].text.strip()))
                        data['Variation'].append(self._clean_number(cols[2].text.strip()))
                        data['Volume'].append(self._clean_number(cols[3].text.strip()))
            
            df = pd.DataFrame(data)
            
            if df.empty:
                return None
            
            df = self._clean_dataframe(df)
            
            time.sleep(self.delay)
            return df
            
        except Exception as e:
            print(f"❌ Erreur indice {index_name}: {str(e)}")
            return None
    
    def get_masi(self, days=90):
        """Récupère l'historique du MASI"""
        return self.get_index_historical('MASI', days)
    
    def get_msi20_index(self, days=90):
        """Récupère l'historique du MSI20"""
        return self.get_index_historical('MSI20', days)
    
    # -------------------------------------------------------------------------
    # 5. STATUT DU MARCHÉ
    # -------------------------------------------------------------------------
    
    def get_market_status(self):
        """
        Récupère le statut actuel du marché (ouvert/fermé)
        
        Returns:
            dict: is_open, status_text, last_update, masi_value, msi20_value
        """
        try:
            url = f"{self.BASE_URL}/bourse-de-casablanca"
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            status = {
                'is_open': False,
                'status_text': 'Inconnu',
                'last_update': datetime.now().isoformat(),
                'masi_value': None,
                'masi_change': None,
                'msi20_value': None,
                'msi20_change': None
            }
            
            # Chercher les indicateurs de marché
            # Note: Les sélecteurs peuvent varier selon la structure du site
            
            # MASI
            masi_elem = soup.find('div', {'class': lambda x: x and 'masi' in x.lower()})
            if masi_elem:
                status['masi_value'] = self._clean_number(masi_elem.find('span', class_='value').text)
                status['masi_change'] = self._clean_number(masi_elem.find('span', class_='change').text)
            
            # MSI20
            msi20_elem = soup.find('div', {'class': lambda x: x and 'msi20' in x.lower()})
            if msi20_elem:
                status['msi20_value'] = self._clean_number(msi20_elem.find('span', class_='value').text)
                status['msi20_change'] = self._clean_number(msi20_elem.find('span', class_='change').text)
            
            # Statut (ouvert/fermé)
            status_elem = soup.find('div', {'class': 'market-status'})
            if status_elem:
                status_text = status_elem.text.strip().lower()
                status['is_open'] = 'ouvert' in status_text or 'open' in status_text
                status['status_text'] = status_text
            
            # Sauvegarder le statut
            self._save_market_status(status)
            
            return status
            
        except Exception as e:
            print(f"❌ Erreur statut marché: {str(e)}")
            return {
                'is_open': False,
                'status_text': f'Erreur: {str(e)}',
                'last_update': datetime.now().isoformat()
            }
    
    def _save_market_status(self, status):
        """Sauvegarde le statut du marché"""
        filepath = DATA_DIR / 'market_status.json'
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(status, f, ensure_ascii=False, indent=2)
    
    # -------------------------------------------------------------------------
    # 6. FONCTIONS UTILITAIRES
    # -------------------------------------------------------------------------
    
    def _clean_number(self, text):
        """
        Nettoie un nombre (enlève espaces, virgules, symboles)
        
        Parameters:
            text (str): Texte à nettoyer
        
        Returns:
            float: Nombre nettoyé ou None
        """
        if not text:
            return None
        
        text = str(text).strip()
        text = text.replace(' ', '').replace('\xa0', '')
        text = text.replace(',', '.')  # Virgule → point
        text = text.replace('%', '')
        text = text.replace('+', '')
        
        try:
            return float(text)
        except:
            return None
    
    def _clean_date(self, text):
        """
        Nettoie et convertit une date
        
        Parameters:
            text (str): Date au format texte
        
        Returns:
            str: Date au format YYYY-MM-DD
        """
        if not text:
            return None
        
        formats = [
            '%d/%m/%Y',
            '%d-%m-%Y',
            '%Y/%m/%d',
            '%Y-%m-%d',
            '%d %b %Y',
            '%d %B %Y'
        ]
        
        for fmt in formats:
            try:
                date_obj = datetime.strptime(text.strip(), fmt)
                return date_obj.strftime('%Y-%m-%d')
            except:
                continue
        
        return text.strip()
    
    def _clean_dataframe(self, df):
        """
        Nettoie un DataFrame (conversion des types, suppression NaN)
        
        Parameters:
            df (DataFrame): DataFrame à nettoyer
        
        Returns:
            DataFrame: DataFrame nettoyé
        """
        # Convertir Date
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        
        # Convertir les colonnes numériques
        numeric_cols = ['Open', 'High', 'Low', 'Close', 'Volume', 'Value', 'Variation']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Supprimer les lignes avec des NaN critiques
        df = df.dropna(subset=['Date'])
        
        # Trier par date
        if 'Date' in df.columns:
            df = df.sort_values('Date').reset_index(drop=True)
        
        return df
    
    # -------------------------------------------------------------------------
    # 7. EXPORT DES DONNÉES
    # -------------------------------------------------------------------------
    
    def save_all_data(self, days=90):
        """
        Récupère et sauvegarde toutes les données dans des fichiers CSV
        
        Parameters:
            days (int): Nombre de jours d'historique
        
        Returns:
            dict: Chemins des fichiers sauvegardés
        """
        print("🔄 Début de la récupération complète des données...")
        
        saved_files = {}
        
        # 1. Composition MSI20
        print("  📋 Composition MSI20...")
        msi20 = self.get_msi20_composition()
        saved_files['msi20_composition'] = str(DATA_DIR / 'msi20_composition.json')
        
        # 2. Historique MASI
        print("  📈 Indice MASI...")
        masi = self.get_masi(days)
        if masi is not None:
            filepath = DATA_DIR / 'masi_historical.csv'
            masi.to_csv(filepath, index=False)
            saved_files['masi'] = str(filepath)
        
        # 3. Historique MSI20
        print("  📊 Indice MSI20...")
        msi20_idx = self.get_msi20_index(days)
        if msi20_idx is not None:
            filepath = DATA_DIR / 'msi20_historical.csv'
            msi20_idx.to_csv(filepath, index=False)
            saved_files['msi20_index'] = str(filepath)
        
        # 4. Historique des actions
        print("  🏢 Actions du MSI20...")
        actions_df = self.get_all_msi20_historical(days)
        if actions_df is not None:
            filepath = DATA_DIR / 'actions_historical.csv'
            actions_df.to_csv(filepath)
            saved_files['actions'] = str(filepath)
        
        # 5. Statut du marché
        print("  📊 Statut du marché...")
        status = self.get_market_status()
        saved_files['market_status'] = str(DATA_DIR / 'market_status.json')
        
        print(f"✅ Données sauvegardées dans {DATA_DIR}")
        
        return saved_files


# -----------------------------------------------------------------------------
# 8. FONCTIONS DE COMMODITÉ
# -----------------------------------------------------------------------------

def get_bourse_scraper():
    """Factory function pour créer un scraper"""
    return BourseCasaScraper()

def download_all_data(days=90):
    """
    Fonction rapide pour télécharger toutes les données
    
    Parameters:
        days (int): Nombre de jours d'historique
    
    Returns:
        dict: Chemins des fichiers sauvegardés
    """
    scraper = BourseCasaScraper()
    return scraper.save_all_data(days)


# -----------------------------------------------------------------------------
# 9. POINT D'ENTRÉE POUR TEST
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    print("🚀 Test du scraper Bourse de Casablanca")
    print("=" * 60)
    
    scraper = BourseCasaScraper()
    
    # Test 1: Statut du marché
    print("\n1️⃣ Statut du marché:")
    status = scraper.get_market_status()
    print(f"   Ouvert: {'✅' if status['is_open'] else '❌'}")
    print(f"   MASI: {status.get('masi_value', 'N/A')}")
    
    # Test 2: Composition MSI20
    print("\n2️⃣ Composition MSI20:")
    msi20 = scraper.get_msi20_composition()
    print(f"   {len(msi20)} actions trouvées")
    for action in msi20[:5]:
        print(f"   - {action['nom']} ({action['ticker']})")
    
    # Test 3: Historique d'une action
    print("\n3️⃣ Historique ATT (Attijariwafa Bank):")
    att_df = scraper.get_action_historical('ATT', days=10)
    if att_df is not None:
        print(f"   {len(att_df)} lignes récupérées")
        print(att_df.head(3))
    
    # Test 4: Sauvegarde complète
    print("\n4️⃣ Sauvegarde complète:")
    saved = scraper.save_all_data(days=30)
    for key, path in saved.items():
        print(f"   ✅ {key}: {path}")
    
    print("\n" + "=" * 60)
    print("✅ Test terminé !")
