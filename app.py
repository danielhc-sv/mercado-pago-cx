"""
CX Command — Quality Management
App principal Streamlit com salvamento automático no Google Sheets.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date
import anthropic
import mammoth
import io

import sheets as db

# ─────────────────────────────────────────
# CONFIGURAÇÃO DA PÁGINA
# ─────────────────────────────────────────
st.set_page_config(
    page_title="CX Command — Quality Management",
    page_icon="⊞",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────
# CSS GLOBAL
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap');

:root {
  --bg: #0e0e0e; --surface: #131313; --surface-low: #1c1b1b;
  --on-surface: #e5e2e1; --on-surface-dim: #a09d9c;
  --primary: #FFD700; --primary-text: #1a1200;
  --secondary: #dcb8ff; --tertiary: #00e479;
  --error: #FF3B3B; --error-dim: #ff6b6b;
  --glass-border: rgba(255,255,255,0.08);
}

html, body, [class*="css"] {
  font-family: 'Inter', sans-serif !important;
  background-color: #0e0e0e !important;
  color: #e5e2e1 !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background: #131313 !important;
  border-right: 1px solid rgba(255,255,255,0.08) !important;
}
[data-testid="stSidebar"] * { color: #a09d9c !important; }
[data-testid="stSidebarNav"] { display: none; }

/* Garante que o botão nativo de colapso/reabrir a sidebar permaneça visível */
button[data-testid="collapsedControl"],
button[kind="header"],
[data-testid="collapsedControl"] {
  display: flex !important;
  visibility: visible !important;
  opacity: 1 !important;
  pointer-events: auto !important;
}

/* Todos os botões da sidebar: estilo de nav-link neutro */
[data-testid="stSidebar"] .stButton > button {
  background: transparent !important;
  color: #a09d9c !important;
  border: none !important;
  border-left: 3px solid transparent !important;
  border-radius: 0 4px 4px 0 !important;
  text-align: left !important;
  font-family: 'Inter', sans-serif !important;
  font-weight: 500 !important;
  font-size: 14px !important;
  padding: 10px 14px !important;
  box-shadow: none !important;
  transition: color 0.15s, background 0.15s, border-color 0.15s !important;
  width: 100% !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
  background: rgba(255,255,255,0.05) !important;
  color: #e5e2e1 !important;
  border-left-color: rgba(255,255,255,0.15) !important;
  box-shadow: none !important;
}

/* Botão de logout: mais discreto */
[data-testid="stSidebar"] .stButton > button[key="btn_logout"],
[data-testid="stSidebar"] div:last-child .stButton > button {
  color: #555 !important;
  font-size: 13px !important;
}

/* ── Área principal ── */
[data-testid="stAppViewContainer"] > .main { background: #0e0e0e !important; }
[data-testid="block-container"] { padding: 1.5rem 2rem !important; }

/* ── Cards ── */
.cx-card {
  background: #131313;
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 16px;
}
.cx-card-yellow { border-color: rgba(255,215,0,0.4); }
.cx-card-purple { border-color: rgba(220,184,255,0.3); }
.cx-card-green  { border-color: rgba(0,228,121,0.35); }
.cx-card-red    { border-color: rgba(255,59,59,0.3); }

/* ── KPI ── */
.kpi-value  { font-family: 'Space Grotesk', sans-serif; font-size: 2.4rem; font-weight: 700; line-height: 1; margin: 4px 0 8px; }
.kpi-yellow { color: #FFD700; }
.kpi-purple { color: #dcb8ff; }
.kpi-green  { color: #00e479; }
.kpi-white  { color: #e5e2e1; }
.kpi-label  { font-size: 10px; letter-spacing: 0.12em; text-transform: uppercase; color: #a09d9c; font-weight: 600; }
.kpi-delta-pos { color: #00e479; font-size: 12px; font-weight: 600; }
.kpi-delta-neg { color: #ff6b6b; font-size: 12px; font-weight: 600; }

/* ── Títulos de página ── */
.page-title { font-family: 'Space Grotesk', sans-serif; font-size: 1.8rem; font-weight: 700; color: #e5e2e1; margin-bottom: 4px; }
.page-sub   { font-size: 14px; color: #a09d9c; margin-bottom: 20px; }

/* ── Badge ── */
.badge { display: inline-block; font-size: 10px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; padding: 3px 10px; border-radius: 9999px; }
.badge-yellow { background: rgba(255,215,0,0.15); color: #FFD700; border: 1px solid rgba(255,215,0,0.3); }
.badge-green  { background: rgba(0,228,121,0.12); color: #00e479; border: 1px solid rgba(0,228,121,0.3); }
.badge-red    { background: rgba(255,59,59,0.12); color: #ff6b6b; border: 1px solid rgba(255,59,59,0.3); }
.badge-purple { background: rgba(220,184,255,0.12); color: #dcb8ff; border: 1px solid rgba(220,184,255,0.3); }
.badge-gray   { background: rgba(255,255,255,0.08); color: #a09d9c; }

/* ── CORREÇÃO 1: Botões globais APENAS na área principal (não afeta sidebar) ── */
[data-testid="stAppViewContainer"] .stButton > button {
  background: #FFD700 !important; color: #1a1200 !important;
  font-family: 'Space Grotesk', sans-serif !important;
  font-weight: 700 !important; border: none !important;
  border-radius: 4px !important;
  transition: box-shadow 0.2s !important;
}
[data-testid="stAppViewContainer"] .stButton > button:hover {
  box-shadow: 0 0 20px rgba(255,215,0,0.35) !important;
}

/* Botão secundário */
.btn-secondary > button {
  background: transparent !important; color: #a09d9c !important;
  border: 1px solid rgba(255,255,255,0.08) !important;
}
.btn-secondary > button:hover { border-color: #a09d9c !important; color: #e5e2e1 !important; }

/* ── Inputs ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div,
.stDateInput > div > div > input,
.stNumberInput > div > div > input {
  background: #1c1b1b !important;
  border: 1px solid #4d4732 !important;
  color: #e5e2e1 !important;
  border-radius: 4px !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
  border-color: #FFD700 !important;
  box-shadow: 0 0 0 2px rgba(255,215,0,0.15) !important;
}

/* Checkbox (lembrar acesso) */
.stCheckbox > label { color: #a09d9c !important; font-size: 13px !important; }
.stCheckbox > label > span { color: #a09d9c !important; }

/* Selectbox */
.stSelectbox > div > div { background: #1c1b1b !important; color: #e5e2e1 !important; }
.stSelectbox > div > div > div { color: #e5e2e1 !important; }

/* Slider */
.stSlider > div > div > div { background: #FFD700 !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] { background: #131313 !important; gap: 4px; }
.stTabs [data-baseweb="tab"] {
  background: #131313 !important; color: #a09d9c !important;
  border: 1px solid rgba(255,255,255,0.08) !important;
  border-radius: 4px !important; font-size: 13px !important;
}
.stTabs [aria-selected="true"] {
  background: #FFD700 !important; color: #1a1200 !important;
  border-color: #FFD700 !important; font-weight: 700 !important;
}
.stTabs [data-baseweb="tab-panel"] { background: transparent !important; padding-top: 20px !important; }

/* ── Métricas ── */
[data-testid="stMetric"] { background: #131313; border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 16px !important; }
[data-testid="stMetricLabel"] { color: #a09d9c !important; font-size: 10px !important; letter-spacing: 0.1em !important; text-transform: uppercase !important; }
[data-testid="stMetricValue"] { color: #FFD700 !important; font-family: 'Space Grotesk', sans-serif !important; }
[data-testid="stMetricDelta"] svg { display: none; }

/* ── Dataframe ── */
[data-testid="stDataFrame"] { border: 1px solid rgba(255,255,255,0.08) !important; border-radius: 8px !important; }

/* ── Divider ── */
hr { border-color: rgba(255,255,255,0.08) !important; }

/* ── Chat IA ── */
.ia-msg-user {
  background: rgba(255,215,0,0.07); border: 1px solid rgba(255,215,0,0.15);
  border-radius: 8px; padding: 12px 14px; margin: 8px 0; margin-left: 40px;
  font-size: 13px; line-height: 1.6;
}
.ia-msg-assistant {
  background: rgba(220,184,255,0.06); border: 1px solid rgba(220,184,255,0.15);
  border-radius: 8px; padding: 12px 14px; margin: 8px 0; margin-right: 40px;
  font-size: 13px; line-height: 1.6;
}
.ia-role { font-size: 10px; letter-spacing: 0.1em; text-transform: uppercase; font-weight: 700; margin-bottom: 5px; }
.ia-role-user { color: #FFD700; }
.ia-role-bot  { color: #dcb8ff; }

/* ── Score display ── */
.score-display {
  text-align: center; padding: 20px;
  background: #131313; border: 1px solid rgba(255,215,0,0.3);
  border-radius: 8px;
}
.score-big { font-family: 'Space Grotesk', sans-serif; font-size: 3rem; font-weight: 700; color: #FFD700; }

/* ── Info/success/error boxes ── */
.cx-success { background: rgba(0,228,121,0.08); border: 1px solid rgba(0,228,121,0.25); border-radius: 4px; padding: 12px 14px; color: #00e479; }
.cx-error   { background: rgba(255,59,59,0.08); border: 1px solid rgba(255,59,59,0.25); border-radius: 4px; padding: 12px 14px; color: #ff6b6b; }
.cx-info    { background: rgba(255,215,0,0.08); border: 1px solid rgba(255,215,0,0.2); border-radius: 4px; padding: 12px 14px; color: #FFD700; }

/* ── Ocultar elementos padrão do Streamlit ── */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────
def init_session():
    defaults = {
        "logged_in": False,
        "user": None,
        "page": "dashboard",
        "ia_messages": [],
        "score_avaliacao": 8.0,
        "remembered_user": "",
        "remembered_pass": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()


# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────
def perfil_label(p):
    return {"admin":"Administrador","gestor":"Gestor CX","auditor":"Auditor","operador":"Operador"}.get(p, p)

def badge_html(text, color="yellow"):
    return f'<span class="badge badge-{color}">{text}</span>'

def card(content_fn, color=""):
    cls = f"cx-card cx-card-{color}" if color else "cx-card"
    st.markdown(f'<div class="{cls}">', unsafe_allow_html=True)
    content_fn()
    st.markdown('</div>', unsafe_allow_html=True)

def section_title(text):
    st.markdown(f'<div class="page-title">{text}</div>', unsafe_allow_html=True)

def section_sub(text):
    st.markdown(f'<div class="page-sub">{text}</div>', unsafe_allow_html=True)

def score_color(n):
    try:
        v = float(n)
        if v >= 80: return "green"
        if v >= 60: return "yellow"
        return "red"
    except: return "gray"

def kpi_card(label, value, delta=None, color="yellow"):
    delta_html = ""
    if delta:
        cls = "kpi-delta-pos" if delta.startswith("▲") or delta.startswith("+") else "kpi-delta-neg"
        delta_html = f'<div class="{cls}">{delta}</div>'
    st.markdown(f"""
    <div class="cx-card cx-card-{color}">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value kpi-{color}">{value}</div>
      {delta_html}
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# PLOTLY THEME
# ─────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#a09d9c", family="Inter"),
    margin=dict(l=0, r=0, t=40, b=0),
    xaxis=dict(gridcolor="rgba(0,0,0,0)", color="#555", tickfont=dict(size=11, color="#666")),
    yaxis=dict(gridcolor="rgba(255,255,255,0.05)", color="#555", tickfont=dict(size=11, color="#555"), zeroline=False),
)

