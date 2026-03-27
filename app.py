# =============================================================================
# NEWZ - Market Data Platform
# app.py — Point d'entrée principal (Version 2.0)
# =============================================================================

import streamlit as st
from pathlib import Path
import sys
from datetime import datetime

st.set_page_config(
    page_title="Newz | Market Data Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

sys.path.append(str(Path(__file__).resolve().parent))

try:
    from config.settings import COLORS, APP_INFO
except ImportError:
    COLORS   = {'primary':'#0b1e3d','secondary':'#1a56db','accent':'#06b6d4',
                 'success':'#10b981','danger':'#ef4444','warning':'#f59e0b',
                 'bg':'#f1f5f9','card':'#ffffff','muted':'#64748b',
                 'border':'#e2e8f0','light':'#f8fafc'}
    APP_INFO = {'name':'Newz','version':'2.0.0',
                'author':'OULMADANI Ilyas & ATANANE Oussama',
                'copyright':'© 2026 CDG Capital',
                'confidentiality':'Usage interne uniquement',
                'company':'CDG Capital'}

try:
    from utils.design import inject_global_css
    inject_global_css()
except Exception:
    pass

# ── Sidebar branding + horloge dynamique ─────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="padding:20px 8px 16px 8px;border-bottom:1px solid rgba(255,255,255,.12);margin-bottom:16px;">
      <div style="font-family:'Syne',sans-serif;font-size:22px;font-weight:800;color:white;letter-spacing:-0.5px;">
        📊 NEWZ
      </div>
      <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:rgba(255,255,255,.45);
                  letter-spacing:2px;text-transform:uppercase;margin-top:3px;">
        Market Data Platform
      </div>
      <div style="font-family:'IBM Plex Mono',monospace;font-size:10px;
                  color:rgba(255,255,255,.35);margin-top:6px;">
        {APP_INFO.get('company','CDG Capital')} · v{APP_INFO.get('version','2.0.0')}
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.components.v1.html("""
    <div style="text-align:center;padding:6px 0 14px 0;">
      <div id="sc" style="font-family:'IBM Plex Mono',monospace;font-size:20px;
           font-weight:600;color:rgba(255,255,255,.9);letter-spacing:2px;">--:--:--</div>
      <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;
           color:rgba(255,255,255,.4);margin-top:3px;letter-spacing:2px;text-transform:uppercase;">
        Casablanca
      </div>
    </div>
    <script>
    (function(){
      function tick(){
        var t=new Date().toLocaleTimeString('fr-MA',{timeZone:'Africa/Casablanca',hour12:false});
        var e=document.getElementById('sc');if(e)e.textContent=t;setTimeout(tick,1000);
      }
      tick();
    })();
    </script>
    """, height=60)

    st.markdown(f"""
    <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;
                color:rgba(255,255,255,.35);padding:8px;text-align:center;
                border-top:1px solid rgba(255,255,255,.08);">
      Séance BVC : 09:00 – 15:30
    </div>
    """, unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
def init_session():
    for k, v in [
        ('data_loaded', False), ('excel_data', {}), ('bourse_data', {}),
        ('bdc_indices', None), ('bdc_top_movers', None), ('bdc_last_refresh', None),
        ('news_data', []), ('actions_data', None), ('last_update', None),
        ('fx_data', {}), ('fx_history', {}), ('inflation_rate', None),
        ('inflation_source', None), ('inflation_last_update', None),
        ('report_html', None), ('report_config', {}), ('top_movers', None),
        ('correlation_period', 90), ('news_sources_status', {}),
    ]:
        if k not in st.session_state:
            st.session_state[k] = v

init_session()

# ── Navigation ────────────────────────────────────────────────────────────────
pages = [
    st.Page("pages/home.py",           title="Accueil",        icon="🏠"),
    st.Page("pages/data_ingestion.py", title="Data Ingestion", icon="📥"),
    st.Page("pages/bdc_statut.py",     title="BDC Statut",     icon="📈"),
    st.Page("pages/bam.py",            title="BAM",            icon="🏦"),
    st.Page("pages/macronews.py",      title="Macronews",      icon="📰"),
    st.Page("pages/export.py",         title="Export",         icon="📤"),
]
pg = st.navigation(pages)
pg.run()

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="margin-top:48px;padding:14px 24px;
            border-top:1px solid {COLORS.get('border','#e2e8f0')};
            display:flex;justify-content:space-between;align-items:center;
            flex-wrap:wrap;gap:8px;font-family:'IBM Plex Mono',monospace;
            font-size:10px;color:{COLORS.get('muted','#64748b')};">
  <span><b style="color:{COLORS.get('primary','#0b1e3d')};">{APP_INFO.get('name','Newz')}</b>
    v{APP_INFO.get('version','2.0.0')} · {APP_INFO.get('author','')} · {APP_INFO.get('copyright','')}</span>
  <span>{APP_INFO.get('confidentiality','Usage interne')}</span>
  <span id="footer-time">{datetime.now().strftime('%d/%m/%Y %H:%M')}</span>
</div>
""", unsafe_allow_html=True)
