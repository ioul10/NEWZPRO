# =============================================================================
# NEWZ - Configuration
# =============================================================================

from pathlib import Path

# Couleurs CDG Capital
COLORS = {
    'primary': '#005696',
    'secondary': '#003d6b',
    'accent': '#00a8e8',
    'success': '#28a745',
    'warning': '#ffc107',
    'danger': '#dc3545',
    'light': '#f8f9fa'
}

# Chemins
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / 'data'
ASSETS_DIR = ROOT_DIR / 'assets'

# Création des dossiers
DATA_DIR.mkdir(exist_ok=True)
ASSETS_DIR.mkdir(exist_ok=True)

# Info application
APP_TITLE = "Newz | Market Data"
APP_VERSION = "2.0.0"
