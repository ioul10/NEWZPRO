# =============================================================================
# NEWZ - Page Accueil — Version 2.0 (Design unifié)
# pages/home.py
# =============================================================================

import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))

_DEFAULTS = {
    'primary':'#0b1e3d','secondary':'#1a56db','accent':'#06b6d4',
    'success':'#10b981','danger':'#ef4444','warning':'#f59e0b',
    'bg':'#f1f5f9','card':'#ffffff','muted':'#64748b',
    'border':'#e2e8f0','light':'#f8fafc',
}
try:
    from config.settings import COLORS as _IMP, APP_INFO, MSI20_COMPOSITION
    COLORS = {**_DEFAULTS, **_IMP}
except ImportError:
    COLORS = _DEFAULTS
    APP_INFO = {'name':'Newz','version':'2.0.0','author':'OULMADANI Ilyas & ATANANE Oussama',
                'company':'CDG Capital','copyright':'© 2026 CDG Capital',
                'confidentiality':'Usage interne uniquement'}
    MSI20_COMPOSITION = []

try:
    from utils.design import inject_global_css, market_clock_html, page_hero
    inject_global_css()
except Exception:
    def market_clock_html(): return ""
    def page_hero(i, t, s, tags=None): return f"<h2>{i} {t}</h2>"

# ─────────────────────────────────────────────────────────────────────────────

