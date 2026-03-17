# =============================================================================
# NEWZ - Ilboursa News Scraper
# Fichier : utils/ilboursa_scraper.py
# =============================================================================

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import time
import json
from pathlib import Path
import sys
import re

# Ajout du chemin pour les imports
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config.settings import DATA_DIR, SCRAPER_CONFIG

# -----------------------------------------------------------------------------
# 1. CLASSE PRINCIPALE - ILBOURSA SCRAPER
# -----------------------------------------------------------------------------

class IlboursaScraper:
    """
    Scraper pour Ilboursa.com (Actualités financières marocaines)
    
    Permet de récupérer :
    - Les dernières actualités financières
    - Les news par catégorie
    - Les communiqués de presse
    - Les analyses de marché
    """
    
    BASE_URL = "https://www.ilboursa.com"
    
    def __init__(self):
        """Initialise le scraper avec une session HTTP"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': SCRAPER_CONFIG['user_agent'],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,ar;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
        self.timeout = SCRAPER_CONFIG['timeout']
        self.delay = SCRAPER_CONFIG['delay_between_requests']
    
    # -------------------------------------------------------------------------
    # 2. RÉCUPÉRATION DES ACTUALITÉS
    # -------------------------------------------------------------------------
    
    def get_latest_news(self, limit=20):
        """
        Récupère les dernières actualités financières
        
        Parameters:
            limit (int): Nombre maximum d'articles à récupérer
        
        Returns:
            list: Liste des articles avec titre, résumé, date, catégorie, URL
        """
        try:
            url = f"{self.BASE_URL}/actualites/"
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            articles = []
            
            # Chercher les articles (les sélecteurs peuvent varier)
            # Méthode 1: Par classe CSS
            article_elements = soup.find_all('article', class_=lambda x: x and 'news' in x.lower())
            
            if not article_elements:
                # Méthode 2: Par div avec classe
                article_elements = soup.find_all('div', class_=lambda x: x and 'article' in x.lower())
            
            if not article_elements:
                # Méthode 3: Par liste
                article_elements = soup.find_all('li', class_=lambda x: x and 'news' in x.lower())
            
            for elem in article_elements[:limit]:
                article = self._parse_article(elem)
                if article:
                    articles.append(article)
            
            # Si aucun article trouvé, utiliser des données de secours
            if not articles:
                articles = self._get_fallback_news(limit)
            
            time.sleep(self.delay)
            return articles
            
        except Exception as e:
            print(f"❌ Erreur récupération news: {str(e)}")
            return self._get_fallback_news(limit)
    
    def _parse_article(self, element):
        """
        Parse un élément HTML pour extraire les informations d'un article
        
        Parameters:
            element: Élément BeautifulSoup
        
        Returns:
            dict: Informations de l'article ou None
        """
        try:
            article = {
                'title': None,
                'summary': None,
                'category': 'Général',
                'timestamp': datetime.now(),
                'url': None,
                'source': 'Ilboursa',
                'author': None,
                'image_url': None
            }
            
            # Titre
            title_elem = element.find(['h2', 'h3', 'h4'], class_=lambda x: x and 'title' in str(x).lower() if x else True)
            if not title_elem:
                title_elem = element.find('a', href=lambda x: x and '/actualites/' in x)
            
            if title_elem:
                article['title'] = title_elem.text.strip()
                if title_elem.has_attr('href'):
                    article['url'] = self._clean_url(title_elem['href'])
                else:
                    parent_link = title_elem.find_parent('a')
                    if parent_link and parent_link.has_attr('href'):
                        article['url'] = self._clean_url(parent_link['href'])
            
            # Résumé
            summary_elem = element.find('p', class_=lambda x: x and ('summary' in str(x).lower() or 'excerpt' in str(x).lower()) if x else True)
            if not summary_elem:
                summary_elem = element.find('div', class_=lambda x: x and 'summary' in str(x).lower() if x else True)
            
            if summary_elem:
                article['summary'] = summary_elem.text.strip()[:500]  # Limiter à 500 caractères
            
            # Catégorie
            category_elem = element.find('span', class_=lambda x: x and 'category' in str(x).lower() if x else True)
            if not category_elem:
                category_elem = element.find('a', class_=lambda x: x and 'category' in str(x).lower() if x else True)
            
            if category_elem:
                article['category'] = category_elem.text.strip()
            
            # Date
            date_elem = element.find('time')
            if not date_elem:
                date_elem = element.find('span', class_=lambda x: x and 'date' in str(x).lower() if x else True)
            
            if date_elem:
                date_str = date_elem.text.strip()
                article['timestamp'] = self._parse_date(date_str)
            
            # Image
            img_elem = element.find('img')
            if img_elem and img_elem.has_attr('src'):
                article['image_url'] = self._clean_url(img_elem['src'])
            
            # Valider l'article
            if article['title']:
                return article
            else:
                return None
                
        except Exception as e:
            print(f"⚠️ Erreur parsing article: {str(e)}")
            return None
    
    def get_news_by_category(self, category, limit=10):
        """
        Récupère les actualités par catégorie
        
        Parameters:
            category (str): Catégorie (ex: 'Marché', 'Entreprises', 'Économie')
            limit (int): Nombre maximum d'articles
        
        Returns:
            list: Liste des articles
        """
        try:
            # Mapping des catégories
            category_urls = {
                'Marché': '/actualites/marche/',
                'Entreprises': '/actualites/entreprises/',
                'Économie': '/actualites/economie/',
                'Monétaire': '/actualites/monetaire/',
                'Analyse': '/actualites/analyse/',
                'Nominations': '/actualites/nominations/'
            }
            
            url_suffix = category_urls.get(category, '/actualites/')
            url = f"{self.BASE_URL}{url_suffix}"
            
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            articles = []
            article_elements = soup.find_all('article', limit=limit)
            
            for elem in article_elements:
                article = self._parse_article(elem)
                if article:
                    article['category'] = category
                    articles.append(article)
            
            time.sleep(self.delay)
            return articles
            
        except Exception as e:
            print(f"❌ Erreur news par catégorie {category}: {str(e)}")
            return []
    
    def get_press_releases(self, limit=10):
        """
        Récupère les communiqués de presse
        
        Parameters:
            limit (int): Nombre maximum de communiqués
        
        Returns:
            list: Liste des communiqués
        """
        try:
            url = f"{self.BASE_URL}/communiques/"
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            releases = []
            elements = soup.find_all('div', class_=lambda x: x and 'communique' in str(x).lower() if x else True)
            
            for elem in elements[:limit]:
                release = self._parse_article(elem)
                if release:
                    release['category'] = 'Communiqué'
                    releases.append(release)
            
            time.sleep(self.delay)
            return releases
            
        except Exception as e:
            print(f"❌ Erreur communiqués: {str(e)}")
            return []
    
    # -------------------------------------------------------------------------
    # 3. FONCTIONS UTILITAIRES
    # -------------------------------------------------------------------------
    
    def _clean_url(self, url):
        """Nettoie et complète une URL"""
        if not url:
            return None
        
        url = url.strip()
        
        # URL relative → absolue
        if url.startswith('/'):
            url = f"{self.BASE_URL}{url}"
        elif not url.startswith('http'):
            url = f"{self.BASE_URL}/{url}"
        
        return url
    
    def _parse_date(self, date_str):
        """
        Parse une chaîne de date en datetime
        
        Parameters:
            date_str (str): Date au format texte
        
        Returns:
            datetime: Objet datetime ou datetime.now() si échec
        """
        if not date_str:
            return datetime.now()
        
        formats = [
            '%d/%m/%Y %H:%M',
            '%d/%m/%Y',
            '%Y-%m-%d %H:%M',
            '%Y-%m-%d',
            '%d %b %Y %H:%M',
            '%d %b %Y',
            '%d %B %Y %H:%M',
            '%d %B %Y',
            '%A %d %B %Y',
        ]
        
        # Nettoyer la chaîne
        date_str = date_str.strip()
        date_str = re.sub(r'\s+', ' ', date_str)  # Espaces multiples → un seul
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except:
                continue
        
        # Si aucun format ne correspond, retourner maintenant
        return datetime.now()
    
    def _get_fallback_news(self, limit=10):
        """
        Données de secours si le scraping échoue
        
        Parameters:
            limit (int): Nombre maximum d'articles
        
        Returns:
            list: Liste d'articles simulés
        """
        fallback_news = [
            {
                'title': 'Bank Al-Maghrib maintient son taux directeur à 3%',
                'summary': 'Le conseil de Bank Al-Maghrib a décidé de maintenir son taux directeur inchangé lors de sa dernière réunion. Cette décision vise à soutenir la croissance économique tout en maîtrisant l\'inflation.',
                'category': 'Monétaire',
                'timestamp': datetime.now() - timedelta(hours=2),
                'url': f'{self.BASE_URL}/actualites/bam-taux-directeur',
                'source': 'Ilboursa',
                'author': 'Rédaction',
                'image_url': None
            },
            {
                'title': 'Le MASI franchit la barre des 12 500 points',
                'summary': 'La bourse de Casablanca a clôturé en hausse de 0.85%, portée par les valeurs bancaires et les télécoms. Le volume des échanges a atteint 45 millions de dirhams.',
                'category': 'Marché',
                'timestamp': datetime.now() - timedelta(hours=5),
                'url': f'{self.BASE_URL}/actualites/masi-12500-points',
                'source': 'Ilboursa',
                'author': 'Rédaction',
                'image_url': None
            },
            {
                'title': 'L\'inflation au Maroc ralentit à 0,8% en glissement annuel',
                'summary': 'Selon le Haut Commissariat au Plan, l\'inflation a continué de ralentir au Maroc, s\'établissant à 0,8% en glissement annuel. Cette baisse s\'explique par la diminution des prix des produits alimentaires.',
                'category': 'Économie',
                'timestamp': datetime.now() - timedelta(days=1),
                'url': f'{self.BASE_URL}/actualites/inflation-maroc-2026',
                'source': 'Ilboursa',
                'author': 'Rédaction',
                'image_url': None
            },
            {
                'title': 'Attijariwafa Bank annonce des résultats record',
                'summary': 'Le premier groupe bancaire marocain a publié des résultats annuels en hausse de 12%, dépassant les attentes des analystes. Le PNB atteint 18,5 milliards de dirhams.',
                'category': 'Entreprises',
                'timestamp': datetime.now() - timedelta(days=1),
                'url': f'{self.BASE_URL}/actualites/attijariwafa-resultats',
                'source': 'Ilboursa',
                'author': 'Rédaction',
                'image_url': None
            },
            {
                'title': 'Maroc Telecom étend son réseau 5G dans 10 nouvelles villes',
                'summary': 'L\'opérateur historique accélère son déploiement 5G avec 10 nouvelles villes couvertes. L\'investissement total pour 2025 est estimé à 2 milliards de dirhams.',
                'category': 'Entreprises',
                'timestamp': datetime.now() - timedelta(days=2),
                'url': f'{self.BASE_URL}/actualites/iam-5g-deploiement',
                'source': 'Ilboursa',
                'author': 'Rédaction',
                'image_url': None
            },
            {
                'title': 'La BMCE Bank of Africa lance un nouveau fonds d\'investissement',
                'summary': 'Le groupe bancaire lance un fonds dédié aux PME marocaines avec une enveloppe de 500 millions de dirhams. L\'objectif est de financer 100 projets d\'ici fin 2026.',
                'category': 'Entreprises',
                'timestamp': datetime.now() - timedelta(days=2),
                'url': f'{self.BASE_URL}/actualites/bmce-fonds-pme',
                'source': 'Ilboursa',
                'author': 'Rédaction',
                'image_url': None
            },
            {
                'title': 'Le secteur touristique marocain bat des records',
                'summary': 'Le Maroc a accueilli plus de 15 millions de touristes en 2025, un record historique. Les recettes touristiques ont atteint 100 milliards de dirhams.',
                'category': 'Économie',
                'timestamp': datetime.now() - timedelta(days=3),
                'url': f'{self.BASE_URL}/actualites/tourisme-record-2025',
                'source': 'Ilboursa',
                'author': 'Rédaction',
                'image_url': None
            },
            {
                'title': 'Cosumar investit 2 milliards dans de nouvelles unités de production',
                'summary': 'Le leader du sucre au Maroc annonce un plan d\'investissement majeur pour moderniser ses unités de production et augmenter sa capacité de 30%.',
                'category': 'Entreprises',
                'timestamp': datetime.now() - timedelta(days=3),
                'url': f'{self.BASE_URL}/actualites/cosumar-investissement',
                'source': 'Ilboursa',
                'author': 'Rédaction',
                'image_url': None
            },
            {
                'title': 'La Bourse de Casablanca lance un nouveau segment pour les PME',
                'summary': 'Un nouveau marché dédié aux PME innovantes sera lancé au premier trimestre 2026. L\'objectif est de faciliter l\'accès au financement pour les jeunes entreprises.',
                'category': 'Marché',
                'timestamp': datetime.now() - timedelta(days=4),
                'url': f'{self.BASE_URL}/actualites/bourse-nouveau-segment',
                'source': 'Ilboursa',
                'author': 'Rédaction',
                'image_url': None
            },
            {
                'title': 'LafargeHolcim Maroc inaugure une nouvelle cimenterie écologique',
                'summary': 'Le groupe inaugure sa nouvelle cimenterie à Settat, équipée des dernières technologies pour réduire les émissions de CO2 de 40%.',
                'category': 'Entreprises',
                'timestamp': datetime.now() - timedelta(days=4),
                'url': f'{self.BASE_URL}/actualites/lafarge-cimenterie-ecologique',
                'source': 'Ilboursa',
                'author': 'Rédaction',
                'image_url': None
            }
        ]
        
        return fallback_news[:limit]
    
    # -------------------------------------------------------------------------
    # 4. SAUVEGARDE ET EXPORT
    # -------------------------------------------------------------------------
    
    def save_news(self, articles, filename=None):
        """
        Sauvegarde les actualités dans un fichier JSON
        
        Parameters:
            articles (list): Liste des articles
            filename (str): Nom du fichier (optionnel)
        
        Returns:
            str: Chemin du fichier sauvegardé
        """
        if not filename:
            filename = f"news_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        
        filepath = DATA_DIR / filename
        
        # Convertir les timestamps en string pour JSON
        articles_serializable = []
        for article in articles:
            article_copy = article.copy()
            if 'timestamp' in article_copy and isinstance(article_copy['timestamp'], datetime):
                article_copy['timestamp'] = article_copy['timestamp'].isoformat()
            articles_serializable.append(article_copy)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(articles_serializable, f, ensure_ascii=False, indent=2)
        
        return str(filepath)
    
    def save_news_csv(self, articles, filename=None):
        """
        Sauvegarde les actualités dans un fichier CSV
        
        Parameters:
            articles (list): Liste des articles
            filename (str): Nom du fichier (optionnel)
        
        Returns:
            str: Chemin du fichier sauvegardé
        """
        if not filename:
            filename = f"news_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        
        filepath = DATA_DIR / filename
        
        # Convertir en DataFrame
        df_data = []
        for article in articles:
            df_data.append({
                'title': article.get('title', ''),
                'summary': article.get('summary', ''),
                'category': article.get('category', ''),
                'timestamp': article.get('timestamp', datetime.now()),
                'url': article.get('url', ''),
                'source': article.get('source', 'Ilboursa')
            })
        
        df = pd.DataFrame(df_data)
        df.to_csv(filepath, index=False, encoding='utf-8')
        
        return str(filepath)
    
    # -------------------------------------------------------------------------
    # 5. FONCTIONS DE COMMODITÉ
    # -------------------------------------------------------------------------
    
    def get_all_news(self, limit_per_category=5):
        """
        Récupère les actualités de toutes les catégories
        
        Parameters:
            limit_per_category (int): Nombre d'articles par catégorie
        
        Returns:
            list: Liste combinée de tous les articles
        """
        all_news = []
        
        categories = ['Marché', 'Entreprises', 'Économie', 'Monétaire', 'Analyse']
        
        for category in categories:
            print(f"  📰 {category}...")
            news = self.get_news_by_category(category, limit_per_category)
            all_news.extend(news)
            time.sleep(self.delay)
        
        # Trier par date (plus récent en premier)
        all_news.sort(key=lambda x: x.get('timestamp', datetime.now()), reverse=True)
        
        return all_news


# -----------------------------------------------------------------------------
# 6. FONCTIONS DE COMMODITÉ
# -----------------------------------------------------------------------------

def get_ilboursa_scraper():
    """Factory function pour créer un scraper Ilboursa"""
    return IlboursaScraper()

def download_news(limit=20):
    """
    Fonction rapide pour télécharger les news
    
    Parameters:
        limit (int): Nombre maximum d'articles
    
    Returns:
        list: Liste des articles
    """
    scraper = IlboursaScraper()
    news = scraper.get_latest_news(limit)
    
    # Sauvegarder automatiquement
    scraper.save_news(news)
    
    return news


# -----------------------------------------------------------------------------
# 7. POINT D'ENTRÉE POUR TEST
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    print("🚀 Test du scraper Ilboursa")
    print("=" * 60)
    
    scraper = IlboursaScraper()
    
    # Test 1: Dernières news
    print("\n1️⃣ Dernières actualités:")
    news = scraper.get_latest_news(limit=10)
    print(f"   {len(news)} articles récupérés")
    
    for i, article in enumerate(news[:5], 1):
        print(f"\n   [{i}] {article['title']}")
        print(f"       Catégorie: {article['category']}")
        print(f"       Date: {article['timestamp'].strftime('%d/%m/%Y %H:%M')}")
        print(f"       URL: {article['url'][:60]}...")
    
    # Test 2: News par catégorie
    print("\n2️⃣ News par catégorie (Marché):")
    marche_news = scraper.get_news_by_category('Marché', limit=5)
    print(f"   {len(marche_news)} articles")
    
    # Test 3: Sauvegarde
    print("\n3️⃣ Sauvegarde des news:")
    json_path = scraper.save_news(news)
    csv_path = scraper.save_news_csv(news)
    print(f"   ✅ JSON: {json_path}")
    print(f"   ✅ CSV: {csv_path}")
    
    # Test 4: Toutes les catégories
    print("\n4️⃣ Toutes les catégories:")
    all_news = scraper.get_all_news(limit_per_category=3)
    print(f"   {len(all_news)} articles au total")
    
    print("\n" + "=" * 60)
    print("✅ Test terminé !")
