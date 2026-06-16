import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date
from pathlib import Path
 
# ─── Configuração da página ───────────────────────────────────────────────────
st.set_page_config(
    page_title="Leal — CX",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded",
)
 
# ─── CSS: Tema Galáxia ────────────────────────────────────────────────────────
GALAXY_CSS = """
<style>
/* === BASE GALÁXIA === */
html, body, [data-testid="stApp"], [data-testid="stAppViewContainer"] {
    background-color: #05050A !important;
    color: #E2E8F0 !important;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0B132B 0%, #05050A 100%) !important;
    border-right: 1px solid #1F3A52 !important;
}
[data-testid="stSidebar"] * { color: #E2E8F0 !important; }
 
/* === BOKEH / ESTRELAS (pseudo-elementos no body) === */
body::before {
    content: '';
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    background-image:
        radial-gradient(circle, rgba(76,201,240,0.18) 1px, transparent 1px),
        radial-gradient(circle, rgba(226,232,240,0.10) 1px, transparent 1px),
        radial-gradient(circle, rgba(76,201,240,0.08) 1px, transparent 1px);
    background-size: 120px 120px, 80px 80px, 200px 200px;
    background-position: 10px 10px, 40px 60px, 90px 30px;
    pointer-events: none;
    z-index: 0;
    animation: twinkle 8s ease-in-out infinite alternate;
}
@keyframes twinkle {
    0%   { opacity: 0.6; }
    50%  { opacity: 1.0; }
    100% { opacity: 0.6; }
}
 
/* === CARDS / CONTAINERS === */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #0B132B, #1C1A27) !important;
    border: 1px solid #1F3A52 !important;
    border-radius: 12px !important;
    padding: 16px !important;
}
[data-testid="stMetricLabel"] { color: #4CC9F0 !important; font-size: 12px !important; }
[data-testid="stMetricValue"] { color: #E2E8F0 !important; }
[data-testid="stMetricDelta"] { color: #4CC9F0 !important; }
 
div[data-testid="stBlock"], section[data-testid="stSidebar"] > div {
    background: transparent !important;
}
 
/* === INPUTS === */
input, textarea, select,
[data-testid="stTextInput"] input,
[data-testid="stSelectbox"] select,
[data-testid="stNumberInput"] input {
    background: #0B132B !important;
    border: 1px solid #1F3A52 !important;
    color: #E2E8F0 !important;
    border-radius: 8px !important;
}
input:focus, textarea:focus {
    border-color: #4CC9F0 !important;
    box-shadow: 0 0 8px rgba(76,201,240,0.3) !important;
}
 
/* === BOTÕES === */
.stButton > button {
    background: linear-gradient(135deg, #1F3A52, #0B132B) !important;
    color: #4CC9F0 !important;
    border: 1px solid #4CC9F0 !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: #4CC9F0 !important;
    color: #05050A !important;
    box-shadow: 0 0 16px rgba(76,201,240,0.5) !important;
}
 
/* === TABELAS === */
[data-testid="stDataFrame"] table,
.stDataFrame table {
    background: #0B132B !important;
    color: #E2E8F0 !important;
    border: 1px solid #1F3A52 !important;
}
[data-testid="stDataFrame"] thead tr th {
    background: #1C1A27 !important;
    color: #4CC9F0 !important;
    border-bottom: 1px solid #1F3A52 !important;
}
[data-testid="stDataFrame"] tbody tr:nth-child(even) td {
    background: rgba(31,58,82,0.3) !important;
}
 
/* === TABS === */
[data-testid="stTabs"] [data-baseweb="tab"] {
    color: #E2E8F0 !important;
    border-bottom: 2px solid transparent !important;
}
[data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"] {
    color: #4CC9F0 !important;
    border-bottom: 2px solid #4CC9F0 !important;
}
[data-testid="stTabsContent"] {
    background: transparent !important;
}
 
/* === DIVIDER === */
hr { border-color: #1F3A52 !important; }
 
/* === SELECTBOX / MULTISELECT === */
[data-baseweb="select"] > div {
    background: #0B132B !important;
    border: 1px solid #1F3A52 !important;
    color: #E2E8F0 !important;
}
[data-baseweb="popover"] { background: #0B132B !important; border: 1px solid #1F3A52 !important; }
[data-baseweb="menu"] { background: #0B132B !important; }
[data-baseweb="option"]:hover { background: #1F3A52 !important; }
 
/* === ALERTS / EXPANDER === */
[data-testid="stExpander"] {
    background: #0B132B !important;
    border: 1px solid #1F3A52 !important;
    border-radius: 8px !important;
}
.stAlert { border-radius: 8px !important; }
 
/* === PROGRESS BAR === */
[data-testid="stProgressBar"] > div > div {
    background: linear-gradient(90deg, #1F3A52, #4CC9F0) !important;
}
 
/* === SCROLLBAR === */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #05050A; }
::-webkit-scrollbar-thumb { background: #1F3A52; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #4CC9F0; }
 
/* === HEADINGS === */
h1 { color: #4CC9F0 !important; font-size: 28px !important; }
h2 { color: #E2E8F0 !important; }
h3 { color: #4CC9F0 !important; }
 
/* === LOGIN CARD === */
.login-card {
    background: linear-gradient(135deg, #0B132B, #1C1A27);
    border: 1px solid #1F3A52;
    border-radius: 16px;
    padding: 2rem;
    max-width: 420px;
    margin: 4rem auto;
    box-shadow: 0 0 40px rgba(76,201,240,0.12);
}
 
/* === BADGE FAIXA === */
.badge-meta {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
}
 
/* === SIDEBAR LOGO === */
.sidebar-logo {
    text-align: center;
    padding: 1rem 0 1.5rem;
    border-bottom: 1px solid #1F3A52;
    margin-bottom: 1rem;
}
</style>
"""
 
st.markdown(GALAXY_CSS, unsafe_allow_html=True)
 
# ─── Constantes ───────────────────────────────────────────────────────────────
DATA_DIR   = Path("data")
DATA_DIR.mkdir(exist_ok=True)
OPS_FILE   = DATA_DIR / "operadores.json"
EVALS_FILE = DATA_DIR / "avaliacoes.json"
FAIXAS_FILE = DATA_DIR / "faixas.json"
USERS_FILE = DATA_DIR / "usuarios.json"
 