def render():
    C = COLORS

    # ── Hero ──────────────────────────────────────────────────────────────────
    st.markdown(page_hero(
        '🏠', 'Accueil',
        'Bienvenue sur la plateforme de Market Data CDG Capital',
        tags=['BVC', 'BAM', 'HCP', 'Devises', 'Marché Monétaire']
    ), unsafe_allow_html=True)

    # ── Horloge / Statut Marché ───────────────────────────────────────────────
    st.components.v1.html(market_clock_html(), height=65)

    # ── Statut des données ────────────────────────────────────────────────────
    has_excel   = bool(st.session_state.get('excel_data', {}))
    has_bourse  = bool(st.session_state.get('bourse_data', {}).get('status') == 'success')
    has_news    = len(st.session_state.get('news_data', [])) > 0
    has_actions = st.session_state.get('actions_data') is not None
    has_fx      = bool(st.session_state.get('fx_data', {}).get('status') == 'success')
    last_upd    = st.session_state.get('last_update')

    def pill(ok, label):
        cls = 'chip-ok' if ok else 'chip-wait'
        ico = '✅' if ok else '⏳'
        return f'<span class="{cls}">{ico} {label}</span>'

    st.markdown(f"""
    <div style="background:{C['card']};border:1px solid {C['border']};border-radius:14px;
                padding:20px 24px;margin-bottom:24px;">
      <div style="font-family:'Syne',sans-serif;font-size:14px;font-weight:700;
                  color:{C['primary']};margin-bottom:12px;">État des données</div>
      <div style="display:flex;gap:10px;flex-wrap:wrap;">
        {pill(has_excel,'Excel')}
        {pill(has_bourse,'Bourse')}
        {pill(has_news,f"News ({len(st.session_state.get('news_data',[]))})")}
        {pill(has_actions,'Actions')}
        {pill(has_fx,'Devises')}
      </div>
      {f'<div style="font-family:IBM Plex Mono,monospace;font-size:10px;color:{C["muted"]};margin-top:10px;">Dernière MAJ : {last_upd.strftime("%d/%m/%Y à %H:%M")}</div>' if last_upd else ''}
    </div>
    """, unsafe_allow_html=True)

    # ── Modules de la plateforme ──────────────────────────────────────────────
    st.markdown('<p class="sec-title">🚀 Modules disponibles</p>', unsafe_allow_html=True)

    modules = [
        {
            'icon': '📥', 'title': 'Data Ingestion',
            'color': C['secondary'],
            'items': ['Upload fichier Excel (BDT, MONIA, Devises)',
                      'Scraping BVC en temps réel (lematin.ma / yfinance)',
                      'Flux RSS presse économique marocaine',
                      'Historique actions MSI20'],
        },
        {
            'icon': '📈', 'title': 'BDC Statut',
            'color': C['accent'],
            'items': ['Indices MASI · MASI 20 · MASI ESG',
                      'Évolution historique (1j–1an)',
                      'Top Movers hausses & baisses',
                      'Matrice de corrélation MSI20'],
        },
        {
            'icon': '🏦', 'title': 'BAM',
            'color': C['success'],
            'items': ['Taux directeur & décisions BAM',
                      'Courbe des taux BDT (Excel)',
                      'Indice MONIA — marché monétaire',
                      'Devises EUR/MAD · USD/MAD en direct'],
        },
        {
            'icon': '📰', 'title': 'Macronews',
            'color': C['warning'],
            'items': ['Inflation IPC — scraping HCP.ma',
                      'Historique 12 mois (données HCP réelles)',
                      'Actualités macroéconomiques',
                      'Calendrier événements économiques'],
        },
        {
            'icon': '📤', 'title': 'Export',
            'color': '#8b5cf6',
            'items': ['Rapport HTML hebdomadaire complet',
                      'Graphiques Plotly embarqués (interactifs)',
                      'Sections configurables par module',
                      'Aperçu inline + téléchargement direct'],
        },
    ]

    col1, col2 = st.columns(2)
    for i, m in enumerate(modules):
        target = col1 if i % 2 == 0 else col2
        items_html = "".join(f'<li style="margin-bottom:4px;">{it}</li>' for it in m['items'])
        with target:
            st.markdown(f"""
            <div class="step-card" style="border-left:4px solid {m['color']};">
              <div style="font-family:'Syne',sans-serif;font-size:16px;font-weight:700;
                          color:{C['primary']};margin-bottom:10px;">
                {m['icon']} {m['title']}
              </div>
              <ul style="color:{C['muted']};font-size:13px;padding-left:18px;margin:0;line-height:1.8;">
                {items_html}
              </ul>
            </div>
            """, unsafe_allow_html=True)

    # ── Composition MSI20 ─────────────────────────────────────────────────────
    st.markdown('<p class="sec-title">📊 Composition MSI20</p>', unsafe_allow_html=True)

    if MSI20_COMPOSITION:
        df = pd.DataFrame(MSI20_COMPOSITION)

        # Donut secteurs
        import plotly.express as px
        sector_count = df.groupby('secteur').size().reset_index(name='count')
        fig = px.pie(sector_count, values='count', names='secteur', hole=0.55,
                     color_discrete_sequence=[
                         C['primary'], C['secondary'], C['accent'],
                         C['success'], C['warning'], C['danger'],
                         '#8b5cf6', '#f97316', '#14b8a6', '#ec4899',
                     ])
        fig.update_layout(
            height=300, margin=dict(l=0, r=0, t=20, b=0),
            paper_bgcolor='rgba(0,0,0,0)', showlegend=True,
            legend=dict(font=dict(size=11), orientation='v'),
        )
        fig.update_traces(textinfo='percent', textfont_size=11)

        c1, c2 = st.columns([2, 3])
        with c1:
            st.info(f"**{len(df)} valeurs** — Révisé trimestriellement")
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    'nom':     st.column_config.TextColumn('Société',  width='large'),
                    'ticker':  st.column_config.TextColumn('Ticker',   width='small'),
                    'secteur': st.column_config.TextColumn('Secteur',  width='medium'),
                }
            )
    else:
        st.warning("⚠️ Composition MSI20 non disponible")

    # ── Sources & Horaires ────────────────────────────────────────────────────
    st.markdown('<p class="sec-title">🔗 Sources & Horaires</p>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="step-card">
          <div class="step-title">🏛️ Institutions officielles</div>
          <ul style="color:{C['muted']};font-size:13px;padding-left:18px;line-height:2;">
            <li><a href="https://www.casablanca-bourse.com" target="_blank">Bourse de Casablanca</a></li>
            <li><a href="https://www.bkam.ma" target="_blank">Bank Al-Maghrib</a></li>
            <li><a href="https://www.hcp.ma" target="_blank">HCP</a></li>
          </ul>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="step-card">
          <div class="step-title">📰 Presse économique</div>
          <ul style="color:{C['muted']};font-size:13px;padding-left:18px;line-height:2;">
            <li><a href="https://medias24.com" target="_blank">Médias24</a></li>
            <li><a href="https://fr.hespress.com" target="_blank">Hespress Économie</a></li>
            <li><a href="https://lematin.ma" target="_blank">Le Matin</a></li>
          </ul>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="step-card">
          <div class="step-title">🕐 Horaires BVC</div>
          <div style="font-family:'IBM Plex Mono',monospace;font-size:13px;
                      color:{C['primary']};line-height:2.2;">
            <div>⏰ Ouverture : <b>09:00</b></div>
            <div>⏰ Clôture : <b>15:30</b></div>
            <div>📅 Jours : <b>Lun – Ven</b></div>
            <div>🌍 Fuseau : <b>Africa/Casablanca</b></div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ── À propos ──────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="background:{C['primary']};border-radius:14px;padding:20px 28px;
                margin-top:8px;display:flex;justify-content:space-between;
                align-items:center;flex-wrap:wrap;gap:12px;">
      <div>
        <div style="font-family:'Syne',sans-serif;font-size:16px;font-weight:700;color:white;">
          {APP_INFO.get('name','Newz')} v{APP_INFO.get('version','2.0.0')}
        </div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:11px;
                    color:rgba(255,255,255,.5);margin-top:4px;">
          {APP_INFO.get('author','')} · {APP_INFO.get('copyright','')}
        </div>
      </div>
      <div style="font-family:'IBM Plex Mono',monospace;font-size:10px;
                  color:rgba(255,255,255,.35);text-align:right;">
        {APP_INFO.get('confidentiality','Usage interne uniquement')}
      </div>
    </div>
    """, unsafe_allow_html=True)


render()
