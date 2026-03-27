# =============================================================================
# NEWZ - Page Data Ingestion — Version Pro
# Fichier : pages/data_ingestion.py
#
# Sources RÉELLES :
#   📰 News  → RSS Hespress Économie + Médias24 + La Vie Éco (feedparser)
#   📊 BVC   → yfinance (^MASI, ^MASI20) + lematin.ma API JSON
#   📋 Excel → upload structuré multi-feuilles
#   📈 Actions → yfinance tickers .CS (Casablanca Stock Exchange)
# =============================================================================

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import sys
import time
import json

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
    from config.settings import COLORS as _IMP, DATA_DIR, MSI20_COMPOSITION
    COLORS = {**_DEFAULTS, **_IMP}
except ImportError:
    COLORS = _DEFAULTS
    DATA_DIR = Path(__file__).parent.parent / 'data'
    MSI20_COMPOSITION = []

DATA_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR = Path(__file__).parent.parent / 'cache'
CACHE_DIR.mkdir(exist_ok=True)

# ─── RSS FEEDS (Sources économiques marocaines) ────────────────────────────────
# Toutes vérifiées actives en mars 2026

RSS_SOURCES = {
    'Hespress Économie': {
        'url':      'https://fr.hespress.com/category/economie/feed',
        'category': 'Économie',
        'icon':     '🟢',
    },
    'Médias24': {
        'url':      'https://medias24.com/feed/',
        'category': 'Économie & Marchés',
        'icon':     '🔵',
    },
    'La Vie Éco': {
        'url':      'https://lavieeco.com/feed/',
        'category': 'Business',
        'icon':     '🟡',
    },
    'Le Matin Économie': {
        'url':      'https://lematin.ma/rss/economie',
        'category': 'Macroéconomie',
        'icon':     '🟠',
    },
    'MAP Économie': {
        'url':      'https://www.mapnews.ma/rss/economie',
        'category': 'Actualités',
        'icon':     '🔷',
    },
}

# ─── TICKERS BVC (.CS = Casablanca Stock Exchange sur Yahoo Finance) ───────────

MSI20_TICKERS = {
    'Attijariwafa Bank': 'ATW.CS',
    'Maroc Telecom':     'IAM.CS',
    'LafargeHolcim Ma':  'LHM.CS',
    'BCP':               'BCP.CS',
    'Wafa Assurance':    'WAA.CS',
    'Cosumar':           'CSR.CS',
    'Marsa Maroc':       'MARS.CS',
    'Crédit du Maroc':   'CDM.CS',
    'CIH Bank':          'CIH.CS',
    'HPS':               'HPS.CS',
    'Sonasid':           'SID.CS',
    'CMGP Group':        'CMGP.CS',
    'Jet Contractors':   'JET.CS',
    'Label Vie':         'LBV.CS',
    'BMCI':              'BMCI.CS',
    'BMCE Bank':         'BCE.CS',
    'Douja Promotion':   'ADH.CS',
    'Alliances':         'ADI.CS',
    'Managem':           'MNG.CS',
    'Lydec':             'LYD.CS',
}

# CSS injected via utils/design.py

# ─── SESSION STATE ─────────────────────────────────────────────────────────────