NIVEIS = {
    "comandante": "Comandante 🌌",
    "copiloto":   "Copiloto 🚀",
    "observador": "Observador Estelar 🔭",
    "tripulacao": "Tripulação ⭐",
}
 
MESES_LABEL = {str(i): f"Mês {i:02d}" for i in range(1, 13)}
CICLOS = ["Ciclo 1", "Ciclo 2", "Ciclo 3", "Ciclo 4", "Ciclo 5"]
 
# ─── Persistência JSON ────────────────────────────────────────────────────────
def load_json(path, default):
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default
 
def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
 
def load_operadores():
    return load_json(OPS_FILE, [])
 
def save_operadores(data):
    save_json(OPS_FILE, data)
 
def load_avaliacoes():
    return load_json(EVALS_FILE, [])
 
def save_avaliacoes(data):
    save_json(EVALS_FILE, data)
 
def load_faixas():
    default = [
        {"id": "f1", "desc": "Abaixo da meta",    "min": 0,  "max": 79.9, "bonus": 0},
        {"id": "f2", "desc": "Faixa Bronze",       "min": 80, "max": 84.9, "bonus": 75},
        {"id": "f3", "desc": "Faixa Prata",        "min": 85, "max": 89.9, "bonus": 150},
        {"id": "f4", "desc": "Faixa Ouro",         "min": 90, "max": 94.9, "bonus": 250},
        {"id": "f5", "desc": "Faixa Diamante",     "min": 95, "max": 100,  "bonus": 400},
    ]
    return load_json(FAIXAS_FILE, default)
 
def save_faixas(data):
    save_json(FAIXAS_FILE, data)
 
def load_usuarios():
    default = [
        {"login": "comandante", "senha": "leal2024", "nivel": "comandante", "nome": "Gerente de Qualidade", "op_id": None},
        {"login": "copiloto",   "senha": "leal2024", "nivel": "copiloto",   "nome": "Coordenadora",         "op_id": None},
        {"login": "observador", "senha": "leal2024", "nivel": "observador", "nome": "Gerente",               "op_id": None},
    ]
    return load_json(USERS_FILE, default)
 
def save_usuarios(data):
    save_json(USERS_FILE, data)
 
# ─── Helpers de negócio ───────────────────────────────────────────────────────
def avg_of(values):
    vals = [float(v) for v in values if v not in (None, "", 0) and str(v).strip() != ""]
    return round(sum(vals) / len(vals), 2) if vals else None
 
def eval_int(e):
    return avg_of([e.get("cord"), e.get("res"), e.get("agi"), e.get("script")])
 
def eval_final(e, pesos):
    mp = e.get("mp")
    iv = eval_int(e)
    if mp in (None, "") and iv is None:
        return None
    pm = pesos.get("mp", 50) / 100
    pi = pesos.get("int", 50) / 100
    mp_f = float(mp) if mp not in (None, "") else None
    if mp_f is not None and iv is not None:
        return round((mp_f / 10 * pm + iv / 10 * pi) * 100, 2)
    if mp_f is not None:
        return round(mp_f / 10 * 100, 2)
    return round(iv / 10 * 100, 2)
 
def get_faixa(nota, faixas):
    if nota is None:
        return None
    for f in sorted(faixas, key=lambda x: x["min"]):
        if f["min"] <= nota <= f["max"]:
            return f
    return None
 
def tenure(adm_str):
    if not adm_str:
        return "—"
    try:
        adm = datetime.strptime(adm_str, "%Y-%m-%d").date()
        delta = date.today() - adm
        months = int(delta.days / 30.44)
        if months < 0:
            months = 0
        if months < 12:
            return f"{months}m"
        return f"{months // 12}a {months % 12}m"
    except Exception:
        return "—"
 
def score_color(v, is_final=False):
    if v is None:
        return "#888"
    if is_final:
        return "#4CC9F0" if v >= 90 else "#FAC775" if v >= 80 else "#F09595"
    return "#4CC9F0" if v >= 8 else "#FAC775" if v >= 6 else "#F09595"
 
def badge_faixa(fx):
    if not fx:
        return "<span style='color:#888'>—</span>"
    bonus = fx["bonus"]
    if bonus == 0:
        cor = "#F09595"; bg = "rgba(240,149,149,0.15)"
    elif bonus < 150:
        cor = "#FAC775"; bg = "rgba(250,199,117,0.15)"
    elif bonus < 300:
        cor = "#4CC9F0"; bg = "rgba(76,201,240,0.15)"
    else:
        cor = "#9FE1CB"; bg = "rgba(159,225,203,0.15)"
    return f"<span class='badge-meta' style='color:{cor};background:{bg};border:1px solid {cor}'>{fx['desc']} · R$ {fx['bonus']:.2f}</span>"
 
def pesos_default():
    return {"mp": 50, "int": 50}
 
# ─── Sessão ───────────────────────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None
 
if "pesos" not in st.session_state:
    st.session_state.pesos = pesos_default()
 
