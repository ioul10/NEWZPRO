# =============================================================================
# NEWZ - Page Export de Rapports — Version Pro
# Fichier : pages/export_rapport.py
#
# Génère un rapport HTML hebdomadaire complet avec :
#   📊 KPIs synthèse (MASI · MASI20 · MONIA · Devises · Inflation)
#   📈 Graphiques interactifs Plotly (depuis session_state)
#   🏦 Section BAM (courbe BDT · MONIA · taux directeur)
#   📰 Veille actualités (top news RSS)
#   📤 Téléchargement HTML prêt à partager
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import sys
import json

sys.path.append(str(Path(__file__).resolve().parent.parent))

# ─── CONFIG ───────────────────────────────────────────────────────────────────

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
    from config.settings import COLORS as _IMP, APP_INFO
    COLORS = {**_DEFAULTS, **_IMP}
except ImportError:
    COLORS = _DEFAULTS
    APP_INFO = {'name': 'NEWZ', 'version': '2.0.0', 'company': 'CDG Capital'}

# ─── SESSION STATE ─────────────────────────────────────────────────────────────

def init_session():
    defaults = {
        'report_html':    None,
        'report_config':  {
            'synthese':    True,
            'bourse':      True,
            'bam':         True,
            'devises':     True,
            'monia_bdt':   True,
            'news':        True,
            'inflation':   False,
        },
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()

# ─── STYLE ────────────────────────────────────────────────────────────────────

st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=IBM+Plex+Mono:wght@400;600&family=Mulish:wght@300;400;500;600;700&display=swap');

  html, body, [class*="css"] {{
      font-family: 'Mulish', sans-serif;
      background: {COLORS['bg']};
  }}

  .page-hero {{
      background: linear-gradient(135deg, {COLORS['primary']} 0%, #162d52 100%);
      border-radius: 18px; padding: 28px 36px; margin-bottom: 28px;
      color: white; position: relative; overflow: hidden;
  }}
  .page-hero::after {{
      content: ''; position: absolute; top: -30px; right: -30px;
      width: 180px; height: 180px; border-radius: 50%;
      background: rgba(6,182,212,.1);
  }}
  .hero-title {{
      font-family: 'Syne', sans-serif; font-size: 25px;
      font-weight: 800; margin: 0;
  }}
  .hero-sub {{
      font-family: 'IBM Plex Mono', monospace; font-size: 12px;
      opacity: .65; margin-top: 6px;
  }}

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

  /* STATUS */
  .status-row {{
      display:flex; gap:10px; flex-wrap:wrap; margin-bottom:18px;
  }}
  .status-pill {{
      display:inline-flex; align-items:center; gap:6px;
      border-radius:20px; padding:5px 14px; font-size:12px; font-weight:600;
  }}
  .status-pill.ok    {{ background:#dcfce7; color:#166534; }}
  .status-pill.warn  {{ background:#fff7ed; color:#9a3412; }}
  .status-pill.empty {{ background:#f1f5f9; color:{COLORS['muted']}; }}

  /* SECTION CHECKBOXES */
  .section-grid {{
      display:grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
      gap:12px; margin-bottom:20px;
  }}
  .section-item {{
      background:{COLORS['light']}; border:1px solid {COLORS['border']};
      border-radius:12px; padding:14px 16px;
      display:flex; align-items:center; gap:10px;
      font-size:13px; font-weight:600; color:{COLORS['primary']};
  }}
  .section-item .icon {{ font-size:18px; }}

  /* KPI ROW */
  .kpi-row {{ display:flex; gap:14px; flex-wrap:wrap; margin-bottom:20px; }}
  .kpi-mini {{
      background:{COLORS['card']}; border:1px solid {COLORS['border']};
      border-radius:12px; padding:14px 18px; flex:1; min-width:110px;
  }}
  .kpi-mini-label {{
      font-family:'IBM Plex Mono',monospace; font-size:9px;
      letter-spacing:1.5px; text-transform:uppercase; color:{COLORS['muted']};
  }}
  .kpi-mini-value {{
      font-family:'Syne',sans-serif; font-size:20px;
      font-weight:700; color:{COLORS['primary']}; margin-top:4px;
  }}

  .src-bar {{
      font-family:'IBM Plex Mono',monospace; font-size:10px;
      background:{COLORS['light']}; border:1px solid {COLORS['border']};
      border-radius:8px; padding:6px 14px; color:{COLORS['muted']};
      margin-top:8px; display:inline-block;
  }}

  div[data-testid="stExpander"] {{
      border:1px solid {COLORS['border']} !important;
      border-radius:12px !important;
  }}
</style>
""", unsafe_allow_html=True)

# ─── COLLECTE DES GRAPHIQUES (depuis session_state + fonctions BAM/BVC) ────────

def _fig_to_html(fig):
    """Convertit un Figure Plotly en HTML embarquable (sans cdn répété)"""
    return fig.to_html(full_html=False, include_plotlyjs=False)


def get_chart_masi():
    try:
        import plotly.graph_objects as go
        bourse  = st.session_state.get('bourse_data', {})
        actions = st.session_state.get('actions_data')

        if actions is not None and not actions.empty:
            df = actions.copy()
            # L'index est déjà date
            col = actions.columns[0]  # première action comme proxy
            base = bourse.get('masi', {}).get('value', float(df[col].iloc[-1]))
            norm = (df[col] / df[col].iloc[0]) * base
            dates = list(df.index)
            vals  = list(norm.round(2))
        else:
            base = bourse.get('masi', {}).get('value', 17243.58)
            np.random.seed(1)
            n = 30
            ret = np.random.normal(0.0002, 0.007, n)
            vals = list(np.round(base * (1 + ret).cumprod() * (base / (base * (1 + ret).cumprod()[-1])), 2))
            dates = [str((datetime.now() - timedelta(days=n - i)).date()) for i in range(n)]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates, y=vals, mode='lines',
            line=dict(color='#0b1e3d', width=2.5),
            fill='tozeroy', fillcolor='rgba(11,30,61,0.07)',
            hovertemplate='%{x}<br><b>%{y:,.2f}</b><extra></extra>',
        ))
        fig.update_layout(
            title='Évolution MASI (30 jours)', height=320,
            margin=dict(l=55, r=20, t=40, b=40),
            plot_bgcolor='white', paper_bgcolor='white',
            xaxis=dict(showgrid=False, tickfont=dict(size=10)),
            yaxis=dict(showgrid=True, gridcolor='#eee', tickformat=',.0f',
                       tickfont=dict(size=10)),
        )
        return _fig_to_html(fig)
    except Exception as e:
        return f'<p style="color:#999;font-size:12px">MASI indisponible : {e}</p>'


def get_chart_masi20():
    try:
        import plotly.graph_objects as go
        bourse  = st.session_state.get('bourse_data', {})
        actions = st.session_state.get('actions_data')

        base = bourse.get('masi20', {}).get('value', 1358.42)
        if actions is not None and not actions.empty and len(actions.columns) >= 2:
            proxy = actions.iloc[:, :5].mean(axis=1)
            norm  = (proxy / proxy.iloc[0]) * base
            dates = [str(d) for d in actions.index]
            vals  = list(norm.round(2))
        else:
            np.random.seed(2)
            n = 30
            ret = np.random.normal(0.0003, 0.008, n)
            vals = list(np.round(base * (1 + ret).cumprod() * (base / (base * (1 + ret).cumprod()[-1])), 2))
            dates = [str((datetime.now() - timedelta(days=n - i)).date()) for i in range(n)]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates, y=vals, mode='lines',
            line=dict(color='#1a56db', width=2.5),
            fill='tozeroy', fillcolor='rgba(26,86,219,0.07)',
            hovertemplate='%{x}<br><b>%{y:,.2f}</b><extra></extra>',
        ))
        fig.update_layout(
            title='Évolution MASI 20 (30 jours)', height=320,
            margin=dict(l=55, r=20, t=40, b=40),
            plot_bgcolor='white', paper_bgcolor='white',
            xaxis=dict(showgrid=False, tickfont=dict(size=10)),
            yaxis=dict(showgrid=True, gridcolor='#eee', tickformat=',.2f',
                       tickfont=dict(size=10)),
        )
        return _fig_to_html(fig)
    except Exception as e:
        return f'<p style="color:#999;font-size:12px">MASI20 indisponible : {e}</p>'


def get_chart_bdt():
    try:
        from pages.bam import build_bdt_chart
        excel_data = st.session_state.get('excel_data', {})
        fig, src = build_bdt_chart(excel_data)
        fig.update_layout(title=f'Courbe des Taux BDT — {src}')
        return _fig_to_html(fig)
    except Exception as e:
        return f'<p style="color:#999;font-size:12px">BDT indisponible : {e}</p>'


def get_chart_monia():
    try:
        from pages.bam import build_monia_chart
        excel_data = st.session_state.get('excel_data', {})
        fig, last, delta, src = build_monia_chart(excel_data)
        fig.update_layout(title=f'Indice MONIA — {src}')
        return _fig_to_html(fig)
    except Exception as e:
        return f'<p style="color:#999;font-size:12px">MONIA indisponible : {e}</p>'


def get_chart_fx(sym='EUR'):
    try:
        from pages.bam import build_fx_history_chart
        fx_hist = st.session_state.get('fx_history', {})
        fig, last, pct, src = build_fx_history_chart(fx_hist, sym)
        fig.update_layout(title=f'{sym}/MAD — {src}', height=280)
        return _fig_to_html(fig), last, pct
    except Exception as e:
        return f'<p style="color:#999;font-size:12px">{sym}/MAD indisponible : {e}</p>', None, None


def get_chart_actions_perf():
    """Sparklines performance relative des actions MSI20"""
    try:
        import plotly.graph_objects as go
        actions = st.session_state.get('actions_data')
        if actions is None or actions.empty:
            return None

        fig = go.Figure()
        cols = actions.columns[:8]
        colors = ['#0b1e3d','#1a56db','#06b6d4','#10b981','#f59e0b','#ef4444','#8b5cf6','#64748b']
        for i, col in enumerate(cols):
            s = actions[col].dropna()
            if s.empty:
                continue
            norm = (s / s.iloc[0]) * 100
            fig.add_trace(go.Scatter(
                x=[str(d) for d in norm.index],
                y=list(norm.round(2)),
                mode='lines', name=col[:18],
                line=dict(color=colors[i % len(colors)], width=1.5),
                hovertemplate=col + '<br>%{x}<br>%{y:.1f}<extra></extra>',
            ))
        fig.update_layout(
            title='Performance relative MSI20 (base 100)',
            height=340, margin=dict(l=50, r=20, t=40, b=40),
            plot_bgcolor='white', paper_bgcolor='white',
            legend=dict(font=dict(size=9)),
            xaxis=dict(showgrid=False, tickfont=dict(size=9)),
            yaxis=dict(showgrid=True, gridcolor='#eee', tickformat='.0f',
                       ticksuffix='', tickfont=dict(size=10)),
        )
        return _fig_to_html(fig)
    except Exception:
        return None


# ─── RAPPORT HTML ─────────────────────────────────────────────────────────────

def generate_report_html(config):
    """
    Génère le rapport HTML complet prêt à télécharger.
    config = dict de sections activées (bool).
    """
    today     = datetime.now().strftime('%d/%m/%Y')
    week_num  = datetime.now().isocalendar()[1]
    year      = datetime.now().year
    generated = datetime.now().strftime('%d/%m/%Y à %H:%M:%S')
    company   = APP_INFO.get('company', 'CDG Capital')
    app_name  = APP_INFO.get('name', 'NEWZ')
    version   = APP_INFO.get('version', '2.0.0')

    # ── Collecte données ──────────────────────────────────────────────────────
    bourse    = st.session_state.get('bourse_data', {})
    excel_d   = st.session_state.get('excel_data', {})
    news_data = st.session_state.get('news_data', [])
    fx_live   = st.session_state.get('fx_data', {})

    masi_v  = bourse.get('masi',  {}).get('value')
    masi_c  = bourse.get('masi',  {}).get('change')
    m20_v   = bourse.get('masi20',{}).get('value')
    m20_c   = bourse.get('masi20',{}).get('change')
    mesg_v  = bourse.get('masi_esg', {}).get('value')

    eur_v   = fx_live.get('EUR', {}).get('rate')
    usd_v   = fx_live.get('USD', {}).get('rate')
    fx_src  = fx_live.get('source', '—')

    # MONIA dernière valeur depuis Excel
    monia_last = None
    monia_src  = '—'
    monia_df   = excel_d.get('MONIA', pd.DataFrame())
    if not monia_df.empty:
        rate_col = next((c for c in monia_df.columns
                         if any(x in c.lower() for x in ['rate', 'taux'])), None)
        if rate_col:
            s = monia_df[rate_col].dropna()
            s = s[s > 0]
            if not s.empty:
                monia_last = float(s.iloc[-1])
                monia_src  = 'Excel importé'

    # ── Graphiques ────────────────────────────────────────────────────────────
    plotly_cdn = '<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>'

    charts = {}
    if config.get('bourse'):
        charts['masi']    = get_chart_masi()
        charts['masi20']  = get_chart_masi20()
        charts['actions'] = get_chart_actions_perf()
    if config.get('monia_bdt'):
        charts['bdt']   = get_chart_bdt()
        charts['monia'] = get_chart_monia()
    if config.get('devises'):
        charts['eur_html'], eur_v_chart, eur_pct = get_chart_fx('EUR')
        charts['usd_html'], usd_v_chart, usd_pct = get_chart_fx('USD')
        if eur_v is None:
            eur_v = eur_v_chart
        if usd_v is None:
            usd_v = usd_v_chart

    # ── Helpers HTML ──────────────────────────────────────────────────────────
    def kpi_card(label, value, delta=None, delta_positive=None):
        delta_html = ''
        if delta is not None:
            clr = '#10b981' if delta_positive else '#ef4444'
            arrow = '▲' if delta_positive else '▼'
            delta_html = f'<div style="font-size:12px;color:{clr};margin-top:4px;">{arrow} {delta}</div>'
        val_str = value if isinstance(value, str) else str(value)
        return f"""
        <div style="background:white;border:1px solid #e2e8f0;border-radius:12px;
                    padding:18px 20px;flex:1;min-width:130px;position:relative;overflow:hidden;">
          <div style="position:absolute;top:0;left:0;right:0;height:3px;
                      background:linear-gradient(90deg,#06b6d4,#1a56db);
                      border-radius:12px 12px 0 0;"></div>
          <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;letter-spacing:1.5px;
                      text-transform:uppercase;color:#64748b;">{label}</div>
          <div style="font-family:'Syne',sans-serif;font-size:22px;font-weight:700;
                      color:#0b1e3d;margin-top:6px;">{val_str}</div>
          {delta_html}
        </div>"""

    def section_header(icon, title, subtitle=''):
        sub_html = f'<div style="font-size:12px;color:#64748b;margin-top:4px;">{subtitle}</div>' if subtitle else ''
        return f"""
        <div style="display:flex;align-items:center;gap:14px;margin-bottom:22px;
                    padding-bottom:14px;border-bottom:2px solid #e2e8f0;">
          <div style="font-size:28px;">{icon}</div>
          <div>
            <div style="font-family:'Syne',sans-serif;font-size:20px;font-weight:700;
                        color:#0b1e3d;">{title}</div>
            {sub_html}
          </div>
        </div>"""

    def chart_box(html_content, caption=''):
        cap_html = f'<div style="font-family:IBM Plex Mono,monospace;font-size:9px;color:#94a3b8;margin-top:6px;letter-spacing:1px;">{caption.upper()}</div>' if caption else ''
        return f"""
        <div style="background:white;border:1px solid #e2e8f0;border-radius:12px;
                    padding:20px;margin-bottom:20px;box-shadow:0 1px 3px rgba(0,0,0,0.04);">
          {html_content or '<div style="padding:30px;text-align:center;color:#94a3b8;font-size:13px;">Données non disponibles</div>'}
          {cap_html}
        </div>"""

    def section_wrap(content):
        return f"""
        <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:16px;
                    padding:28px 32px;margin-bottom:28px;">
          {content}
        </div>"""

    def two_col(left, right):
        return f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">{left}{right}</div>'

    # ══════════════════════════════════════════════════════════════════════════
    # CONSTRUCTION HTML
    # ══════════════════════════════════════════════════════════════════════════
    body = ''

    # ── SYNTHÈSE ─────────────────────────────────────────────────────────────
    if config.get('synthese'):
        kpis_html = '<div style="display:flex;gap:14px;flex-wrap:wrap;margin-bottom:8px;">'

        kpis_html += kpi_card('MASI',
            f"{masi_v:,.2f}" if masi_v else '—',
            f"{masi_c:+.2f}%" if masi_c else None,
            delta_positive=(masi_c or 0) >= 0)

        kpis_html += kpi_card('MASI 20',
            f"{m20_v:,.2f}" if m20_v else '—',
            f"{m20_c:+.2f}%" if m20_c else None,
            delta_positive=(m20_c or 0) >= 0)

        kpis_html += kpi_card('MASI ESG',
            f"{mesg_v:,.2f}" if mesg_v else '—')

        kpis_html += kpi_card('Taux Directeur BAM', '2.75%',
            '−0.25 pts (déc. 2024)', delta_positive=False)

        kpis_html += kpi_card('MONIA',
            f"{monia_last:.4f}%" if monia_last else '—')

        kpis_html += kpi_card('EUR / MAD',
            f"{eur_v:.4f}" if eur_v else '—')

        kpis_html += kpi_card('USD / MAD',
            f"{usd_v:.4f}" if usd_v else '—')

        kpis_html += '</div>'

        body += section_wrap(
            section_header('📊', f'Synthèse — Semaine {week_num}/{year}', today) +
            kpis_html
        )

    # ── BOURSE DE CASABLANCA ──────────────────────────────────────────────────
    if config.get('bourse'):
        content = section_header('📈', 'Bourse de Casablanca', 'Indices & Performance actions MSI20')

        bvc_src = bourse.get('source', '—')
        content += f'<div style="font-family:IBM Plex Mono,monospace;font-size:10px;color:#94a3b8;margin-bottom:16px;">Source : {bvc_src}</div>'

        content += two_col(
            chart_box(charts.get('masi'), 'MASI — 30 jours'),
            chart_box(charts.get('masi20'), 'MASI 20 — 30 jours'),
        )

        if charts.get('actions'):
            content += chart_box(charts['actions'], 'Performance relative MSI20 — Base 100')

        body += section_wrap(content)

    # ── BAM : COURBE BDT & MONIA ──────────────────────────────────────────────
    if config.get('monia_bdt'):
        content = section_header('📉', 'Bank Al-Maghrib — Taux & Marché Monétaire',
                                  'Courbe BDT · Indice MONIA · Taux directeur 2.75%')

        # Mini tableau taux BAM
        content += """
        <div style="display:flex;gap:12px;margin-bottom:18px;flex-wrap:wrap;">
          <div style="background:white;border:1px solid #e2e8f0;border-radius:10px;padding:14px 18px;flex:1;min-width:120px;">
            <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;letter-spacing:1.5px;text-transform:uppercase;color:#64748b;">Taux Directeur</div>
            <div style="font-family:'Syne',sans-serif;font-size:22px;font-weight:700;color:#0b1e3d;">2.75%</div>
          </div>
          <div style="background:white;border:1px solid #e2e8f0;border-radius:10px;padding:14px 18px;flex:1;min-width:120px;">
            <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;letter-spacing:1.5px;text-transform:uppercase;color:#64748b;">Prêt Marginal</div>
            <div style="font-family:'Syne',sans-serif;font-size:22px;font-weight:700;color:#0b1e3d;">3.25%</div>
          </div>
          <div style="background:white;border:1px solid #e2e8f0;border-radius:10px;padding:14px 18px;flex:1;min-width:120px;">
            <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;letter-spacing:1.5px;text-transform:uppercase;color:#64748b;">MONIA</div>
            <div style="font-family:'Syne',sans-serif;font-size:22px;font-weight:700;color:#0b1e3d;">{}</div>
          </div>
        </div>
        """.format(f"{monia_last:.4f}%" if monia_last else '—')

        content += chart_box(charts.get('bdt'), 'Courbe des Taux BDT')
        content += chart_box(charts.get('monia'), 'Indice MONIA — Série temporelle')

        body += section_wrap(content)

    # ── DEVISES ───────────────────────────────────────────────────────────────
    if config.get('devises'):
        content = section_header('💱', 'Devises', f'EUR/MAD · USD/MAD — Source : {fx_src}')

        eur_ask = fx_live.get('EUR', {}).get('ask')
        eur_bid = fx_live.get('EUR', {}).get('bid')
        usd_ask = fx_live.get('USD', {}).get('ask')
        usd_bid = fx_live.get('USD', {}).get('bid')

        def fx_card_html(sym, mid, ask, bid):
            mid_str = f"{mid:.4f}" if mid else '—'
            ask_str = f"{ask:.4f}" if ask else '—'
            bid_str = f"{bid:.4f}" if bid else '—'
            return f"""
            <div style="background:white;border:1px solid #e2e8f0;border-radius:12px;
                        padding:18px 22px;margin-bottom:16px;">
              <div style="font-family:'IBM Plex Mono',monospace;font-size:12px;
                          font-weight:600;color:#64748b;letter-spacing:1px;">{sym} / MAD</div>
              <div style="font-family:'Syne',sans-serif;font-size:30px;font-weight:800;
                          color:#0b1e3d;margin:4px 0;">{mid_str}</div>
              <div style="font-family:'IBM Plex Mono',monospace;font-size:11px;color:#94a3b8;">
                Ask : <b>{ask_str}</b> &nbsp;|&nbsp; Bid : <b>{bid_str}</b>
              </div>
            </div>"""

        content += two_col(
            fx_card_html('EUR', eur_v, eur_ask, eur_bid),
            fx_card_html('USD', usd_v, usd_ask, usd_bid),
        )
        content += two_col(
            chart_box(charts.get('eur_html'), 'EUR/MAD — 30 jours'),
            chart_box(charts.get('usd_html'), 'USD/MAD — 30 jours'),
        )

        body += section_wrap(content)

    # ── ACTUALITÉS ────────────────────────────────────────────────────────────
    if config.get('news') and news_data:
        content = section_header('📰', 'Veille Économique', f'{min(len(news_data), 10)} articles sélectionnés')

        for art in news_data[:10]:
            ts = art.get('timestamp')
            ts_str = ts.strftime('%d/%m/%Y') if isinstance(ts, datetime) else str(ts)[:10]
            summary = art.get('summary', '')[:220]
            ellipsis = '…' if len(art.get('summary', '')) > 220 else ''
            url = art.get('url', '#')
            source = art.get('source', '')
            cat    = art.get('category', '')

            content += f"""
            <div style="background:white;border:1px solid #e2e8f0;border-radius:10px;
                        padding:14px 18px;margin-bottom:10px;">
              <div style="font-size:14px;font-weight:600;color:#0b1e3d;line-height:1.4;">
                {art['icon']} <a href="{url}" style="color:#0b1e3d;text-decoration:none;">{art['title']}</a>
              </div>
              <div style="font-size:11px;color:#64748b;margin-top:5px;">
                <span style="background:#06b6d422;color:#06b6d4;border-radius:5px;
                             padding:2px 8px;font-weight:700;font-size:10px;">{source}</span>
                &nbsp;
                <span style="background:#f59e0b20;color:#92400e;border-radius:5px;
                             padding:2px 8px;font-weight:700;font-size:10px;">{cat}</span>
                &nbsp; 🕐 {ts_str}
              </div>
              {f'<div style="font-size:12px;color:#64748b;margin-top:8px;line-height:1.6;">{summary}{ellipsis}</div>' if summary else ''}
            </div>"""

        body += section_wrap(content)

    # ── INFLATION ──────────────────────────────────────────────────────────────
    if config.get('inflation'):
        infl = st.session_state.get('inflation_rate')
        if infl is not None:
            try:
                import plotly.graph_objects as go
                fig = go.Figure(go.Indicator(
                    mode='gauge+number+delta',
                    value=infl,
                    title={'text': 'Inflation HCP (%)'},
                    delta={'reference': 2.5},
                    gauge={
                        'axis': {'range': [0, 6]},
                        'bar':  {'color': '#0b1e3d'},
                        'steps': [
                            {'range': [0, 2],   'color': '#dbeafe'},
                            {'range': [2, 3],   'color': '#dcfce7'},
                            {'range': [3, 6],   'color': '#fee2e2'},
                        ],
                        'threshold': {'line': {'color': '#ef4444', 'width': 3}, 'value': 3},
                    }
                ))
                fig.update_layout(height=320, paper_bgcolor='white', margin=dict(t=40, b=20))
                infl_html = _fig_to_html(fig)
                content = section_header('📊', 'Inflation', 'Indice des Prix à la Consommation — HCP')
                content += chart_box(infl_html, 'Taux d\'inflation annuel')
                body += section_wrap(content)
            except Exception:
                pass

    # ══════════════════════════════════════════════════════════════════════════
    # ASSEMBLAGE FINAL
    # ══════════════════════════════════════════════════════════════════════════
    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{app_name} — Rapport Semaine {week_num}/{year}</title>
  {plotly_cdn}
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=IBM+Plex+Mono:wght@400;600&family=Mulish:wght@300;400;500;600;700&display=swap');
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Mulish', sans-serif;
      background: #f1f5f9;
      color: #0b1e3d;
      padding: 32px 20px;
    }}
    .wrapper {{
      max-width: 1100px;
      margin: 0 auto;
    }}
    /* HEADER */
    .report-header {{
      background: linear-gradient(135deg, #0b1e3d 0%, #162d52 60%, #1a3a6b 100%);
      border-radius: 18px; padding: 40px 48px; margin-bottom: 32px;
      color: white; position: relative; overflow: hidden;
    }}
    .report-header::before {{
      content: 'NEWZ';
      position: absolute; right: 40px; top: 50%; transform: translateY(-50%);
      font-family: 'Syne', sans-serif; font-size: 80px; font-weight: 800;
      opacity: .04; letter-spacing: 4px; pointer-events: none;
    }}
    .report-header .tag-row {{ margin-top: 14px; display: flex; gap: 8px; flex-wrap: wrap; }}
    .report-tag {{
      display: inline-block;
      background: rgba(6,182,212,.18); border: 1px solid rgba(6,182,212,.3);
      color: #67e8f9; border-radius: 6px; padding: 3px 12px;
      font-family: 'IBM Plex Mono', monospace; font-size: 10px; font-weight: 600;
    }}
    /* FOOTER */
    .report-footer {{
      background: linear-gradient(135deg, #0b1e3d, #162d52);
      border-radius: 14px; padding: 28px 36px; margin-top: 32px;
      color: rgba(255,255,255,0.6); text-align: center;
      font-family: 'IBM Plex Mono', monospace; font-size: 11px; line-height: 2;
    }}
    .report-footer b {{ color: white; }}
    @media print {{
      body {{ background: white; padding: 0; }}
      .wrapper {{ max-width: 100%; }}
    }}
  </style>
</head>
<body>
<div class="wrapper">

  <div class="report-header">
    <div style="position:relative;z-index:1;">
      <div style="font-family:'IBM Plex Mono',monospace;font-size:11px;opacity:.6;letter-spacing:2px;text-transform:uppercase;">
        {company} · Market Data Platform
      </div>
      <div style="font-family:'Syne',sans-serif;font-size:30px;font-weight:800;margin-top:8px;">
        Rapport Hebdomadaire
      </div>
      <div style="font-family:'Syne',sans-serif;font-size:18px;opacity:.8;margin-top:4px;">
        Semaine {week_num} — {year}
      </div>
      <div class="tag-row">
        <span class="report-tag">BVC</span>
        <span class="report-tag">Bank Al-Maghrib</span>
        <span class="report-tag">Devises</span>
        <span class="report-tag">Marché Monétaire</span>
        <span class="report-tag">Généré le {today}</span>
      </div>
    </div>
  </div>

  {body}

  <div class="report-footer">
    <b>{company}</b> · {app_name} v{version}<br>
    Rapport généré automatiquement le {generated}<br>
    <span style="opacity:.5;">Ce document est destiné à un usage interne. Les données sont indicatives.</span>
  </div>

</div>
</body>
</html>"""

    return html


# ─── PAGE PRINCIPALE ───────────────────────────────────────────────────────────

def render():
    now_str = datetime.now().strftime("%d %b %Y — %H:%M")
    week_num = datetime.now().isocalendar()[1]

    # ── Hero ───────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="page-hero">
      <div style="position:relative;z-index:1;">
        <p class="hero-title">📤 Export Rapport Hebdomadaire</p>
        <p class="hero-sub">Configuration · Génération · Téléchargement — Semaine {week_num} · {now_str}</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── État des sources ───────────────────────────────────────────────────────
    bourse    = st.session_state.get('bourse_data', {})
    excel_d   = st.session_state.get('excel_data', {})
    news_data = st.session_state.get('news_data', [])
    actions   = st.session_state.get('actions_data')
    fx_live   = st.session_state.get('fx_data', {})

    bvc_ok     = bourse.get('status') == 'success'
    excel_ok   = len([s for s in excel_d.values()
                      if isinstance(s, pd.DataFrame) and not s.empty])
    news_ok    = len(news_data)
    actions_ok = actions is not None and not actions.empty
    fx_ok      = fx_live.get('status') == 'success'

    def pill(icon, label, cls):
        return f'<span class="status-pill {cls}">{icon} {label}</span>'

    pills = (
        pill('📊', f"Bourse {'chargée' if bvc_ok else 'manquante'}", 'ok' if bvc_ok else 'empty') +
        pill('📁', f"Excel {excel_ok}/6 feuilles", 'ok' if excel_ok >= 4 else 'warn' if excel_ok else 'empty') +
        pill('📰', f"{news_ok} articles", 'ok' if news_ok else 'empty') +
        pill('📈', f"Actions {'chargées' if actions_ok else 'manquantes'}", 'ok' if actions_ok else 'empty') +
        pill('💱', f"Devises {'live' if fx_ok else 'manquantes'}", 'ok' if fx_ok else 'empty')
    )

    st.markdown(f'<div class="status-row">{pills}</div>', unsafe_allow_html=True)

    if not any([bvc_ok, excel_ok, news_ok, actions_ok]):
        st.warning("⚠️ Aucune donnée chargée. Rendez-vous sur **Data Ingestion** pour charger les sources.")

    # ── Onglets ────────────────────────────────────────────────────────────────
    tab1, tab2 = st.tabs(["⚙️ Configuration & Génération", "👁️ Aperçu & Téléchargement"])

    # ══════════════════════════════════════════════════════════════════════════
    # ONGLET 1 : CONFIGURATION
    # ══════════════════════════════════════════════════════════════════════════
    with tab1:

        # — Informations rapport —
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="step-title">
          📋 Informations du rapport
          <span class="step-badge">Semaine {week_num}</span>
        </div>
        """, unsafe_allow_html=True)

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            company_name = st.text_input("Société", value=APP_INFO.get('company', 'CDG Capital'),
                                         label_visibility="visible")
        with col_b:
            report_title = st.text_input("Titre rapport",
                                          value=f"Rapport Hebdomadaire — Semaine {week_num}",
                                          label_visibility="visible")
        with col_c:
            report_date  = st.date_input("Date", value=datetime.now().date())

        st.markdown('</div>', unsafe_allow_html=True)

        # — Sélection des sections —
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="step-title">
          🗂️ Sections à inclure
          <span class="step-badge">Choisissez les modules</span>
        </div>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        sections_config = {}

        with c1:
            sections_config['synthese'] = st.checkbox(
                "📊 Synthèse KPIs", value=True,
                help="MASI · MASI20 · Taux directeur · MONIA · Devises"
            )
            sections_config['bourse'] = st.checkbox(
                "📈 Bourse de Casablanca", value=bvc_ok or actions_ok,
                help="Graphiques MASI · MASI20 · Performance actions MSI20"
            )
            sections_config['monia_bdt'] = st.checkbox(
                "📉 Courbe BDT & MONIA", value=bool(excel_ok),
                help="Courbe des taux BDT · Indice MONIA (depuis Excel)"
            )

        with c2:
            sections_config['devises'] = st.checkbox(
                "💱 Devises (EUR/MAD · USD/MAD)", value=fx_ok,
                help="Taux live + graphiques historiques"
            )
            sections_config['news'] = st.checkbox(
                "📰 Veille Économique", value=bool(news_ok),
                help=f"{news_ok} articles disponibles"
            )
            sections_config['inflation'] = st.checkbox(
                "📊 Inflation (HCP)", value=False,
                help="Nécessite st.session_state.inflation_rate"
            )

        st.session_state.report_config = sections_config
        active = sum(1 for v in sections_config.values() if v)
        st.markdown(f'<span class="src-bar">{active} section(s) sélectionnée(s)</span>',
                    unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # — Options avancées —
        with st.expander("⚙️ Options avancées"):
            st.markdown(f"""
            **Graphiques inclus par section :**

            | Section | Graphiques |
            |---------|-----------|
            | Bourse  | MASI (30j) · MASI20 (30j) · Performance relative MSI20 |
            | BDT & MONIA | Courbe taux (Excel ou référence) · Série MONIA |
            | Devises | Taux live Ask/Bid/Spread · EUR/MAD 30j · USD/MAD 30j |

            **Import des graphiques :** les fonctions `build_bdt_chart`, `build_monia_chart`,
            `build_fx_history_chart` sont importées directement depuis `pages/bam.py`.
            Les graphiques MASI/MSI20 sont reconstruits depuis `session_state.actions_data`.
            """)

        # — Bouton génération —
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="step-title">
          🚀 Génération
          <span class="step-badge">HTML · Plotly interactif</span>
        </div>
        """, unsafe_allow_html=True)

        col_gen, col_info = st.columns([2, 3])
        with col_gen:
            generate_btn = st.button("🚀 Générer le rapport",
                                     type="primary", use_container_width=True)
        with col_info:
            st.markdown(f"""
            <div style="font-size:12px;color:{COLORS['muted']};padding-top:10px;">
              Le rapport HTML contient les graphiques Plotly interactifs embarqués.
              Il peut être ouvert dans n'importe quel navigateur ou partagé par email.
            </div>
            """, unsafe_allow_html=True)

        if generate_btn:
            with st.spinner("Compilation des graphiques et génération du rapport..."):
                try:
                    html = generate_report_html(sections_config)
                    st.session_state.report_html = html
                    st.success(f"✅ Rapport généré — {active} sections · {len(html) // 1024} KB")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erreur lors de la génération : {e}")
                    st.exception(e)

        st.markdown('</div>', unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # ONGLET 2 : APERÇU & TÉLÉCHARGEMENT
    # ══════════════════════════════════════════════════════════════════════════
    with tab2:
        report_html = st.session_state.get('report_html')

        if not report_html:
            st.markdown(f"""
            <div style="text-align:center;padding:60px 20px;color:{COLORS['muted']};">
              <div style="font-size:48px;margin-bottom:16px;">📄</div>
              <div style="font-family:'Syne',sans-serif;font-size:18px;font-weight:700;
                          color:{COLORS['primary']};">Aucun rapport généré</div>
              <div style="font-size:13px;margin-top:8px;">
                Configurez les sections dans l'onglet <b>Configuration</b> puis cliquez sur <b>Générer</b>.
              </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Bouton téléchargement
            st.markdown('<div class="step-card">', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="step-title">
              📥 Téléchargement
              <span class="step-badge-green" style="background:#dcfce7;color:#166534;border-radius:8px;padding:2px 10px;font-family:'IBM Plex Mono',monospace;font-size:11px;font-weight:600;">Rapport prêt</span>
            </div>
            """, unsafe_allow_html=True)

            week_num_dl = datetime.now().isocalendar()[1]
            year_dl     = datetime.now().year
            filename    = f"NEWZ_Rapport_S{week_num_dl}_{year_dl}.html"

            col_dl1, col_dl2, col_dl3 = st.columns([2, 1, 2])
            with col_dl1:
                st.download_button(
                    label="📥 Télécharger le rapport HTML",
                    data=report_html,
                    file_name=filename,
                    mime="text/html",
                    type="primary",
                    use_container_width=True,
                )
            with col_dl2:
                size_kb = len(report_html) // 1024
                st.markdown(f"""
                <div style="text-align:center;padding-top:12px;">
                  <div style="font-family:'IBM Plex Mono',monospace;font-size:10px;
                              color:{COLORS['muted']};">TAILLE</div>
                  <div style="font-family:'Syne',sans-serif;font-size:18px;
                              font-weight:700;color:{COLORS['primary']};">{size_kb} KB</div>
                </div>
                """, unsafe_allow_html=True)
            with col_dl3:
                active_sections = sum(1 for v in st.session_state.get('report_config', {}).values() if v)
                st.markdown(f"""
                <div style="text-align:center;padding-top:12px;">
                  <div style="font-family:'IBM Plex Mono',monospace;font-size:10px;
                              color:{COLORS['muted']};">SECTIONS</div>
                  <div style="font-family:'Syne',sans-serif;font-size:18px;
                              font-weight:700;color:{COLORS['primary']};">{active_sections}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

            # Aperçu iframe
            st.markdown('<div class="step-card">', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="step-title">
              👁️ Aperçu du rapport
              <span class="step-badge">Rendu HTML interactif</span>
            </div>
            """, unsafe_allow_html=True)
            st.components.v1.html(report_html, height=900, scrolling=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # ── Regénérer / Reset ──────────────────────────────────────────────────────
    st.markdown("---")
    col_r, col_info2 = st.columns([1, 3])
    with col_r:
        if st.button("🗑️ Effacer le rapport", type="secondary"):
            st.session_state.report_html = None
            st.success("Rapport effacé.")
            st.rerun()
    with col_info2:
        if st.session_state.get('report_html'):
            st.caption(f"📄 Rapport en mémoire — {len(st.session_state.report_html) // 1024} KB")


# ─── ENTRY POINT ───────────────────────────────────────────────────────────────
render()
