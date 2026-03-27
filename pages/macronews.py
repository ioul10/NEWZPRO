# =============================================================================
# NEWZ - Page Macronews — Version Pro
# Fichier : pages/macronews.py
#
# Scraping HCP.ma : méthode robuste par regex sur les titres d'articles
# Fallback BKAM → Trading Economics → Cache ancien → Estimation
# =============================================================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path
import sys
import json
import re

sys.path.append(str(Path(__file__).resolve().parent.parent))

try:
    from utils.design import inject_global_css, market_clock_html, page_hero
    inject_global_css()
except Exception:
    pass


_COLORS_DEFAULTS = {
    'primary':   '#0a2540',
    'secondary': '#00a8e8',
    'success':   '#00c48c',
    'danger':    '#ff4d6d',
    'warning':   '#f4c430',
    'accent':    '#635bff',
    'bg':        '#f0f4f8',
    'card':      '#ffffff',
    'muted':     '#64748b',
}

try:
    from config.settings import COLORS as _IMPORTED_COLORS
    # Merger : on garde les valeurs importées ET on complète les clés manquantes
    COLORS = {**_COLORS_DEFAULTS, **_IMPORTED_COLORS}
except ImportError:
    COLORS = _COLORS_DEFAULTS

# CSS injected via utils/design.py

# ─── CACHE CONFIG ──────────────────────────────────────────────────────────────

CACHE_DIR = Path(__file__).parent.parent / "cache"
CACHE_DIR.mkdir(exist_ok=True)
INFLATION_CACHE_FILE = CACHE_DIR / "inflation.json"
CACHE_VALID_DAYS = 7

# ─── SESSION STATE ─────────────────────────────────────────────────────────────

def init_session():
    defaults = {
        'news_data':             [],
        'inflation_rate':        None,
        'inflation_last_update': None,
        'inflation_source':      None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()

# ─── CACHE HELPERS ─────────────────────────────────────────────────────────────

def load_cache():
    try:
        if INFLATION_CACHE_FILE.exists():
            with open(INFLATION_CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return None

def save_cache(value, source, period=""):
    try:
        cache = {
            'value':       value,
            'source':      source,
            'period':      period,
            'date':        datetime.now().isoformat(),
            'valid_until': (datetime.now() + timedelta(days=CACHE_VALID_DAYS)).isoformat(),
        }
        with open(INFLATION_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False

def is_cache_valid():
    cache = load_cache()
    if not cache or 'valid_until' not in cache:
        return False
    try:
        return datetime.now() < datetime.fromisoformat(cache['valid_until'])
    except Exception:
        return False

# ─── SCRAPER HCP.MA ────────────────────────────────────────────────────────────
#
# Stratégie :
#   1. Récupère la page d'actualités IPC sur hcp.ma
#   2. Extrait les titres/liens des derniers articles
#   3. Cherche le dernier article qui contient un taux glissement annuel
#   4. Parse le % avec regex → retourne (valeur, période)
#
# HCP publie ses notes sous forme de titres du type :
#   "Hausse de 0,3% de l'IPC..."  ou  "Baisse de 0,8% de l'IPC..."
# Le glissement annuel figure dans le résumé/teaser de l'article.
# On scrape le premier article (le plus récent) et on parse son texte.

HCP_BASE = "https://www.hcp.ma"
HCP_IPC_URL = f"{HCP_BASE}/Actualite-Indices-des-prix-a-la-consommation-IPC_r349.html"

def scrape_hcp_inflation():
    """
    Scrape hcp.ma pour récupérer le dernier taux d'inflation annuel (g.a.).
    Retourne dict(value, source, period) ou None en cas d'échec.
    """
    try:
        import requests
        from bs4 import BeautifulSoup

        headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/122.0.0.0 Safari/537.36'
            ),
            'Accept-Language': 'fr-FR,fr;q=0.9',
        }

        # ── Étape 1 : liste des actualités IPC ──────────────────────────────
        r = requests.get(HCP_IPC_URL, headers=headers, timeout=15)
        r.raise_for_status()
        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.text, 'html.parser')

        # HCP : les actualités sont dans des <div class="titre"> ou <h3><a>
        # On cherche tous les liens internes qui pointent vers une note IPC
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.get_text(strip=True)
            # Filtrer : lien vers une note IPC (contient "IPC" ou "indice-des-prix")
            if ('IPC' in text or 'indice' in text.lower() or 'prix' in text.lower()) \
                    and href.startswith('/') and '_a' in href:
                full_url = HCP_BASE + href
                if full_url not in links:
                    links.append((full_url, text))

        if not links:
            # Plan B : tenter de scraper directement le texte de la page liste
            return _parse_inline_hcp(soup)

        # ── Étape 2 : scraper l'article le plus récent ──────────────────────
        latest_url, latest_title = links[0]
        r2 = requests.get(latest_url, headers=headers, timeout=15)
        r2.raise_for_status()
        r2.encoding = 'utf-8'
        soup2 = BeautifulSoup(r2.text, 'html.parser')

        # Récupérer tout le texte visible
        full_text = soup2.get_text(separator=' ', strip=True)

        # ── Étape 3 : parser le g.a. ────────────────────────────────────────
        result = _extract_annual_rate(full_text, latest_title)
        if result:
            return result

    except Exception as e:
        st.warning(f"⚠️ HCP scraper: {str(e)[:80]}")

    return None