# ═══════════════════════════════════════════════════════════════════════════════
# TELA DE LOGIN
# ═══════════════════════════════════════════════════════════════════════════════
def tela_login():
    st.markdown("""
    <div style='text-align:center; padding-top: 2rem;'>
        <div style='font-size:52px; margin-bottom:8px;'>🌌</div>
        <h1 style='font-size:32px; color:#4CC9F0; margin-bottom:4px;'>LEAL — CX</h1>
        <p style='color:#1F3A52; font-size:14px; letter-spacing:0.1em;'>SISTEMA DE GESTÃO DE QUALIDADE</p>
        <p style='color:#E2E8F0; font-size:13px; margin-top:4px;'>Operação Mercado Pago</p>
    </div>
    """, unsafe_allow_html=True)
 
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<div style='background:linear-gradient(135deg,#0B132B,#1C1A27);border:1px solid #1F3A52;border-radius:16px;padding:2rem;box-shadow:0 0 40px rgba(76,201,240,0.12);'>", unsafe_allow_html=True)
        st.markdown("<p style='color:#4CC9F0;font-size:13px;letter-spacing:0.08em;margin-bottom:1rem;'>ACESSO À MISSÃO</p>", unsafe_allow_html=True)
        login_input = st.text_input("Login", placeholder="Seu identificador", key="login_field")
        senha_input = st.text_input("Senha", type="password", placeholder="••••••••", key="senha_field")
        entrar = st.button("🚀 Iniciar missão", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
 
        if entrar:
            usuarios = load_usuarios()
            user = next((u for u in usuarios if u["login"] == login_input and u["senha"] == senha_input), None)
            if user:
                st.session_state.logged_in = True
                st.session_state.user = user
                st.rerun()
            else:
                st.error("Login ou senha incorretos. Tente novamente.")
 
    st.markdown("""
    <div style='text-align:center; margin-top:3rem; color:#1F3A52; font-size:12px;'>
        Leal — CX · Sistema de Qualidade · Operação Mercado Pago
    </div>
    """, unsafe_allow_html=True)
 
# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
def render_sidebar(user):
    with st.sidebar:
        st.markdown(f"""
        <div class='sidebar-logo'>
            <div style='font-size:36px;'>🌌</div>
            <div style='font-size:18px; font-weight:700; color:#4CC9F0;'>LEAL — CX</div>
            <div style='font-size:11px; color:#1F3A52; letter-spacing:0.08em;'>GESTÃO DE QUALIDADE</div>
        </div>
        <div style='background:rgba(76,201,240,0.08); border:1px solid #1F3A52; border-radius:10px; padding:12px; margin-bottom:1rem;'>
            <div style='font-size:12px; color:#4CC9F0;'>CONECTADO COMO</div>
            <div style='font-size:14px; font-weight:600; color:#E2E8F0; margin-top:2px;'>{user["nome"]}</div>
            <div style='font-size:12px; color:#1F3A52; margin-top:2px;'>{NIVEIS.get(user["nivel"], user["nivel"])}</div>
        </div>
        """, unsafe_allow_html=True)
 
        nivel = user["nivel"]
 
        if nivel in ("comandante", "copiloto", "observador"):
            st.markdown("**Navegação**")
            pages = [
                ("🏠", "Dashboard"),
                ("👥", "Operadores"),
                ("📋", "Avaliações"),
                ("🏆", "Metas"),
                ("📈", "Evolução"),
            ]
            if nivel == "comandante":
                pages += [("⚙️", "Configurações")]
 
            if "page" not in st.session_state:
                st.session_state.page = "Dashboard"
 
            for icon, page in pages:
                active = "🔵 " if st.session_state.page == page else ""
                if st.button(f"{icon} {active}{page}", key=f"nav_{page}", use_container_width=True):
                    st.session_state.page = page
                    st.rerun()
 
        st.markdown("---")
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.rerun()
 
# ═══════════════════════════════════════════════════════════════════════════════
# PÁGINA: DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
def pagina_dashboard(user, readonly=False):
    st.markdown("# 🌌 Dashboard")
    st.markdown(f"<p style='color:#4CC9F0;font-size:13px;'>Atualizado em {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>", unsafe_allow_html=True)
 
    operadores = load_operadores()
    avaliacoes = load_avaliacoes()
    faixas     = load_faixas()
    pesos      = st.session_state.pesos
 
    ativos = [o for o in operadores if o.get("status") == "Ativo"]
 
    # Métricas do topo
    all_mps    = [float(e["mp"]) for e in avaliacoes if e.get("mp") not in (None, "")]
    all_finals = [eval_final(e, pesos) for e in avaliacoes]
    all_finals = [v for v in all_finals if v is not None]
 
    avg_mp  = round(sum(all_mps) / len(all_mps), 2) if all_mps else None
    avg_fin = round(sum(all_finals) / len(all_finals), 2) if all_finals else None
 
    # Total de bonificação: última avaliação de cada operador ativo
    total_bonus = 0
    for op in ativos:
        op_evals = sorted([e for e in avaliacoes if e["op_id"] == op["id"]], key=lambda x: (x.get("mes",""), x.get("ciclo","")), reverse=True)
        if op_evals:
            fn = eval_final(op_evals[0], pesos)
            fx = get_faixa(fn, faixas)
            total_bonus += fx["bonus"] if fx else 0
 
    abaixo_80 = sum(
        1 for op in ativos
        if (lambda ev: ev is not None and eval_final(ev, pesos) is not None and eval_final(ev, pesos) < 80)(
            next((e for e in sorted([e for e in avaliacoes if e["op_id"] == op["id"]],
                                     key=lambda x:(x.get("mes",""),x.get("ciclo","")),reverse=True)), None)
        )
    )
 
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("👥 Operadores ativos", len(ativos), f"de {len(operadores)}")
    c2.metric("📊 Avaliações", len(avaliacoes))
    c3.metric("🎯 Média MP", f"{avg_mp:.1f}" if avg_mp else "—")
    c4.metric("🏆 Nota final média", f"{avg_fin:.1f}%" if avg_fin else "—")
    c5.metric("⚠️ Abaixo de 80%", abaixo_80)
    c6.metric("💰 Total bonificação", f"R$ {total_bonus:.2f}")
 
    st.markdown("---")
 
    # Seletor de mês
    meses_disponíveis = sorted(set(e.get("mes","") for e in avaliacoes if e.get("mes")), reverse=True)
    col_sel, _ = st.columns([2, 4])
    with col_sel:
        mes_sel = st.selectbox("📅 Filtrar por mês", ["Todos"] + meses_disponíveis, key="dash_mes")
 
    # Tabela resumo da equipe
    st.markdown("### 🧑‍🚀 Resumo da equipe")
    rows = []
    for op in ativos:
        op_evals = [e for e in avaliacoes if e["op_id"] == op["id"]]
        if mes_sel != "Todos":
            op_evals = [e for e in op_evals if e.get("mes") == mes_sel]
        op_evals_sorted = sorted(op_evals, key=lambda x: x.get("ciclo",""), reverse=True)
        last = op_evals_sorted[0] if op_evals_sorted else None
 
        mp_val  = float(last["mp"]) if last and last.get("mp") not in (None,"") else None
        int_val = eval_int(last) if last else None
        fin_val = eval_final(last, pesos) if last else None
        fx      = get_faixa(fin_val, faixas)
 
        rows.append({
            "Operador":    op["nome"],
            "Cargo":       op.get("cargo","—"),
            "Tempo de casa": tenure(op.get("adm")),
            "Nota MP":     f"{mp_val:.1f}" if mp_val is not None else "—",
            "Média interna": f"{int_val:.1f}" if int_val is not None else "—",
            "Nota final":  f"{fin_val:.1f}%" if fin_val is not None else "—",
            "Faixa":       fx["desc"] if fx else "—",
            "Bônus":       f"R$ {fx['bonus']:.2f}" if fx else "R$ 0,00",
        })
 
    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum dado para exibir. Cadastre operadores e avaliações.")
 
    # Médias por ciclo no mês selecionado
    if mes_sel != "Todos":
        st.markdown(f"### 📊 Médias por ciclo — {mes_sel}")
        ciclo_data = []
        for ciclo in CICLOS:
            ciclo_evals = [e for e in avaliacoes if e.get("mes") == mes_sel and e.get("ciclo") == ciclo]
            if not ciclo_evals:
                continue
            fins = [eval_final(e, pesos) for e in ciclo_evals]
            fins = [v for v in fins if v is not None]
            mps  = [float(e["mp"]) for e in ciclo_evals if e.get("mp") not in (None,"")]
            ciclo_data.append({
                "Ciclo":      ciclo,
                "Média MP":   round(sum(mps)/len(mps),2) if mps else None,
                "Nota final": round(sum(fins)/len(fins),2) if fins else None,
                "Operadores avaliados": len(ciclo_evals),
            })
        if ciclo_data:
            df_c = pd.DataFrame(ciclo_data)
            st.dataframe(df_c, use_container_width=True, hide_index=True)
 
            import json as _json
            labels = [r["Ciclo"] for r in ciclo_data]
            finals = [r["Nota final"] or 0 for r in ciclo_data]
            chart_data = pd.DataFrame({"Ciclo": labels, "Nota Final (%)": finals})
            st.line_chart(chart_data.set_index("Ciclo"), color="#4CC9F0")
 
# ═══════════════════════════════════════════════════════════════════════════════
# PÁGINA: OPERADORES
# ═══════════════════════════════════════════════════════════════════════════════
def pagina_operadores(user, readonly=False):
    st.markdown("# 👥 Operadores")
 
    operadores = load_operadores()
    pesos      = st.session_state.pesos
    avaliacoes = load_avaliacoes()
    faixas     = load_faixas()
 
    if not readonly:
        with st.expander("➕ Cadastrar novo operador", expanded=False):
            with st.form("form_op"):
                c1, c2 = st.columns(2)
                nome   = c1.text_input("Nome completo")
                cargo  = c2.selectbox("Cargo", ["Atendente","Atendente Sênior","Analista","Especialista"])
                c3, c4 = st.columns(2)
                adm    = c3.date_input("Data de admissão", value=date.today())
                status = c4.selectbox("Status", ["Ativo","Afastado","Desligado"])
                notas  = st.text_area("Observações gerais", height=80)
                # Criar login de tripulação
                st.markdown("**Login do operador (Tripulação)**")
                c5, c6 = st.columns(2)
                login_op = c5.text_input("Login", placeholder="Ex.: ana.silva")
                senha_op = c6.text_input("Senha", placeholder="Ex.: cx2024", type="password")
                submit = st.form_submit_button("🚀 Salvar operador")
 
            if submit:
                if not nome.strip():
                    st.error("Informe o nome do operador.")
                else:
                    op_id = f"op_{int(datetime.now().timestamp()*1000)}"
                    op = {
                        "id": op_id, "nome": nome.strip(), "cargo": cargo,
                        "adm": adm.strftime("%Y-%m-%d"), "status": status, "notas": notas,
                    }
                    operadores.append(op)
                    save_operadores(operadores)
                    # Criar usuário de tripulação se informado login
                    if login_op.strip() and senha_op.strip():
                        usuarios = load_usuarios()
                        if any(u["login"] == login_op.strip() for u in usuarios):
                            st.warning(f"Login '{login_op}' já existe. Operador salvo, mas login não criado.")
                        else:
                            usuarios.append({
                                "login": login_op.strip(), "senha": senha_op.strip(),
                                "nivel": "tripulacao", "nome": nome.strip(), "op_id": op_id
                            })
                            save_usuarios(usuarios)
                    st.success(f"✅ Operador {nome} cadastrado com sucesso!")
                    st.rerun()
 
    st.markdown("---")
    # Filtros
    c1, c2 = st.columns([3, 1])
    busca   = c1.text_input("🔍 Buscar operador", placeholder="Nome...")
    filtro  = c2.selectbox("Status", ["Todos","Ativo","Afastado","Desligado"], key="op_filtro")
 
    lista = [o for o in operadores
             if (not busca or busca.lower() in o["nome"].lower())
             and (filtro == "Todos" or o.get("status") == filtro)]
 
    if not lista:
        st.info("Nenhum operador encontrado.")
        return
 
    for op in lista:
        op_evals = sorted([e for e in avaliacoes if e["op_id"] == op["id"]],
                          key=lambda x:(x.get("mes",""), x.get("ciclo","")), reverse=True)
        last = op_evals[0] if op_evals else None
        fn   = eval_final(last, pesos) if last else None
        fx   = get_faixa(fn, faixas)
 
        with st.expander(f"🧑‍🚀 {op['nome']} — {op.get('cargo','—')} · {tenure(op.get('adm'))} de empresa"):
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Status", op.get("status","—"))
            c2.metric("Tempo de casa", tenure(op.get("adm")))
            if last:
                mp_v = float(last["mp"]) if last.get("mp") not in (None,"") else None
                c3.metric("Nota MP (última)", f"{mp_v:.1f}" if mp_v else "—")
                c4.metric("Nota final", f"{fn:.1f}%" if fn else "—")
            if op.get("notas"):
                st.markdown(f"*Observações:* {op['notas']}")
 
            if fn is not None:
                pct = min(100, max(0, fn))
                cor = "#4CC9F0" if fn >= 90 else "#FAC775" if fn >= 80 else "#F09595"
                st.markdown(f"**Progresso na meta — {fn:.1f}%**")
                st.progress(pct / 100)
                st.markdown(badge_faixa(fx), unsafe_allow_html=True)
 
                # Quanto falta para próxima faixa?
                faixas_sorted = sorted(faixas, key=lambda x: x["min"])
                proxima = next((f for f in faixas_sorted if f["min"] > fn), None)
                if proxima:
                    falta = round(proxima["min"] - fn, 2)
                    st.markdown(f"<p style='color:#4CC9F0;font-size:13px;'>⭐ Faltam <strong>{falta} pontos</strong> para {proxima['desc']} (R$ {proxima['bonus']:.2f})</p>", unsafe_allow_html=True)
 
            if not readonly:
                col_e, col_d = st.columns([1, 5])
                with col_e:
                    if st.button("🗑️ Excluir", key=f"del_op_{op['id']}"):
                        operadores = [o for o in operadores if o["id"] != op["id"]]
                        save_operadores(operadores)
                        st.success("Operador removido.")
                        st.rerun()
 
# ═══════════════════════════════════════════════════════════════════════════════
# PÁGINA: AVALIAÇÕES
# ═══════════════════════════════════════════════════════════════════════════════
def pagina_avaliacoes(user, readonly=False):
    st.markdown("# 📋 Avaliações")
 
    operadores = load_operadores()
    avaliacoes = load_avaliacoes()
    pesos      = st.session_state.pesos
 
    ativos = [o for o in operadores if o.get("status") == "Ativo"]
 
    if not readonly and ativos:
        with st.expander("➕ Registrar nova avaliação", expanded=False):
            with st.form("form_eval"):
                c1, c2, c3 = st.columns(3)
                op_names = {o["id"]: o["nome"] for o in ativos}
                op_sel_nome = c1.selectbox("Operador", list(op_names.values()))
                op_sel_id   = next(k for k, v in op_names.items() if v == op_sel_nome)
                mes_sel     = c2.selectbox("Mês de referência", list(MESES_LABEL.values()))
                ciclo_sel   = c3.selectbox("Ciclo / Semana", CICLOS)
 
                st.markdown("**Notas do Mercado Pago**")
                c4, c5, c6, c7 = st.columns(4)
                mp_val   = c4.number_input("Nota MP (0–10)", 0.0, 10.0, step=0.1, format="%.1f")
                tma_val  = c5.number_input("TMA (min)", 0.0, 999.0, step=0.1, format="%.1f")
                fcr_val  = c6.number_input("FCR (%)", 0.0, 100.0, step=0.1, format="%.1f")
                csat_val = c7.number_input("CSAT (0–10)", 0.0, 10.0, step=0.1, format="%.1f")
 
                st.markdown("**Avaliação interna (0–10)**")
                c8, c9, c10, c11 = st.columns(4)
                cord_val   = c8.number_input("Cordialidade",      0.0, 10.0, step=0.1, format="%.1f")
                res_val    = c9.number_input("Resolução",         0.0, 10.0, step=0.1, format="%.1f")
                agi_val    = c10.number_input("Agilidade",        0.0, 10.0, step=0.1, format="%.1f")
                script_val = c11.number_input("Aderência script", 0.0, 10.0, step=0.1, format="%.1f")
 
                c12, c13 = st.columns(2)
                feedback_val = c12.text_area("Pontos de melhoria", height=90)
                positivos_val= c13.text_area("Pontos positivos",   height=90)
                acao_val = st.text_input("Plano de ação / Desenvolvimento")
 
                submit = st.form_submit_button("💾 Salvar avaliação")
 
            if submit:
                ev = {
                    "id":      f"ev_{int(datetime.now().timestamp()*1000)}",
                    "op_id":   op_sel_id,
                    "mes":     mes_sel,
                    "ciclo":   ciclo_sel,
                    "mp":      mp_val,
                    "tma":     tma_val,
                    "fcr":     fcr_val,
                    "csat":    csat_val,
                    "cord":    cord_val,
                    "res":     res_val,
                    "agi":     agi_val,
                    "script":  script_val,
                    "feed":    feedback_val,
                    "pos":     positivos_val,
                    "acao":    acao_val,
                    "criado":  datetime.now().isoformat(),
                }
                avaliacoes.append(ev)
                save_avaliacoes(avaliacoes)
                st.success(f"✅ Avaliação de {op_sel_nome} — {mes_sel} / {ciclo_sel} salva!")
                st.rerun()
 
    st.markdown("---")
 
    # Filtros
    c1, c2, c3 = st.columns(3)
    op_filtro  = c1.selectbox("Operador", ["Todos"] + [o["nome"] for o in operadores], key="eval_op")
    mes_filtro = c2.selectbox("Mês", ["Todos"] + sorted(set(e.get("mes","") for e in avaliacoes if e.get("mes")), reverse=True), key="eval_mes")
    ciclo_filtro = c3.selectbox("Ciclo", ["Todos"] + CICLOS, key="eval_ciclo")
 
    lista = avaliacoes
    if op_filtro != "Todos":
        op_id = next((o["id"] for o in operadores if o["nome"] == op_filtro), None)
        lista = [e for e in lista if e["op_id"] == op_id]
    if mes_filtro != "Todos":
        lista = [e for e in lista if e.get("mes") == mes_filtro]
    if ciclo_filtro != "Todos":
        lista = [e for e in lista if e.get("ciclo") == ciclo_filtro]
 
    lista = sorted(lista, key=lambda x: (x.get("mes",""), x.get("ciclo","")), reverse=True)
 
    if not lista:
        st.info("Nenhuma avaliação encontrada para os filtros selecionados.")
        return
 
    rows = []
    for e in lista:
        op = next((o for o in operadores if o["id"] == e["op_id"]), {})
        iv = eval_int(e)
        fn = eval_final(e, pesos)
        rows.append({
            "Operador":    op.get("nome","—"),
            "Mês":         e.get("mes","—"),
            "Ciclo":       e.get("ciclo","—"),
            "MP":          f"{float(e['mp']):.1f}"   if e.get("mp") not in (None,"") else "—",
            "TMA":         f"{float(e['tma']):.1f}"  if e.get("tma") else "—",
            "FCR":         f"{float(e['fcr']):.1f}%" if e.get("fcr") else "—",
            "CSAT":        f"{float(e['csat']):.1f}" if e.get("csat") else "—",
            "Cord.":       f"{float(e['cord']):.1f}" if e.get("cord") else "—",
            "Resol.":      f"{float(e['res']):.1f}"  if e.get("res") else "—",
            "Agil.":       f"{float(e['agi']):.1f}"  if e.get("agi") else "—",
            "Script":      f"{float(e['script']):.1f}" if e.get("script") else "—",
            "Média int.":  f"{iv:.1f}"  if iv  is not None else "—",
            "Nota final":  f"{fn:.1f}%" if fn  is not None else "—",
            "Plano de ação": e.get("acao","—"),
        })
 
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)
 
    # Exportar CSV
    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ Exportar CSV",
        data=csv,
        file_name=f"leal_cx_avaliacoes_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )
 