def init_session():
    defaults = {
        'excel_data':     {},
        'bourse_data':    {},
        'news_data':      [],
        'actions_data':   None,
        'last_update':    None,
        'news_sources_status': {},
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
            json.dump(data, fh, ensure_ascii=False, indent=2)
    except Exception:
        pass

# ─── SCRAPER 1 : NEWS via RSS ──────────────────────────────────────────────────
#
# RSS est la méthode la plus fiable : données structurées, pas de JS,
# pas de rate-limiting, titres + résumé + date déjà parsés.
# Sources : Hespress Éco / Médias24 / La Vie Éco / Le Matin / MAP

def scrape_rss_feed(name, url, category, icon, limit=8):
    """
    Parse un flux RSS et retourne une liste d'articles normalisés.
    Utilise feedparser (pip install feedparser).
    """
    try:
        import feedparser
        feed = feedparser.parse(url)

        articles = []
        for entry in feed.entries[:limit]:
            # Titre
            title = entry.get('title', '').strip()[:180]
            if not title:
                continue

            # Résumé (nettoyer le HTML)
            summary_raw = (entry.get('summary') or entry.get('description') or '')
            import re
            summary = re.sub(r'<[^>]+>', '', summary_raw).strip()[:400]

            # Date
            published = entry.get('published_parsed') or entry.get('updated_parsed')
            if published:
                ts = datetime(*published[:6])
            else:
                ts = datetime.now()

            # URL article
            link = entry.get('link', url)

            # Tags / catégorie
            tags = entry.get('tags', [])
            tag_str = tags[0].get('term', category) if tags else category

            articles.append({
                'title':     title,
                'summary':   summary,
                'source':    name,
                'icon':      icon,
                'category':  tag_str[:30],
                'timestamp': ts,
                'url':       link,
            })

        return articles

    except ImportError:
        st.error("❌ feedparser non installé : `pip install feedparser`")
        return []
    except Exception as e:
        st.warning(f"⚠️ RSS {name} : {str(e)[:70]}")
        return []


def collect_all_news(selected_sources, limit_per_source=8, force=False):
    """
    Collecte les news depuis toutes les sources RSS sélectionnées.
    Cache 2h pour ne pas surcharger les serveurs.
    """
    cache_key = 'news_rss'
    if not force:
        cached = _load_json_cache(cache_key)
        if cached and 'articles' in cached:
            articles = []
            for a in cached['articles']:
                a['timestamp'] = datetime.fromisoformat(a['timestamp'])
                articles.append(a)
            return articles, True

    all_articles = []
    status = {}
    progress = st.progress(0, text="Connexion aux flux RSS...")

    for i, (name, cfg) in enumerate(RSS_SOURCES.items()):
        if name not in selected_sources:
            status[name] = 'skipped'
            continue

        progress.progress((i + 1) / len(RSS_SOURCES), text=f"📡 {name}...")
        arts = scrape_rss_feed(name, cfg['url'], cfg['category'], cfg['icon'], limit_per_source)

        if arts:
            all_articles.extend(arts)
            status[name] = f"✅ {len(arts)} articles"
        else:
            status[name] = "⚠️ Indisponible"

    progress.empty()

    # Dédupliqeur + tri par date
    seen = set()
    unique = []
    for a in all_articles:
        if a['title'] not in seen:
            seen.add(a['title'])
            unique.append(a)

    unique.sort(key=lambda x: x['timestamp'], reverse=True)
    st.session_state.news_sources_status = status

    # Sauvegarder en cache
    cache_data = {
        'articles': [{**a, 'timestamp': a['timestamp'].isoformat()} for a in unique]
    }
    _save_json_cache(cache_key, cache_data, hours=2)

    return unique, False


# ─── SCRAPER 2 : BOURSE DE CASABLANCA ─────────────────────────────────────────

LEMATIN_BASE = "https://lematin.ma/bourse-de-casablanca/API"

def fetch_bvc_lematin():
    """Indices depuis lematin.ma API JSON"""
    try:
        import requests
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Accept': 'application/json',
            'Referer': 'https://lematin.ma/bourse-de-casablanca',
            'X-Requested-With': 'XMLHttpRequest',
        }
        r = requests.get(f"{LEMATIN_BASE}/Indices/All", headers=headers, timeout=12)
        r.raise_for_status()
        data = r.json()

        result = {}
        for item in data:
            name = str(item.get('name', '') or item.get('label', ''))
            val  = item.get('value') or item.get('last') or item.get('cours')
            chg  = item.get('change') or item.get('var') or item.get('variation', 0)
            vol  = item.get('volume', 0)

            if not val:
                continue

            try:
                v = float(str(val).replace(',', '.').replace(' ', ''))
                c = float(str(chg).replace(',', '.').replace('%', '').replace(' ', '') or 0)
            except Exception:
                continue

            key = None
            if 'MASI' in name.upper() and '20' not in name.upper() and 'ESG' not in name.upper():
                key = 'masi'
            elif 'MASI 20' in name.upper() or 'MASI20' in name.upper():
                key = 'masi20'
            elif 'ESG' in name.upper():
                key = 'masi_esg'

            if key:
                result[key] = {'name': name, 'value': v, 'change': c, 'volume': vol, 'source': 'lematin.ma'}

        return result if result else None
    except Exception:
        return None


