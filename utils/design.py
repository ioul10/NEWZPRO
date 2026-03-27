# =============================================================================
# NEWZ — Système de Design Partagé
# utils/design.py
#
# Importer dans chaque page :
#   from utils.design import inject_global_css, page_hero, market_clock_html
# =============================================================================

import streamlit as st
from datetime import datetime
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))

try:
    from config.settings import COLORS as _IMP
    _DEFAULTS = {
        'primary': '#0b1e3d', 'secondary': '#1a56db', 'accent': '#06b6d4',
        'success': '#10b981', 'danger': '#ef4444', 'warning': '#f59e0b',
        'bg': '#f1f5f9', 'card': '#ffffff', 'muted': '#64748b',
        'border': '#e2e8f0', 'light': '#f8fafc',
    }
    COLORS = {**_DEFAULTS, **_IMP}
except ImportError:
    COLORS = {
        'primary': '#0b1e3d', 'secondary': '#1a56db', 'accent': '#06b6d4',
        'success': '#10b981', 'danger': '#ef4444', 'warning': '#f59e0b',
        'bg': '#f1f5f9', 'card': '#ffffff', 'muted': '#64748b',
        'border': '#e2e8f0', 'light': '#f8fafc',
    }


def inject_global_css():
    """
    Injecte le CSS global de l'application.
    À appeler en haut de chaque page (une seule fois suffit car Streamlit
    re-render la page à chaque interaction).
    """
    C = COLORS
    st.markdown(f"""
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=IBM+Plex+Mono:wght@400;600&family=Mulish:wght@300;400;500;600;700&display=swap');

      /* ── BASE ──────────────────────────────────────────────────────────── */
      html, body, [class*="css"] {{
          font-family: 'Mulish', sans-serif !important;
          background: {C['bg']} !important;
      }}
      .block-container {{
          padding-top: 1.5rem !important;
          max-width: 1200px !important;
      }}

      /* ── HERO ──────────────────────────────────────────────────────────── */
      .page-hero {{
          background: linear-gradient(135deg, {C['primary']} 0%, #162d52 60%, #1a3a6b 100%);
          border-radius: 18px; padding: 28px 36px; margin-bottom: 28px;
          color: white; position: relative; overflow: hidden;
      }}
      .page-hero::before {{
          content: ''; position: absolute; bottom: -50px; right: -50px;
          width: 220px; height: 220px; border-radius: 50%;
          background: rgba(6,182,212,.07);
      }}
      .page-hero::after {{
          content: ''; position: absolute; top: -30px; right: 120px;
          width: 100px; height: 100px; border-radius: 50%;
          background: rgba(255,255,255,.03);
      }}
      .hero-eyebrow {{
          font-family: 'IBM Plex Mono', monospace;
          font-size: 10px; letter-spacing: 2.5px;
          text-transform: uppercase; opacity: .55; margin-bottom: 6px;
      }}
      .hero-title {{
          font-family: 'Syne', sans-serif;
          font-size: 26px; font-weight: 800; margin: 0; line-height: 1.2;
      }}
      .hero-sub {{
          font-family: 'IBM Plex Mono', monospace;
          font-size: 11px; opacity: .6; margin-top: 8px;
      }}
      .hero-tag {{
          display: inline-block;
          background: rgba(6,182,212,.2); border: 1px solid rgba(6,182,212,.35);
          color: #67e8f9; border-radius: 6px; padding: 2px 10px;
          font-family: 'IBM Plex Mono', monospace; font-size: 10px;
          font-weight: 600; margin: 8px 4px 0 0;
      }}
      .hero-clock {{
          font-family: 'IBM Plex Mono', monospace;
          font-size: 13px; font-weight: 600; opacity: .85;
          letter-spacing: 1px; margin-top: 6px;
      }}

      /* ── MARKET STATUS BANNER ───────────────────────────────────────────── */
      .market-banner {{
          border-radius: 12px; padding: 14px 20px; margin-bottom: 20px;
          display: flex; align-items: center; gap: 14px;
      }}
      .market-banner.open   {{ background: linear-gradient(90deg, #052e16, #064e3b);
                               border-left: 4px solid {C['success']}; }}
      .market-banner.closed {{ background: linear-gradient(90deg, #1c0a0a, #450a0a);
                               border-left: 4px solid {C['danger']}; }}
      .market-dot {{ font-size: 24px; }}
      .market-text-main {{ font-size: 15px; font-weight: 700; color: white; }}
      .market-text-sub  {{
          font-size: 11px; color: rgba(255,255,255,.65);
          font-family: 'IBM Plex Mono', monospace; margin-top: 2px;
      }}

      /* ── STEP / SECTION CARD ────────────────────────────────────────────── */
      .step-card {{
          background: {C['card']}; border: 1px solid {C['border']};
          border-radius: 16px; padding: 24px 28px; margin-bottom: 20px;
          box-shadow: 0 1px 4px rgba(0,0,0,.05);
      }}
      .sec-title {{
          font-family: 'Syne', sans-serif; font-size: 15px; font-weight: 700;
          color: {C['primary']}; border-left: 3px solid {C['accent']};
          padding-left: 12px; margin: 28px 0 16px 0;
      }}
      .step-title {{
          font-family: 'Syne', sans-serif; font-size: 16px; font-weight: 700;
          color: {C['primary']}; display: flex; align-items: center;
          gap: 10px; margin-bottom: 14px;
      }}
      .step-badge {{
          background: {C['accent']}22; color: {C['accent']};
          border-radius: 8px; padding: 2px 10px;
          font-family: 'IBM Plex Mono', monospace; font-size: 11px; font-weight: 600;
      }}
      .step-badge-green {{ background:#dcfce7; color:#166534; border-radius:8px;
                           padding:2px 10px; font-family:'IBM Plex Mono',monospace;
                           font-size:11px; font-weight:600; }}
      .step-badge-orange {{ background:#fff7ed; color:#9a3412; border-radius:8px;
                            padding:2px 10px; font-family:'IBM Plex Mono',monospace;
                            font-size:11px; font-weight:600; }}

      /* ── KPI CARDS ─────────────────────────────────────────────────────── */
      .kpi-row {{ display:flex; gap:14px; flex-wrap:wrap; margin-bottom:20px; }}
      .kpi-mini {{
          background:{C['card']}; border:1px solid {C['border']};
          border-radius:12px; padding:16px 18px; flex:1; min-width:110px;
          position:relative; overflow:hidden;
      }}
      .kpi-mini::before {{
          content:''; position:absolute; top:0; left:0; right:0; height:3px;
          background: linear-gradient(90deg, {C['accent']}, {C['secondary']});
      }}
      .kpi-mini.up::before    {{ background: linear-gradient(90deg,{C['success']},#34d399); }}
      .kpi-mini.down::before  {{ background: linear-gradient(90deg,{C['danger']},#f87171); }}
      .kpi-mini.warn::before  {{ background: linear-gradient(90deg,{C['warning']},#fcd34d); }}
      .kpi-mini-label {{
          font-family:'IBM Plex Mono',monospace; font-size:9px;
          letter-spacing:1.5px; text-transform:uppercase; color:{C['muted']};
      }}
      .kpi-mini-value {{
          font-family:'Syne',sans-serif; font-size:24px;
          font-weight:700; color:{C['primary']}; margin-top:6px; line-height:1.1;
      }}
      .kpi-mini-sub {{ font-size:11px; color:{C['muted']}; margin-top:3px; }}
      .kpi-mini-delta-up   {{ font-size:12px; color:{C['success']}; font-weight:700; }}
      .kpi-mini-delta-down {{ font-size:12px; color:{C['danger']};  font-weight:700; }}
      .kpi-mini-delta-flat {{ font-size:12px; color:{C['muted']};   font-weight:700; }}

      /* ── STATUS CHIPS ───────────────────────────────────────────────────── */
      .chip-ok   {{ display:inline-flex;align-items:center;gap:4px;background:#dcfce7;
                    color:#166534;border-radius:20px;padding:4px 12px;font-size:11px;font-weight:700; }}
      .chip-err  {{ display:inline-flex;align-items:center;gap:4px;background:#fee2e2;
                    color:#991b1b;border-radius:20px;padding:4px 12px;font-size:11px;font-weight:700; }}
      .chip-wait {{ display:inline-flex;align-items:center;gap:4px;background:#f1f5f9;
                    color:{C['muted']};border-radius:20px;padding:4px 12px;font-size:11px;font-weight:700; }}
      .chip-info {{ display:inline-flex;align-items:center;gap:4px;background:{C['accent']}15;
                    color:{C['accent']};border-radius:20px;padding:4px 12px;font-size:11px;font-weight:700; }}
      .status-row {{ display:flex; gap:10px; flex-wrap:wrap; margin-bottom:18px; }}
      .status-pill {{ display:inline-flex;align-items:center;gap:6px;border-radius:20px;
                      padding:5px 14px;font-size:12px;font-weight:600; }}
      .status-pill.ok    {{ background:#dcfce7; color:#166534; }}
      .status-pill.warn  {{ background:#fff7ed; color:#9a3412; }}
      .status-pill.empty {{ background:#f1f5f9; color:{C['muted']}; }}

      /* ── SOURCE BAR ─────────────────────────────────────────────────────── */
      .src-bar {{
          font-family:'IBM Plex Mono',monospace; font-size:10px;
          background:{C['light']}; border:1px solid {C['border']};
          border-radius:8px; padding:6px 14px; color:{C['muted']};
          margin-top:8px; display:inline-block;
      }}

      /* ── NEWS CARD ──────────────────────────────────────────────────────── */
      .news-card {{
          background:{C['card']}; border:1px solid {C['border']};
          border-radius:12px; padding:14px 18px; margin-bottom:10px;
          transition: box-shadow .15s;
      }}
      .news-card:hover {{ box-shadow: 0 4px 16px rgba(0,0,0,.09); }}
      .news-card-title {{ font-size:14px;font-weight:600;color:{C['primary']};line-height:1.4; }}
      .news-card-meta  {{ font-size:11px;color:{C['muted']};margin-top:5px; }}
      .src-badge {{ display:inline-block;border-radius:5px;padding:2px 8px;font-size:10px;
                    font-weight:700;margin-right:5px;background:{C['accent']}15;color:{C['accent']}; }}
      .cat-badge {{ display:inline-block;border-radius:5px;padding:2px 8px;font-size:10px;
                    font-weight:700;background:{C['warning']}20;color:#92400e; }}

      /* ── MOVER BADGES ───────────────────────────────────────────────────── */
      .badge-up   {{ background:#dcfce7;color:#166534;border-radius:6px;
                     padding:3px 9px;font-size:12px;font-weight:700; }}
      .badge-down {{ background:#fee2e2;color:#991b1b;border-radius:6px;
                     padding:3px 9px;font-size:12px;font-weight:700; }}

      /* ── FX CARD ────────────────────────────────────────────────────────── */
      .fx-card {{
          background:{C['card']};border:1px solid {C['border']};
          border-radius:14px;padding:20px 22px;margin-bottom:14px;
      }}
      .fx-pair {{ font-family:'IBM Plex Mono',monospace;font-size:13px;
                  font-weight:600;color:{C['muted']};letter-spacing:1px; }}
      .fx-rate {{ font-family:'Syne',sans-serif;font-size:32px;
                  font-weight:800;color:{C['primary']};line-height:1.1;margin:4px 0; }}
      .fx-spread {{ font-size:11px;color:{C['muted']};font-family:'IBM Plex Mono',monospace; }}

      /* ── EXPANDER & TABS ────────────────────────────────────────────────── */
      div[data-testid="stExpander"] {{
          border:1px solid {C['border']} !important; border-radius:12px !important;
      }}
      .stTabs [data-baseweb="tab-list"] {{
          gap: 8px; background: transparent;
      }}
      .stTabs [data-baseweb="tab"] {{
          border-radius: 8px; font-family: 'Mulish', sans-serif; font-weight: 600;
          font-size: 13px;
      }}

      /* ── SIDEBAR ────────────────────────────────────────────────────────── */
      section[data-testid="stSidebar"] {{
          background: linear-gradient(180deg, {C['primary']} 0%, #162d52 100%) !important;
      }}
      section[data-testid="stSidebar"] * {{ color: rgba(255,255,255,.85) !important; }}
      section[data-testid="stSidebar"] .stMarkdown h1,
      section[data-testid="stSidebar"] .stMarkdown h2,
      section[data-testid="stSidebar"] .stMarkdown h3 {{
          color: white !important;
      }}

      /* ── PLOTLY RESPONSIVE FIX ──────────────────────────────────────────── */
      .js-plotly-plot, .plotly {{ width: 100% !important; }}
    </style>
    """, unsafe_allow_html=True)