# ═══════════════════════════════════════════════════════════════════════════════
# PÁGINA: METAS
# ═══════════════════════════════════════════════════════════════════════════════
def pagina_metas(user, readonly=False):
    st.markdown("# 🏆 Metas e Bonificações")
 
    faixas     = load_faixas()
    operadores = load_operadores()
    avaliacoes = load_avaliacoes()
    pesos      = st.session_state.pesos
 
    c_pesos, c_faixas = st.columns([1, 2])
 
    with c_pesos:
        st.markdown("### ⚖️ Pesos da nota final")
        if not readonly:
            pm  = st.slider("Peso Nota MP (%)",      0, 100, pesos.get("mp", 50), step=5)
            pi  = st.slider("Peso Nota interna (%)", 0, 100, pesos.get("int", 50), step=5)
            if pm + pi != 100:
                st.warning(f"Soma atual: {pm+pi}% (deve ser 100%)")
            else:
                st.session_state.pesos = {"mp": pm, "int": pi}
                st.success("Pesos: OK ✓")
        else:
            st.markdown(f"- Nota MP: **{pesos['mp']}%**")
            st.markdown(f"- Nota interna: **{pesos['int']}%**")
 
    with c_faixas:
        st.markdown("### 🎯 Faixas de bonificação")
        for i, f in enumerate(sorted(faixas, key=lambda x: x["min"])):
            cc1, cc2, cc3, cc4 = st.columns([2, 1, 1, 1])
            cc1.markdown(f"**{f['desc']}**")
            cc2.markdown(f"{f['min']}% – {f['max']}%")
            cc3.markdown(f"R$ {f['bonus']:.2f}")
            if not readonly:
                if cc4.button("🗑️", key=f"del_faixa_{f['id']}"):
                    faixas = [x for x in faixas if x["id"] != f["id"]]
                    save_faixas(faixas)
                    st.rerun()
 
        if not readonly:
            st.markdown("---")
            with st.form("form_faixa"):
                c1, c2, c3, c4 = st.columns(4)
                f_desc  = c1.text_input("Descrição", placeholder="Ex.: Faixa Ouro")
                f_min   = c2.number_input("Nota mínima (%)", 0.0, 100.0, step=0.1)
                f_max   = c3.number_input("Nota máxima (%)", 0.0, 100.0, step=0.1)
                f_bonus = c4.number_input("Bônus (R$)", 0.0, step=0.01)
                if st.form_submit_button("➕ Adicionar faixa"):
                    if not f_desc.strip():
                        st.error("Informe a descrição.")
                    elif f_min > f_max:
                        st.error("Nota mínima deve ser menor que a máxima.")
                    else:
                        faixas.append({"id": f"f_{int(datetime.now().timestamp()*1000)}", "desc": f_desc, "min": f_min, "max": f_max, "bonus": f_bonus})
                        save_faixas(faixas)
                        st.success("Faixa adicionada!")
                        st.rerun()
 
    st.markdown("---")
    st.markdown("### 📊 Resultado do mês mais recente")
 
    meses = sorted(set(e.get("mes","") for e in avaliacoes if e.get("mes")), reverse=True)
    col_m, _ = st.columns([2, 4])
    mes_sel = col_m.selectbox("Mês", meses if meses else ["—"], key="metas_mes")
 
    ativos = [o for o in operadores if o.get("status") == "Ativo"]
    rows = []
    total_bonus = 0
    for op in ativos:
        op_evals = sorted(
            [e for e in avaliacoes if e["op_id"] == op["id"] and e.get("mes") == mes_sel],
            key=lambda x: x.get("ciclo",""), reverse=True
        )
        # Média de todos os ciclos do mês para a nota final
        fn_vals = [eval_final(e, pesos) for e in op_evals]
        fn_vals = [v for v in fn_vals if v is not None]
        fn_med  = round(sum(fn_vals)/len(fn_vals), 2) if fn_vals else None
        mp_vals = [float(e["mp"]) for e in op_evals if e.get("mp") not in (None,"")]
        mp_med  = round(sum(mp_vals)/len(mp_vals), 2) if mp_vals else None
        iv_vals = [eval_int(e) for e in op_evals]
        iv_vals = [v for v in iv_vals if v is not None]
        iv_med  = round(sum(iv_vals)/len(iv_vals), 2) if iv_vals else None
        fx = get_faixa(fn_med, faixas)
        bonus_v = fx["bonus"] if fx else 0
        total_bonus += bonus_v
        sit = "✅ Meta atingida" if fn_med and fn_med >= 80 else ("⚠️ Abaixo da meta" if fn_med is not None else "📭 Sem avaliação")
        rows.append({
            "Operador":      op["nome"],
            "Cargo":         op.get("cargo","—"),
            "Nota MP média": f"{mp_med:.1f}" if mp_med else "—",
            "Média interna": f"{iv_med:.1f}" if iv_med else "—",
            "Nota final":    f"{fn_med:.1f}%" if fn_med else "—",
            "Faixa":         fx["desc"] if fx else "—",
            "Bônus":         f"R$ {bonus_v:.2f}",
            "Situação":      sit,
        })
 
    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.markdown(f"<p style='color:#4CC9F0;font-weight:600;'>💰 Total de bonificação da equipe: R$ {total_bonus:.2f}</p>", unsafe_allow_html=True)
 
        csv = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button("⬇️ Exportar metas CSV", data=csv,
                           file_name=f"leal_cx_metas_{mes_sel}_{datetime.now().strftime('%Y%m%d')}.csv",
                           mime="text/csv")
    else:
        st.info("Nenhuma avaliação para o mês selecionado.")
 