def line_chart(labels, datasets):
    """datasets = list of {name, data, color, fill}"""
    fig = go.Figure()
    for d in datasets:
        fill_color = d.get("fill", "rgba(255,255,255,0.04)")
        fig.add_trace(go.Scatter(
            x=labels,
            y=d["data"],
            name=d["name"],
            line=dict(color=d["color"], width=3, shape="spline", smoothing=1.3),
            mode="lines",
            fill="tozeroy",
            fillcolor=fill_color,
        ))
    layout = dict(**PLOTLY_LAYOUT)
    layout["showlegend"] = True
    layout["legend"] = dict(
        bgcolor="rgba(0,0,0,0)",
        font=dict(color="#a09d9c", size=11),
        orientation="h",
        yanchor="bottom", y=1.02,
        xanchor="right", x=1,
    )
    fig.update_layout(**layout)
    return fig

def bar_chart(labels, values, colors=None):
    if not colors:
        colors = ["rgba(255,255,255,0.1)"] * len(values)
    fig = go.Figure(go.Bar(x=labels, y=values, marker_color=colors, marker_line_width=0))
    layout = dict(**PLOTLY_LAYOUT)
    layout["showlegend"] = False
    fig.update_layout(**layout)
    fig.update_traces(marker_cornerradius=3)
    return fig

def donut_chart(values, colors, labels):
    fig = go.Figure(go.Pie(
        values=values, labels=labels, marker_colors=colors,
        hole=0.72, textinfo="none",
    ))
    layout = dict(**PLOTLY_LAYOUT)
    layout["showlegend"] = False
    fig.update_layout(**layout)
    return fig


