# =============================================================================
# NEWZ - Page Export — Version 2.0
# pages/export.py
#
# FIXES v2 :
#   ✅ Graphiques Plotly embarqués correctement (include_plotlyjs='cdn' dans
#      le premier graphique, False dans les suivants)
#   ✅ st.components.v1.html hauteur adaptative (scrolling=True + hauteur 950)
#   ✅ Design unifié via utils/design.py
#   ✅ Horaires dynamiques
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import sys
import json

sys.path.append(str(Path(__file__).resolve().parent.parent))

_DEFAULTS = {
    'primary':'#0b1e3d','secondary':'#1a56db','accent':'#06b6d4',
    'success':'#10b981','danger':'#ef4444','warning':'#f59e0b',
    'bg':'#f1f5f9','card':'#ffffff','muted':'#64748b',
    'border':'#e2e8f0','light':'#f8fafc',
}
try:
    from config.settings import COLORS as _IMP, APP_INFO
    COLORS = {**_DEFAULTS, **_IMP}
except ImportError:
    COLORS = _DEFAULTS
    APP_INFO = {'name':'NEWZ','version':'2.0.0','company':'CDG Capital',
                'author':'OULMADANI Ilyas & ATANANE Oussama',
                'copyright':'© 2026 CDG Capital',
                'confidentiality':'Usage interne uniquement'}

try:
    from utils.design import inject_global_css, page_hero, market_clock_html
    inject_global_css()
except Exception:
    def page_hero(i,t,s,tags=None): return f"<h2>{i} {t}</h2>"
    def market_clock_html(): return ""

# ── Session init ──────────────────────────────────────────────────────────────
def init_session():
    for k, v in [
        ('report_html', None),
        ('report_config', {
            'synthese':True,'bourse':True,'bam':True,
            'devises':True,'monia_bdt':True,'news':True,'inflation':False,
        }),
    ]:
        if k not in st.session_state:
            st.session_state[k] = v

init_session()

# ─────────────────────────────────────────────────────────────────────────────
# CONSTRUCTION DES GRAPHIQUES
# FIX CRITIQUE : utiliser fig.to_html(full_html=False, include_plotlyjs=False)
# + inclure le CDN Plotly UNE SEULE FOIS en haut du document HTML
# ─────────────────────────────────────────────────────────────────────────────

def _fig_to_html_snippet(fig):
    """Convertit Figure → fragment HTML (sans CDN, sans <html>/<body>)"""
    return fig.to_html(full_html=False, include_plotlyjs=False)


def _fetch_index_history_for_report(ticker, label, color_hex, fallback_base):
    """
    Récupère l'historique d'un indice via yfinance pour le rapport.
    Même source que bdc_statut.py → graphiques cohérents.
    """
    import plotly.graph_objects as go
    dates, vals, note = None, None, None

    # 1. Essayer yfinance (même source que BDC Statut)
    try:
        import yfinance as yf
        hist = yf.Ticker(ticker).history(period='1mo')
        if not hist.empty:
            dates = [str(d.date()) for d in hist.index]
            vals  = list(hist['Close'].round(2))
            note  = 'Yahoo Finance'
    except Exception:
        pass

    # 2. Fallback : utiliser la valeur courante de session_state
    if not dates:
        bourse = st.session_state.get('bdc_indices') or st.session_state.get('bourse_data', {})
        if isinstance(bourse, dict):
            key  = 'masi' if 'MASI' in ticker and '20' not in ticker else 'masi20'
            base = bourse.get(key, {}).get('value', fallback_base)
        else:
            base = fallback_base
        # Simuler une courbe autour de la vraie valeur actuelle
        np.random.seed(hash(ticker) % 9999)
        n    = 22  # ~1 mois jours ouvrés
        base = float(base) if base else fallback_base
        vals  = list(np.round(base + np.cumsum(np.random.normal(0, base*0.007, n)), 2))
        dates = [str((datetime.now()-timedelta(days=n-i)).date()) for i in range(n)]
        note  = 'Simulé (yfinance indisponible)'

    min_v, max_v = min(vals), max(vals)
    pad = (max_v - min_v) * 0.15 or max_v * 0.02
    r,g,b = int(color_hex[1:3],16), int(color_hex[3:5],16), int(color_hex[5:7],16)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, y=vals, mode='lines',
        line=dict(color=color_hex, width=2.5),
        fill='tozeroy', fillcolor=f'rgba({r},{g},{b},0.07)',
        hovertemplate='%{x}<br><b>'+label+' : %{y:,.2f}</b><extra></extra>',
    ))
    fig.update_layout(
        title=f'Évolution {label} — 1 mois', height=300,
        margin=dict(l=55, r=20, t=40, b=40),
        plot_bgcolor='white', paper_bgcolor='white',
        xaxis=dict(showgrid=False, tickfont=dict(size=10)),
        yaxis=dict(showgrid=True, gridcolor='#eee', tickformat=',.0f',
                   range=[min_v-pad, max_v+pad], tickfont=dict(size=10), zeroline=False),
        annotations=[dict(text=f'Source : {note}', showarrow=False,
                          x=1, y=0, xref='paper', yref='paper',
                          xanchor='right', yanchor='bottom',
                          font=dict(size=9, color='#94a3b8'))],
    )
    return _fig_to_html_snippet(fig)