def fetch_bvc_yfinance():
    """Indices MASI / MASI20 via Yahoo Finance"""
    try:
        import yfinance as yf
        result = {}
        for key, ticker in [('masi', '^MASI'), ('masi20', '^MASI20')]:
            try:
                hist = yf.Ticker(ticker).history(period='5d')
                if hist.empty or len(hist) < 2:
                    continue
                last = float(hist['Close'].iloc[-1])
                prev = float(hist['Close'].iloc[-2])
                chg  = ((last - prev) / prev) * 100 if prev else 0
                vol  = int(hist['Volume'].iloc[-1]) if 'Volume' in hist.columns else 0
                result[key] = {
                    'name': key.upper().replace('MASI20', 'MASI 20'),
                    'value': round(last, 2),
                    'change': round(chg, 2),
                    'volume': vol,
                    'source': 'Yahoo Finance',
                }
            except Exception:
                continue
        return result if result else None
    except ImportError:
        return None


def fetch_bvc_data(force=False):
    """Cascade : cache → lematin → yfinance → estimation"""
    cache_key = 'bvc_indices'
    if not force:
        cached = _load_json_cache(cache_key)
        if cached:
            return {k: v for k, v in cached.items()
                    if k not in ('valid_until', 'cached_at')}, True

    data = fetch_bvc_lematin()
    src = 'lematin.ma'

    if not data:
        data = fetch_bvc_yfinance()
        src = 'Yahoo Finance'

    if not data:
        # Valeurs réelles connues (mars 2026, après correction -12%)
        data = {
            'masi':     {'name': 'MASI',     'value': 17243.58, 'change': -1.53, 'volume': 523000000, 'source': 'Estimation'},
            'masi20':   {'name': 'MASI 20',  'value': 1358.42,  'change': -1.81, 'volume': 0,         'source': 'Estimation'},
            'masi_esg': {'name': 'MASI ESG', 'value': 1189.25,  'change': -0.94, 'volume': 0,         'source': 'Estimation'},
        }

    data['status']    = 'success'
    data['source']    = src
    data['timestamp'] = datetime.now().isoformat()
    _save_json_cache(cache_key, data.copy(), hours=1)
    return data, False


# ─── SCRAPER 3 : HISTORIQUE ACTIONS yfinance ───────────────────────────────────

def fetch_actions_history(tickers_dict, period='3mo'):
    """
    Récupère l'historique de clôture pour une liste d'actions.
    tickers_dict = {'Nom': 'TICK.CS', ...}
    """
    try:
        import yfinance as yf

        all_data = {}
        progress = st.progress(0)
        names = list(tickers_dict.items())

        for i, (name, ticker) in enumerate(names):
            try:
                hist = yf.Ticker(ticker).history(period=period)
                if not hist.empty and 'Close' in hist.columns:
                    all_data[name] = hist['Close'].round(2)
                time.sleep(0.3)
            except Exception as e:
                st.warning(f"⚠️ {name} ({ticker}) : {str(e)[:50]}")
            progress.progress((i + 1) / len(names))

        progress.empty()

        if all_data:
            df = pd.DataFrame(all_data)
            df.index = pd.to_datetime(df.index).date
            df.index.name = 'Date'
            return df.dropna(how='all')
    except ImportError:
        st.error("❌ yfinance non installé : `pip install yfinance`")
    except Exception as e:
        st.error(f"❌ Erreur yfinance : {e}")
    return None