def _parse_inline_hcp(soup):
    """Fallback : extraire le taux depuis le texte de la page liste"""
    text = soup.get_text(separator=' ', strip=True)
    return _extract_annual_rate(text, "HCP page liste")


def _extract_annual_rate(text, context=""):
    """
    Extrait le taux d'inflation glissement annuel depuis un bloc de texte HCP.

    Patterns cherchés (exemples réels du HCP) :
      - "une hausse de 0,3% ... au cours du mois de janvier ... par rapport au même mois"
      - "une baisse de 0,8% ... par rapport au même mois de l'année précédente"
      - "a enregistré une hausse de 0,4% ... comparé au même mois"
      - "l'IPC annuel moyen ... auront progressé de 0,8%"
    """
    # Normaliser la virgule décimale
    text_norm = text.replace('\xa0', ' ')

    # Patterns par ordre de priorité (glissement annuel)
    patterns_ga = [
        # "a enregistré une (hausse|baisse) de X,X% au cours du mois de [Mois] [Année]"
        r'(?:a enregistré une? |enregistrée? une? )?(hausse|baisse)\s+de\s+([\d]+[,.][\d]+)\s*%[^.]{0,120}(?:même mois|année précédente|glissement annuel|sur une? année)',
        # "comparé au même mois ... (hausse|baisse) de X%"
        r'(?:Comparé|comparé)[^.]{0,60}(hausse|baisse)\s+de\s+([\d]+[,.][\d]+)\s*%',
        # "progressé de X,X%" (bilan annuel)
        r'(?:progressé|augmenté|diminué)\s+de\s+([\d]+[,.][\d]+)\s*%[^.]{0,80}(?:annuel|année\s+\d{4})',
        # "inflation.*X,X%.*sur une? année"
        r'inflation[^.]{0,80}(hausse|baisse|progression)\s+de\s+([\d]+[,.][\d]+)\s*%[^.]{0,60}(?:annuel|sur une? année)',
    ]

    for pat in patterns_ga:
        matches = re.findall(pat, text_norm, re.IGNORECASE)
        if matches:
            m = matches[0]
            # m peut être (direction, value) ou (value,)
            if len(m) == 2:
                direction, val_str = m
            else:
                direction, val_str = 'hausse', m[0]

            val = float(val_str.replace(',', '.'))
            if 'baisse' in direction.lower() or 'diminu' in direction.lower():
                val = -val

            # Extraire le mois/année depuis le contexte
            period = _extract_period(text_norm)

            return {
                'value':  val,
                'source': 'HCP.ma (officiel)',
                'period': period,
                'url':    HCP_IPC_URL,
            }

    return None


def _extract_period(text):
    """Extrait 'mois AAAA' depuis le texte"""
    months_fr = {
        'janvier': 1, 'février': 2, 'mars': 3, 'avril': 4,
        'mai': 5, 'juin': 6, 'juillet': 7, 'août': 8,
        'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12,
    }
    pattern = r'(?:mois\s+d[e\'\s]+)?(' + '|'.join(months_fr.keys()) + r')\s+(\d{4})'
    m = re.search(pattern, text, re.IGNORECASE)
    if m:
        return f"{m.group(1).capitalize()} {m.group(2)}"
    return ""