# ═══════════════════════════════════════════════════════════════════════════════
# PÁGINA: EVOLUÇÃO
# ═══════════════════════════════════════════════════════════════════════════════
def pagina_evolucao(user, readonly=False):
    st.markdown("# 📈 Evolução — Visão macrossistêmica")
 
    operadores = load_operadores()
    avaliacoes = load_avaliacoes()
    pesos      = st.session_state.pesos
 
    if not avaliacoes:
        st.info("Registre avaliações para visualizar a evolução.")
        return
 
    meses = sorted(set(e.get("mes","") for e in avaliacoes if e.get("mes")))
 
    c1, c2 = st.columns(2)
    opcao  = c1.selectbox("Visualizar", ["Média da equipe"] + [o["nome"] for o in operadores])
    metrica = c2.selectbox("Métrica", ["Nota final (%)", "Nota MP", "Média interna", "Cordialidade", "Resolução", "Agilidade"])
 
    def get_val(e, met):
        if met == "Nota final (%)": return eval_final(e, pesos)
        if met == "Nota MP":        return float(e["mp"]) if e.get("mp") not in (None,"") else None
        if met == "Média interna":  return eval_int(e)
        if met == "Cordialidade":   return float(e["cord"]) if e.get("cord") else None
        if met == "Resolução":      return float(e["res"])  if e.get("res") else None
        if met == "Agilidade":      return float(e["agi"])  if e.get("agi") else None
 
    # Gráfico de linha: fechamento por mês
    data_linhas = {}
    for mes in meses:
        mes_evals = [e for e in avaliacoes if e.get("mes") == mes]
        if opcao == "Média da equipe":
            vals = [get_val(e, metrica) for e in mes_evals]
        else:
            op = next((o for o in operadores if o["nome"] == opcao), None)
            vals = [get_val(e, metrica) for e in mes_evals if op and e["op_id"] == op["id"]]
        vals = [v for v in vals if v is not None]
        data_linhas[mes] = round(sum(vals)/len(vals), 2) if vals else None
 
    df_line = pd.DataFrame({"Mês": list(data_linhas.keys()), metrica: list(data_linhas.values())}).dropna()
    if not df_line.empty:
        st.markdown(f"### 🌌 {opcao} — {metrica}")
        st.line_chart(df_line.set_index("Mês"), color="#4CC9F0")
 
    # Comparativo entre operadores no mês mais recente
    st.markdown("---")
    st.markdown("### 🧑‍🚀 Comparativo entre operadores — mês mais recente")
    mes_rec = meses[-1] if meses else None
    if mes_rec:
        comp_rows = []
        for op in operadores:
            op_evals = [e for e in avaliacoes if e["op_id"] == op["id"] and e.get("mes") == mes_rec]
            vals = [get_val(e, metrica) for e in op_evals]
            vals = [v for v in vals if v is not None]
            if vals:
                comp_rows.append({"Operador": op["nome"], metrica: round(sum(vals)/len(vals),2)})
        if comp_rows:
            df_comp = pd.DataFrame(comp_rows).sort_values(metrica, ascending=False)
            st.bar_chart(df_comp.set_index("Operador"), color="#4CC9F0")
 
