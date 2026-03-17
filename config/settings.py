# =============================================================================
# NEWZ - Configuration Centrale
# Fichier : config/settings.py
# =============================================================================

from pathlib import Path
from datetime import datetime

# -----------------------------------------------------------------------------
# 1. CHEMINS ET RÉPERTOIRES
# -----------------------------------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / 'data'
ASSETS_DIR = ROOT_DIR / 'assets'
REPORTS_DIR = ROOT_DIR / 'reports'
CACHE_DIR = ROOT_DIR / '.cache'

# Créer les dossiers s'ils n'existent pas
for directory in [DATA_DIR, ASSETS_DIR, REPORTS_DIR, CACHE_DIR]:
    directory.mkdir(exist_ok=True)

# -----------------------------------------------------------------------------
# 2. CHARTE GRAPHIQUE CDG CAPITAL
# -----------------------------------------------------------------------------

COLORS = {
    'primary': '#005696',      # Bleu CDG
    'secondary': '#003d6b',    # Bleu foncé
    'accent': '#00a8e8',       # Bleu clair
    'success': '#28a745',      # Vert (hausse)
    'warning': '#ffc107',      # Jaune (attention)
    'danger': '#dc3545',       # Rouge (baisse)
    'light': '#f8f9fa',        # Gris clair
    'dark': '#343a40',         # Gris foncé
    'white': '#ffffff'
}

FONTS = {
    'primary': "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
    'monospace': "'Courier New', Courier, monospace"
}

# -----------------------------------------------------------------------------
# 3. INDICES BOURSIERS
# -----------------------------------------------------------------------------

INDICES = {
    'MASI': {
        'name': 'MASI',
        'description': 'Moroccan All Shares Index',
        'base': 1000,
        'base_date': '1992-12-31'
    },
    'MSI20': {
        'name': 'MSI20',
        'description': 'Moroccan Most Active Shares Index',
        'base': 1000,
        'base_date': '2008-12-31'
    }
}

# -----------------------------------------------------------------------------
# 4. COMPOSITION MSI20 (À METTRE À JOUR TRIMESTRIELLEMENT)
# -----------------------------------------------------------------------------

MSI20_COMPOSITION = [
    {'nom': 'Attijariwafa Bank', 'ticker': 'ATT', 'secteur': 'Banque'},
    {'nom': 'Maroc Telecom', 'ticker': 'IAM', 'secteur': 'Télécom'},
    {'nom': 'BCP', 'ticker': 'BCP', 'secteur': 'Banque'},
    {'nom': 'BMCE Bank of Africa', 'ticker': 'BMCE', 'secteur': 'Banque'},
    {'nom': 'Cosumar', 'ticker': 'CSR', 'secteur': 'Agroalimentaire'},
    {'nom': 'LafargeHolcim', 'ticker': 'LHM', 'secteur': 'Matériaux'},
    {'nom': 'CIH Bank', 'ticker': 'CIH', 'secteur': 'Banque'},
    {'nom': 'Sonasid', 'ticker': 'SID', 'secteur': 'Métallurgie'},
    {'nom': 'Managem', 'ticker': 'MNG', 'secteur': 'Mines'},
    {'nom': 'Crédit du Maroc', 'ticker': 'CDM', 'secteur': 'Banque'},
    {'nom': 'SNI (Al Mada)', 'ticker': 'SNI', 'secteur': 'Holding'},
    {'nom': 'LabelVie', 'ticker': 'LVB', 'secteur': 'Distribution'},
    {'nom': 'Auto Hall', 'ticker': 'AUT', 'secteur': 'Automobile'},
    {'nom': 'Afriquia Gaz', 'ticker': 'AFG', 'secteur': 'Énergie'},
    {'nom': 'BMCI', 'ticker': 'BMC', 'secteur': 'Banque'},
    {'nom': 'HPS', 'ticker': 'HPS', 'secteur': 'Technologie'},
    {'nom': 'Wafacash', 'ticker': 'WAC', 'secteur': 'Finance'},
    {'nom': 'Wafa Assurance', 'ticker': 'WAA', 'secteur': 'Assurance'},
    {'nom': 'Ciments du Maroc', 'ticker': 'CIM', 'secteur': 'Matériaux'},
    {'nom': 'Saham RE', 'ticker': 'SAH', 'secteur': 'Assurance'}
]

# -----------------------------------------------------------------------------
# 5. SOURCES DE DONNÉES
# -----------------------------------------------------------------------------