def get_chart_masi():
    try:
        return _fetch_index_history_for_report('^MASI', 'MASI', '#0b1e3d', 17243.58)
    except Exception as e:
        return f'<p style="color:#999;padding:20px;">MASI indisponible : {e}</p>'


def get_chart_masi20():
    try:
        return _fetch_index_history_for_report('^MASI20', 'MASI 20', '#1a56db', 1358.42)
    except Exception as e:
        return f'<p style="color:#999;padding:20px;">MASI20 indisponible : {e}</p>'


def get_chart_bdt():
    try:
        from pages.bam import build_bdt_chart
        fig, src = build_bdt_chart(st.session_state.get('excel_data', {}))
        fig.update_layout(title=f'Courbe des Taux BDT — {src}', height=300)
        return _fig_to_html_snippet(fig)
    except Exception as e:
        return f'<p style="color:#999;padding:20px;">BDT indisponible : {e}</p>'


def get_chart_monia():
    try:
        from pages.bam import build_monia_chart
        fig, last, delta, src = build_monia_chart(st.session_state.get('excel_data', {}))
        fig.update_layout(title=f'Indice MONIA — {src}', height=300)
        return _fig_to_html_snippet(fig)
    except Exception as e:
        return f'<p style="color:#999;padding:20px;">MONIA indisponible : {e}</p>'


def get_chart_fx(sym='EUR'):
    try:
        from pages.bam import build_fx_history_chart
        fig, last, pct, src = build_fx_history_chart(
            st.session_state.get('fx_history', {}), sym)
        fig.update_layout(title=f'{sym}/MAD — {src}', height=260)
        return _fig_to_html_snippet(fig), last, pct
    except Exception as e:
        return f'<p style="color:#999;padding:20px;">{sym}/MAD indisponible : {e}</p>', None, None


def get_chart_actions_perf():
    try:
        import plotly.graph_objects as go
        actions = st.session_state.get('actions_data')
        if actions is None or actions.empty:
            return None
        fig = go.Figure()
        cols   = actions.columns[:8]
        colors = ['#0b1e3d','#1a56db','#06b6d4','#10b981',
                  '#f59e0b','#ef4444','#8b5cf6','#64748b']
        for i, col in enumerate(cols):
            s = actions[col].dropna()
            if s.empty: continue
            norm = (s / s.iloc[0]) * 100
            fig.add_trace(go.Scatter(
                x=[str(d) for d in norm.index], y=list(norm.round(2)),
                mode='lines', name=col[:18],
                line=dict(color=colors[i % len(colors)], width=1.5),
            ))
        fig.update_layout(
            title='Performance relative MSI20 (base 100)', height=320,
            margin=dict(l=50, r=20, t=40, b=40),
            plot_bgcolor='white', paper_bgcolor='white',
            legend=dict(font=dict(size=9)),
            xaxis=dict(showgrid=False, tickfont=dict(size=9)),
            yaxis=dict(showgrid=True, gridcolor='#eee', tickfont=dict(size=10)),
        )
        return _fig_to_html_snippet(fig)
    except Exception:
        return None