# ─────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────
def page_login():
    col_left, col_right = st.columns([1, 1])
    with col_left:
        st.markdown("""
        <div style="padding: 20px 0">
          <div style="font-family:'Space Grotesk',sans-serif;font-size:24px;font-weight:700;color:#FFD700;margin-bottom:4px">CX Command</div>
          <div style="font-size:11px;letter-spacing:0.12em;text-transform:uppercase;color:#a09d9c;margin-bottom:48px">Quality Management</div>
          <h1 style="font-family:'Space Grotesk',sans-serif;font-size:2.2rem;font-weight:700;color:#e5e2e1;line-height:1.15;margin-bottom:12px">Bem-vindo ao<br>centro de controle.</h1>
          <p style="color:#a09d9c;font-size:15px;margin-bottom:32px">Insira suas credenciais para gerenciar a qualidade operacional.</p>
        </div>
        """, unsafe_allow_html=True)

        default_user = st.session_state.get("remembered_user", "")
        default_pass = st.session_state.get("remembered_pass", "")

        usuario = st.text_input("Usuário", value=default_user, placeholder="ex: admin", key="login_user")
        senha   = st.text_input("Senha",   value=default_pass, placeholder="••••••••", type="password", key="login_pass")
        lembrar = st.checkbox("Lembrar meu acesso", value=bool(default_user), key="login_lembrar")

        if st.button("ENTRAR", use_container_width=True):
            try:
                df = db.load_usuarios()
                if df.empty:
                    db.seed_admin()
                    df = db.load_usuarios()
                match = df[
                    (df["usuario"].str.lower() == usuario.strip().lower()) &
                    (df["senha"] == senha) &
                    (df["ativo"].astype(str).str.lower() != "false")
                ]
                if not match.empty:
                    user = match.iloc[0].to_dict()
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    if lembrar:
                        st.session_state["remembered_user"] = usuario.strip().lower()
                        st.session_state["remembered_pass"] = senha
                    else:
                        st.session_state["remembered_user"] = ""
                        st.session_state["remembered_pass"] = ""
                    st.rerun()
                else:
                    st.markdown('<div class="cx-error">✕ Usuário ou senha incorretos.</div>', unsafe_allow_html=True)
            except Exception as e:
                st.markdown(f'<div class="cx-error">Erro ao conectar ao banco de dados: {e}</div>', unsafe_allow_html=True)

        st.markdown('<div style="font-size:12px;color:#444;margin-top:24px">Acesso restrito para auditores e gestores CX.<br>Versão 4.2.0 · Usuário padrão: <strong style="color:#666">admin</strong> / senha: <strong style="color:#666">admin123</strong></div>', unsafe_allow_html=True)

    with col_right:
        st.markdown("""
        <div class="cx-card" style="margin-top:20px">
          <div style="display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:16px">
            <div>
              <div style="font-family:'Space Grotesk',sans-serif;font-size:20px;font-weight:600">Operational Health</div>
              <div style="font-size:13px;color:#a09d9c;margin-top:3px">Real-time performance diagnostics</div>
            </div>
            <span style="display:inline-flex;align-items:center;gap:6px;background:rgba(0,228,121,0.1);color:#00e479;font-size:11px;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;padding:4px 10px;border-radius:9999px;border:1px solid rgba(0,228,121,0.3)">● Sistema Nominal</span>
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
            <div style="background:#201f1f;border:1px solid rgba(255,255,255,0.08);border-radius:8px;padding:16px">
              <div style="font-size:11px;text-transform:uppercase;letter-spacing:0.08em;color:#a09d9c;margin-bottom:6px">Média Global</div>
              <div style="font-family:'Space Grotesk',sans-serif;font-size:28px;font-weight:700;color:#FFD700">94.2 <span style="font-size:12px;color:#00e479">+1.4%</span></div>
            </div>
            <div style="background:#201f1f;border:1px solid rgba(255,255,255,0.08);border-radius:8px;padding:16px">
              <div style="font-size:11px;text-transform:uppercase;letter-spacing:0.08em;color:#a09d9c;margin-bottom:6px">Operadores Ativos</div>
              <div style="font-family:'Space Grotesk',sans-serif;font-size:28px;font-weight:700;color:#e5e2e1">1,248</div>
            </div>
          </div>
        </div>
        <div style="font-family:'Space Grotesk',sans-serif;font-size:16px;font-style:italic;color:#a09d9c;text-align:center;margin-top:20px">
          Transforme cada feedback em uma oportunidade de ouro.
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────
def render_sidebar():
    user = st.session_state.user or {}
    nome = user.get("nome","—")
    initials = "".join(w[0] for w in nome.split()[:2]).upper()

    with st.sidebar:
        st.markdown(f"""
        <div style="padding:0 0 20px;border-bottom:1px solid rgba(255,255,255,0.08);margin-bottom:20px">
          <div style="font-family:'Space Grotesk',sans-serif;font-size:18px;font-weight:700;color:#FFD700">CX Command</div>
          <div style="font-size:9px;letter-spacing:0.12em;text-transform:uppercase;color:#a09d9c">Quality Management</div>
        </div>
        """, unsafe_allow_html=True)

        pages = [
            ("⊞", "Dashboard",         "dashboard"),
            ("👥", "Operadores",         "operadores"),
            ("☑", "Avaliações",         "avaliacoes"),
            ("⏱", "Banco de Erros",     "bancoerros"),
            ("✉", "Entregar Feedback",  "feedback_op"),
            ("✦", "IA de Qualidade",    "ia"),
            ("📋", "Base QA",            "base_qa"),
        ]
        if user.get("perfil") == "admin":
            pages.append(("⚙", "Configurações", "config"))

        current = st.session_state.page

        # CORREÇÃO 2: destaque da página ativa via wrapper <div> inline,
        # sem injetar <style> por loop (evita conflitos de especificidade a cada rerun)
        for icon, label, pid in pages:
            is_active = (current == pid)
            if is_active:
                st.markdown(
                    '<div style="border-left:3px solid #FFD700;background:rgba(255,215,0,0.06);'
                    'border-radius:0 4px 4px 0;margin-bottom:2px">',
                    unsafe_allow_html=True
                )
            if st.button(f"{icon}  {label}", key=f"nav_{pid}", use_container_width=True):
                st.session_state.page = pid
                st.rerun()
            if is_active:
                st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<div style='margin-top:auto;padding-top:16px;border-top:1px solid rgba(255,255,255,0.08)'></div>", unsafe_allow_html=True)

        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:10px;padding:8px 4px">
          <div style="width:36px;height:36px;border-radius:50%;background:#2a2a2a;border:1px solid rgba(255,255,255,0.08);display:flex;align-items:center;justify-content:center;font-family:'Space Grotesk',sans-serif;font-size:13px;font-weight:700;color:#FFD700;flex-shrink:0">{initials}</div>
          <div><div style="font-size:13px;font-weight:600;color:#e5e2e1">{nome.split()[0]}</div><div style="font-size:11px;color:#a09d9c">{perfil_label(user.get("perfil",""))}</div></div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("⇥  Sair", use_container_width=True, key="btn_logout"):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.page = "dashboard"
            st.rerun()


# ─────────────────────────────────────────
# PÁGINA: DASHBOARD
# ─────────────────────────────────────────
def page_dashboard():
    section_title("Dashboard")
    section_sub("Visão geral da qualidade operacional em tempo real.")

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi_card("Nota Média Geral", "95.0", "▲ 4.2%", "yellow")
    with c2: kpi_card("Nota Mercado Pago", "92.1", "▲ 1.8%", "purple")
    with c3: kpi_card("Nota Avaliador", "96.5", "▼ 0.5%", "green")
    with c4: kpi_card("Operadores Ativos", "142", "Steady", "white")

    st.markdown("---")

    col_chart, col_trends = st.columns([2, 1])
    with col_chart:
        st.markdown('<div class="cx-card">', unsafe_allow_html=True)
        st.markdown('<div style="font-family:\'Space Grotesk\',sans-serif;font-size:16px;font-weight:600;margin-bottom:14px">Evolução Mensal Quality</div>', unsafe_allow_html=True)
        meses = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
        fig = line_chart(meses, [
            {"name": "Média Geral",       "data": [70,72,68,75,80,78,82,85,88,90,93,95],      "color": "#FFD700",  "fill": "rgba(255,215,0,0.08)"},
            {"name": "Mercado Pago",      "data": [65,68,65,70,72,70,74,78,80,83,88,92],      "color": "#dcb8ff",  "fill": "rgba(220,184,255,0.06)"},
            {"name": "Avaliação Interna", "data": [72,75,72,78,82,80,84,88,90,92,95,96.5],    "color": "#00e479",  "fill": "rgba(0,228,121,0.05)"},
        ])
        fig.update_layout(height=260, yaxis_range=[55, 100], margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with col_trends:
        st.markdown('<div class="cx-card"><div style="font-family:\'Space Grotesk\',sans-serif;font-size:15px;font-weight:600;margin-bottom:14px">🧭 Mapa de Tendências</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="background:#1c1b1b;border:1px solid rgba(255,255,255,0.08);border-left:3px solid #FFD700;border-radius:0 8px 8px 0;padding:14px;margin-bottom:10px">
          <div style="font-size:10px;text-transform:uppercase;letter-spacing:0.1em;color:#FFD700;font-weight:700;margin-bottom:6px">⚠ Informação Crítica</div>
          <div style="font-size:12px;color:#a09d9c;line-height:1.5">Erros de informação incorreta aumentaram 18% neste ciclo.</div>
        </div>
        <div style="background:#1c1b1b;border:1px solid rgba(255,255,255,0.08);border-left:3px solid #00e479;border-radius:0 8px 8px 0;padding:14px">
          <div style="font-size:10px;text-transform:uppercase;letter-spacing:0.1em;color:#00e479;font-weight:700;margin-bottom:6px">▲ Tendência Positiva</div>
          <div style="font-size:12px;color:#a09d9c;line-height:1.5">Resolução na 1ª chamada subiu 6% nos últimos 15 dias.</div>
        </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    col_ops, col_status = st.columns([2, 1])
    with col_ops:
        st.markdown('<div class="cx-card"><div style="font-family:\'Space Grotesk\',sans-serif;font-size:15px;font-weight:600;margin-bottom:14px">Operadores em Destaque</div>', unsafe_allow_html=True)
        try:
            df_ops = db.load_operadores()
            if not df_ops.empty:
                df_show = df_ops[df_ops["ativo"].astype(str).str.lower() != "false"].head(5)
                for _, row in df_show.iterrows():
                    nota = float(row.get("nota_geral", 0) or 0)
                    cor = "#00e479" if nota >= 90 else "#FFD700" if nota >= 70 else "#ff6b6b"
                    st.markdown(f"""
                    <div style="display:flex;align-items:center;justify-content:space-between;padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.04)">
                      <div style="display:flex;align-items:center;gap:10px">
                        <div style="width:32px;height:32px;border-radius:50%;background:#2a2a2a;display:flex;align-items:center;justify-content:center;font-family:'Space Grotesk',sans-serif;font-size:11px;font-weight:700;color:#FFD700">{"".join(w[0] for w in str(row.get("nome","?")).split()[:2]).upper()}</div>
                        <div><div style="font-size:14px;font-weight:500">{row.get("nome","—")}</div><div style="font-size:11px;color:#a09d9c">{row.get("matricula","—")}</div></div>
                      </div>
                      <div style="font-family:'Space Grotesk',sans-serif;font-size:16px;font-weight:700;color:{cor}">{nota:.1f}</div>
                    </div>""", unsafe_allow_html=True)
            else:
                st.markdown('<div style="text-align:center;padding:24px;color:#a09d9c;font-size:13px">Nenhum operador cadastrado ainda.</div>', unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f'<div style="color:#ff6b6b;font-size:12px">Erro ao carregar: {e}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_status:
        st.markdown("""
        <div class="cx-card">
          <div style="font-family:'Space Grotesk',sans-serif;font-size:15px;font-weight:600;margin-bottom:14px">Status do Sistema</div>
          <div style="font-size:12px;color:#00e479;margin-bottom:14px">● Sincronização em tempo real ativa.</div>
          <div style="margin-bottom:10px">
            <div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:5px"><span>Processamento de Voz (AI)</span><span style="color:#00e479;font-weight:600">99.9%</span></div>
            <div style="height:4px;background:#2a2a2a;border-radius:2px"><div style="height:100%;width:99.9%;background:#00e479;border-radius:2px"></div></div>
          </div>
          <div style="margin-bottom:14px">
            <div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:5px"><span>Banco de Dados</span><span style="color:#00e479;font-weight:600">Operacional</span></div>
            <div style="height:4px;background:#2a2a2a;border-radius:2px"><div style="height:100%;width:95%;background:#00e479;border-radius:2px"></div></div>
          </div>
          <div style="background:rgba(255,215,0,0.08);border:1px solid rgba(255,215,0,0.2);border-radius:4px;padding:12px 14px;display:flex;align-items:center;gap:8px">
            <div style="width:8px;height:8px;border-radius:50%;background:#FFD700"></div>
            <div style="font-size:12px;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;color:#FFD700">Google Sheets Conectado</div>
          </div>
        </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# PÁGINA: OPERADORES
# ─────────────────────────────────────────
def page_operadores():
    section_title("Operadores")
    section_sub("Gestão de desempenho individual e ranking de qualidade.")

    tab_lista, tab_novo = st.tabs(["📋  Lista de Operadores", "➕  Novo Operador"])

    with tab_lista:
        try:
            df = db.load_operadores()
        except Exception as e:
            st.error(f"Erro ao carregar operadores: {e}")
            df = pd.DataFrame()

        if df.empty:
            st.markdown('<div class="cx-info" style="text-align:center;padding:40px">Nenhum operador cadastrado ainda. Use a aba "Novo Operador" para adicionar.</div>', unsafe_allow_html=True)
        else:
            col_f1, col_f2 = st.columns([2, 1])
            with col_f1:
                busca = st.text_input("🔍 Buscar operador", placeholder="Nome ou matrícula...", label_visibility="collapsed")
            with col_f2:
                filtro_tier = st.selectbox("Filtrar por Tier", ["Todos","Sênior Tier 3","Pleno Tier 2","Júnior Tier 1"], label_visibility="collapsed")

            df_show = df.copy()
            if busca:
                df_show = df_show[df_show["nome"].str.contains(busca, case=False, na=False) |
                                  df_show["matricula"].str.contains(busca, case=False, na=False)]
            if filtro_tier != "Todos":
                df_show = df_show[df_show["tier"] == filtro_tier]

            cols = st.columns(4)
            for i, (_, row) in enumerate(df_show.iterrows()):
                with cols[i % 4]:
                    nota = float(row.get("nota_geral", 0) or 0)
                    cor = "#00e479" if nota >= 90 else "#FFD700" if nota >= 70 else "#ff6b6b"
                    st.markdown(f"""
                    <div class="cx-card" style="border-color:rgba(255,215,0,0.15)">
                      <div style="font-family:'Space Grotesk',sans-serif;font-size:15px;font-weight:600;margin-bottom:4px">{row.get("nome","—")}</div>
                      <div style="font-size:11px;color:#a09d9c;margin-bottom:12px">{row.get("matricula","—")} · {row.get("tier","—")}</div>
                      <div style="display:flex;justify-content:space-between;margin-bottom:6px"><span style="font-size:11px;text-transform:uppercase;letter-spacing:0.06em;color:#a09d9c">Nota Geral</span><span style="font-family:'Space Grotesk',sans-serif;font-size:14px;font-weight:700;color:{cor}">{nota:.1f}%</span></div>
                      <div style="height:2px;background:#2a2a2a;border-radius:1px;margin-bottom:8px"><div style="height:100%;width:{min(nota,100):.0f}%;background:{cor};border-radius:1px"></div></div>
                      <div style="display:flex;justify-content:space-between;margin-bottom:6px"><span style="font-size:11px;text-transform:uppercase;letter-spacing:0.06em;color:#a09d9c">MP</span><span style="font-size:13px;font-weight:600;color:#e5e2e1">{row.get("nota_mp","—")}%</span></div>
                      <div style="display:flex;justify-content:space-between;margin-bottom:6px"><span style="font-size:11px;text-transform:uppercase;letter-spacing:0.06em;color:#a09d9c">Interna</span><span style="font-size:13px;font-weight:600;color:#dcb8ff">{row.get("nota_interna","—")}%</span></div>
                    </div>""", unsafe_allow_html=True)
                    if st.button("✕ Remover", key=f"del_op_{row.get('id','')}", use_container_width=True):
                        try:
                            db.delete_operador(row.get("id"))
                            st.success("Operador removido.")
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))

    with tab_novo:
        st.markdown('<div class="cx-card">', unsafe_allow_html=True)
        st.markdown('<div style="font-family:\'Space Grotesk\',sans-serif;font-size:15px;font-weight:600;margin-bottom:20px">Cadastrar Novo Operador</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            nome_op = st.text_input("Nome Completo *", key="op_nome")
            tier_op = st.selectbox("Tier", ["Júnior Tier 1","Pleno Tier 2","Sênior Tier 3"], key="op_tier")
        with c2:
            mat_op = st.text_input("Matrícula *", key="op_mat")
            canal_op = st.selectbox("Canal Principal", ["Inbound","Outbound","Chat","E-mail"], key="op_canal")
        with c3:
            nota_g   = st.number_input("Nota Geral (%)",   0.0, 100.0, 0.0, key="op_ng")
            nota_mp  = st.number_input("Nota MP (%)",      0.0, 100.0, 0.0, key="op_mp")
            nota_int = st.number_input("Nota Interna (%)", 0.0, 100.0, 0.0, key="op_int")

        if st.button("Salvar Operador", use_container_width=True, key="btn_salvar_op"):
            if not nome_op or not mat_op:
                st.markdown('<div class="cx-error">Nome e matrícula são obrigatórios.</div>', unsafe_allow_html=True)
            else:
                try:
                    db.save_operador({
                        "nome": nome_op, "matricula": mat_op, "tier": tier_op,
                        "canal": canal_op, "nota_geral": nota_g,
                        "nota_mp": nota_mp, "nota_interna": nota_int, "ativo": "true"
                    })
                    st.markdown('<div class="cx-success">✓ Operador cadastrado e salvo no Google Sheets!</div>', unsafe_allow_html=True)
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
        st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────
# PÁGINA: AVALIAÇÕES
# ─────────────────────────────────────────
def page_avaliacoes():
    section_title("Registro de Qualidade")
    section_sub("Preencha os critérios técnicos para validação da operação.")

    tab_nova, tab_historico = st.tabs(["📝  Nova Avaliação", "📊  Histórico"])

    with tab_nova:
        col_form, col_score = st.columns([2, 1])

        with col_form:
            st.markdown('<div class="cx-card"><div style="font-family:\'Space Grotesk\',sans-serif;font-size:15px;font-weight:600;margin-bottom:16px;padding-bottom:12px;border-bottom:1px solid rgba(255,255,255,0.08)">⚙ Parâmetros de Operação</div>', unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            with c1:
                try:
                    df_ops = db.load_operadores()
                    op_lista = df_ops["nome"].tolist() if not df_ops.empty else []
                except: op_lista = []
                operador_sel = st.selectbox("Operador *", ["Selecionar..."] + op_lista, key="av_op")
            with c2:
                data_chamada = st.date_input("Data da Chamada", key="av_data")
            with c3:
                tipo_av = st.selectbox("Tipo", ["Interna","Mercado Pago","Avaliador Externo"], key="av_tipo")
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="cx-card"><div style="font-family:\'Space Grotesk\',sans-serif;font-size:15px;font-weight:600;margin-bottom:16px;padding-bottom:12px;border-bottom:1px solid rgba(255,255,255,0.08)">☑ Critérios de Qualidade</div>', unsafe_allow_html=True)
            criterios = {
                "saudacao":     ("Saudação Inicial e Identificação", 10),
                "empatia":      ("Escuta Ativa e Empatia", 25),
                "resolucao":    ("Resolução Técnica", 40),
                "encerramento": ("Encerramento e Próximos Passos", 25),
            }
            scores = {}
            for key, (label, peso) in criterios.items():
                c_l, c_s = st.columns([3, 1])
                with c_l:
                    st.markdown(f'<div style="font-size:14px;font-weight:500;margin-bottom:4px">{label} <span style="font-size:11px;color:#FFD700;font-weight:600">(Peso: {peso}%)</span></div>', unsafe_allow_html=True)
                with c_s:
                    scores[key] = st.number_input("", 0.0, 10.0, 8.0, 0.1, key=f"av_{key}", label_visibility="collapsed")
                pct = scores[key] / 10
                st.markdown(f'<div style="height:2px;background:#2a2a2a;border-radius:1px;margin-bottom:12px"><div style="height:100%;width:{pct*100:.0f}%;background:#FFD700;border-radius:1px"></div></div>', unsafe_allow_html=True)

            nota_calc = sum(scores[k] * criterios[k][1] / 100 for k in scores) * 10
            st.session_state.score_avaliacao = nota_calc / 10
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="cx-card"><div style="font-family:\'Space Grotesk\',sans-serif;font-size:15px;font-weight:600;margin-bottom:12px">☰ Parecer do Analista</div>', unsafe_allow_html=True)
            parecer = st.text_area("Observação qualitativa", placeholder="Descreva sua observação sobre o atendimento...", height=120, key="av_parecer", label_visibility="collapsed")
            st.markdown('</div>', unsafe_allow_html=True)

        with col_score:
            nota_final = st.session_state.score_avaliacao
            cor_nota = "#00e479" if nota_final >= 8 else "#FFD700" if nota_final >= 6 else "#ff6b6b"
            st.markdown(f"""
            <div class="score-display" style="border-color:rgba(255,215,0,0.3);position:sticky;top:80px">
              <div style="font-size:10px;letter-spacing:0.12em;text-transform:uppercase;color:#a09d9c;margin-bottom:16px">Nota Final Calculada</div>
              <div class="score-big" style="color:{cor_nota}">{nota_final:.1f}</div>
              <div style="font-size:14px;color:#a09d9c;margin-bottom:16px">/ 10.0</div>
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:16px">
                <div style="background:#1c1b1b;border-radius:4px;padding:10px;text-align:center">
                  <div style="font-size:10px;color:#a09d9c;text-transform:uppercase;letter-spacing:0.08em">Soft Skills</div>
                  <div style="font-family:'Space Grotesk',sans-serif;font-size:18px;font-weight:600;color:#00e479">{(scores.get("saudacao",0)+scores.get("empatia",0))/2:.1f}</div>
                </div>
                <div style="background:#1c1b1b;border-radius:4px;padding:10px;text-align:center">
                  <div style="font-size:10px;color:#a09d9c;text-transform:uppercase;letter-spacing:0.08em">Técnico</div>
                  <div style="font-family:'Space Grotesk',sans-serif;font-size:18px;font-weight:600;color:#dcb8ff">{(scores.get("resolucao",0)+scores.get("encerramento",0))/2:.1f}</div>
                </div>
              </div>
            </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("💾 Salvar Avaliação", use_container_width=True, key="btn_salvar_av"):
                if operador_sel == "Selecionar...":
                    st.markdown('<div class="cx-error">Selecione um operador.</div>', unsafe_allow_html=True)
                else:
                    try:
                        user = st.session_state.user or {}
                        db.save_avaliacao({
                            "operador": operador_sel,
                            "data_chamada": str(data_chamada),
                            "tipo": tipo_av,
                            "nota_final": round(nota_final, 2),
                            "soft_skills": round((scores.get("saudacao",0)+scores.get("empatia",0))/2, 1),
                            "tecnico": round((scores.get("resolucao",0)+scores.get("encerramento",0))/2, 1),
                            "saudacao": scores.get("saudacao",0),
                            "empatia": scores.get("empatia",0),
                            "resolucao": scores.get("resolucao",0),
                            "encerramento": scores.get("encerramento",0),
                            "parecer": parecer,
                            "auditor": user.get("nome","Sistema"),
                        })
                        st.markdown('<div class="cx-success">✓ Avaliação salva no Google Sheets!</div>', unsafe_allow_html=True)
                    except Exception as e:
                        st.error(str(e))

            if st.button("📄 Salvar Rascunho", use_container_width=True, key="btn_rascunho_av"):
                st.markdown('<div class="cx-info">Rascunho salvo localmente.</div>', unsafe_allow_html=True)

    with tab_historico:
        try:
            df_av = db.load_avaliacoes()
            if df_av.empty:
                st.markdown('<div class="cx-info" style="text-align:center;padding:40px">Nenhuma avaliação registrada ainda.</div>', unsafe_allow_html=True)
            else:
                c1, c2 = st.columns(2)
                with c1:
                    busca_av = st.text_input("🔍 Buscar operador", key="hist_busca", label_visibility="collapsed", placeholder="Buscar operador...")
                with c2:
                    filtro_tipo = st.selectbox("Tipo", ["Todos","Interna","Mercado Pago","Avaliador Externo"], key="hist_tipo", label_visibility="collapsed")

                df_show = df_av.copy()
                if busca_av:
                    df_show = df_show[df_show["operador"].str.contains(busca_av, case=False, na=False)]
                if filtro_tipo != "Todos":
                    df_show = df_show[df_show["tipo"] == filtro_tipo]

                df_show["nota_final"] = pd.to_numeric(df_show["nota_final"], errors="coerce")
                st.markdown(f'<div style="font-size:13px;color:#a09d9c;margin-bottom:12px">{len(df_show)} registro(s) encontrado(s)</div>', unsafe_allow_html=True)

                for _, row in df_show.sort_values("criado_em", ascending=False).head(20).iterrows():
                    nota = row.get("nota_final", 0)
                    cor = "#00e479" if float(nota or 0) >= 8 else "#FFD700" if float(nota or 0) >= 6 else "#ff6b6b"
                    st.markdown(f"""
                    <div class="cx-card" style="margin-bottom:10px">
                      <div style="display:flex;align-items:center;justify-content:space-between">
                        <div>
                          <div style="font-size:15px;font-weight:600">{row.get("operador","—")}</div>
                          <div style="font-size:11px;color:#a09d9c;margin-top:2px">{row.get("data_chamada","—")} · {row.get("tipo","—")} · Auditor: {row.get("auditor","—")}</div>
                        </div>
                        <div style="font-family:'Space Grotesk',sans-serif;font-size:28px;font-weight:700;color:{cor}">{nota}/10</div>
                      </div>
                      {f'<div style="font-size:13px;color:#a09d9c;margin-top:10px;font-style:italic">{row.get("parecer","")[:120]}...</div>' if row.get("parecer") else ""}
                    </div>""", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Erro ao carregar histórico: {e}")


# ─────────────────────────────────────────
# PÁGINA: BANCO DE ERROS
# ─────────────────────────────────────────
def page_bancoerros():
    section_title("Banco de Erros")
    section_sub("Monitoramento crítico de falhas processuais e comportamentais.")

    tab_log, tab_novo, tab_stats = st.tabs(["📋  Log de Erros", "➕  Registrar Erro", "📊  Estatísticas"])

    with tab_log:
        try:
            df_erros = db.load_erros()
        except Exception as e:
            st.error(str(e)); df_erros = pd.DataFrame()

        cats = [
            ("PROC-01","Procedimento","yellow","4.2/5.0","↘ −8%","pos"),
            ("COMM-02","Comunicação","purple","2.8/5.0","↗ +15%","neg"),
            ("SYS-03","Sistema","red","4.9/5.0","↗ +22%","neg"),
            ("FIN-04","Financeiro","green","5.0/5.0","— Estável","stable"),
            ("CSR-05","Atendimento","gray","3.1/5.0","↘ −12%","pos"),
        ]
        cols = st.columns(5)
        for i, (cid, ctitle, ccor, imp, trend, tcor) in enumerate(cats):
            with cols[i]:
                border_colors = {"yellow":"#FFD700","purple":"#dcb8ff","red":"#FF3B3B","green":"#00e479","gray":"#a09d9c"}
                trend_colors  = {"pos":"#00e479","neg":"#ff6b6b","stable":"#a09d9c"}
                st.markdown(f"""
                <div class="cx-card" style="border-top:2px solid {border_colors.get(ccor,'#444')}">
                  <div style="font-size:10px;text-transform:uppercase;letter-spacing:0.08em;color:#a09d9c;margin-bottom:6px">{cid}</div>
                  <div style="font-family:'Space Grotesk',sans-serif;font-size:17px;font-weight:600;margin-bottom:8px">{ctitle}</div>
                  <div style="font-size:12px;color:#a09d9c;margin-bottom:10px">Impacto: <strong style="color:#e5e2e1">{imp}</strong></div>
                  <div style="font-size:12px;font-weight:600;color:{trend_colors.get(tcor,'#a09d9c')}">{trend}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("---")

        if df_erros.empty:
            st.markdown('<div class="cx-info" style="text-align:center;padding:32px">Nenhum erro registrado. Use a aba "Registrar Erro".</div>', unsafe_allow_html=True)
        else:
            st.dataframe(
                df_erros[["horario","categoria","descricao","operador","severidade","status"]].rename(columns={
                    "horario":"Horário","categoria":"Categoria","descricao":"Descrição",
                    "operador":"Operador","severidade":"Severidade","status":"Status"
                }),
                use_container_width=True, hide_index=True
            )

    with tab_novo:
        st.markdown('<div class="cx-card">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            cat_err = st.selectbox("Categoria", ["PROC-01 - Procedimento","COMM-02 - Comunicação","SYS-03 - Sistema","FIN-04 - Financeiro","CSR-05 - Atendimento"], key="err_cat")
            sev_err = st.selectbox("Severidade", ["Crítica","Alta","Média","Baixa"], key="err_sev")
        with c2:
            try:
                df_ops = db.load_operadores()
                op_lista = df_ops["nome"].tolist() if not df_ops.empty else []
            except: op_lista = []
            op_err  = st.selectbox("Operador", ["—"] + op_lista, key="err_op")
            hora_err = st.text_input("Horário", value=datetime.now().strftime("%H:%M:%S"), key="err_hora")
        with c3:
            desc_err = st.text_area("Descrição do Erro *", height=100, key="err_desc")

        if st.button("Registrar Erro", use_container_width=True, key="btn_salvar_err"):
            if not desc_err:
                st.markdown('<div class="cx-error">Descrição é obrigatória.</div>', unsafe_allow_html=True)
            else:
                try:
                    db.save_erro({"horario":hora_err,"categoria":cat_err.split(" - ")[0],"descricao":desc_err,"operador":op_err,"severidade":sev_err,"status":"Aberto"})
                    st.markdown('<div class="cx-success">✓ Erro registrado no Google Sheets!</div>', unsafe_allow_html=True)
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_stats:
        try:
            df_erros = db.load_erros()
            if not df_erros.empty and "categoria" in df_erros.columns:
                contagem = df_erros["categoria"].value_counts()
                fig = px.pie(values=contagem.values, names=contagem.index,
                             color_discrete_sequence=["#FFD700","#dcb8ff","#FF3B3B","#00e479","#a09d9c"],
                             hole=0.6)
                layout_pie = dict(**PLOTLY_LAYOUT)
                layout_pie["showlegend"] = True
                layout_pie["height"] = 300
                fig.update_layout(**layout_pie)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
            else:
                st.markdown('<div class="cx-info" style="text-align:center;padding:32px">Sem dados suficientes para estatísticas.</div>', unsafe_allow_html=True)
        except Exception as e:
            st.error(str(e))


# ─────────────────────────────────────────
# PÁGINA: FEEDBACK AO OPERADOR
# ─────────────────────────────────────────
def page_feedback_op():
    section_title("Entregar Feedback")
    section_sub("Registre e envie feedback de avaliação ao operador.")

    col_form, col_preview = st.columns([2, 1])

    with col_form:
        st.markdown('<div class="cx-card"><div style="font-family:\'Space Grotesk\',sans-serif;font-size:15px;font-weight:600;margin-bottom:16px;padding-bottom:12px;border-bottom:1px solid rgba(255,255,255,0.08)">👤 Operador</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            try:
                df_ops = db.load_operadores()
                op_lista = df_ops["nome"].tolist() if not df_ops.empty else []
            except: op_lista = []
            op_fb = st.selectbox("Operador *", ["Selecionar..."] + op_lista, key="fb_op")
        with c2:
            data_fb = st.date_input("Data da Avaliação", key="fb_data")
        with c3:
            tipo_fb = st.selectbox("Tipo de Feedback", ["Positivo","Corretivo","Desenvolvimento","Reconhecimento"], key="fb_tipo")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="cx-card"><div style="font-family:\'Space Grotesk\',sans-serif;font-size:15px;font-weight:600;margin-bottom:16px;padding-bottom:12px;border-bottom:1px solid rgba(255,255,255,0.08)">☑ Critérios Avaliados</div>', unsafe_allow_html=True)
        criterios_fb = {
            "Saudação e Identificação": ("saud", 10),
            "Escuta Ativa e Empatia":   ("emp",  25),
            "Resolução Técnica":        ("res",  40),
            "Encerramento":             ("enc",  25),
        }
        star_scores = {}
        labels_stars = ["Não avaliado","Insuficiente","Abaixo do esperado","Dentro do esperado","Acima do esperado","Excelente"]
        for label, (key, peso) in criterios_fb.items():
            c_l, c_s = st.columns([3, 1])
            with c_l:
                st.markdown(f'<div style="font-size:14px;font-weight:500;margin-bottom:4px">{label} <span style="font-size:11px;color:#FFD700">Peso {peso}%</span></div>', unsafe_allow_html=True)
            with c_s:
                val = st.select_slider("", options=[0,1,2,3,4,5], value=0, key=f"fb_star_{key}", label_visibility="collapsed")
                star_scores[key] = (val, peso)
            st.markdown(f'<div style="font-size:11px;color:#a09d9c;margin-bottom:10px">{"★"*val}{"☆"*(5-val)} — {labels_stars[val]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="cx-card"><div style="font-family:\'Space Grotesk\',sans-serif;font-size:15px;font-weight:600;margin-bottom:16px;padding-bottom:12px;border-bottom:1px solid rgba(255,255,255,0.08)">✉ Mensagem ao Operador</div>', unsafe_allow_html=True)
        positivo = st.text_area("Pontos Positivos",   placeholder="O que o operador fez bem...",      height=80, key="fb_pos")
        melhoria = st.text_area("Pontos de Melhoria", placeholder="O que precisa ser ajustado...",    height=80, key="fb_mel")
        plano    = st.text_area("Plano de Ação",      placeholder="Próximos passos concretos...",     height=60, key="fb_pln")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="cx-card"><div style="font-family:\'Space Grotesk\',sans-serif;font-size:15px;font-weight:600;margin-bottom:12px">👁 Visibilidade</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: vis_op  = st.checkbox("Visível para o operador", value=True, key="fb_vis_op")
        with c2: vis_ges = st.checkbox("Visível para gestores",   value=True, key="fb_vis_ges")
        with c3: notif   = st.checkbox("Notificar por e-mail",    value=False, key="fb_notif")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_preview:
        total, peso_total = 0, 0
        for key, (val, peso) in star_scores.items():
            if val > 0:
                total += (val/5) * peso
                peso_total += peso
        nota_fb = round(total/peso_total*100) if peso_total > 0 else 0
        cor_fb = "#00e479" if nota_fb >= 80 else "#FFD700" if nota_fb >= 60 else "#ff6b6b"

        nome_op_display = op_fb.split("—")[0].strip() if op_fb != "Selecionar..." else "—"
        initials_fb = "".join(w[0] for w in nome_op_display.split()[:2]).upper() if nome_op_display != "—" else "—"

        st.markdown(f"""
        <div class="cx-card" style="border-color:rgba(255,215,0,0.2)">
          <div style="font-size:10px;text-transform:uppercase;letter-spacing:0.1em;color:#a09d9c;margin-bottom:14px">Preview</div>
          <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px">
            <div style="width:48px;height:48px;border-radius:50%;background:#2a2a2a;display:flex;align-items:center;justify-content:center;font-family:'Space Grotesk',sans-serif;font-size:16px;font-weight:700;color:#FFD700">{initials_fb}</div>
            <div>
              <div style="font-family:'Space Grotesk',sans-serif;font-size:16px;font-weight:600">{nome_op_display}</div>
              <div style="font-size:12px;color:#a09d9c">{tipo_fb}</div>
            </div>
          </div>
          <div style="font-size:11px;color:#a09d9c;margin-bottom:8px;text-transform:uppercase;letter-spacing:0.08em">Nota Calculada</div>
          <div style="font-family:'Space Grotesk',sans-serif;font-size:48px;font-weight:700;color:{cor_fb};line-height:1">{nota_fb}</div>
          <div style="font-size:16px;color:#a09d9c;margin-bottom:12px">/100</div>
          <div style="height:6px;background:#2a2a2a;border-radius:3px"><div style="height:100%;width:{nota_fb}%;background:{cor_fb};border-radius:3px;transition:width 0.4s"></div></div>
        </div>""", unsafe_allow_html=True)

        st.markdown('<div class="cx-card" style="margin-top:14px"><div style="font-size:13px;font-weight:600;margin-bottom:12px">Feedbacks Anteriores</div>', unsafe_allow_html=True)
        if op_fb != "Selecionar...":
            try:
                df_fb = db.load_feedbacks()
                if not df_fb.empty:
                    op_hist = df_fb[df_fb["operador"] == nome_op_display].tail(3)
                    if op_hist.empty:
                        st.markdown('<div style="font-size:12px;color:#a09d9c">Nenhum feedback anterior.</div>', unsafe_allow_html=True)
                    else:
                        for _, r in op_hist.iterrows():
                            st.markdown(f"""
                            <div style="padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.04)">
                              <div style="display:flex;justify-content:space-between"><span style="font-size:13px;font-weight:500">{r.get("tipo","—")}</span><span style="font-size:11px;color:#FFD700;font-weight:700">{r.get("nota","—")}/100</span></div>
                              <div style="font-size:11px;color:#a09d9c">{r.get("data","—")}</div>
                            </div>""", unsafe_allow_html=True)
            except:
                st.markdown('<div style="font-size:12px;color:#a09d9c">Sem histórico disponível.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="font-size:12px;color:#a09d9c">Selecione um operador.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if st.button("📤 Enviar Feedback", use_container_width=True, key="btn_enviar_fb"):
            if op_fb == "Selecionar...":
                st.markdown('<div class="cx-error">Selecione um operador.</div>', unsafe_allow_html=True)
            else:
                try:
                    user = st.session_state.user or {}
                    db.save_feedback({
                        "operador": nome_op_display,
                        "data": str(data_fb),
                        "tipo": tipo_fb,
                        "nota": nota_fb,
                        "positivo": positivo,
                        "melhoria": melhoria,
                        "plano": plano,
                        "vis_operador": str(vis_op),
                        "vis_gestor": str(vis_ges),
                        "notif_email": str(notif),
                        "auditor": user.get("nome","Sistema"),
                        "status": "Enviado",
                    })
                    st.markdown(f'<div class="cx-success">✓ Feedback enviado para {nome_op_display} e salvo no Google Sheets!</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(str(e))

        if st.button("💾 Salvar Rascunho", use_container_width=True, key="btn_rascunho_fb"):
            if op_fb != "Selecionar...":
                try:
                    user = st.session_state.user or {}
                    db.save_feedback({"operador":nome_op_display,"data":str(data_fb),"tipo":tipo_fb,"nota":nota_fb,"positivo":positivo,"melhoria":melhoria,"plano":plano,"auditor":user.get("nome","Sistema"),"status":"Rascunho"})
                    st.markdown('<div class="cx-info">Rascunho salvo!</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(str(e))


# ─────────────────────────────────────────
# PÁGINA: IA DE QUALIDADE
# ─────────────────────────────────────────
def page_ia():
    section_title("✦ IA de Qualidade")
    section_sub("Insights executivos e análise preditiva powered by Claude.")

    col_main, col_side = st.columns([2, 1])

    with col_main:
        st.markdown("""
        <div class="cx-card">
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px">
            <div style="font-family:'Space Grotesk',sans-serif;font-size:16px;font-weight:600">☰ Diagnóstico de IA</div>
            <div style="display:flex;align-items:center;gap:6px;font-size:11px;color:#00e479;font-weight:600"><div style="width:6px;height:6px;border-radius:50%;background:#00e479"></div>Processamento em Tempo Real</div>
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
            <div style="background:#1c1b1b;border:1px solid rgba(255,255,255,0.08);border-radius:4px;padding:14px">
              <div style="font-size:10px;text-transform:uppercase;letter-spacing:0.1em;color:#a09d9c;margin-bottom:10px">Principais Gargalos</div>
              <div style="font-size:14px;font-weight:500;margin-bottom:3px">Tempo Médio de Silêncio <span style="color:#ff6b6b;font-size:13px;font-weight:600">+22%</span></div>
              <div style="font-size:12px;color:#a09d9c;margin-bottom:10px">Crítico em 14% das chamadas</div>
              <div style="display:flex;justify-content:space-between;margin-bottom:3px"><span style="font-size:13px;font-weight:500">FCR na 1ª Chamada</span><span style="color:#FFD700;font-weight:700">78%</span></div>
              <div style="height:4px;background:#2a2a2a;border-radius:2px"><div style="height:100%;width:78%;background:#FFD700;border-radius:2px"></div></div>
              <div style="font-size:11px;color:#a09d9c;margin-top:3px">Abaixo do KPI alvo (85%)</div>
            </div>
            <div style="background:#1c1b1b;border:1px solid rgba(255,255,255,0.08);border-radius:4px;padding:14px">
              <div style="font-size:10px;text-transform:uppercase;letter-spacing:0.1em;color:#a09d9c;margin-bottom:10px">Operadores em Risco</div>
              <div style="display:flex;align-items:center;gap:8px;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.04)">
                <div style="width:28px;height:28px;border-radius:50%;background:#2a2a2a;display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:700;color:#FFD700">RS</div>
                <div><div style="font-size:13px;font-weight:500">Ricardo Silva</div><div style="font-size:11px;color:#ff6b6b">Tendência de Queda ↘</div></div>
              </div>
              <div style="display:flex;align-items:center;gap:8px;padding:8px 0">
                <div style="width:28px;height:28px;border-radius:50%;background:#2a2a2a;display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:700;color:#FFD700">AM</div>
                <div><div style="font-size:13px;font-weight:500">Ana Martins</div><div style="font-size:11px;color:#ffa040">Alta Irritabilidade ⚠</div></div>
              </div>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)

        st.markdown('<div class="cx-card"><div style="font-family:\'Space Grotesk\',sans-serif;font-size:16px;font-weight:600;color:#dcb8ff;margin-bottom:16px">✦ Chat com a IA de Qualidade</div>', unsafe_allow_html=True)

        chat_container = st.container()
        with chat_container:
            if not st.session_state.ia_messages:
                st.markdown('<div class="ia-msg-assistant"><div class="ia-role ia-role-bot">✦ IA CX Command</div>Olá! Sou a IA de Qualidade do CX Command. Posso analisar métricas, identificar padrões de erros e gerar insights executivos. Como posso ajudar?</div>', unsafe_allow_html=True)
            for msg in st.session_state.ia_messages:
                if msg["role"] == "user":
                    st.markdown(f'<div class="ia-msg-user"><div class="ia-role ia-role-user">👤 Analista</div>{msg["content"]}</div>', unsafe_allow_html=True)
                else:
                    content = msg["content"].replace("\n", "<br>").replace("**","<strong>",1)
                    st.markdown(f'<div class="ia-msg-assistant"><div class="ia-role ia-role-bot">✦ IA CX Command</div>{content}</div>', unsafe_allow_html=True)

        qcols = st.columns(4)
        quick_prompts = [
            ("📊 Problemas da semana", "Quais são os principais problemas de qualidade desta semana?"),
            ("🎯 Plano de melhoria",   "Gere um plano de melhoria para operadores com nota abaixo de 70%"),
            ("🔮 Previsão de riscos",  "Analise tendências de erro nos últimos 30 dias e preveja riscos"),
            ("⚠ Operadores em risco", "Quais operadores estão em risco de queda de performance?"),
        ]
        for i, (label, prompt) in enumerate(quick_prompts):
            with qcols[i]:
                if st.button(label, key=f"quick_{i}", use_container_width=True):
                    st.session_state.ia_messages.append({"role":"user","content":prompt})
                    with st.spinner("IA analisando..."):
                        resposta = chamar_claude(prompt)
                    st.session_state.ia_messages.append({"role":"assistant","content":resposta})
                    st.rerun()

        col_inp, col_send = st.columns([5, 1])
        with col_inp:
            user_msg = st.text_input("", placeholder="Faça uma pergunta sobre a operação...", key="ia_input", label_visibility="collapsed")
        with col_send:
            if st.button("Enviar ✦", use_container_width=True, key="ia_send"):
                if user_msg.strip():
                    st.session_state.ia_messages.append({"role":"user","content":user_msg})
                    with st.spinner("IA analisando..."):
                        resposta = chamar_claude(user_msg)
                    st.session_state.ia_messages.append({"role":"assistant","content":resposta})
                    st.rerun()

        if st.button("🗑 Limpar conversa", key="ia_clear"):
            st.session_state.ia_messages = []
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    with col_side:
        st.markdown("""
        <div class="cx-card" style="border-color:rgba(220,184,255,0.25);text-align:center">
          <div style="font-size:11px;text-transform:uppercase;letter-spacing:0.1em;color:#a09d9c;margin-bottom:16px">Status da IA</div>
          <div style="font-family:'Space Grotesk',sans-serif;font-size:56px;font-weight:700;color:#dcb8ff;line-height:1">89</div>
          <div style="font-size:11px;color:#a09d9c;margin-bottom:12px">SCORE GERAL</div>
          <div style="font-size:14px;font-weight:600;margin-bottom:6px">Performance Ótima</div>
          <div style="font-size:12px;color:#a09d9c;margin-bottom:16px">Operação 12% acima da média do setor.</div>
          <div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.04)"><span style="font-size:12px;color:#a09d9c">Confiança da IA</span><span style="font-size:12px;font-weight:600;color:#00e479">98.2%</span></div>
          <div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.04)"><span style="font-size:12px;color:#a09d9c">Modelo</span><span style="font-size:12px;font-weight:600;color:#dcb8ff">Claude Sonnet</span></div>
        </div>""", unsafe_allow_html=True)

        st.markdown("""
        <div class="cx-card" style="border-color:rgba(220,184,255,0.2);margin-top:14px">
          <div style="font-size:10px;text-transform:uppercase;letter-spacing:0.1em;color:#dcb8ff;font-weight:700;margin-bottom:10px">🔮 IA Predição</div>
          <div style="font-size:13px;color:#a09d9c;line-height:1.6;font-style:italic">"Com base na tendência atual de reclamações, prevemos aumento de 15% no volume de chamadas nas próximas 48h."</div>
        </div>""", unsafe_allow_html=True)

        if st.button("✦ Análise Executiva Completa", use_container_width=True, key="ia_full"):
            prompt = "Faça uma análise executiva completa da operação atual. Identifique os 3 principais problemas, os maiores riscos para os próximos 7 dias e sugira 3 ações prioritárias com responsáveis e prazos."
            st.session_state.ia_messages.append({"role":"user","content":prompt})
            with st.spinner("Gerando análise completa..."):
                resposta = chamar_claude(prompt)
            st.session_state.ia_messages.append({"role":"assistant","content":resposta})
            st.rerun()


def chamar_claude(mensagem: str) -> str:
    """Chama a API do Claude com contexto da operação."""
    try:
        api_key = st.secrets.get("anthropic_api_key", "")
        if not api_key:
            return "⚠ API Key do Claude não configurada. Adicione `anthropic_api_key` no arquivo `.streamlit/secrets.toml`."

        client = anthropic.Anthropic(api_key=api_key)

        system_prompt = """Você é a IA de Qualidade do CX Command, especializada em análise de call centers.

Dados atuais da operação:
- Nota Média Geral: 95.0 (↑4.2%) | Nota MP: 92.1 (↑1.8%)
- Operadores: 142 ativos | FCR: 78% (meta 85%)
- Erros 24h: 124 (↑12%) | NPS: 8.7
- Top: Ana Silva (98.5%), Henrique M. (96.8%), Clara J. (92.0%)
- Em risco: Ricardo Silva (queda), Ana Martins (irritabilidade alta)

Responda em português, de forma objetiva e executiva. Use **negrito** para pontos críticos."""

        history = [{"role": m["role"], "content": m["content"]}
                   for m in st.session_state.ia_messages[:-1]]

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            system=system_prompt,
            messages=history + [{"role":"user","content":mensagem}]
        )
        return response.content[0].text
    except Exception as e:
        return f"❌ Erro ao chamar Claude: {str(e)}"


# ─────────────────────────────────────────
# PÁGINA: BASE QA
# ─────────────────────────────────────────
def page_base_qa():
    section_title("Base QA")
    section_sub("Matriz de critérios e avaliações individuais de operadores.")

    tab_matriz, tab_av = st.tabs(["📋  Matriz de Critérios", "📄  Avaliações Individuais (.docx)"])

    with tab_matriz:
        col_up, col_status = st.columns([2, 1])
        with col_up:
            st.markdown('<div class="cx-card"><div style="font-family:\'Space Grotesk\',sans-serif;font-size:15px;font-weight:600;margin-bottom:6px">Matriz de Qualidade (PDF)</div><div style="font-size:13px;color:#a09d9c;margin-bottom:20px">Faça upload da sua matriz QA em PDF como referência central do sistema.</div>', unsafe_allow_html=True)
            pdf_file = st.file_uploader("Selecione o PDF da Matriz QA", type=["pdf"], key="matriz_upload")
            if pdf_file:
                st.session_state["matriz_pdf"]  = pdf_file.read()
                st.session_state["matriz_nome"] = pdf_file.name
                st.markdown(f'<div class="cx-success">✓ Matriz "{pdf_file.name}" carregada com sucesso!</div>', unsafe_allow_html=True)
                st.download_button("⬇ Baixar Matriz", data=st.session_state["matriz_pdf"], file_name=pdf_file.name, mime="application/pdf")
            st.markdown('</div>', unsafe_allow_html=True)

        with col_status:
            if "matriz_nome" in st.session_state:
                st.markdown(f"""
                <div class="cx-card">
                  <div style="font-size:10px;text-transform:uppercase;letter-spacing:0.08em;color:#a09d9c;margin-bottom:12px">Status da Matriz</div>
                  <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px">
                    <div style="width:36px;height:36px;border-radius:4px;background:rgba(0,228,121,0.1);border:1px solid rgba(0,228,121,0.25);display:flex;align-items:center;justify-content:center;font-size:18px">✓</div>
                    <div><div style="font-size:13px;font-weight:600;color:#00e479">Matriz carregada</div><div style="font-size:11px;color:#a09d9c">{st.session_state.get("matriz_nome","—")}</div></div>
                  </div>
                  <div style="font-size:12px;color:#a09d9c;line-height:1.6">Esta matriz está sendo usada como referência para análises de IA do sistema.</div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown('<div class="cx-card"><div style="text-align:center;padding:24px 0;color:#a09d9c"><div style="font-size:32px;margin-bottom:8px">📭</div><div style="font-size:13px">Nenhuma matriz carregada</div></div></div>', unsafe_allow_html=True)

    with tab_av:
        col_up2, col_hist = st.columns([2, 1])
        with col_up2:
            st.markdown('<div class="cx-card"><div style="font-family:\'Space Grotesk\',sans-serif;font-size:15px;font-weight:600;margin-bottom:6px">Enviar Avaliação Individual</div><div style="font-size:13px;color:#a09d9c;margin-bottom:16px">Envie o .docx com a avaliação do operador. A IA extrai as informações automaticamente.</div>', unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                try:
                    df_ops = db.load_operadores()
                    op_lista = df_ops["nome"].tolist() if not df_ops.empty else []
                except: op_lista = []
                op_av = st.selectbox("Operador *", ["Selecionar..."] + op_lista, key="qa_op")
            with c2:
                periodo_av = st.text_input("Período (ex: Jun/2024)", key="qa_periodo")

            docx_file = st.file_uploader("Selecione o arquivo .docx", type=["docx","doc"], key="qa_docx_upload")

            if docx_file and op_av != "Selecionar...":
                if st.button("✦ Analisar com IA", use_container_width=True, key="btn_analisar_docx"):
                    with st.spinner("Extraindo texto do .docx..."):
                        try:
                            result = mammoth.extract_raw_text(docx_file)
                            texto  = result.value
                        except Exception as e:
                            texto = f"[Erro ao extrair: {e}]"

                    with st.spinner("IA analisando avaliação — extraindo todos os critérios..."):
                        texto_truncado = texto[:8000]
                        prompt = f"""Você é um extrator de dados de documentos de avaliação de qualidade (QA) de call center.

Leia o documento abaixo e extraia TODAS as informações de avaliação presentes.
Retorne SOMENTE um JSON válido, sem markdown, sem texto antes ou depois.

Regras:
- Extraia TODOS os critérios de avaliação encontrados no documento, sem omitir nenhum.
- Para cada critério, extraia o nome exato, a nota recebida e o peso (se disponível).
- Se uma nota estiver em escala diferente de 0-10, converta proporcionalmente para 0-10.
- Se não encontrar um campo, use null (não invente valores).
- O campo "acertos" deve conter pontos positivos mencionados no documento.
- O campo "erros" deve conter falhas ou pontos negativos mencionados.
- O campo "melhorias" deve conter sugestões de desenvolvimento mencionadas.
- O campo "observacoes" deve conter quaisquer outros comentários do avaliador.
- "notaFinal" deve ser a nota geral final do documento (escala 0-100).
- "softSkills" e "tecnico" devem ser extraídos se o documento os mencionar separadamente (escala 0-100).

DOCUMENTO:
{texto_truncado}

Formato JSON de saída (retorne exatamente neste formato, sem texto adicional):
{{
  "notaFinal": null,
  "softSkills": null,
  "tecnico": null,
  "criterios": [
    {{"nome": "Nome exato do critério", "nota": null, "peso": "ex: 20%", "observacao": ""}}
  ],
  "acertos": "",
  "erros": "",
  "melhorias": "",
  "observacoes": ""
}}"""
                        resposta_ia = chamar_claude(prompt)

                    try:
                        import json, re
                        match = re.search(r'\{.*\}', resposta_ia, re.DOTALL)
                        dados = json.loads(match.group(0)) if match else {}
                    except:
                        dados = {}

                    st.session_state["qa_resultado"]   = dados
                    st.session_state["qa_texto_bruto"] = texto

            if "qa_resultado" in st.session_state:
                dados = st.session_state["qa_resultado"]
                st.markdown('<hr><div style="font-family:\'Space Grotesk\',sans-serif;font-size:15px;font-weight:600;color:#dcb8ff;margin:12px 0">✦ Resultado da Análise — Edite antes de salvar</div>', unsafe_allow_html=True)

                c1, c2, c3 = st.columns(3)
                with c1: nf  = st.number_input("Nota Final",   0.0, 100.0, float(dados.get("notaFinal")  or 0), key="qa_nf")
                with c2: ss  = st.number_input("Soft Skills",  0.0, 100.0, float(dados.get("softSkills") or 0), key="qa_ss")
                with c3: tec = st.number_input("Técnico",      0.0, 100.0, float(dados.get("tecnico")    or 0), key="qa_tec")

                criterios_extraidos = dados.get("criterios", [])
                if criterios_extraidos:
                    st.markdown("""
                    <div style="font-size:13px;font-weight:600;color:#a09d9c;margin:14px 0 8px;
                                text-transform:uppercase;letter-spacing:0.08em;
                                padding-bottom:6px;border-bottom:1px solid rgba(255,255,255,0.08)">
                      Critérios Extraídos
                    </div>""", unsafe_allow_html=True)
                    for i, crit in enumerate(criterios_extraidos):
                        cc1, cc2, cc3 = st.columns([3, 1, 1])
                        with cc1:
                            st.text_input(
                                f"Critério {i+1}",
                                value=crit.get("nome", ""),
                                key=f"qa_crit_nome_{i}"
                            )
                        with cc2:
                            nota_raw = crit.get("nota")
                            nota_val = float(nota_raw) if nota_raw is not None else 0.0
                            st.number_input(
                                "Nota (0-10)",
                                min_value=0.0, max_value=10.0,
                                value=min(nota_val, 10.0),
                                step=0.1,
                                key=f"qa_crit_nota_{i}"
                            )
                        with cc3:
                            st.text_input(
                                "Peso",
                                value=crit.get("peso", ""),
                                key=f"qa_crit_peso_{i}"
                            )
                        obs_crit = crit.get("observacao", "")
                        if obs_crit:
                            st.markdown(f'<div style="font-size:11px;color:#a09d9c;margin:-8px 0 10px;font-style:italic">{obs_crit}</div>', unsafe_allow_html=True)

                acertos   = st.text_area("✓ Pontos Certos",      value=dados.get("acertos",""),    height=80, key="qa_ac")
                erros     = st.text_area("✕ Pontos de Erro",     value=dados.get("erros",""),      height=80, key="qa_er")
                melhorias = st.text_area("↗ Pontos de Melhoria", value=dados.get("melhorias",""),  height=80, key="qa_me")
                obs       = st.text_area("Observações Gerais",   value=dados.get("observacoes",""),height=80, key="qa_ob")

                if st.button("💾 Salvar Avaliação", use_container_width=True, key="btn_salvar_qa"):
                    try:
                        user = st.session_state.user or {}

                        criterios_str = ""
                        if criterios_extraidos:
                            linhas = []
                            for i, crit in enumerate(criterios_extraidos):
                                nome_c = st.session_state.get(f"qa_crit_nome_{i}", crit.get("nome",""))
                                nota_c = st.session_state.get(f"qa_crit_nota_{i}", 0.0)
                                peso_c = st.session_state.get(f"qa_crit_peso_{i}", crit.get("peso",""))
                                linhas.append(f"• {nome_c} | Nota: {nota_c} | Peso: {peso_c}")
                            criterios_str = "CRITÉRIOS:\n" + "\n".join(linhas) + "\n\n"

                        parecer_completo = (
                            f"{criterios_str}"
                            f"Acertos: {acertos}\n"
                            f"Erros: {erros}\n"
                            f"Melhorias: {melhorias}\n"
                            f"Obs: {obs}"
                        )

                        db.save_avaliacao({
                            "operador": op_av,
                            "data_chamada": periodo_av,
                            "tipo": "Base QA (.docx)",
                            "nota_final": nf,
                            "soft_skills": ss,
                            "tecnico": tec,
                            "saudacao": "", "empatia": "", "resolucao": "", "encerramento": "",
                            "parecer": parecer_completo,
                            "auditor": user.get("nome","Sistema"),
                        })
                        del st.session_state["qa_resultado"]
                        st.markdown('<div class="cx-success">✓ Avaliação salva no Google Sheets!</div>', unsafe_allow_html=True)
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))

            st.markdown('</div>', unsafe_allow_html=True)

        with col_hist:
            st.markdown('<div class="cx-card"><div style="font-size:13px;font-weight:600;margin-bottom:12px">Avaliações Registradas</div>', unsafe_allow_html=True)
            try:
                df_av2  = db.load_avaliacoes()
                qa_avs  = df_av2[df_av2["tipo"].str.contains("docx|QA", case=False, na=False)] if not df_av2.empty else pd.DataFrame()
                if qa_avs.empty:
                    st.markdown('<div style="text-align:center;padding:28px 0;color:#a09d9c;font-size:13px">📭 Nenhuma avaliação ainda.</div>', unsafe_allow_html=True)
                else:
                    for _, r in qa_avs.tail(10).iterrows():
                        nota    = r.get("nota_final","—")
                        cor     = score_color(nota)
                        cor_css = {"green":"#00e479","yellow":"#FFD700","red":"#ff6b6b","gray":"#a09d9c"}[cor]
                        st.markdown(f"""
                        <div style="padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.04)">
                          <div style="display:flex;justify-content:space-between;margin-bottom:3px">
                            <span style="font-size:13px;font-weight:600">{r.get("operador","—")}</span>
                            <span style="font-family:'Space Grotesk',sans-serif;font-size:14px;font-weight:700;color:{cor_css}">{nota}/100</span>
                          </div>
                          <div style="font-size:11px;color:#a09d9c">{r.get("data_chamada","—")} · {r.get("auditor","—")}</div>
                        </div>""", unsafe_allow_html=True)
            except Exception as e:
                st.error(str(e))
            st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────
# PÁGINA: CONFIGURAÇÕES
# ─────────────────────────────────────────
def page_config():
    section_title("Configurações")
    section_sub("Gerencie usuários e credenciais de acesso ao sistema.")

    tab_users, tab_sys = st.tabs(["👥  Gerenciar Usuários", "⚙  Sistema"])

    with tab_users:
        col_list, col_form = st.columns([2, 1])

        with col_list:
            st.markdown('<div class="cx-card"><div style="font-family:\'Space Grotesk\',sans-serif;font-size:15px;font-weight:600;margin-bottom:16px">Usuários Cadastrados</div>', unsafe_allow_html=True)
            try:
                df_users = db.load_usuarios()
                if df_users.empty:
                    st.markdown('<div style="text-align:center;padding:24px;color:#a09d9c">Nenhum usuário. Crie o primeiro ao lado.</div>', unsafe_allow_html=True)
                else:
                    for _, u in df_users.iterrows():
                        ativo  = str(u.get("ativo","true")).lower() != "false"
                        perfil = u.get("perfil","—")
                        badge_colors = {"admin":"red","gestor":"yellow","auditor":"green","operador":"gray"}
                        st.markdown(f"""
                        <div style="display:flex;align-items:center;justify-content:space-between;padding:12px 0;border-bottom:1px solid rgba(255,255,255,0.04)">
                          <div style="display:flex;align-items:center;gap:10px">
                            <div style="width:32px;height:32px;border-radius:50%;background:#2a2a2a;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;color:#FFD700">{"".join(w[0] for w in str(u.get("nome","?")).split()[:2]).upper()}</div>
                            <div>
                              <div style="font-size:14px;font-weight:600">{u.get("nome","—")}</div>
                              <div style="font-size:11px;color:#a09d9c">@{u.get("usuario","—")} · {perfil_label(perfil)}</div>
                            </div>
                          </div>
                          <div style="display:flex;align-items:center;gap:8px">
                            <span class="badge badge-{badge_colors.get(perfil,'gray')}">{perfil_label(perfil)}</span>
                            <span class="badge {'badge-green' if ativo else 'badge-red'}">{'Ativo' if ativo else 'Inativo'}</span>
                          </div>
                        </div>""", unsafe_allow_html=True)

                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button("Desativar" if ativo else "Ativar", key=f"tog_{u.get('id')}"):
                                session = st.session_state.user or {}
                                if u.get("usuario") == session.get("usuario"):
                                    st.error("Você não pode desativar o próprio usuário.")
                                else:
                                    row = u.to_dict()
                                    row["ativo"] = "false" if ativo else "true"
                                    db.save_usuario(row)
                                    st.rerun()
                        with col_b:
                            if st.button("✕ Excluir", key=f"del_{u.get('id')}"):
                                session = st.session_state.user or {}
                                if u.get("usuario") == session.get("usuario"):
                                    st.error("Você não pode excluir o próprio usuário.")
                                else:
                                    db.delete_usuario(u.get("id"))
                                    st.rerun()
            except Exception as e:
                st.error(str(e))
            st.markdown('</div>', unsafe_allow_html=True)

        with col_form:
            st.markdown('<div class="cx-card" style="position:sticky;top:80px"><div style="font-family:\'Space Grotesk\',sans-serif;font-size:15px;font-weight:600;margin-bottom:16px">Novo Usuário</div>', unsafe_allow_html=True)
            f_nome   = st.text_input("Nome Completo *",    key="f_nome")
            f_user   = st.text_input("Usuário de Login *", key="f_user")
            f_pass   = st.text_input("Senha *",            key="f_pass", type="password")
            f_perfil = st.selectbox("Perfil", ["admin","gestor","auditor","operador"], key="f_perfil")

            if st.button("Salvar Usuário", use_container_width=True, key="btn_criar_user"):
                if not f_nome or not f_user or not f_pass:
                    st.markdown('<div class="cx-error">Todos os campos são obrigatórios.</div>', unsafe_allow_html=True)
                else:
                    try:
                        df_u = db.load_usuarios()
                        if not df_u.empty and f_user.lower() in df_u["usuario"].str.lower().values:
                            st.markdown('<div class="cx-error">Este usuário já existe.</div>', unsafe_allow_html=True)
                        else:
                            db.save_usuario({"nome":f_nome,"usuario":f_user.lower(),"senha":f_pass,"perfil":f_perfil,"ativo":"true"})
                            st.markdown('<div class="cx-success">✓ Usuário criado no Google Sheets!</div>', unsafe_allow_html=True)
                            st.rerun()
                    except Exception as e:
                        st.error(str(e))
            st.markdown('</div>', unsafe_allow_html=True)

    with tab_sys:
        st.markdown("""
        <div class="cx-card">
          <div style="font-family:'Space Grotesk',sans-serif;font-size:15px;font-weight:600;margin-bottom:16px">Conexão com Google Sheets</div>
          <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px">
            <div style="width:36px;height:36px;border-radius:4px;background:rgba(0,228,121,0.1);border:1px solid rgba(0,228,121,0.25);display:flex;align-items:center;justify-content:center;font-size:18px">✓</div>
            <div>
              <div style="font-size:13px;font-weight:600;color:#00e479">Conectado ao Google Sheets</div>
              <div style="font-size:11px;color:#a09d9c">Salvamento automático ativo</div>
            </div>
          </div>
          <div style="font-size:13px;color:#a09d9c;line-height:1.7">
            Abas sincronizadas:<br>
            ✓ usuarios &nbsp; ✓ operadores &nbsp; ✓ avaliacoes &nbsp; ✓ feedbacks &nbsp; ✓ banco_erros
          </div>
        </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# ROTEADOR PRINCIPAL
# ─────────────────────────────────────────
def main():
    if not st.session_state.logged_in:
        page_login()
        return

    render_sidebar()

    page = st.session_state.page
    routes = {
        "dashboard":   page_dashboard,
        "operadores":  page_operadores,
        "avaliacoes":  page_avaliacoes,
        "bancoerros":  page_bancoerros,
        "feedback_op": page_feedback_op,
        "ia":          page_ia,
        "base_qa":     page_base_qa,
        "config":      page_config,
    }
    fn = routes.get(page, page_dashboard)
    fn()


if __name__ == "__main__":
    main()