# ═══════════════════════════════════════════════════════════════════════════════
# PÁGINA: CONFIGURAÇÕES (só Comandante)
# ═══════════════════════════════════════════════════════════════════════════════
def pagina_configuracoes(user):
    st.markdown("# ⚙️ Configurações")
 
    # Gestão de usuários
    st.markdown("### 👤 Usuários do sistema")
    usuarios = load_usuarios()
    for u in usuarios:
        c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
        c1.markdown(f"**{u['nome']}**")
        c2.markdown(f"`{u['login']}`")
        c3.markdown(NIVEIS.get(u["nivel"], u["nivel"]))
        if c4.button("🗑️", key=f"del_user_{u['login']}") and u["login"] != user["login"]:
            usuarios = [x for x in usuarios if x["login"] != u["login"]]
            save_usuarios(usuarios)
            st.success("Usuário removido.")
            st.rerun()
 
    st.markdown("---")
    st.markdown("### 🔒 Alterar senha")
    with st.form("form_senha"):
        nova_senha = st.text_input("Nova senha", type="password")
        confirmar  = st.text_input("Confirmar senha", type="password")
        if st.form_submit_button("💾 Salvar"):
            if nova_senha != confirmar:
                st.error("As senhas não coincidem.")
            elif len(nova_senha) < 4:
                st.error("Senha muito curta (mínimo 4 caracteres).")
            else:
                usuarios = load_usuarios()
                for u in usuarios:
                    if u["login"] == user["login"]:
                        u["senha"] = nova_senha
                save_usuarios(usuarios)
                st.success("Senha alterada com sucesso!")
 
    st.markdown("---")
    st.markdown("### 💾 Backup completo")
    operadores = load_operadores()
    avaliacoes = load_avaliacoes()
    faixas     = load_faixas()
    backup = {
        "exportado_em": datetime.now().isoformat(),
        "operadores": operadores,
        "avaliacoes": avaliacoes,
        "faixas": faixas,
        "pesos": st.session_state.pesos,
    }
    st.download_button(
        "⬇️ Baixar backup JSON",
        data=json.dumps(backup, ensure_ascii=False, indent=2).encode("utf-8"),
        file_name=f"leal_cx_backup_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
        mime="application/json",
    )
 
    st.markdown("### 📥 Importar backup")
    arquivo = st.file_uploader("Selecione um arquivo .json de backup", type=["json"])
    if arquivo:
        try:
            dados = json.load(arquivo)
            if st.button("⚠️ Confirmar importação (sobrescreve dados atuais)"):
                if "operadores" in dados: save_operadores(dados["operadores"])
                if "avaliacoes" in dados: save_avaliacoes(dados["avaliacoes"])
                if "faixas"     in dados: save_faixas(dados["faixas"])
                if "pesos"      in dados: st.session_state.pesos = dados["pesos"]
                st.success("Dados importados com sucesso!")
                st.rerun()
        except Exception as ex:
            st.error(f"Erro ao ler o arquivo: {ex}")
 