def market_clock_html():
    """
    Retourne le HTML + JS d'une horloge dynamique Casablanca.
    Le JS met à jour l'horloge toutes les secondes côté client.
    """
    try:
        import pytz
        tz   = pytz.timezone('Africa/Casablanca')
        now  = datetime.now(tz)
    except ImportError:
        now  = datetime.now()

    t    = now.time()
    day  = now.strftime('%A')
    open_ = datetime.strptime('09:00', '%H:%M').time()
    close = datetime.strptime('15:30', '%H:%M').time()
    wdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

    if day in wdays and open_ <= t <= close:
        is_open = True
        label   = 'Marché Ouvert'
        info    = 'Séance en cours — Clôture 15:30'
    elif day in wdays and t < open_:
        is_open = False
        label   = 'Pré-ouverture'
        info    = f'Ouverture à 09:00'
    elif day not in wdays:
        is_open = False
        label   = 'Week-end'
        info    = 'Reprise lundi à 09:00'
    else:
        is_open = False
        label   = 'Clôture'
        info    = 'Prochaine séance demain 09:00'

    cls = 'open' if is_open else 'closed'
    time_str = now.strftime('%H:%M:%S')

    html = f"""
    <div class="market-banner {cls}">
      <div class="market-dot">{'🟢' if is_open else '🔴'}</div>
      <div>
        <div class="market-text-main">{label}</div>
        <div class="market-text-sub" id="mkt-sub">
          {info} &nbsp;·&nbsp; ⏰ <span id="mkt-clock">{time_str}</span> (Casablanca)
        </div>
      </div>
    </div>
    <script>
    (function() {{
      function tick() {{
        var now = new Date();
        var t = now.toLocaleTimeString('fr-MA', {{timeZone:'Africa/Casablanca', hour12:false}});
        var el = document.getElementById('mkt-clock');
        if (el) el.textContent = t;
        setTimeout(tick, 1000);
      }}
      tick();
    }})();
    </script>
    """
    return html


def page_hero(icon, title, subtitle, tags=None):
    """Génère un hero banner standardisé"""
    now_str = datetime.now().strftime("%d %b %Y — %H:%M")
    tags_html = ""
    if tags:
        tags_html = "".join(f'<span class="hero-tag">{t}</span>' for t in tags)

    return f"""
    <div class="page-hero">
      <div style="position:relative;z-index:1;">
        <div class="hero-eyebrow">NEWZ · CDG Capital · Market Data Platform</div>
        <p class="hero-title">{icon} {title}</p>
        <p class="hero-sub">{subtitle} — {now_str}</p>
        {tags_html}
      </div>
    </div>
    """