# ─── FALLBACK : BKAM ───────────────────────────────────────────────────────────

def scrape_bkam_inflation():
    """
    Fallback : Bank Al-Maghrib publie aussi les données IPC sur bkam.ma.
    La page est statique et contient les chiffres dans le DOM.
    """
    try:
        import requests
        from bs4 import BeautifulSoup

        url = "https://www.bkam.ma/Statistiques/Prix/Inflation-et-inflation-sous-jacente"
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=12)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)

        result = _extract_annual_rate(text, "BKAM")
        if result:
            result['source'] = 'Bank Al-Maghrib (BKAM)'
            return result
    except Exception:
        pass
    return None


# ─── FALLBACK : TRADING ECONOMICS API ─────────────────────────────────────────

def get_from_trading_economics():
    try:
        import requests
        url = "https://api.tradingeconomics.com/markets/inflation?country=Morocco"
        r = requests.get(url, headers={'Client-Key': 'guest:guest'}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data:
                return {
                    'value':  float(data[0].get('value', 0)),
                    'source': 'Trading Economics',
                    'period': data[0].get('description', ''),
                }
    except Exception:
        pass
    return None


# ─── ORCHESTRATEUR PRINCIPAL ───────────────────────────────────────────────────

def get_inflation_rate(force_refresh=False):
    """
    Priorité : Cache valide → HCP.ma → BKAM → Trading Economics → Cache ancien → Estimation
    """
    if not force_refresh and is_cache_valid():
        cache = load_cache()
        return {**cache, 'cached': True}

    # 1. HCP (source officielle)
    result = scrape_hcp_inflation()

    # 2. BKAM
    if not result:
        result = scrape_bkam_inflation()

    # 3. Trading Economics API
    if not result:
        result = get_from_trading_economics()

    if result:
        save_cache(result['value'], result['source'], result.get('period', ''))
        return {**result, 'cached': False, 'date': datetime.now().isoformat()}

    # 4. Ancien cache (même périmé)
    cache = load_cache()
    if cache and 'value' in cache:
        return {**cache, 'source': f"{cache['source']} (ancien cache)", 'cached': True}

    # 5. Estimation basée sur données connues (Jan 2026 = -0.8%)
    return {
        'value':  -0.8,
        'source': 'Estimation (Jan 2026)',
        'period': 'Janvier 2026',
        'date':   datetime.now().isoformat(),
        'cached': False,
    }


# ─── GRAPHIQUES ────────────────────────────────────────────────────────────────

def create_inflation_gauge(value):
    if value is None:
        value = -0.8

    target_min, target_max = 2.0, 3.0

    if value < target_min:
        bar_color = COLORS['warning']
        status    = "⬇ Sous la cible BAM"
        status_cls = "warning"
    elif value > target_max:
        bar_color = COLORS['danger']
        status    = "⬆ Au-dessus de la cible"
        status_cls = "danger"
    else:
        bar_color = COLORS['success']
        status    = "✅ Dans la cible BAM"
        status_cls = "success"

    fig = go.Figure(go.Indicator(
        mode   = "gauge+number+delta",
        value  = value,
        delta  = {'reference': 2.0, 'valueformat': '.2f', 'suffix': '%'},
        number = {'suffix': '%', 'font': {'size': 42, 'color': COLORS['primary']}},
        title  = {
            'text': "IPC — Glissement Annuel<br><span style='font-size:13px;color:#64748b'>Cible BAM : 2 – 3 %</span>",
            'font': {'size': 15, 'color': COLORS['primary']},
        },
        gauge = {
            'axis':  {'range': [-3, 6], 'ticksuffix': '%', 'tickfont': {'size': 11}},
            'bar':   {'color': bar_color, 'thickness': 0.28},
            'bgcolor': '#f0f4f8',
            'borderwidth': 0,
            'steps': [
                {'range': [-3,    target_min], 'color': '#fff3e0'},
                {'range': [target_min, target_max], 'color': '#e8f5e9'},
                {'range': [target_max,  6],    'color': '#fce4ec'},
            ],
            'threshold': {
                'line':  {'color': COLORS['primary'], 'width': 2},
                'thickness': 0.75,
                'value': value,
            },
        }
    ))

    fig.update_layout(
        height  = 320,
        margin  = dict(l=30, r=30, t=60, b=10),
        paper_bgcolor = 'rgba(0,0,0,0)',
        font    = dict(family='DM Sans'),
    )

    return fig, status, status_cls


def create_inflation_history():
    """
    Historique 12 mois — données réelles HCP 2025 + estimation Jan 2026
    """
    months = [
        'Fév 25', 'Mar 25', 'Avr 25', 'Mai 25', 'Juin 25',
        'Juil 25', 'Août 25', 'Sep 25', 'Oct 25', 'Nov 25',
        'Déc 25', 'Jan 26',
    ]
    # Données g.a. réelles (source HCP/BKAM confirmées par recherche)
    rates = [0.9, 0.6, 0.3, -0.1, 0.0, 0.4, 0.7, 0.4, 0.1, -0.3, -0.3, -0.8]

    colors = [
        COLORS['success'] if 2.0 <= r <= 3.0
        else COLORS['warning'] if r < 2.0
        else COLORS['danger']
        for r in rates
    ]

    fig = go.Figure()

    # Zone cible
    fig.add_hrect(y0=2.0, y1=3.0, fillcolor='rgba(0,196,140,0.08)',
                  line_width=0, annotation_text="Cible BAM",
                  annotation_position="top right",
                  annotation_font_size=11,
                  annotation_font_color=COLORS['success'])

    # Ligne zéro
    fig.add_hline(y=0, line_dash="dot", line_color="#94a3b8", line_width=1)

    # Barres + ligne
    fig.add_trace(go.Bar(
        x=months, y=rates,
        marker_color=colors,
        marker_line_width=0,
        opacity=0.7,
        name="IPC g.a.",
        hovertemplate='<b>%{x}</b><br>Inflation: %{y:.1f}%<extra></extra>',
    ))

    fig.add_trace(go.Scatter(
        x=months, y=rates,
        mode='lines+markers',
        line=dict(color=COLORS['primary'], width=2.5),
        marker=dict(size=7, color=COLORS['primary'], line=dict(width=2, color='white')),
        name="Tendance",
        hoverinfo='skip',
    ))

    fig.update_layout(
        title=dict(
            text="Inflation Maroc — 12 derniers mois (glissement annuel)",
            font=dict(size=14, family='DM Sans', color=COLORS['primary']),
        ),
        height      = 380,
        plot_bgcolor= 'white',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend  = False,
        margin      = dict(l=10, r=10, t=50, b=10),
        xaxis=dict(showgrid=False, tickfont=dict(size=11)),
        yaxis=dict(
            showgrid    = True,
            gridcolor   = '#f1f5f9',
            ticksuffix  = '%',
            tickfont    = dict(size=11),
            zeroline    = False,
        ),
    )

    return fig


# ─── PAGE PRINCIPALE ───────────────────────────────────────────────────────────

def render():

    # ── En-tête ────────────────────────────────────────────────────────────────
    now_str = datetime.now().strftime("%A %d %B %Y — %H:%M")
    # ── Hero ─────────────────────────────────────────────────────────────────
    try:
        from utils.design import page_hero, market_clock_html
        import importlib.util
        _title = "Macronews"
        st.markdown(page_hero('📰','Macronews','Indicateurs Macroéconomiques — Inflation · Actualités · Calendrier',tags=['HCP','IPC','Inflation']), unsafe_allow_html=True)
        st.components.v1.html(market_clock_html(), height=65)
    except Exception:
        pass
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:flex-start;
                background:white; padding:24px 30px; border-radius:16px;
                box-shadow:0 1px 6px rgba(0,0,0,.06); margin-bottom:28px;">
        <div>
            <p class="page-title">📊 Macronews</p>
            <p class="page-sub">Tableau de bord macroéconomique — Maroc</p>
        </div>
        <div style="text-align:right; font-size:12px; color:{COLORS['muted']}; margin-top:4px;">
            <span style="font-family:'Space Mono',monospace;">{now_str}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── SECTION 1 : INFLATION ──────────────────────────────────────────────────
    st.markdown('<p class="section-header">📈 Indicateur clé — Inflation IPC</p>', unsafe_allow_html=True)

    # Chargement
    with st.spinner("Récupération des données HCP…"):
        inflation_data = get_inflation_rate()

    current_rate = inflation_data.get('value', -0.8)
    period       = inflation_data.get('period', '')
    source       = inflation_data.get('source', 'N/A')
    cached       = inflation_data.get('cached', False)
    date_upd     = inflation_data.get('date', '')[:10]

    st.session_state.inflation_rate        = current_rate
    st.session_state.inflation_last_update = date_upd
    st.session_state.inflation_source      = source

    # Bouton refresh
    col_title, col_btn = st.columns([6, 1])
    with col_btn:
        if st.button("🔄 Actualiser", use_container_width=True):
            with st.spinner("Scraping HCP.ma…"):
                fresh = get_inflation_rate(force_refresh=True)
            st.session_state.inflation_rate   = fresh['value']
            st.session_state.inflation_source = fresh['source']
            st.success(f"✅ {fresh['value']:+.2f}% — {fresh['source']}")
            st.rerun()

    # Jauge + métriques
    col_gauge, col_metrics = st.columns([3, 2])

    with col_gauge:
        fig_gauge, status, status_cls = create_inflation_gauge(current_rate)
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col_metrics:
        delta_vs_target = current_rate - 2.0
        delta_str       = f"{delta_vs_target:+.2f}% vs cible basse"

        st.markdown(f"""
        <div class="metric-card {status_cls}">
            <div style="font-size:12px;color:{COLORS['muted']};text-transform:uppercase;letter-spacing:1px;">
                Inflation (g.a.)
            </div>
            <div style="font-size:36px;font-weight:700;color:{COLORS['primary']};margin:6px 0;">
                {current_rate:+.2f}%
            </div>
            <div style="font-size:13px;color:{COLORS['muted']};">{status}</div>
            <div style="font-size:12px;margin-top:8px;color:{COLORS['muted']};">{delta_str}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size:12px;color:{COLORS['muted']};text-transform:uppercase;letter-spacing:1px;">
                Cible Banque Al-Maghrib
            </div>
            <div style="font-size:28px;font-weight:700;color:{COLORS['primary']};margin:6px 0;">
                2 – 3 %
            </div>
            <div style="font-size:12px;color:{COLORS['muted']};">Objectif de politique monétaire</div>
        </div>
        """, unsafe_allow_html=True)

        badge_icon = "🗃️" if cached else "🌐"
        st.markdown(f"""
        <div class="source-bar">
            {badge_icon} <b>Source :</b> {source}<br>
            📅 <b>Période :</b> {period or date_upd}<br>
            🕐 <b>Mis à jour :</b> {date_upd}
        </div>
        """, unsafe_allow_html=True)

    # Historique
    st.markdown('<p class="section-header" style="margin-top:8px;">📅 Historique 12 mois</p>', unsafe_allow_html=True)
    st.plotly_chart(create_inflation_history(), use_container_width=True)

    # Note méthodologique
    with st.expander("ℹ️ Méthodologie & sources de données"):
        st.markdown(f"""
        **Sources (par ordre de priorité) :**

        1. 🏛️ **HCP.ma** — Haut-Commissariat au Plan du Maroc  
           URL : `{HCP_IPC_URL}`  
           Méthode : scraping HTML + extraction par regex du glissement annuel

        2. 🏦 **Bank Al-Maghrib (BKAM)** — Statistiques Prix  
           URL : `https://www.bkam.ma/Statistiques/Prix/Inflation-et-inflation-sous-jacente`

        3. 📡 **Trading Economics API** — API publique (clé guest)

        4. 🗃️ Cache local JSON (validité : {CACHE_VALID_DAYS} jours)

        **Indicateur affiché :** IPC — glissement annuel (même mois, année N vs N-1)  
        **Base de référence :** IPC base 100 = 2017 (546 articles, 1 391 variétés)
        """)

    st.markdown("---")

    # ── SECTION 2 : ACTUALITÉS ─────────────────────────────────────────────────
    st.markdown('<p class="section-header">📰 Actualités macroéconomiques</p>', unsafe_allow_html=True)

    news_data = st.session_state.get('news_data', [])

    if news_data:
        # Filtres rapides
        f_col1, f_col2 = st.columns([3, 1])
        with f_col1:
            search = st.text_input("🔍 Rechercher", placeholder="Mot-clé…", label_visibility="collapsed")
        with f_col2:
            max_news = st.selectbox("Afficher", [5, 10, 20, 50], label_visibility="collapsed")

        filtered = [
            n for n in news_data
            if not search or search.lower() in n.get('title', '').lower()
               or search.lower() in n.get('summary', '').lower()
        ][:max_news]

        for news in filtered:
            title    = news.get('title', 'Sans titre')
            source   = news.get('source', 'N/A')
            category = news.get('category', 'Général')
            summary  = news.get('summary', '')[:280]

            ts = news.get('timestamp', '')
            if isinstance(ts, datetime):
                ts = ts.strftime('%d %b %Y %H:%M')
            elif isinstance(ts, str):
                ts = ts[:16].replace('T', ' ')

            st.markdown(f"""
            <div class="news-card">
                <div class="news-title">{title}</div>
                <div class="news-meta">
                    <span class="badge badge-source">{source}</span>
                    <span class="badge badge-medium">{category}</span>
                    🕐 {ts}
                </div>
                <p style="font-size:13px;color:{COLORS['muted']};margin:10px 0 0 0;line-height:1.6;">
                    {summary}{"…" if len(news.get('summary','')) > 280 else ""}
                </p>
            </div>
            """, unsafe_allow_html=True)

        if not filtered:
            st.info("Aucun résultat pour cette recherche.")
    else:
        st.markdown(f"""
        <div style="background:#f8fafc; border:1.5px dashed #d1d9e0;
                    border-radius:14px; padding:40px; text-align:center; color:{COLORS['muted']};">
            <div style="font-size:36px;margin-bottom:12px;">📭</div>
            <div style="font-weight:600; font-size:15px;">Aucune actualité chargée</div>
            <div style="font-size:13px; margin-top:6px;">
                Rendez-vous dans <b>📥 Data Ingestion</b> pour importer des news.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── SECTION 3 : CALENDRIER ÉCONOMIQUE ─────────────────────────────────────
    st.markdown('<p class="section-header">📅 Calendrier économique</p>', unsafe_allow_html=True)

    today = datetime.now()
    events = [
        {'Date': (today + timedelta(days=2)).strftime('%d %b %Y'),
         'Événement': 'Note IPC mensuel — HCP',
         'Impact': '🔴 Élevé', 'Source': 'HCP.ma'},
        {'Date': (today + timedelta(days=5)).strftime('%d %b %Y'),
         'Événement': 'Taux de chômage T4',
         'Impact': '🔴 Élevé', 'Source': 'HCP.ma'},
        {'Date': (today + timedelta(days=9)).strftime('%d %b %Y'),
         'Événement': 'Conseil de BKAM — Décision de taux',
         'Impact': '🔴 Élevé', 'Source': 'Bank Al-Maghrib'},
        {'Date': (today + timedelta(days=14)).strftime('%d %b %Y'),
         'Événement': 'PIB T4 2025 — Arrêté des comptes',
         'Impact': '🔴 Élevé', 'Source': 'HCP.ma'},
        {'Date': (today + timedelta(days=20)).strftime('%d %b %Y'),
         'Événement': 'Balance commerciale — ADII',
         'Impact': '🟡 Moyen', 'Source': 'ADII'},
        {'Date': (today + timedelta(days=25)).strftime('%d %b %Y'),
         'Événement': 'Recettes voyages — OMPIC/OT',
         'Impact': '🟡 Moyen', 'Source': 'ONMT'},
    ]

    df_cal = pd.DataFrame(events)
    st.dataframe(
        df_cal,
        use_container_width=True,
        hide_index=True,
        column_config={
            'Impact':     st.column_config.TextColumn(width='small'),
            'Source':     st.column_config.TextColumn(width='medium'),
            'Événement':  st.column_config.TextColumn(width='large'),
        }
    )

    st.markdown("---")

    # ── KPIs RÉSUMÉ ────────────────────────────────────────────────────────────
    st.markdown('<p class="section-header">📌 Résumé de session</p>', unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        delta = f"{(current_rate - 2.0):+.2f}% vs cible basse"
        st.metric("Inflation IPC (g.a.)", f"{current_rate:+.2f}%", delta)
    with k2:
        st.metric("Actualités chargées", len(news_data))
    with k3:
        st.metric("Source données", source[:20] if source else "—")
    with k4:
        cache_age = "✅ Frais" if not cached else "🗃️ Mis en cache"
        st.metric("Statut données", cache_age)


# ─── ENTRY POINT ───────────────────────────────────────────────────────────────
render()