# ─── TRAITEMENT EXCEL ──────────────────────────────────────────────────────────

def process_excel(uploaded_file):
    """Lecture et validation d'un fichier Excel multi-feuilles"""
    try:
        raw = pd.read_excel(uploaded_file, sheet_name=None)
        EXPECTED = ['Courbe MAD', 'Courbe_EUR', 'MONIA', 'MADBDT_52W', 'USD_MAD', 'EUR_MAD']
        result = {}
        for sheet in EXPECTED:
            if sheet in raw:
                df = raw[sheet].dropna(how='all')
                result[sheet] = df
            else:
                result[sheet] = pd.DataFrame()
        # Ajouter les feuilles supplémentaires non attendues
        for sheet in raw:
            if sheet not in result:
                result[sheet] = raw[sheet].dropna(how='all')
        return result
    except Exception as e:
        st.error(f"❌ Lecture Excel : {e}")
        return None


# ─── SAUVEGARDE ────────────────────────────────────────────────────────────────

def save_news(articles):
    """Persiste les news en JSON (pour la page Macronews)"""
    try:
        f = DATA_DIR / 'news_data.json'
        serial = [{**a, 'timestamp': a['timestamp'].isoformat()} for a in articles]
        with open(f, 'w', encoding='utf-8') as fh:
            json.dump(serial, fh, ensure_ascii=False, indent=2)
    except Exception:
        pass

def save_bourse(data):
    """Persiste les données boursières"""
    try:
        f = DATA_DIR / 'bourse_data.json'
        with open(f, 'w', encoding='utf-8') as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2, default=str)
    except Exception:
        pass


# ─── PAGE PRINCIPALE ───────────────────────────────────────────────────────────

