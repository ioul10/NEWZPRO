# =============================================================================
# NEWZ - Market Data Platform
# Fichier Principal — app.py
# =============================================================================

import streamlit as st
from pathlib import Path
import sys
from datetime import datetime

# DOIT ÊTRE LA PREMIÈRE COMMANDE
st.set_page_config(
    page_title="NEWZ | Market Data Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

sys.path.append(str(Path(__file__).resolve().parent))

try:
    from config.settings import COLORS, APP_INFO
except ImportError:
    COLORS = {
        'primary':   '#0b1e3d',
        'secondary': '#1a56db',
        'accent':    '#06b6d4',
        'success':   '#10b981',
        'danger':    '#ef4444',
        'warning':   '#f59e0b',
        'bg':        '#f1f5f9',
        'card':      '#ffffff',
        'muted':     '#64748b',
        'border':    '#e2e8f0',
        'light':     '#f8fafc',
    }
    APP_INFO = {
        'name':          'NEWZ',
        'version':       '2.0.0',
        'author':        'OULMADANI Ilyas & ATANANE Oussama',
        'company':       'CDG Capital',
        'copyright':     '© 2026 CDG Capital',
        'confidentiality': 'Document confidentiel — usage interne',
    }

# ─── SESSION STATE ─────────────────────────────────────────────────────────────

def init_session_state():
    defaults = {
        'data_loaded':              False,
        'excel_data':               {},
        'bourse_data':              {},
        'news_data':                [],
        'actions_data':             None,
        'fx_data':                  {},
        'fx_history':               {},
        'last_update':              None,
        'report_html':              None,
        'report_config':            {},
        'news_sources_status':      {},
        'top_movers':               None,
        'correlation_period':       90,
        'export_selected_sections': ['synthese', 'bourse', 'bam', 'devises', 'news'],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session_state()

# ─── STYLE GLOBAL ─────────────────────────────────────────────────────────────

st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=IBM+Plex+Mono:wght@400;600&family=Mulish:wght@300;400;500;600;700&display=swap');

  html, body, [class*="css"] {{
      font-family: 'Mulish', sans-serif;
      background: {COLORS['bg']};
  }}

  /* ─── HEADER ─────────────────────────────────────────────────────────────── */
  .app-header {{
      background: linear-gradient(135deg, {COLORS['primary']} 0%, #162d52 60%, #1a3a6b 100%);
      border-radius: 16px; padding: 22px 36px;
      margin-bottom: 24px; color: white;
      display: flex; align-items: center;
      justify-content: space-between;
      position: relative; overflow: hidden;
  }}
  .app-header::before {{
      content: 'NEWZ';
      position: absolute; right: 36px; top: 50%; transform: translateY(-50%);
      font-family: 'Syne', sans-serif; font-size: 80px; font-weight: 800;
      opacity: .04; letter-spacing: 8px; pointer-events: none;
  }}
  .app-header-left {{ position: relative; z-index: 1; }}
  .app-header-title {{
      font-family: 'Syne', sans-serif; font-size: 26px;
      font-weight: 800; letter-spacing: 1px; margin: 0;
  }}
  .app-header-sub {{
      font-family: 'IBM Plex Mono', monospace; font-size: 11px;
      opacity: .6; margin-top: 4px;
  }}
  .app-header-right {{
      position: relative; z-index: 1;
      text-align: right;
      font-family: 'IBM Plex Mono', monospace; font-size: 10px;
      opacity: .55; line-height: 1.8;
  }}

  /* ─── FOOTER ─────────────────────────────────────────────────────────────── */
  .app-footer {{
      margin-top: 40px;
      border-top: 1px solid {COLORS['border']};
      padding: 18px 0 8px 0;
      display: flex; justify-content: space-between; align-items: center;
      flex-wrap: wrap; gap: 8px;
  }}
  .app-footer-left {{
      font-family: 'IBM Plex Mono', monospace; font-size: 10px;
      color: {COLORS['muted']};
  }}
  .app-footer-right {{
      font-family: 'IBM Plex Mono', monospace; font-size: 10px;
      color: {COLORS['muted']}; text-align: right;
  }}
  .footer-dot {{
      display: inline-block; width: 6px; height: 6px;
      border-radius: 50%; background: {COLORS['success']};
      margin-right: 6px; vertical-align: middle;
  }}

  /* ─── SIDEBAR ────────────────────────────────────────────────────────────── */
  [data-testid="stSidebar"] {{
      background: {COLORS['card']};
      border-right: 1px solid {COLORS['border']};
  }}
  [data-testid="stSidebar"] * {{
      font-family: 'Mulish', sans-serif !important;
  }}
</style>
""", unsafe_allow_html=True)

# ─── HEADER ───────────────────────────────────────────────────────────────────

now_str = datetime.now().strftime("%d %b %Y — %H:%M")
version = APP_INFO.get('version', '2.0.0')
company = APP_INFO.get('company', 'CDG Capital')
conf    = APP_INFO.get('confidentiality', 'Usage interne')

st.markdown(f"""
<div class="app-header">
  <div class="app-header-left">
    <p class="app-header-title">📊 NEWZ</p>
    <p class="app-header-sub">Market Data Platform · v{version} · {company}</p>
  </div>
  <div class="app-header-right">
    {now_str}<br>
    {conf}
  </div>
</div>
""", unsafe_allow_html=True)

# ─── NAVIGATION ───────────────────────────────────────────────────────────────

pages = [
    st.Page("pages/home.py",             title="Accueil",        icon="🏠"),
    st.Page("pages/data_ingestion.py",   title="Data Ingestion", icon="📥"),
    st.Page("pages/bdc_statut.py",       title="BDC Statut",     icon="📊"),
    st.Page("pages/bam.py",              title="BAM",            icon="🏦"),
    st.Page("pages/macronews.py",        title="Macronews",      icon="📰"),
    st.Page("pages/export_rapport.py",   title="Export",         icon="📤"),
]

pg = st.navigation(pages)
pg.run()

# ─── FOOTER ───────────────────────────────────────────────────────────────────

author   = APP_INFO.get('author', 'OULMADANI Ilyas & ATANANE Oussama')
ts_full  = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
copyright = APP_INFO.get('copyright', '© 2026 CDG Capital')

st.markdown(f"""
<div class="app-footer">
  <div class="app-footer-left">
    <span class="footer-dot"></span>
    <b>{APP_INFO.get('name','NEWZ')}</b> v{version} &nbsp;·&nbsp; {author}
  </div>
  <div class="app-footer-right">
    MAJ : {ts_full} &nbsp;·&nbsp; {copyright}
  </div>
</div>
""", unsafe_allow_html=True)