DATA_SOURCES = {
    'bourse_casa': {
        'name': 'Bourse de Casablanca',
        'url': 'https://www.casablanca-bourse.com',
        'type': 'official',
        'priority': 1
    },
    'ilboursa': {
        'name': 'Ilboursa',
        'url': 'https://www.ilboursa.com',
        'type': 'news',
        'priority': 2
    },
    'yahoo_finance': {
        'name': 'Yahoo Finance',
        'url': 'https://finance.yahoo.com',
        'type': 'api',
        'priority': 3
    },
    'bam': {
        'name': 'Bank Al-Maghrib',
        'url': 'https://www.bkam.ma',
        'type': 'official',
        'priority': 1
    },
    'hcp': {
        'name': 'Haut Commissariat au Plan',
        'url': 'https://www.hcp.ma',
        'type': 'official',
        'priority': 1
    }
}

# -----------------------------------------------------------------------------
# 6. CONFIGURATION SCRAPING
# -----------------------------------------------------------------------------

SCRAPER_CONFIG = {
    'timeout': 10,
    'retry_attempts': 3,
    'delay_between_requests': 1,  # secondes
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# -----------------------------------------------------------------------------
# 7. CONFIGURATION EXPORT
# -----------------------------------------------------------------------------

EXPORT_CONFIG = {
    'default_format': 'html',
    'pdf_margins': {'top': 20, 'bottom': 20, 'left': 20, 'right': 20},
    'include_charts': True,
    'include_watermark': True
}

# -----------------------------------------------------------------------------
# 8. INFORMATIONS APPLICATION
# -----------------------------------------------------------------------------

APP_INFO = {
    'name': 'Newz',
    'version': '2.0.0',
    'description': 'Market Data Platform for CDG Capital',
    'author': 'CDG Capital - Market Data Team',
    'copyright': '© 2025 CDG Capital',
    'confidentiality': 'Usage interne uniquement'
}

# -----------------------------------------------------------------------------
# 9. HORAIRES DE LA BOURSE
# -----------------------------------------------------------------------------

MARKET_HOURS = {
    'open': '09:00',
    'close': '15:30',
    'timezone': 'Africa/Casablanca',
    'working_days': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
}

# -----------------------------------------------------------------------------
# 10. FONCTIONS UTILITAIRES
# -----------------------------------------------------------------------------

def get_msi20_tickers():
    """Retourne la liste des tickers du MSI20"""
    return [action['ticker'] for action in MSI20_COMPOSITION]

def get_msi20_names():
    """Retourne la liste des noms du MSI20"""
    return [action['nom'] for action in MSI20_COMPOSITION]

def get_sectors():
    """Retourne la liste des secteurs représentés"""
    return list(set(action['secteur'] for action in MSI20_COMPOSITION))

def is_market_open():
    """Vérifie si le marché est ouvert"""
    from datetime import datetime
    import pytz
    
    now = datetime.now(pytz.timezone('Africa/Casablanca'))
    
    # Vérifier jour ouvré
    if now.strftime('%A') not in MARKET_HOURS['working_days']:
        return False
    
    # Vérifier horaire
    open_time = datetime.strptime(MARKET_HOURS['open'], '%H:%M').time()
    close_time = datetime.strptime(MARKET_HOURS['close'], '%H:%M').time()
    
    return open_time <= now.time() <= close_time

def get_last_update_timestamp():
    """Retourne le timestamp de dernière mise à jour"""
    return datetime.now().strftime('%d/%m/%Y %H:%M:%S')

# -----------------------------------------------------------------------------
# 11. VALIDATION AU CHARGEMENT
# -----------------------------------------------------------------------------

def validate_config():
    """Valide la configuration au chargement"""
    errors = []
    
    # Vérifier les dossiers
    for directory in [DATA_DIR, ASSETS_DIR, REPORTS_DIR]:
        if not directory.exists():
            try:
                directory.mkdir(exist_ok=True)
            except Exception as e:
                errors.append(f"Impossible de créer {directory}: {str(e)}")
    
    # Vérifier MSI20
    if len(MSI20_COMPOSITION) != 20:
        errors.append(f"MSI20: {len(MSI20_COMPOSITION)} actions au lieu de 20")
    
    if errors:
        print("⚠️ Avertissements de configuration:")
        for error in errors:
            print(f"  - {error}")
    
    return len(errors) == 0

# Validation automatique au chargement du module
validate_config()