# ═══════════════════════════════════════════════════════════════════════════════
# PORTAL DO OPERADOR (Tripulação)
# ═══════════════════════════════════════════════════════════════════════════════
def portal_tripulacao(user):
    operadores = load_operadores()
    avaliacoes = load_avaliacoes()
    faixas     = load_faixas()
    pesos      = st.session_state.pesos
 
    op = next((o for o in operadores if o["id"] == user.get("op_id")), None)
    if not op:
        st.error("Operador não encontrado. Contate o administrador.")
        return
 
    st.markdown(f"""
    <div style='text-align:center;padding:1rem 0;'>
        <div style='font-size:40px;'>⭐</div>
        <h1 style='color:#4CC9F0;'>Olá, {op['nome'].split()[0]}!</h1>
        <p style='color:#E2E8F0;font-size:14px;'>{op.get('cargo','—')} · {tenure(op.get('adm'))} de empresa</p>
    </div>
    """, unsafe_allow_html=True)
 
    op_evals = sorted([e for e in avaliacoes if e["op_id"] == op["id"]],
                      key=lambda x: (x.get("mes",""), x.get("ciclo","")), reverse=True)
 
    if not op_evals:
        st.info("Você ainda não possui avaliações registradas.")
        return
 
    # Última avaliação
    last = op_evals[0]
    fn   = eval_final(last, pesos)
    fx   = get_faixa(fn, faixas)
    iv   = eval_int(last)
    mp_v = float(last["mp"]) if last.get("mp") not in (None,"") else None
 
    st.markdown("---")
    st.markdown(f"### 🎯 Sua situação — {last.get('mes','—')} / {last.get('ciclo','—')}")
 
    c1, c2, c3 = st.columns(3)
    c1.metric("Nota MP",      f"{mp_v:.1f}" if mp_v else "—")
    c2.metric("Média interna", f"{iv:.1f}" if iv else "—")
    c3.metric("Nota final",   f"{fn:.1f}%" if fn else "—")
 
    if fn is not None:
        pct = min(100, max(0, fn))
        cor = "#4CC9F0" if fn >= 90 else "#FAC775" if fn >= 80 else "#F09595"
        st.markdown(f"""
        <div style='margin:1rem 0;'>
            <div style='display:flex;justify-content:space-between;font-size:13px;margin-bottom:6px;'>
                <span style='color:#E2E8F0;'>Progresso da meta</span>
                <span style='color:{cor};font-weight:700;'>{fn:.1f}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(pct / 100)
        st.markdown(badge_faixa(fx), unsafe_allow_html=True)
 
        faixas_sorted = sorted(faixas, key=lambda x: x["min"])
        proxima = next((f for f in faixas_sorted if f["min"] > fn), None)
        if proxima:
            falta = round(proxima["min"] - fn, 2)
            st.markdown(f"<p style='color:#4CC9F0;'>⭐ Faltam <strong>{falta} pontos</strong> para <strong>{proxima['desc']}</strong> (R$ {proxima['bonus']:.2f})</p>", unsafe_allow_html=True)
        else:
            st.markdown("<p style='color:#9FE1CB;font-weight:600;'>🏆 Você está na faixa máxima! Parabéns!</p>", unsafe_allow_html=True)
 
    # Detalhes por critério
    st.markdown("---")
    st.markdown("### 📊 Critérios — avaliação interna")
    c1, c2, c3, c4 = st.columns(4)
    criterios = [("Cordialidade","cord"), ("Resolução","res"), ("Agilidade","agi"), ("Script","script")]
    for col, (label, key) in zip([c1,c2,c3,c4], criterios):
        val = float(last[key]) if last.get(key) not in (None,"",0) else None
        col.metric(label, f"{val:.1f}" if val else "—")
 
    # Feedback
    if last.get("feed") or last.get("pos") or last.get("acao"):
        st.markdown("---")
        st.markdown("### 💬 Feedback da última avaliação")
        if last.get("pos"):
            st.markdown(f"""
            <div style='background:rgba(159,225,203,0.1);border:1px solid rgba(159,225,203,0.3);border-radius:10px;padding:14px;margin-bottom:10px;'>
                <p style='color:#9FE1CB;font-size:12px;font-weight:600;margin-bottom:6px;'>✅ PONTOS POSITIVOS</p>
                <p style='color:#E2E8F0;font-size:14px;'>{last['pos']}</p>
            </div>
            """, unsafe_allow_html=True)
        if last.get("feed"):
            st.markdown(f"""
            <div style='background:rgba(250,199,117,0.1);border:1px solid rgba(250,199,117,0.3);border-radius:10px;padding:14px;margin-bottom:10px;'>
                <p style='color:#FAC775;font-size:12px;font-weight:600;margin-bottom:6px;'>⚠️ PONTOS DE MELHORIA</p>
                <p style='color:#E2E8F0;font-size:14px;'>{last['feed']}</p>
            </div>
            """, unsafe_allow_html=True)
        if last.get("acao"):
            st.markdown(f"""
            <div style='background:rgba(76,201,240,0.1);border:1px solid rgba(76,201,240,0.3);border-radius:10px;padding:14px;'>
                <p style='color:#4CC9F0;font-size:12px;font-weight:600;margin-bottom:6px;'>🚀 PLANO DE AÇÃO</p>
                <p style='color:#E2E8F0;font-size:14px;'>{last['acao']}</p>
            </div>
            """, unsafe_allow_html=True)
 
    # Histórico simplificado
    st.markdown("---")
    st.markdown("### 📅 Meu histórico")
    hist_rows = []
    for e in op_evals[:10]:
        fn_h = eval_final(e, pesos)
        fx_h = get_faixa(fn_h, faixas)
        hist_rows.append({
            "Mês":        e.get("mes","—"),
            "Ciclo":      e.get("ciclo","—"),
            "MP":         f"{float(e['mp']):.1f}" if e.get("mp") not in (None,"") else "—",
            "Nota final": f"{fn_h:.1f}%" if fn_h else "—",
            "Faixa":      fx_h["desc"] if fx_h else "—",
            "Bônus":      f"R$ {fx_h['bonus']:.2f}" if fx_h else "R$ 0,00",
        })
    if hist_rows:
        st.dataframe(pd.DataFrame(hist_rows), use_container_width=True, hide_index=True)
 
# ═══════════════════════════════════════════════════════════════════════════════
# ROTEADOR PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    tela_login()
else:
    user  = st.session_state.user
    nivel = user["nivel"]
 
    # Tripulação: portal individual
    if nivel == "tripulacao":
        render_sidebar(user)
        portal_tripulacao(user)
 
    # Demais perfis: sistema completo
    else:
        render_sidebar(user)
        readonly = (nivel == "observador")
        page = st.session_state.get("page", "Dashboard")
 
        if page == "Dashboard":
            pagina_dashboard(user, readonly)
        elif page == "Operadores":
            pagina_operadores(user, readonly)
        elif page == "Avaliações":
            pagina_avaliacoes(user, readonly)
        elif page == "Metas":
            pagina_metas(user, readonly)
        elif page == "Evolução":
            pagina_evolucao(user, readonly)
        elif page == "Configurações" and nivel == "comandante":
            pagina_configuracoes(user)
            