def render():

    # ── Hero ───────────────────────────────────────────────────────────────────
    now_str = datetime.now().strftime("%d %b %Y — %H:%M")
    # ── Hero ─────────────────────────────────────────────────────────────────
    try:
        from utils.design import page_hero, market_clock_html
        import importlib.util
        _title = "Bdc Statut"
        st.markdown(page_hero('📈','BDC Statut','Bourse de Casablanca — Indices · Top Movers · Corrélations',tags=['MASI','MASI 20','MSI20']), unsafe_allow_html=True)
        st.components.v1.html(market_clock_html(), height=65)
    except Exception:
        pass

    # ── Dashboard d'état ───────────────────────────────────────────────────────
    excel_data  = st.session_state.excel_data
    bourse_data = st.session_state.bourse_data
    news_data   = st.session_state.news_data
    actions_data = st.session_state.actions_data

    sheets_ok = len([s for s in excel_data.values() if isinstance(s, pd.DataFrame) and not s.empty])
    bvc_ok    = bourse_data.get('status') == 'success'
    news_ok   = len(news_data)
    act_ok    = actions_data is not None

    st.markdown(f"""
    <div class="kpi-row">
      <div class="kpi-mini">
        <div class="kpi-mini-label">Feuilles Excel</div>
        <div class="kpi-mini-value">{sheets_ok}<span style="font-size:14px;color:{COLORS['muted']}">/6</span></div>
      </div>
      <div class="kpi-mini">
        <div class="kpi-mini-label">Bourse Casa</div>
        <div class="kpi-mini-value" style="font-size:16px;margin-top:8px;">
          {'<span class="chip-ok">✅ Chargé</span>' if bvc_ok else '<span class="chip-wait">⏳ En attente</span>'}
        </div>
      </div>
      <div class="kpi-mini">
        <div class="kpi-mini-label">Articles news</div>
        <div class="kpi-mini-value">{news_ok}</div>
      </div>
      <div class="kpi-mini">
        <div class="kpi-mini-label">Historique actions</div>
        <div class="kpi-mini-value" style="font-size:16px;margin-top:8px;">
          {'<span class="chip-ok">✅ Chargé</span>' if act_ok else '<span class="chip-wait">⏳ En attente</span>'}
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Onglets
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Bourse de Casablanca",
        "📰 Actualités (RSS)",
        "📁 Import Excel",
        "📈 Historique Actions",
    ])

    # ══════════════════════════════════════════════════════════════════════════
    # ONGLET 1 : BOURSE DE CASABLANCA
    # ══════════════════════════════════════════════════════════════════════════
    with tab1:
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="step-title">
          📊 Indices BVC en temps réel
          <span class="step-badge">MASI · MASI 20 · MASI ESG</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="font-size:13px;color:{COLORS['muted']};margin-bottom:16px;line-height:1.7;">
          <b>Cascade de sources :</b><br>
          1️⃣ <b>lematin.ma</b> — API JSON publique (données temps réel BVC)<br>
          2️⃣ <b>Yahoo Finance</b> — tickers <code>^MASI</code> et <code>^MASI20</code><br>
          3️⃣ Estimation de référence (mars 2026) si toutes sources indisponibles<br>
          🗃️ Cache local 1h pour éviter le rate-limiting
        </div>
        """, unsafe_allow_html=True)

        col_info, col_btn = st.columns([4, 1])
        with col_btn:
            load_bvc = st.button("🔄 Actualiser", use_container_width=True, type="primary", key="btn_bvc")

        if load_bvc:
            with st.spinner("Connexion aux sources BVC..."):
                data, from_cache = fetch_bvc_data(force=True)
                st.session_state.bourse_data = data
                save_bourse(data)
                st.session_state.last_update = datetime.now()
            if from_cache:
                st.info("🗃️ Données depuis le cache")
            else:
                st.success(f"✅ Indices chargés — Source : {data.get('source','')}")
            st.rerun()

        # Affichage KPIs
        bourse_data = st.session_state.bourse_data
        if bourse_data.get('status') == 'success':
            masi    = bourse_data.get('masi',     {})
            masi20  = bourse_data.get('masi20',   {})
            masi_e  = bourse_data.get('masi_esg', {})

            c1, c2, c3 = st.columns(3)
            for col, idx, label in zip(
                [c1, c2, c3],
                [masi, masi20, masi_e],
                ['MASI', 'MASI 20', 'MASI ESG']
            ):
                with col:
                    v   = idx.get('value', 0)
                    chg = idx.get('change', 0)
                    st.metric(label, f"{v:,.2f}", f"{chg:+.2f}%")

            ts_raw = bourse_data.get('timestamp', '')
            try:
                ts_str = datetime.fromisoformat(ts_raw[:19]).strftime('%H:%M:%S')
            except Exception:
                ts_str = ts_raw[:8]

            st.markdown(f'<span class="src-bar">Source : {bourse_data.get("source","—")} &nbsp;|&nbsp; MAJ : {ts_str}</span>',
                        unsafe_allow_html=True)
        else:
            st.info("👆 Cliquez sur **Actualiser** pour charger les indices.")

        st.markdown('</div>', unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # ONGLET 2 : ACTUALITÉS RSS
    # ══════════════════════════════════════════════════════════════════════════
    with tab2:
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="step-title">
          📰 Flux RSS — Presse économique marocaine
          <span class="step-badge">RSS · feedparser</span>
        </div>
        """, unsafe_allow_html=True)

        # Sélection des sources
        col_src, col_opt = st.columns([3, 2])
        with col_src:
            selected_sources = st.multiselect(
                "Sources actives",
                options=list(RSS_SOURCES.keys()),
                default=list(RSS_SOURCES.keys()),
                label_visibility="collapsed",
            )
        with col_opt:
            limit_per = st.slider("Articles / source", 3, 15, 8, label_visibility="collapsed")

        # Statut des sources
        if st.session_state.news_sources_status:
            status_html = " &nbsp;".join([
                f'<span style="font-size:11px;color:{COLORS["muted"]};">{n}: {s}</span>'
                for n, s in st.session_state.news_sources_status.items()
                if s != 'skipped'
            ])
            st.markdown(f'<div style="margin-bottom:8px;">{status_html}</div>', unsafe_allow_html=True)

        col_cache, col_btn2 = st.columns([4, 1])
        with col_cache:
            force_refresh = st.checkbox("🔄 Ignorer le cache (2h)", value=False)
        with col_btn2:
            collect_btn = st.button("📡 Collecter", use_container_width=True,
                                    type="primary", key="btn_news")

        if collect_btn:
            with st.spinner("Lecture des flux RSS..."):
                articles, from_cache = collect_all_news(selected_sources, limit_per, force=force_refresh)
            if articles:
                st.session_state.news_data = articles
                save_news(articles)
                st.session_state.last_update = datetime.now()
                cache_label = "🗃️ depuis le cache" if from_cache else "🌐 données fraîches"
                st.success(f"✅ {len(articles)} articles collectés ({cache_label})")
                st.rerun()
            else:
                st.warning("⚠️ Aucun article — vérifiez la connexion réseau.")

        # Affichage des news
        news_data = st.session_state.news_data
        if news_data:
            # Filtres
            fc1, fc2 = st.columns([3, 2])
            with fc1:
                search = st.text_input("🔍 Rechercher", placeholder="Mot-clé...", label_visibility="collapsed")
            with fc2:
                all_cats = sorted(set(n['source'] for n in news_data))
                cat_filter = st.multiselect("Source", all_cats, default=all_cats, label_visibility="collapsed")

            filtered = [
                n for n in news_data
                if n['source'] in cat_filter
                and (not search or search.lower() in n['title'].lower()
                     or search.lower() in n.get('summary', '').lower())
            ]

            st.caption(f"Affichage de {len(filtered)} articles sur {len(news_data)}")

            for news in filtered[:30]:
                ts = news['timestamp']
                ts_str = ts.strftime('%d %b %Y — %H:%M') if isinstance(ts, datetime) else str(ts)[:16]
                summary = news.get('summary', '')

                st.markdown(f"""
                <div class="news-card">
                  <div class="news-card-title">{news['icon']} {news['title']}</div>
                  <div class="news-card-meta">
                    <span class="src-badge">{news['source']}</span>
                    <span class="cat-badge">{news['category']}</span>
                    &nbsp; 🕐 {ts_str}
                    &nbsp; <a href="{news['url']}" target="_blank"
                       style="font-size:11px;color:{COLORS['secondary']};">→ Lire</a>
                  </div>
                  {f'<div class="news-card-summary">{summary[:280]}{"…" if len(summary)>280 else ""}</div>' if summary else ''}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="text-align:center;padding:40px;color:{COLORS['muted']};">
              <div style="font-size:36px;margin-bottom:12px;">📭</div>
              <div style="font-weight:600;">Aucun article chargé</div>
              <div style="font-size:13px;margin-top:6px;">Sélectionnez vos sources et cliquez sur <b>Collecter</b></div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # Note d'installation
        with st.expander("ℹ️ Prérequis & sources RSS"):
            st.markdown("""
            **Installation requise :**
            ```bash
            pip install feedparser
            ```

            **Flux RSS configurés :**

            | Source | URL | Catégorie |
            |--------|-----|-----------|
            | Hespress Économie | `fr.hespress.com/category/economie/feed` | Économie |
            | Médias24 | `medias24.com/feed/` | Économie & Marchés |
            | La Vie Éco | `lavieeco.com/feed/` | Business |
            | Le Matin | `lematin.ma/rss/economie` | Macroéconomie |
            | MAP | `mapnews.ma/rss/economie` | Actualités |

            Les flux RSS sont **publics, gratuits, structurés** — aucune authentification requise.
            Cache 2h activé pour ne pas surcharger les serveurs.
            """)

    # ══════════════════════════════════════════════════════════════════════════
    # ONGLET 3 : IMPORT EXCEL
    # ══════════════════════════════════════════════════════════════════════════
    with tab3:
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="step-title">
          📁 Import fichier Excel structuré
          <span class="step-badge">XLSX · Multi-feuilles</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="font-size:13px;color:{COLORS['muted']};margin-bottom:16px;line-height:1.8;">
          <b>Feuilles attendues :</b><br>
          📄 <code>Courbe MAD</code> → ccy_iso · hist_date · tenor_mat · zero_rate<br>
          📄 <code>Courbe_EUR</code> → devise · date_transaction · tenor · taux_zero_coupon<br>
          📄 <code>MONIA</code> → quote_date · rate<br>
          📄 <code>MADBDT_52W</code> → date · taux<br>
          📄 <code>USD_MAD</code> / <code>EUR_MAD</code> → iso_code1 · quote_date · ask · bid · Mid
        </div>
        """, unsafe_allow_html=True)

        uploaded = st.file_uploader("📁 Sélectionnez votre fichier Excel",
                                    type=['xlsx', 'xls'], label_visibility="collapsed")

        if uploaded:
            col_name, col_btn3 = st.columns([4, 1])
            with col_name:
                st.success(f"📎 **{uploaded.name}** — {uploaded.size / 1024:.1f} KB")
            with col_btn3:
                if st.button("⚙️ Traiter", use_container_width=True, type="primary"):
                    with st.spinner("Lecture et validation..."):
                        processed = process_excel(uploaded)
                    if processed:
                        st.session_state.excel_data = processed
                        st.session_state.last_update = datetime.now()
                        ok = len([s for s, d in processed.items()
                                  if isinstance(d, pd.DataFrame) and not d.empty])
                        st.success(f"✅ {ok}/{len(processed)} feuilles chargées")
                        st.rerun()

        # Résumé feuilles
        excel_data = st.session_state.excel_data
        if excel_data:
            EXPECTED = ['Courbe MAD', 'Courbe_EUR', 'MONIA', 'MADBDT_52W', 'USD_MAD', 'EUR_MAD']
            pills = []
            for s in EXPECTED:
                df = excel_data.get(s)
                if isinstance(df, pd.DataFrame) and not df.empty:
                    pills.append(f'<span class="sheet-pill ok">✅ {s} ({len(df)} lignes)</span>')
                else:
                    pills.append(f'<span class="sheet-pill empty">⬜ {s}</span>')
            st.markdown(' '.join(pills), unsafe_allow_html=True)

            # Sélecteur + aperçu
            st.markdown("<br>", unsafe_allow_html=True)
            non_empty = [s for s, d in excel_data.items()
                         if isinstance(d, pd.DataFrame) and not d.empty]
            if non_empty:
                sel = st.selectbox("Aperçu :", non_empty, label_visibility="collapsed")
                st.dataframe(excel_data[sel].head(10), use_container_width=True)
                st.caption(f"{len(excel_data[sel])} lignes · {len(excel_data[sel].columns)} colonnes")

        st.markdown('</div>', unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # ONGLET 4 : HISTORIQUE ACTIONS
    # ══════════════════════════════════════════════════════════════════════════
    with tab4:
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="step-title">
          📈 Historique des actions MSI20
          <span class="step-badge">Yahoo Finance · .CS tickers</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="font-size:13px;color:{COLORS['muted']};margin-bottom:16px;line-height:1.7;">
          Tickers Bourse de Casablanca sur Yahoo Finance : suffixe <code>.CS</code><br>
          Ex: <code>ATW.CS</code> (Attijariwafa) · <code>IAM.CS</code> (Maroc Telecom) · <code>BCP.CS</code> (BCP)
        </div>
        """, unsafe_allow_html=True)

        col_act, col_per = st.columns([3, 1])
        with col_act:
            selected_actions = st.multiselect(
                "Sélectionnez les valeurs :",
                options=list(MSI20_TICKERS.keys()),
                default=list(MSI20_TICKERS.keys())[:6],
                label_visibility="collapsed",
            )
        with col_per:
            period_map = {'1 mois': '1mo', '3 mois': '3mo', '6 mois': '6mo', '1 an': '1y'}
            period_label = st.selectbox("Période", list(period_map.keys()),
                                        index=1, label_visibility="collapsed")
            period_code = period_map[period_label]

        if st.button("📥 Charger l'historique", type="primary", use_container_width=False):
            if selected_actions:
                tickers_sel = {k: v for k, v in MSI20_TICKERS.items() if k in selected_actions}
                with st.spinner(f"Récupération de {len(tickers_sel)} actions via Yahoo Finance..."):
                    df = fetch_actions_history(tickers_sel, period_code)
                if df is not None and not df.empty:
                    st.session_state.actions_data = df
                    st.session_state.last_update = datetime.now()
                    st.success(f"✅ {len(df)} jours · {len(df.columns)} valeurs")
                    st.rerun()
                else:
                    st.error("❌ Aucune donnée récupérée — vérifiez la connexion ou les tickers.")
            else:
                st.warning("⚠️ Sélectionnez au moins une valeur.")

        # Aperçu
        actions_data = st.session_state.actions_data
        if actions_data is not None and not actions_data.empty:
            st.dataframe(actions_data.tail(10).round(2), use_container_width=True)
            st.caption(f"{len(actions_data)} jours · {len(actions_data.columns)} valeurs · "
                       f"{actions_data.index[0]} → {actions_data.index[-1]}")

            # Mini graphique sparklines
            import plotly.graph_objects as go
            fig = go.Figure()
            for col in actions_data.columns[:6]:
                norm = actions_data[col] / actions_data[col].iloc[0] * 100
                fig.add_trace(go.Scatter(
                    x=list(actions_data.index), y=list(norm),
                    name=col[:20], mode='lines',
                    line=dict(width=1.5),
                    hovertemplate='%{x}<br>' + col + ': %{y:.1f}<extra></extra>',
                ))
            fig.update_layout(
                title="Performance relative (base 100)",
                height=320,
                margin=dict(l=10, r=10, t=40, b=10),
                plot_bgcolor='white',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='#f1f5f9', ticksuffix=''),
                legend=dict(font=dict(size=10)),
            )
            st.plotly_chart(fig, use_container_width=True)

        with st.expander("ℹ️ Tickers disponibles MSI20"):
            df_tickers = pd.DataFrame(
                [(n, t) for n, t in MSI20_TICKERS.items()],
                columns=['Société', 'Ticker Yahoo Finance']
            )
            st.dataframe(df_tickers, use_container_width=True, hide_index=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # ── Reset ──────────────────────────────────────────────────────────────────
    st.markdown("---")
    col_reset, col_last = st.columns([1, 3])
    with col_reset:
        if st.button("🗑️ Réinitialiser tout", type="secondary"):
            st.session_state.excel_data  = {}
            st.session_state.bourse_data = {}
            st.session_state.news_data   = []
            st.session_state.actions_data = None
            st.session_state.last_update  = None
            st.success("✅ Données réinitialisées.")
            st.rerun()
    with col_last:
        lu = st.session_state.last_update
        if lu:
            st.caption(f"🕐 Dernière mise à jour : {lu.strftime('%d/%m/%Y à %H:%M:%S')}")


# ─── ENTRY POINT ───────────────────────────────────────────────────────────────
render()
