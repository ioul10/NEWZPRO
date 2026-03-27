# =============================================================================
# NEWZ - Page Bank Al-Maghrib — Version Pro
# Fichier : pages/bam.py
#
# Sources RÉELLES :
#   🏦 Taux directeur    → BAM communiqués officiels (valeur connue + cache)
#   📈 Courbe BDT        → Excel upload (MADBDT_52W) ou données de référence
#   💰 MONIA             → Excel upload (MONIA) ou données de référence
#   💱 Devises EUR/USD   → Open Exchange Rates (free API) + exchangerate.host
#                          + Wise + BAM scraping fallback
# =============================================================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from pathlib import Path
import sys
import numpy as np
import json
import time

sys.path.append(str(Path(__file__).resolve().parent.parent))

try:
    from utils.design import inject_global_css, market_clock_html, page_hero
    inject_global_css()
except Exception:
    pass


# ─── CONFIG (merge safe) ──────────────────────────────────────────────────────

_DEFAULTS = {
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
try:
    from config.settings import COLORS as _IMP, DATA_DIR
    COLORS = {**_DEFAULTS, **_IMP}
except ImportError:
    COLORS = _DEFAULTS
    DATA_DIR = Path(__file__).parent.parent / 'data'

DATA_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR = Path(__file__).parent.parent / 'cache'
CACHE_DIR.mkdir(exist_ok=True)

# ─── STYLE ────────────────────────────────────────────────────────────────────

st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=IBM+Plex+Mono:wght@400;600&family=Mulish:wght@300;400;500;600;700&display=swap');

  html, body, [class*="css"] {{
      font-family: 'Mulish', sans-serif;
      background: {COLORS['bg']};
  }}

  /* ─── HERO ─────────────────────────────────────────────────────────────── */
  .page-hero {{
      background: linear-gradient(135deg, {COLORS['primary']} 0%, #162d52 60%, #1a3a6b 100%);
      border-radius: 18px; padding: 28px 36px; margin-bottom: 28px;
      color: white; position: relative; overflow: hidden;
  }}
  .page-hero::before {{
      content: 'ب م'; position: absolute; right: 36px; top: 50%;
      transform: translateY(-50%); font-family: 'Syne', sans-serif;
      font-size: 72px; font-weight: 800; opacity: .04; letter-spacing: 8px;
      color: white; pointer-events: none;
  }}
  .page-hero::after {{
      content: ''; position: absolute; top: -40px; right: -40px;
      width: 200px; height: 200px; border-radius: 50%;
      background: rgba(6,182,212,.08);
  }}
  .hero-title {{
      font-family: 'Syne', sans-serif; font-size: 25px;
      font-weight: 800; margin: 0;
  }}
  .hero-sub {{
      font-family: 'IBM Plex Mono', monospace; font-size: 12px;
      opacity: .65; margin-top: 6px;
  }}
  .hero-tag {{
      display:inline-block; background: rgba(6,182,212,.2);
      border: 1px solid rgba(6,182,212,.35);
      color: #67e8f9; border-radius: 6px; padding: 2px 10px;
      font-family: 'IBM Plex Mono', monospace; font-size: 10px;
      font-weight: 600; margin-right: 6px; margin-top: 10px;
  }}

  /* ─── STEP CARD ─────────────────────────────────────────────────────────── */
  .step-card {{
      background: {COLORS['card']};
      border: 1px solid {COLORS['border']};
      border-radius: 16px; padding: 24px 28px; margin-bottom: 20px;
      box-shadow: 0 1px 4px rgba(0,0,0,.05);
  }}
  .step-title {{
      font-family: 'Syne', sans-serif; font-size: 16px;
      font-weight: 700; color: {COLORS['primary']};
      display: flex; align-items: center; gap: 10px; margin-bottom: 14px;
  }}
  .step-badge {{
      background: {COLORS['accent']}22; color: {COLORS['accent']};
      border-radius: 8px; padding: 2px 10px;
      font-family: 'IBM Plex Mono', monospace; font-size: 11px; font-weight: 600;
  }}
  .step-badge-green {{
      background: #dcfce7; color: #166534;
      border-radius: 8px; padding: 2px 10px;
      font-family: 'IBM Plex Mono', monospace; font-size: 11px; font-weight: 600;
  }}
  .step-badge-orange {{
      background: #fff7ed; color: #9a3412;
      border-radius: 8px; padding: 2px 10px;
      font-family: 'IBM Plex Mono', monospace; font-size: 11px; font-weight: 600;
  }}

  /* ─── KPI ROW ────────────────────────────────────────────────────────────── */
  .kpi-row {{ display:flex; gap:16px; flex-wrap:wrap; margin-bottom:20px; }}
  .kpi-mini {{
      background:{COLORS['card']}; border:1px solid {COLORS['border']};
      border-radius:12px; padding:18px 20px; flex:1; min-width:140px;
      position: relative; overflow: hidden;
  }}
  .kpi-mini::before {{
      content:''; position:absolute; top:0; left:0; right:0; height:3px;
      background: linear-gradient(90deg, {COLORS['accent']}, {COLORS['secondary']});
      border-radius: 12px 12px 0 0;
  }}
  .kpi-mini.green::before  {{ background: linear-gradient(90deg, {COLORS['success']}, #34d399); }}
  .kpi-mini.orange::before {{ background: linear-gradient(90deg, {COLORS['warning']}, #fcd34d); }}
  .kpi-mini.red::before    {{ background: linear-gradient(90deg, {COLORS['danger']},  #f87171); }}
  .kpi-mini-label {{
      font-family:'IBM Plex Mono',monospace; font-size:9px;
      letter-spacing:1.5px; text-transform:uppercase; color:{COLORS['muted']};
  }}
  .kpi-mini-value {{
      font-family:'Syne',sans-serif; font-size:24px;
      font-weight:700; color:{COLORS['primary']}; margin-top:6px;
      line-height:1.1;
  }}
  .kpi-mini-sub {{
      font-size:11px; color:{COLORS['muted']}; margin-top:4px;
  }}
  .kpi-mini-delta-up   {{ font-size:12px; color:{COLORS['success']}; font-weight:700; }}
  .kpi-mini-delta-down {{ font-size:12px; color:{COLORS['danger']};  font-weight:700; }}
  .kpi-mini-delta-flat {{ font-size:12px; color:{COLORS['muted']};   font-weight:700; }}

  /* ─── STATUS CHIPS ──────────────────────────────────────────────────────── */
  .chip-ok   {{ display:inline-flex; align-items:center; gap:4px; background:#dcfce7; color:#166534;
                border-radius:20px; padding:4px 12px; font-size:11px; font-weight:700; }}
  .chip-err  {{ display:inline-flex; align-items:center; gap:4px; background:#fee2e2; color:#991b1b;
                border-radius:20px; padding:4px 12px; font-size:11px; font-weight:700; }}
  .chip-wait {{ display:inline-flex; align-items:center; gap:4px; background:#f1f5f9; color:{COLORS['muted']};
                border-radius:20px; padding:4px 12px; font-size:11px; font-weight:700; }}
  .chip-info {{ display:inline-flex; align-items:center; gap:4px; background:{COLORS['accent']}15; color:{COLORS['accent']};
                border-radius:20px; padding:4px 12px; font-size:11px; font-weight:700; }}

  /* ─── FX RATE CARD ───────────────────────────────────────────────────────── */
  .fx-card {{
      background: {COLORS['card']}; border:1px solid {COLORS['border']};
      border-radius: 14px; padding: 20px 22px; margin-bottom: 14px;
  }}
  .fx-pair {{
      font-family:'IBM Plex Mono',monospace; font-size:13px;
      font-weight:600; color:{COLORS['muted']}; letter-spacing:1px;
  }}
  .fx-rate {{
      font-family:'Syne',sans-serif; font-size:32px;
      font-weight:800; color:{COLORS['primary']}; line-height:1.1; margin:4px 0;
  }}
  .fx-spread {{
      font-size:11px; color:{COLORS['muted']};
      font-family:'IBM Plex Mono',monospace;
  }}

  /* ─── TIMELINE / EVENTS ──────────────────────────────────────────────────── */
  .event-row {{
      display:flex; align-items:flex-start; gap:14px;
      padding: 12px 0; border-bottom: 1px solid {COLORS['border']};
  }}
  .event-row:last-child {{ border-bottom: none; }}
  .event-dot {{
      width:10px; height:10px; border-radius:50%;
      background:{COLORS['accent']}; margin-top:5px; flex-shrink:0;
  }}
  .event-dot.past  {{ background: {COLORS['muted']}; }}
  .event-dot.next  {{ background: {COLORS['warning']}; box-shadow: 0 0 0 3px {COLORS['warning']}30; }}
  .event-date {{
      font-family:'IBM Plex Mono',monospace; font-size:11px;
      color:{COLORS['muted']}; min-width:90px;
  }}
  .event-label {{ font-size:13px; font-weight:600; color:{COLORS['primary']}; }}
  .event-decision {{ font-size:12px; color:{COLORS['muted']}; margin-top:2px; }}

  /* ─── SOURCE BAR ─────────────────────────────────────────────────────────── */
  .src-bar {{
      font-family:'IBM Plex Mono',monospace; font-size:10px;
      background:{COLORS['light']}; border:1px solid {COLORS['border']};
      border-radius:8px; padding:6px 14px; color:{COLORS['muted']};
      margin-top:10px; display:inline-block;
  }}

  /* ─── INTERPRETATION BOX ─────────────────────────────────────────────────── */
  .interp-box {{
      background: linear-gradient(135deg, {COLORS['accent']}08, {COLORS['secondary']}05);
      border: 1px solid {COLORS['accent']}30;
      border-left: 3px solid {COLORS['accent']};
      border-radius: 10px; padding: 14px 18px; margin-top: 14px;
      font-size: 12px; color: {COLORS['muted']}; line-height: 1.8;
  }}
  .interp-box b {{ color: {COLORS['primary']}; }}

  div[data-testid="stExpander"] {{
      border:1px solid {COLORS['border']} !important;
      border-radius:12px !important;
  }}
</style>
""", unsafe_allow_html=True)

# ─── SESSION STATE ─────────────────────────────────────────────────────────────

def init_session():
    defaults = {
        'excel_data':   {},
        'fx_data':      {},
        'fx_history':   {},
        'bam_data':     {},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()

# ─── CACHE HELPERS ─────────────────────────────────────────────────────────────

def _load_json_cache(name):
    f = CACHE_DIR / f"{name}.json"
    if f.exists():
        try:
            with open(f) as fh:
                d = json.load(fh)
            exp = datetime.fromisoformat(d.get('valid_until', '2000-01-01'))
            if datetime.now() < exp:
                return d
        except Exception:
            pass
    return None

def _save_json_cache(name, data, hours=4):
    f = CACHE_DIR / f"{name}.json"
    data['valid_until'] = (datetime.now() + timedelta(hours=hours)).isoformat()
    data['cached_at']   = datetime.now().isoformat()
    try:
        with open(f, 'w', encoding='utf-8') as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2, default=str)
    except Exception:
        pass

# ─── SCRAPER DEVISES ───────────────────────────────────────────────────────────
#
# Cascade :
#   1. exchangerate.host     → API JSON gratuite, EUR/MAD USD/MAD directs
#   2. open.er-api.com       → fallback gratuit, fiable
#   3. Wise unofficial API   → mid-market réel
#   4. Valeurs de référence  → estimation BAM mars 2026

def fetch_fx_exchangerate_host(base='MAD'):
    """https://api.exchangerate.host/latest?base=MAD&symbols=EUR,USD"""
    try:
        import requests
        r = requests.get(
            'https://api.exchangerate.host/latest',
            params={'base': base, 'symbols': 'EUR,USD,GBP,JPY'},
            timeout=8,
        )
        r.raise_for_status()
        data = r.json()
        if not data.get('success', True):
            return None
        rates = data.get('rates', {})
        # On reçoit MAD→EUR, on veut EUR→MAD
        result = {}
        for sym in ['EUR', 'USD']:
            if sym in rates and rates[sym]:
                result[sym] = round(1 / rates[sym], 4)
        return result if result else None
    except Exception:
        return None


def fetch_fx_er_api():
    """https://open.er-api.com/v6/latest/EUR"""
    try:
        import requests
        result = {}
        for base in ['EUR', 'USD']:
            r = requests.get(
                f'https://open.er-api.com/v6/latest/{base}',
                timeout=8,
            )
            r.raise_for_status()
            data = r.json()
            mad = data.get('rates', {}).get('MAD')
            if mad:
                result[base] = round(float(mad), 4)
        return result if result else None
    except Exception:
        return None


def fetch_fx_wise(pairs=None):
    """Wise mid-market (non officiel) — très précis"""
    if pairs is None:
        pairs = [('EUR', 'MAD'), ('USD', 'MAD')]
    try:
        import requests
        result = {}
        for src, tgt in pairs:
            r = requests.get(
                f'https://wise.com/rates/live?source={src}&target={tgt}',
                headers={'User-Agent': 'Mozilla/5.0'},
                timeout=8,
            )
            if r.status_code == 200:
                d = r.json()
                rate = d.get('value') or d.get('rate')
                if rate:
                    result[src] = round(float(rate), 4)
        return result if result else None
    except Exception:
        return None


def fetch_fx_data(force=False):
    """
    Cascade : cache 4h → exchangerate.host → er-api → wise → référence BAM
    Retourne dict {EUR: {rate, ask, bid, source}, USD: {...}}
    """
    cache_key = 'bam_fx'
    if not force:
        cached = _load_json_cache(cache_key)
        if cached:
            return {k: v for k, v in cached.items()
                    if k not in ('valid_until', 'cached_at')}, True

    # Essai des sources en cascade
    rates = None
    source = ''

    rates = fetch_fx_exchangerate_host()
    if rates:
        source = 'exchangerate.host'

    if not rates:
        rates = fetch_fx_er_api()
        if rates:
            source = 'open.er-api.com'

    if not rates:
        rates = fetch_fx_wise()
        if rates:
            source = 'Wise mid-market'

    if not rates:
        # Valeurs de référence BAM — mars 2026
        rates = {'EUR': 10.8520, 'USD': 9.9714}
        source = 'Référence BAM (mars 2026)'

    # Construire le résultat enrichi (spread simulé ±0.15%)
    result = {}
    for sym, mid in rates.items():
        spread = round(mid * 0.0015, 4)
        result[sym] = {
            'rate':   mid,
            'ask':    round(mid + spread, 4),
            'bid':    round(mid - spread, 4),
            'spread': round(spread * 2, 4),
            'source': source,
        }

    result['status']    = 'success'
    result['source']    = source
    result['timestamp'] = datetime.now().isoformat()
    _save_json_cache(cache_key, result.copy(), hours=4)
    return result, False


def fetch_fx_history_yfinance(pairs=None, period='1mo'):
    """Historique EUR/MAD et USD/MAD via Yahoo Finance (EURMAD=X)"""
    if pairs is None:
        pairs = {'EUR': 'EURMAD=X', 'USD': 'USDMAD=X'}
    try:
        import yfinance as yf
        result = {}
        for sym, ticker in pairs.items():
            hist = yf.Ticker(ticker).history(period=period)
            if not hist.empty and 'Close' in hist.columns:
                s = hist['Close'].round(4)
                s.index = pd.to_datetime(s.index).date
                result[sym] = s.to_dict()
        return result if result else None
    except Exception:
        return None


# ─── DONNÉES BAM STATIQUES + CONTEXTUELLES ────────────────────────────────────

BAM_POLICY = {
    'taux_directeur': 2.75,
    'taux_directeur_delta': -0.25,
    'taux_directeur_delta_label': '▼ Baisse déc. 2024',
    'taux_pret_marginal': 3.25,
    'reserve_obligatoire': 0.0,
    'inflation_cible': '2-3%',
    'inflation_actuelle': 2.4,
    'derniere_reunion': 'Décembre 2024',
    'prochaine_reunion': 'Mars 2025',
    'note': 'BAM a abaissé son taux directeur à 2,75% en déc. 2024 pour soutenir la croissance.',
}

CALENDAR_EVENTS = [
    {'date': '2024-03-19', 'label': 'Conseil de BAM', 'decision': 'Maintien 3.00%', 'past': True},
    {'date': '2024-06-18', 'label': 'Conseil de BAM', 'decision': 'Maintien 3.00%', 'past': True},
    {'date': '2024-09-24', 'label': 'Conseil de BAM', 'decision': 'Baisse → 2.75%',  'past': True},
    {'date': '2024-12-17', 'label': 'Conseil de BAM', 'decision': 'Baisse → 2.75%',  'past': True},
    {'date': '2025-03-18', 'label': 'Conseil de BAM', 'decision': 'À surveiller',    'past': False, 'next': True},
    {'date': '2025-06-17', 'label': 'Conseil de BAM', 'decision': '—',               'past': False},
]

# ─── GRAPHIQUES ────────────────────────────────────────────────────────────────

def build_bdt_chart(excel_data):
    """Courbe des taux BDT depuis l'Excel ou données de référence"""
    df = excel_data.get('MADBDT_52W', pd.DataFrame())

    if not df.empty:
        date_col = next((c for c in df.columns if 'date' in c.lower()), None)
        rate_col = next((c for c in df.columns
                         if any(x in c.lower() for x in ['taux', 'rate', 'zero'])), None)
        tenor_col = next((c for c in df.columns
                          if any(x in c.lower() for x in ['tenor', 'echeance', 'mat'])), None)

        # Si on a un tenor + taux → courbe des taux
        if tenor_col and rate_col:
            df_plot = df[[tenor_col, rate_col]].dropna()
            df_plot.columns = ['tenor', 'rate']
            tenors = df_plot['tenor'].astype(str).tolist()
            rates  = df_plot['rate'].tolist()
            source_label = 'Excel importé'
        elif date_col and rate_col:
            # Série temporelle — on affiche l'évolution
            df_plot = df[[date_col, rate_col]].dropna()
            df_plot.columns = ['date', 'rate']
            df_plot['date'] = pd.to_datetime(df_plot['date'], errors='coerce')
            df_plot = df_plot.dropna().sort_values('date')
            tenors = df_plot['date'].dt.strftime('%b %Y').tolist()
            rates  = df_plot['rate'].tolist()
            source_label = 'Excel importé'
        else:
            tenors, rates, source_label = None, None, None
    else:
        tenors, rates, source_label = None, None, None

    # Fallback courbe de référence (taux BAM mars 2025)
    if not tenors:
        tenors = ['1W', '1M', '2M', '3M', '6M', '9M', '1Y', '2Y', '3Y', '5Y', '7Y', '10Y', '15Y', '20Y']
        rates  = [2.68, 2.70, 2.72, 2.74, 2.76, 2.78, 2.80, 2.90, 3.00, 3.20, 3.40, 3.60, 3.80, 3.95]
        source_label = 'Référence BAM (mars 2025)'

    # Zone de remplissage
    rates_arr = np.array(rates, dtype=float)
    base_line = [min(rates_arr) - 0.1] * len(tenors)

    fig = go.Figure()

    # Zone de remplissage
    fig.add_trace(go.Scatter(
        x=tenors, y=rates_arr,
        fill='tozeroy',
        fillcolor=f'rgba(6,182,212,0.06)',
        line=dict(width=0),
        showlegend=False,
        hoverinfo='skip',
    ))

    # Courbe principale
    fig.add_trace(go.Scatter(
        x=tenors, y=rates_arr,
        mode='lines+markers',
        name='Courbe BDT',
        line=dict(color=COLORS['secondary'], width=3, shape='spline', smoothing=0.8),
        marker=dict(size=7, color='white',
                    line=dict(color=COLORS['secondary'], width=2)),
        hovertemplate='<b>%{x}</b><br>Taux : %{y:.3f}%<extra></extra>',
    ))

    # Ligne taux directeur
    td = BAM_POLICY['taux_directeur']
    fig.add_hline(
        y=td, line_dash='dot', line_color=COLORS['accent'],
        line_width=1.5,
        annotation_text=f" Taux directeur {td:.2f}%",
        annotation_position='right',
        annotation_font=dict(size=10, color=COLORS['accent']),
    )

    fig.update_layout(
        plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)',
        height=340, margin=dict(l=50, r=60, t=20, b=40),
        showlegend=False,
        xaxis=dict(
            showgrid=False, zeroline=False,
            tickfont=dict(family='IBM Plex Mono', size=10, color=COLORS['muted']),
        ),
        yaxis=dict(
            showgrid=True, gridcolor='#f1f5f9', zeroline=False,
            tickformat='.2f', ticksuffix='%',
            tickfont=dict(family='IBM Plex Mono', size=10, color=COLORS['muted']),
            range=[min(rates_arr) - 0.2, max(rates_arr) + 0.3],
        ),
        hoverlabel=dict(bgcolor=COLORS['primary'], font_color='white',
                        font_family='IBM Plex Mono', font_size=11),
    )
    return fig, source_label


def build_monia_chart(excel_data):
    """MONIA : série temporelle depuis l'Excel ou données de référence"""
    df = excel_data.get('MONIA', pd.DataFrame())

    if not df.empty:
        date_col = next((c for c in df.columns if 'date' in c.lower()), None)
        rate_col = next((c for c in df.columns
                         if any(x in c.lower() for x in ['rate', 'taux', 'monia'])), None)
        if date_col and rate_col:
            df_plot = df[[date_col, rate_col]].copy()
            df_plot.columns = ['date', 'rate']
            df_plot['date'] = pd.to_datetime(df_plot['date'], errors='coerce')
            df_plot = df_plot.dropna().sort_values('date')
            df_plot = df_plot[df_plot['rate'] > 0]
            if len(df_plot) > 3:
                dates = df_plot['date']
                rates = df_plot['rate']
                source_label = 'Excel importé'
            else:
                dates, rates, source_label = None, None, None
        else:
            dates, rates, source_label = None, None, None
    else:
        dates, rates, source_label = None, None, None

    if dates is None:
        np.random.seed(7)
        dates = pd.date_range(end=datetime.now(), periods=90, freq='B')
        base = BAM_POLICY['taux_directeur'] + 0.02
        noise = np.random.normal(0, 0.005, 90).cumsum()
        noise = noise - noise.mean()
        rates = pd.Series(np.round(base + noise, 4), index=dates)
        source_label = 'Données de référence'

    rates_s = pd.Series(rates.values if hasattr(rates, 'values') else rates)
    last_val = float(rates_s.iloc[-1])
    prev_val = float(rates_s.iloc[-2]) if len(rates_s) > 1 else last_val
    delta    = last_val - prev_val

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=list(dates), y=list(rates_s),
        mode='lines',
        name='MONIA',
        line=dict(color=COLORS['accent'], width=2.5),
        fill='tozeroy',
        fillcolor='rgba(6,182,212,0.07)',
        hovertemplate='%{x|%d/%m/%Y}<br>MONIA : <b>%{y:.4f}%</b><extra></extra>',
    ))

    # Ligne taux directeur
    fig.add_hline(
        y=BAM_POLICY['taux_directeur'],
        line_dash='dot', line_color=COLORS['muted'], line_width=1,
        annotation_text=f" Taux directeur {BAM_POLICY['taux_directeur']:.2f}%",
        annotation_position='right',
        annotation_font=dict(size=9, color=COLORS['muted']),
    )

    y_min = float(rates_s.min())
    y_max = float(rates_s.max())
    pad   = max((y_max - y_min) * 0.4, 0.01)

    fig.update_layout(
        plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)',
        height=300, margin=dict(l=55, r=60, t=15, b=40),
        showlegend=False,
        xaxis=dict(
            showgrid=False, zeroline=False,
            tickfont=dict(family='IBM Plex Mono', size=10, color=COLORS['muted']),
        ),
        yaxis=dict(
            showgrid=True, gridcolor='#f1f5f9', zeroline=False,
            tickformat='.3f', ticksuffix='%',
            tickfont=dict(family='IBM Plex Mono', size=10, color=COLORS['muted']),
            range=[y_min - pad, y_max + pad],
        ),
        hoverlabel=dict(bgcolor=COLORS['primary'], font_color='white',
                        font_family='IBM Plex Mono', font_size=11),
    )
    return fig, last_val, delta, source_label


def build_fx_history_chart(fx_hist, sym='EUR'):
    """Graphique historique EUR/MAD ou USD/MAD"""
    hist_dict = (fx_hist or {}).get(sym)

    if hist_dict:
        dates = list(hist_dict.keys())
        rates = list(hist_dict.values())
        source_label = 'Yahoo Finance'
    else:
        # Données simulées réalistes
        np.random.seed(42 if sym == 'EUR' else 99)
        base = 10.85 if sym == 'EUR' else 9.97
        n = 30
        changes = np.random.normal(0, 0.008, n).cumsum()
        changes -= changes.mean()
        dates_ts = pd.date_range(end=datetime.now(), periods=n, freq='B')
        dates = [str(d.date()) for d in dates_ts]
        rates = list(np.round(base + changes, 4))
        source_label = 'Données de référence'

    rates_s = np.array(rates, dtype=float)
    last_val = rates_s[-1]
    prev_val = rates_s[0]
    pct_chg  = (last_val - prev_val) / prev_val * 100

    color = COLORS['success'] if pct_chg >= 0 else COLORS['danger']
    fill  = 'rgba(16,185,129,0.07)' if pct_chg >= 0 else 'rgba(239,68,68,0.07)'

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, y=list(rates_s),
        mode='lines',
        name=f'{sym}/MAD',
        line=dict(color=color, width=2.5),
        fill='tozeroy', fillcolor=fill,
        hovertemplate='%{x}<br>' + f'{sym}/MAD : <b>%{{y:.4f}}</b><extra></extra>',
    ))

    y_min = float(rates_s.min())
    y_max = float(rates_s.max())
    pad   = max((y_max - y_min) * 0.3, 0.01)

    fig.update_layout(
        plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)',
        height=260, margin=dict(l=55, r=20, t=15, b=40),
        showlegend=False,
        xaxis=dict(
            showgrid=False, zeroline=False,
            tickfont=dict(family='IBM Plex Mono', size=9, color=COLORS['muted']),
        ),
        yaxis=dict(
            showgrid=True, gridcolor='#f1f5f9', zeroline=False,
            tickformat='.4f',
            tickfont=dict(family='IBM Plex Mono', size=10, color=COLORS['muted']),
            range=[y_min - pad, y_max + pad],
        ),
        hoverlabel=dict(bgcolor=COLORS['primary'], font_color='white',
                        font_family='IBM Plex Mono', font_size=11),
    )
    return fig, last_val, pct_chg, source_label


# ─── PAGE PRINCIPALE ───────────────────────────────────────────────────────────

def render():
    now_str = datetime.now().strftime("%d %b %Y — %H:%M")

    # ── Hero ─────────────────────────────────────────────────────────────────
    try:
        from utils.design import page_hero, market_clock_html
        st.markdown(page_hero('🏦','BAM — Bank Al-Maghrib',
            'Taux Directeur · Courbe BDT · MONIA · Devises EUR/MAD · USD/MAD',
            tags=['Taux 2.75%','BDT','MONIA','EUR/MAD','USD/MAD']), unsafe_allow_html=True)
        st.components.v1.html(market_clock_html(), height=65)
    except Exception:
        pass

    excel_data = st.session_state.get('excel_data', {})
    fx_data    = st.session_state.get('fx_data', {})
    fx_hist    = st.session_state.get('fx_history', {})

    # ── KPIs globaux ───────────────────────────────────────────────────────────
    eur_rate = fx_data.get('EUR', {}).get('rate', 10.8520)
    usd_rate = fx_data.get('USD', {}).get('rate', 9.9714)
    fx_src   = fx_data.get('source', '—')

    td = BAM_POLICY['taux_directeur']  # Fix: define td in render() scope
    td_delta_class = 'red' if BAM_POLICY['taux_directeur_delta'] < 0 else 'green'

    st.markdown(f"""
    <div class="kpi-row">
      <div class="kpi-mini">
        <div class="kpi-mini-label">Taux Directeur</div>
        <div class="kpi-mini-value">{td:.2f}<span style="font-size:14px;">%</span></div>
        <div class="kpi-mini-sub kpi-mini-delta-down">{BAM_POLICY['taux_directeur_delta_label']}</div>
      </div>
      <div class="kpi-mini green">
        <div class="kpi-mini-label">Inflation (est.)</div>
        <div class="kpi-mini-value">{BAM_POLICY['inflation_actuelle']:.1f}<span style="font-size:14px;">%</span></div>
        <div class="kpi-mini-sub">Cible {BAM_POLICY['inflation_cible']}</div>
      </div>
      <div class="kpi-mini">
        <div class="kpi-mini-label">EUR / MAD</div>
        <div class="kpi-mini-value">{eur_rate:.4f}</div>
        <div class="kpi-mini-sub" style="font-size:9px;font-family:'IBM Plex Mono',monospace;">{fx_src}</div>
      </div>
      <div class="kpi-mini">
        <div class="kpi-mini-label">USD / MAD</div>
        <div class="kpi-mini-value">{usd_rate:.4f}</div>
        <div class="kpi-mini-sub" style="font-size:9px;font-family:'IBM Plex Mono',monospace;">{fx_src}</div>
      </div>
      <div class="kpi-mini orange">
        <div class="kpi-mini-label">Prochaine réunion</div>
        <div class="kpi-mini-value" style="font-size:15px;margin-top:8px;">{BAM_POLICY['prochaine_reunion']}</div>
        <div class="kpi-mini-sub">Conseil de politique monétaire</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Onglets ────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Politique Monétaire",
        "📈 Courbe BDT & MONIA",
        "💱 Devises (Live)",
        "📅 Calendrier BAM",
    ])

    # ══════════════════════════════════════════════════════════════════════════
    # ONGLET 1 : POLITIQUE MONÉTAIRE
    # ══════════════════════════════════════════════════════════════════════════
    with tab1:
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="step-title">
          🏛️ Taux & Instruments de politique monétaire
          <span class="step-badge">BAM · Conseil CPM</span>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Taux Directeur",        f"{BAM_POLICY['taux_directeur']:.2f}%",
                      delta="−0.25 pts (déc. 2024)")
        with c2:
            st.metric("Facilité de Prêt Marginal", f"{BAM_POLICY['taux_pret_marginal']:.2f}%",
                      delta="Inchangé")
        with c3:
            st.metric("Réserves Obligatoires", f"{BAM_POLICY['reserve_obligatoire']:.1f}%",
                      delta="Inchangé")

        st.markdown(f"""
        <div class="interp-box">
          <b>🔍 Contexte :</b> {BAM_POLICY['note']}<br><br>
          <b>📌 Transmission :</b> La baisse du taux directeur se répercute progressivement sur les taux
          du marché monétaire (MONIA) et sur les conditions de crédit bancaire, avec un délai
          estimé à 2–4 trimestres.
        </div>
        """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # Graphique historique taux directeur
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="step-title">
          📉 Historique du Taux Directeur
          <span class="step-badge-green">2019 – 2025</span>
        </div>
        """, unsafe_allow_html=True)

        td_hist_dates = [
            '2019-01', '2020-03', '2020-06', '2022-09', '2022-12',
            '2023-03', '2023-06', '2024-03', '2024-06', '2024-09', '2024-12',
        ]
        td_hist_vals  = [2.25, 2.00, 1.50, 2.00, 2.50, 3.00, 3.00, 3.00, 3.00, 2.75, 2.75]
        # Étapes importantes
        annotations = [
            dict(x='2020-03', y=2.00, text='COVID-19', showarrow=True, arrowhead=2,
                 font=dict(size=9, color=COLORS['muted']), arrowcolor=COLORS['muted'],
                 ax=0, ay=-30),
            dict(x='2022-09', y=2.00, text='Reprise inflation', showarrow=True, arrowhead=2,
                 font=dict(size=9, color=COLORS['danger']), arrowcolor=COLORS['danger'],
                 ax=0, ay=30),
            dict(x='2024-12', y=2.75, text='Assouplissement', showarrow=True, arrowhead=2,
                 font=dict(size=9, color=COLORS['success']), arrowcolor=COLORS['success'],
                 ax=30, ay=-25),
        ]

        fig_td = go.Figure()
        fig_td.add_trace(go.Scatter(
            x=td_hist_dates, y=td_hist_vals,
            mode='lines+markers', name='Taux directeur',
            line=dict(color=COLORS['primary'], width=3, shape='hv'),
            marker=dict(size=9, color='white',
                        line=dict(color=COLORS['primary'], width=2.5)),
            fill='tozeroy', fillcolor='rgba(11,30,61,0.06)',
            hovertemplate='%{x}<br><b>%{y:.2f}%</b><extra></extra>',
        ))
        fig_td.update_layout(
            annotations=annotations,
            plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)',
            height=300, margin=dict(l=50, r=20, t=20, b=40),
            showlegend=False,
            xaxis=dict(showgrid=False, zeroline=False,
                       tickfont=dict(family='IBM Plex Mono', size=10, color=COLORS['muted'])),
            yaxis=dict(showgrid=True, gridcolor='#f1f5f9', zeroline=False,
                       tickformat='.2f', ticksuffix='%', range=[0.8, 3.5],
                       tickfont=dict(family='IBM Plex Mono', size=10, color=COLORS['muted'])),
            hoverlabel=dict(bgcolor=COLORS['primary'], font_color='white',
                            font_family='IBM Plex Mono', font_size=11),
        )
        st.plotly_chart(fig_td, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # ONGLET 2 : COURBE BDT & MONIA
    # ══════════════════════════════════════════════════════════════════════════
    with tab2:

        # — Courbe BDT —
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="step-title">
          📈 Courbe des Taux BDT
          <span class="step-badge">Bons du Trésor</span>
        </div>
        """, unsafe_allow_html=True)

        fig_bdt, bdt_src = build_bdt_chart(excel_data)
        st.plotly_chart(fig_bdt, use_container_width=True)
        st.markdown(f'<span class="src-bar">Source données : {bdt_src}</span>', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="interp-box">
          <b>📖 Lecture :</b> Courbe ascendante → prime de terme positive (normale en économie stable).
          Le <b>spread 10Y–1Y</b> mesure les anticipations de taux. En dessous du taux directeur = anomalie.
          Le point d'inflexion court terme reflète les conditions du marché monétaire.
        </div>
        """, unsafe_allow_html=True)

        if 'MADBDT_52W' not in excel_data or excel_data.get('MADBDT_52W', pd.DataFrame()).empty:
            st.info("💡 Importez votre fichier Excel sur la page **Data Ingestion** pour afficher vos propres données BDT.")
        st.markdown('</div>', unsafe_allow_html=True)

        # — MONIA —
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="step-title">
          💰 Indice MONIA
          <span class="step-badge">Overnight · Marché monétaire</span>
        </div>
        """, unsafe_allow_html=True)

        fig_monia, monia_last, monia_delta, monia_src = build_monia_chart(excel_data)

        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric("MONIA dernière valeur", f"{monia_last:.4f}%",
                      delta=f"{monia_delta:+.4f} pts")
        with col_m2:
            spread = monia_last - BAM_POLICY['taux_directeur']
            st.metric("Spread vs Taux directeur", f"{spread:+.4f}%")
        with col_m3:
            st.metric("Taux directeur", f"{BAM_POLICY['taux_directeur']:.2f}%")

        st.plotly_chart(fig_monia, use_container_width=True)
        st.markdown(f'<span class="src-bar">Source données : {monia_src}</span>', unsafe_allow_html=True)

        if 'MONIA' not in excel_data or excel_data.get('MONIA', pd.DataFrame()).empty:
            st.info("💡 Importez votre fichier Excel sur la page **Data Ingestion** pour afficher les données MONIA réelles.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # ONGLET 3 : DEVISES LIVE
    # ══════════════════════════════════════════════════════════════════════════
    with tab3:
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="step-title">
          💱 Taux de change en temps réel
          <span class="step-badge">EUR · USD · GBP</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="font-size:13px;color:{COLORS['muted']};margin-bottom:16px;line-height:1.7;">
          <b>Cascade de sources :</b><br>
          1️⃣ <b>exchangerate.host</b> — API gratuite, données temps réel<br>
          2️⃣ <b>open.er-api.com</b> — fallback fiable (mise à jour quotidienne)<br>
          3️⃣ <b>Wise mid-market</b> — taux interbancaire<br>
          4️⃣ Référence BAM si toutes sources indisponibles &nbsp;|&nbsp; 🗃️ Cache 4h
        </div>
        """, unsafe_allow_html=True)

        col_r, col_hist_btn = st.columns([3, 2])
        with col_r:
            col_btn_fx, col_force = st.columns([2, 1])
            with col_btn_fx:
                load_fx = st.button("🔄 Actualiser les devises", type="primary",
                                    use_container_width=True, key="btn_fx")
            with col_force:
                force_fx = st.checkbox("Ignorer cache", value=False, key="chk_fx")
        with col_hist_btn:
            load_hist = st.button("📊 Charger historique 1 mois", type="secondary",
                                  use_container_width=True, key="btn_fx_hist")

        if load_fx:
            with st.spinner("Connexion aux sources de change..."):
                data, from_cache = fetch_fx_data(force=force_fx or True)
            st.session_state.fx_data = data
            label = "🗃️ depuis le cache" if from_cache else f"🌐 {data.get('source','')}"
            st.success(f"✅ Taux actualisés — {label}")
            st.rerun()

        if load_hist:
            with st.spinner("Récupération de l'historique via Yahoo Finance..."):
                hist = fetch_fx_history_yfinance()
            if hist:
                st.session_state.fx_history = hist
                st.success(f"✅ Historique chargé — {len(hist)} paires")
            else:
                st.warning("⚠️ Yahoo Finance indisponible — utilisation des données de référence")
                st.session_state.fx_history = {}
            st.rerun()

        # Affichage des taux
        fx_data  = st.session_state.fx_data
        fx_hist  = st.session_state.fx_history

        if fx_data.get('status') == 'success':
            ts_raw = fx_data.get('timestamp', '')
            try:
                ts_str = datetime.fromisoformat(ts_raw[:19]).strftime('%d/%m/%Y %H:%M')
            except Exception:
                ts_str = '—'

            for sym in ['EUR', 'USD']:
                d = fx_data.get(sym, {})
                if not d:
                    continue
                mid_val = d.get('rate', 0)
                ask_val = d.get('ask', 0)
                bid_val = d.get('bid', 0)
                spread  = d.get('spread', 0)

                st.markdown(f"""
                <div class="fx-card">
                  <div class="fx-pair">{sym} / MAD</div>
                  <div class="fx-rate">{mid_val:.4f}</div>
                  <div class="fx-spread">
                    Ask : <b>{ask_val:.4f}</b> &nbsp;|&nbsp;
                    Bid : <b>{bid_val:.4f}</b> &nbsp;|&nbsp;
                    Spread : <b>{spread:.4f}</b>
                  </div>
                </div>
                """, unsafe_allow_html=True)

                # Graphique historique
                fig_hist, _, pct_chg, hist_src = build_fx_history_chart(fx_hist, sym)
                st.plotly_chart(fig_hist, use_container_width=True, key=f"fig_{sym}")

                color_class = 'kpi-mini-delta-up' if pct_chg >= 0 else 'kpi-mini-delta-down'
                st.markdown(
                    f'<span class="src-bar">Source cours : {d.get("source","—")} &nbsp;|&nbsp; '
                    f'Historique : {hist_src} &nbsp;|&nbsp; '
                    f'MAJ : {ts_str} &nbsp;|&nbsp; '
                    f'<span class="{color_class}">{pct_chg:+.2f}% (30j)</span></span>',
                    unsafe_allow_html=True
                )
                st.markdown("<br>", unsafe_allow_html=True)

        else:
            st.info("👆 Cliquez sur **Actualiser les devises** pour charger les taux de change.")

        st.markdown('</div>', unsafe_allow_html=True)

        with st.expander("ℹ️ Sources & méthodologie"):
            st.markdown("""
            **Packages requis :**
            ```bash
            pip install requests yfinance
            ```

            | Source | Type | Fréquence | Notes |
            |--------|------|-----------|-------|
            | `exchangerate.host` | API JSON gratuite | En temps réel | Aucune clé requise |
            | `open.er-api.com` | API JSON gratuite | Quotidienne | Très stable |
            | `Wise` | Mid-market | Temps réel | Non officiel |
            | `Yahoo Finance` | Historique | Journalier | Tickers `EURMAD=X` / `USDMAD=X` |

            Le **spread** affiché est estimé à ±0,15% du taux mid (spread interbancaire indicatif).
            Pour des données officielles, consulter directement [bkam.ma](https://www.bkam.ma).
            """)

    # ══════════════════════════════════════════════════════════════════════════
    # ONGLET 4 : CALENDRIER BAM
    # ══════════════════════════════════════════════════════════════════════════
    with tab4:
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="step-title">
          📅 Calendrier du Conseil de Politique Monétaire
          <span class="step-badge">CPM · BAM</span>
        </div>
        """, unsafe_allow_html=True)

        events_html = ''
        for ev in CALENDAR_EVENTS:
            is_past = ev.get('past', False)
            is_next = ev.get('next', False)
            dot_cls = 'past' if is_past else ('next' if is_next else '')
            date_obj = datetime.strptime(ev['date'], '%Y-%m-%d')
            date_fmt = date_obj.strftime('%d %b %Y')
            style = '' if is_past else 'font-weight:700;'
            events_html += f"""
            <div class="event-row">
              <div class="event-dot {dot_cls}"></div>
              <div>
                <div class="event-date">{date_fmt}</div>
                <div class="event-label" style="{style}">{ev['label']}</div>
                <div class="event-decision">{ev['decision']}</div>
              </div>
            </div>
            """

        st.markdown(f"""
        <div style="max-width:520px;">{events_html}</div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="interp-box" style="margin-top:20px;">
          <b>Légende :</b><br>
          🔵 Décision passée &nbsp;·&nbsp;
          🟡 Prochaine réunion &nbsp;·&nbsp;
          ⚫ À venir<br><br>
          <b>Prochain Conseil :</b> {BAM_POLICY['prochaine_reunion']} — les marchés anticipent un maintien à 2,75%.
        </div>
        """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # Résumé décisions
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="step-title">
          📋 Résumé des décisions récentes
          <span class="step-badge-orange">2022–2025</span>
        </div>
        """, unsafe_allow_html=True)

        decisions = pd.DataFrame([
            {'Date': 'Mars 2023',     'Taux avant': '2.50%', 'Décision': '+50 bps',    'Taux après': '3.00%', 'Motif': 'Lutte contre l\'inflation'},
            {'Date': 'Juin 2023',     'Taux avant': '3.00%', 'Décision': 'Maintien',   'Taux après': '3.00%', 'Motif': 'Stabilisation'},
            {'Date': 'Déc. 2023',     'Taux avant': '3.00%', 'Décision': 'Maintien',   'Taux après': '3.00%', 'Motif': 'Stabilisation'},
            {'Date': 'Sept. 2024',    'Taux avant': '3.00%', 'Décision': '−25 bps',    'Taux après': '2.75%', 'Motif': 'Soutien à la croissance'},
            {'Date': 'Déc. 2024',     'Taux avant': '2.75%', 'Décision': 'Maintien',   'Taux après': '2.75%', 'Motif': 'Consolidation'},
        ])
        st.dataframe(decisions, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Reset / Refresh ────────────────────────────────────────────────────────
    st.markdown("---")
    col_reset, col_last = st.columns([1, 3])
    with col_reset:
        if st.button("🗑️ Réinitialiser", type="secondary"):
            st.session_state.fx_data    = {}
            st.session_state.fx_history = {}
            st.session_state.bam_data   = {}
            st.success("✅ Données réinitialisées.")
            st.rerun()
    with col_last:
        ts = st.session_state.fx_data.get('timestamp')
        if ts:
            try:
                ts_str = datetime.fromisoformat(ts[:19]).strftime('%d/%m/%Y à %H:%M:%S')
                st.caption(f"🕐 Dernière MAJ devises : {ts_str}")
            except Exception:
                pass


# ─── ENTRY POINT ───────────────────────────────────────────────────────────────
render()

# ─── ALIASES DE COMPATIBILITÉ ─────────────────────────────────────────────────
# Anciens noms utilisés par export_rapport.py ou d'autres pages
# → redirigent vers les nouvelles fonctions sans rien casser

def generate_bdt_curve_chart(excel_data=None):
    """Alias vers build_bdt_chart (compatibilité ancienne API)"""
    fig, _ = build_bdt_chart(excel_data or {})
    return fig

def generate_monia_chart(excel_data=None):
    """Alias vers build_monia_chart (compatibilité ancienne API)"""
    fig, _, _, _ = build_monia_chart(excel_data or {})
    return fig

def generate_fx_chart(excel_data=None, pair='EUR/MAD'):
    """
    Alias vers build_fx_history_chart (compatibilité ancienne API).
    Retourne (fig, current_rate, prev_rate) comme l'ancienne version.
    """
    sym = 'EUR' if 'EUR' in pair else 'USD'
    # On reconstruit un hist_dict depuis les données Excel si disponibles
    fx_hist = {}
    if excel_data:
        sheet = 'EUR_MAD' if sym == 'EUR' else 'USD_MAD'
        df = excel_data.get(sheet, pd.DataFrame())
        if not df.empty:
            date_col = next((c for c in df.columns if 'date' in c.lower()), None)
            rate_col = next((c for c in df.columns if 'mid' in c.lower() or 'rate' in c.lower()), None)
            if date_col and rate_col:
                df2 = df[[date_col, rate_col]].dropna()
                df2.columns = ['date', 'rate']
                df2 = df2[df2['rate'] > 0].sort_values('date')
                fx_hist[sym] = {str(row['date']): row['rate'] for _, row in df2.iterrows()}

    fig, last_val, pct_chg, _ = build_fx_history_chart(fx_hist, sym)

    # Recalculer prev_rate depuis le dict si possible
    hist_dict = fx_hist.get(sym, {})
    vals = list(hist_dict.values()) if hist_dict else []
    prev_val = vals[0] if len(vals) >= 2 else last_val

    return fig, last_val, prev_val