def get_chart_inflation(infl):
    try:
        import plotly.graph_objects as go
        fig = go.Figure(go.Indicator(
            mode='gauge+number+delta', value=infl,
            title={'text':'Inflation HCP (%)'},
            delta={'reference': 2.5},
            gauge={
                'axis':  {'range': [-2, 6]},
                'bar':   {'color': '#0b1e3d'},
                'steps': [
                    {'range': [-2, 2], 'color': '#fff3e0'},
                    {'range': [2,  3], 'color': '#dcfce7'},
                    {'range': [3,  6], 'color': '#fee2e2'},
                ],
                'threshold': {'line':{'color':'#ef4444','width':3},'value':3},
            }
        ))
        fig.update_layout(height=320, paper_bgcolor='white',
                          margin=dict(t=40, b=20, l=30, r=30))
        return _fig_to_html_snippet(fig)
    except Exception:
        return None


# ─────────────────────────────────────────────────────────────────────────────
# GÉNÉRATION HTML RAPPORT
# ─────────────────────────────────────────────────────────────────────────────

def generate_report_html(config):
    today    = datetime.now().strftime('%d/%m/%Y')
    week_num = datetime.now().isocalendar()[1]
    year     = datetime.now().year
    generated= datetime.now().strftime('%d/%m/%Y à %H:%M:%S')
    company  = APP_INFO.get('company', 'CDG Capital')
    app_name = APP_INFO.get('name', 'NEWZ')
    version  = APP_INFO.get('version', '2.0.0')

    bourse   = st.session_state.get('bourse_data', {})
    excel_d  = st.session_state.get('excel_data', {})
    news_data= st.session_state.get('news_data', [])
    fx_live  = st.session_state.get('fx_data', {})

    masi_v = bourse.get('masi',  {}).get('value')
    masi_c = bourse.get('masi',  {}).get('change')
    m20_v  = bourse.get('masi20',{}).get('value')
    m20_c  = bourse.get('masi20',{}).get('change')
    mesg_v = bourse.get('masi_esg',{}).get('value')
    eur_v  = fx_live.get('EUR', {}).get('rate')
    usd_v  = fx_live.get('USD', {}).get('rate')
    fx_src = fx_live.get('source', '—')

    monia_last = None
    monia_df   = excel_d.get('MONIA', pd.DataFrame())
    if not monia_df.empty:
        rc = next((c for c in monia_df.columns if any(x in c.lower() for x in ['rate','taux'])), None)
        if rc:
            s = monia_df[rc].dropna()
            s = s[s > 0]
            if not s.empty:
                monia_last = float(s.iloc[-1])

    # ── Construire les graphiques AVANT d'assembler le HTML ──────────────────
    # FIX : Le PREMIER snippet inclut le CDN Plotly, les suivants non.
    # On collecte tous les snippets dans un dict, puis on injecte le CDN une fois.

    plotly_cdn = '<script src="https://cdn.plot.ly/plotly-2.27.0.min.js" charset="utf-8"></script>'
    charts = {}

    if config.get('bourse'):
        charts['masi']    = get_chart_masi()
        charts['masi20']  = get_chart_masi20()
        charts['actions'] = get_chart_actions_perf()

    if config.get('monia_bdt'):
        charts['bdt']   = get_chart_bdt()
        charts['monia'] = get_chart_monia()

    if config.get('devises'):
        charts['eur_html'], eur_vc, eur_pct = get_chart_fx('EUR')
        charts['usd_html'], usd_vc, usd_pct = get_chart_fx('USD')
        if eur_v is None: eur_v = eur_vc
        if usd_v is None: usd_v = usd_vc

    if config.get('inflation'):
        infl = st.session_state.get('inflation_rate')
        if infl is not None:
            charts['inflation'] = get_chart_inflation(infl)

    # ── Helpers HTML ──────────────────────────────────────────────────────────
    def kpi(label, value, delta=None, pos=None):
        dh = ''
        if delta:
            c = '#10b981' if pos else '#ef4444'
            a = '▲' if pos else '▼'
            dh = f'<div style="font-size:12px;color:{c};margin-top:4px;">{a} {delta}</div>'
        return f"""
        <div style="background:white;border:1px solid #e2e8f0;border-radius:12px;
                    padding:16px 18px;flex:1;min-width:130px;position:relative;overflow:hidden;">
          <div style="position:absolute;top:0;left:0;right:0;height:3px;
                      background:linear-gradient(90deg,#06b6d4,#1a56db);"></div>
          <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;
                      letter-spacing:1.5px;text-transform:uppercase;color:#64748b;">{label}</div>
          <div style="font-family:'Syne',sans-serif;font-size:22px;font-weight:700;
                      color:#0b1e3d;margin-top:6px;">{value if isinstance(value,str) else str(value)}</div>
          {dh}
        </div>"""

    def sec_hdr(icon, title, subtitle=''):
        sub = f'<div style="font-size:12px;color:#64748b;margin-top:4px;">{subtitle}</div>' if subtitle else ''
        return f"""
        <div style="display:flex;align-items:center;gap:14px;margin-bottom:20px;
                    padding-bottom:12px;border-bottom:2px solid #e2e8f0;">
          <div style="font-size:26px;">{icon}</div>
          <div>
            <div style="font-family:'Syne',sans-serif;font-size:20px;font-weight:700;
                        color:#0b1e3d;">{title}</div>
            {sub}
          </div>
        </div>"""

    def chart_box(html_content, caption=''):
        cap = f'<div style="font-family:IBM Plex Mono,monospace;font-size:9px;color:#94a3b8;margin-top:6px;">{caption.upper()}</div>' if caption else ''
        content = html_content or '<div style="padding:30px;text-align:center;color:#94a3b8;font-size:13px;">Données non disponibles</div>'
        return f"""
        <div style="background:white;border:1px solid #e2e8f0;border-radius:12px;
                    padding:18px;margin-bottom:18px;box-shadow:0 1px 3px rgba(0,0,0,0.04);">
          {content}{cap}
        </div>"""

    def wrap(content):
        return f"""
        <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:16px;
                    padding:26px 30px;margin-bottom:26px;">{content}</div>"""

    def two_col(l, r):
        return f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">{l}{r}</div>'

    # ── Corps du rapport ──────────────────────────────────────────────────────
    body = ''

    if config.get('synthese'):
        kpis = '<div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:8px;">'
        kpis += kpi('MASI',     f"{masi_v:,.2f}" if masi_v else '—',  f"{masi_c:+.2f}%" if masi_c else None, (masi_c or 0)>=0)
        kpis += kpi('MASI 20',  f"{m20_v:,.2f}"  if m20_v  else '—',  f"{m20_c:+.2f}%"  if m20_c  else None, (m20_c or 0)>=0)
        kpis += kpi('MASI ESG', f"{mesg_v:,.2f}" if mesg_v else '—')
        kpis += kpi('Taux Dir. BAM', '2.75%', '−0.25 pts (déc. 2024)', False)
        kpis += kpi('MONIA',    f"{monia_last:.4f}%" if monia_last else '—')
        kpis += kpi('EUR/MAD',  f"{eur_v:.4f}" if eur_v else '—')
        kpis += kpi('USD/MAD',  f"{usd_v:.4f}" if usd_v else '—')
        kpis += '</div>'
        body += wrap(sec_hdr('📊', f'Synthèse — Semaine {week_num}/{year}', today) + kpis)

    if config.get('bourse'):
        c  = sec_hdr('📈', 'Bourse de Casablanca', 'Indices & Performance actions MSI20')
        c += f'<div style="font-family:IBM Plex Mono,monospace;font-size:10px;color:#94a3b8;margin-bottom:16px;">Source : {bourse.get("source","—")}</div>'
        c += two_col(chart_box(charts.get('masi'),'MASI — 30 jours'),
                     chart_box(charts.get('masi20'),'MASI 20 — 30 jours'))
        if charts.get('actions'):
            c += chart_box(charts['actions'],'Performance relative MSI20 — Base 100')
        body += wrap(c)

    if config.get('monia_bdt'):
        c  = sec_hdr('📉','Bank Al-Maghrib — Taux & Marché Monétaire',
                     'Courbe BDT · Indice MONIA · Taux directeur 2.75%')
        c += f"""
        <div style="display:flex;gap:12px;margin-bottom:16px;flex-wrap:wrap;">
          {''.join([
            f'<div style="background:white;border:1px solid #e2e8f0;border-radius:10px;padding:14px 18px;flex:1;min-width:120px;"><div style="font-family:IBM Plex Mono,monospace;font-size:9px;letter-spacing:1.5px;text-transform:uppercase;color:#64748b;">{l}</div><div style="font-family:Syne,sans-serif;font-size:22px;font-weight:700;color:#0b1e3d;">{v}</div></div>'
            for l, v in [('Taux Directeur','2.75%'),('Prêt Marginal','3.25%'),('MONIA', f"{monia_last:.4f}%" if monia_last else '—')]
          ])}
        </div>"""
        c += chart_box(charts.get('bdt'),'Courbe des Taux BDT')
        c += chart_box(charts.get('monia'),'Indice MONIA — Série temporelle')
        body += wrap(c)

    if config.get('devises'):
        c = sec_hdr('💱','Devises', f'EUR/MAD · USD/MAD — Source : {fx_src}')
        eur_ask = fx_live.get('EUR',{}).get('ask'); eur_bid = fx_live.get('EUR',{}).get('bid')
        usd_ask = fx_live.get('USD',{}).get('ask'); usd_bid = fx_live.get('USD',{}).get('bid')
        def fx_card(sym, mid, ask, bid):
            return f"""
            <div style="background:white;border:1px solid #e2e8f0;border-radius:12px;padding:18px 22px;margin-bottom:14px;">
              <div style="font-family:IBM Plex Mono,monospace;font-size:12px;font-weight:600;color:#64748b;">{sym} / MAD</div>
              <div style="font-family:Syne,sans-serif;font-size:28px;font-weight:800;color:#0b1e3d;margin:4px 0;">
                {f"{mid:.4f}" if mid else '—'}</div>
              <div style="font-family:IBM Plex Mono,monospace;font-size:11px;color:#94a3b8;">
                Ask : <b>{f"{ask:.4f}" if ask else '—'}</b> &nbsp;|&nbsp; Bid : <b>{f"{bid:.4f}" if bid else '—'}</b>
              </div>
            </div>"""
        c += two_col(fx_card('EUR',eur_v,eur_ask,eur_bid), fx_card('USD',usd_v,usd_ask,usd_bid))
        c += two_col(chart_box(charts.get('eur_html'),'EUR/MAD — 30 jours'),
                     chart_box(charts.get('usd_html'),'USD/MAD — 30 jours'))
        body += wrap(c)

    if config.get('news') and news_data:
        c = sec_hdr('📰','Veille Économique',f'{min(len(news_data),10)} articles sélectionnés')
        for art in news_data[:10]:
            ts = art.get('timestamp')
            ts_str = ts.strftime('%d/%m/%Y') if isinstance(ts, datetime) else str(ts)[:10]
            summary= (art.get('summary','')[:220])
            c += f"""
            <div style="background:white;border:1px solid #e2e8f0;border-radius:10px;
                        padding:14px 18px;margin-bottom:10px;">
              <div style="font-size:14px;font-weight:600;color:#0b1e3d;line-height:1.4;">
                {art.get('icon','')} <a href="{art.get('url','#')}" style="color:#0b1e3d;text-decoration:none;">{art['title']}</a>
              </div>
              <div style="font-size:11px;color:#64748b;margin-top:5px;">
                <span style="background:#06b6d422;color:#06b6d4;border-radius:5px;padding:2px 8px;font-size:10px;font-weight:700;">{art.get('source','')}</span>
                &nbsp;<span style="background:#f59e0b20;color:#92400e;border-radius:5px;padding:2px 8px;font-size:10px;font-weight:700;">{art.get('category','')}</span>
                &nbsp; 🕐 {ts_str}
              </div>
              {f'<div style="font-size:12px;color:#64748b;margin-top:8px;line-height:1.6;">{summary}{"…" if len(art.get("summary",""))>220 else ""}</div>' if summary else ''}
            </div>"""
        body += wrap(c)

    if config.get('inflation') and charts.get('inflation'):
        c  = sec_hdr('📊','Inflation','Indice des Prix à la Consommation — HCP')
        c += chart_box(charts['inflation'],"Taux d'inflation annuel")
        body += wrap(c)

    # ── HTML final ────────────────────────────────────────────────────────────
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1.0">
  <title>{app_name} — Rapport Semaine {week_num}/{year}</title>
  {plotly_cdn}
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=IBM+Plex+Mono:wght@400;600&family=Mulish:wght@300;400;500;600;700&display=swap');
    *{{box-sizing:border-box;margin:0;padding:0;}}
    body{{font-family:'Mulish',sans-serif;background:#f1f5f9;color:#0b1e3d;padding:32px 20px;}}
    .wrapper{{max-width:1100px;margin:0 auto;}}
    .rpt-header{{
      background:linear-gradient(135deg,#0b1e3d 0%,#162d52 60%,#1a3a6b 100%);
      border-radius:18px;padding:38px 48px;margin-bottom:30px;
      color:white;position:relative;overflow:hidden;
    }}
    .rpt-header::before{{
      content:'NEWZ';position:absolute;right:40px;top:50%;transform:translateY(-50%);
      font-family:'Syne',sans-serif;font-size:80px;font-weight:800;
      opacity:.04;letter-spacing:4px;pointer-events:none;
    }}
    .rpt-tag{{
      display:inline-block;background:rgba(6,182,212,.18);
      border:1px solid rgba(6,182,212,.3);color:#67e8f9;
      border-radius:6px;padding:3px 12px;font-family:'IBM Plex Mono',monospace;
      font-size:10px;font-weight:600;margin:3px 3px 0 0;
    }}
    .rpt-footer{{
      background:linear-gradient(135deg,#0b1e3d,#162d52);
      border-radius:14px;padding:24px 36px;margin-top:30px;
      color:rgba(255,255,255,.55);text-align:center;
      font-family:'IBM Plex Mono',monospace;font-size:11px;line-height:2;
    }}
    @media print{{body{{background:white;padding:0;}}.wrapper{{max-width:100%;}}}}
  </style>
</head>
<body>
<div class="wrapper">

  <div class="rpt-header">
    <div style="position:relative;z-index:1;">
      <div style="font-family:'IBM Plex Mono',monospace;font-size:11px;
                  opacity:.55;letter-spacing:2px;text-transform:uppercase;">
        {company} · Market Data Platform
      </div>
      <div style="font-family:'Syne',sans-serif;font-size:30px;
                  font-weight:800;margin-top:8px;">Rapport Hebdomadaire</div>
      <div style="font-family:'Syne',sans-serif;font-size:18px;
                  opacity:.75;margin-top:4px;">Semaine {week_num} — {year}</div>
      <div style="margin-top:10px;">
        <span class="rpt-tag">BVC</span>
        <span class="rpt-tag">Bank Al-Maghrib</span>
        <span class="rpt-tag">Devises</span>
        <span class="rpt-tag">Marché Monétaire</span>
        <span class="rpt-tag">Généré le {today}</span>
      </div>
    </div>
  </div>

  {body}

  <div class="rpt-footer">
    <b>{company}</b> · {app_name} v{version}<br>
    Rapport généré automatiquement le {generated}<br>
    <span style="opacity:.4;">Ce document est destiné à un usage interne. Les données sont indicatives.</span>
  </div>

</div>
</body>
</html>"""


# ─────────────────────────────────────────────────────────────────────────────
# PAGE PRINCIPALE
# ─────────────────────────────────────────────────────────────────────────────

def render():
    C        = COLORS
    now_str  = datetime.now().strftime("%d %b %Y — %H:%M")
    week_num = datetime.now().isocalendar()[1]

    # ── Hero ──────────────────────────────────────────────────────────────────
    st.markdown(page_hero(
        '📤','Export Rapport Hebdomadaire',
        f'Configuration · Génération · Téléchargement — Semaine {week_num}',
        tags=['HTML','Plotly','Interactif']
    ), unsafe_allow_html=True)

    # ── Statut sources ────────────────────────────────────────────────────────
    bourse   = st.session_state.get('bourse_data', {})
    excel_d  = st.session_state.get('excel_data', {})
    news_data= st.session_state.get('news_data', [])
    actions  = st.session_state.get('actions_data')
    fx_live  = st.session_state.get('fx_data', {})

    bvc_ok     = bourse.get('status') == 'success'
    excel_ok   = len([s for s in excel_d.values() if isinstance(s,pd.DataFrame) and not s.empty])
    news_ok    = len(news_data)
    actions_ok = actions is not None and not actions.empty
    fx_ok      = fx_live.get('status') == 'success'

    def pill(icon, label, cls):
        return f'<span class="status-pill {cls}">{icon} {label}</span>'

    pills = (
        pill('📊',f"Bourse {'✓' if bvc_ok else '✗'}",'ok' if bvc_ok else 'empty') +
        pill('📁',f"Excel {excel_ok}/6",'ok' if excel_ok>=4 else 'warn' if excel_ok else 'empty') +
        pill('📰',f"{news_ok} articles",'ok' if news_ok else 'empty') +
        pill('📈',f"Actions {'✓' if actions_ok else '✗'}",'ok' if actions_ok else 'empty') +
        pill('💱',f"Devises {'✓' if fx_ok else '✗'}",'ok' if fx_ok else 'empty')
    )
    st.markdown(f'<div class="status-row">{pills}</div>', unsafe_allow_html=True)

    if not any([bvc_ok, excel_ok, news_ok, actions_ok]):
        st.warning("⚠️ Aucune donnée chargée — Allez sur **Data Ingestion** pour charger les sources.")

    # ── Onglets ────────────────────────────────────────────────────────────────
    tab_cfg, tab_preview = st.tabs(["⚙️ Configuration & Génération", "👁️ Aperçu & Téléchargement"])

    # ══════════════════════════════════════════════════════════════════════════
    # ONGLET 1 : CONFIGURATION
    # ══════════════════════════════════════════════════════════════════════════
    with tab_cfg:

        # Infos rapport
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="step-title">📋 Informations <span class="step-badge">Semaine {week_num}</span></div>',
                    unsafe_allow_html=True)
        ca, cb, cc = st.columns(3)
        with ca: company_name = st.text_input("Société", value=APP_INFO.get('company','CDG Capital'))
        with cb: report_title = st.text_input("Titre", value=f"Rapport Hebdomadaire — Semaine {week_num}")
        with cc: report_date  = st.date_input("Date", value=datetime.now().date())
        st.markdown('</div>', unsafe_allow_html=True)

        # Sections
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.markdown('<div class="step-title">🗂️ Sections à inclure <span class="step-badge">Modules</span></div>',
                    unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        cfg = {}
        with c1:
            cfg['synthese']  = st.checkbox("📊 Synthèse KPIs",          value=True)
            cfg['bourse']    = st.checkbox("📈 Bourse de Casablanca",    value=bvc_ok or actions_ok)
            cfg['monia_bdt'] = st.checkbox("📉 Courbe BDT & MONIA",     value=bool(excel_ok))
        with c2:
            cfg['devises']   = st.checkbox("💱 Devises EUR/MAD · USD/MAD", value=fx_ok)
            cfg['news']      = st.checkbox("📰 Veille Économique",       value=bool(news_ok))
            cfg['inflation'] = st.checkbox("📊 Inflation HCP",           value=False)

        st.session_state.report_config = cfg
        active = sum(1 for v in cfg.values() if v)
        st.markdown(f'<span class="src-bar">{active} section(s) sélectionnée(s)</span>',
                    unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Génération
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.markdown('<div class="step-title">🚀 Génération <span class="step-badge">HTML · Plotly interactif</span></div>',
                    unsafe_allow_html=True)

        col_gen, col_inf = st.columns([2, 3])
        with col_gen:
            gen_btn = st.button("🚀 Générer le rapport", type="primary", use_container_width=True)
        with col_inf:
            st.markdown(f"""
            <div style="font-size:12px;color:{C['muted']};padding-top:10px;">
              Le rapport HTML contient les graphiques Plotly interactifs embarqués.
              Ouvrable dans tout navigateur ou partageable par email.
            </div>""", unsafe_allow_html=True)

        if gen_btn:
            with st.spinner("Compilation des graphiques et génération du rapport..."):
                try:
                    html = generate_report_html(cfg)
                    st.session_state.report_html = html
                    st.success(f"✅ Rapport généré — {active} sections · {len(html)//1024} KB")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erreur : {e}")
                    st.exception(e)

        st.markdown('</div>', unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # ONGLET 2 : APERÇU & TÉLÉCHARGEMENT
    # ══════════════════════════════════════════════════════════════════════════
    with tab_preview:
        report_html = st.session_state.get('report_html')

        if not report_html:
            st.markdown(f"""
            <div style="text-align:center;padding:60px 20px;color:{C['muted']};">
              <div style="font-size:48px;margin-bottom:16px;">📄</div>
              <div style="font-family:'Syne',sans-serif;font-size:18px;font-weight:700;
                          color:{C['primary']};">Aucun rapport généré</div>
              <div style="font-size:13px;margin-top:8px;">
                Configurez les sections dans l'onglet <b>Configuration</b> puis cliquez sur <b>Générer</b>.
              </div>
            </div>""", unsafe_allow_html=True)
        else:
            # Téléchargement
            st.markdown('<div class="step-card">', unsafe_allow_html=True)
            st.markdown('<div class="step-title">📥 Téléchargement <span class="step-badge-green">Rapport prêt</span></div>',
                        unsafe_allow_html=True)

            wn = datetime.now().isocalendar()[1]
            yr = datetime.now().year
            filename = f"NEWZ_Rapport_S{wn}_{yr}.html"

            cd1, cd2, cd3 = st.columns([3, 1, 1])
            with cd1:
                st.download_button(
                    label="📥 Télécharger le rapport HTML",
                    data=report_html,
                    file_name=filename,
                    mime="text/html",
                    type="primary",
                    use_container_width=True,
                )
            with cd2:
                st.markdown(f"""
                <div style="text-align:center;padding-top:10px;">
                  <div class="kpi-mini-label">TAILLE</div>
                  <div class="kpi-mini-value" style="font-size:18px;">{len(report_html)//1024} KB</div>
                </div>""", unsafe_allow_html=True)
            with cd3:
                active_s = sum(1 for v in st.session_state.get('report_config',{}).values() if v)
                st.markdown(f"""
                <div style="text-align:center;padding-top:10px;">
                  <div class="kpi-mini-label">SECTIONS</div>
                  <div class="kpi-mini-value" style="font-size:18px;">{active_s}</div>
                </div>""", unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

            # ── APERÇU ────────────────────────────────────────────────────────
            st.markdown('<div class="step-card">', unsafe_allow_html=True)
            st.markdown('<div class="step-title">👁️ Aperçu <span class="step-badge">Rendu HTML interactif</span></div>',
                        unsafe_allow_html=True)

            # FIX AFFICHAGE : hauteur suffisante + scrolling=True
            # Le rapport peut faire 4000-8000px selon les sections actives
            # On calcule une hauteur estimée basée sur le nombre de sections
            estimated_height = 600 + active_s * 700
            st.components.v1.html(report_html, height=min(estimated_height, 5000), scrolling=True)

            st.markdown('</div>', unsafe_allow_html=True)

    # ── Reset ──────────────────────────────────────────────────────────────────
    st.markdown("---")
    cr, ci = st.columns([1, 3])
    with cr:
        if st.button("🗑️ Effacer le rapport", type="secondary"):
            st.session_state.report_html = None
            st.rerun()
    with ci:
        if report_html:
            st.caption(f"📄 Rapport en mémoire — {len(report_html)//1024} KB — Généré le {now_str}")


render()
