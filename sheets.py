"""
sheets.py — Camada de acesso ao Google Sheets
Todas as operações de leitura e escrita passam por aqui.
"""
import json
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# Nomes das abas na planilha
SHEET_USUARIOS   = "usuarios"
SHEET_OPERADORES = "operadores"
SHEET_AVALIACOES = "avaliacoes"
SHEET_FEEDBACKS  = "feedbacks"
SHEET_ERROS      = "banco_erros"


@st.cache_resource(show_spinner=False)
def get_client():
    """Retorna cliente gspread autenticado (cached por sessão)."""
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    return gspread.authorize(creds)


def get_sheet(tab_name: str):
    """Abre a aba pelo nome."""
    gc = get_client()
    spreadsheet_id = st.secrets["spreadsheet_id"]
    sh = gc.open_by_key(spreadsheet_id)
    try:
        return sh.worksheet(tab_name)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=tab_name, rows=1000, cols=30)
        return ws


def ensure_header(ws, headers: list):
    """Garante que a primeira linha tem os cabeçalhos corretos."""
    current = ws.row_values(1)
    if current != headers:
        ws.clear()
        ws.append_row(headers)


# ─────────────────────────────────────────
# USUÁRIOS
# ─────────────────────────────────────────
USER_HEADERS = ["id", "nome", "usuario", "senha", "perfil", "ativo", "criado_em"]

def load_usuarios() -> pd.DataFrame:
    ws = get_sheet(SHEET_USUARIOS)
    ensure_header(ws, USER_HEADERS)
    data = ws.get_all_records()
    if not data:
        return pd.DataFrame(columns=USER_HEADERS)
    return pd.DataFrame(data)

def save_usuario(row: dict):
    ws = get_sheet(SHEET_USUARIOS)
    ensure_header(ws, USER_HEADERS)
    df = load_usuarios()
    if "id" not in row or not row["id"]:
        row["id"] = int(datetime.now().timestamp() * 1000)
    if "criado_em" not in row or not row["criado_em"]:
        row["criado_em"] = datetime.now().strftime("%d/%m/%Y %H:%M")
    # Atualiza se já existe
    if not df.empty and str(row["id"]) in df["id"].astype(str).values:
        idx = df[df["id"].astype(str) == str(row["id"])].index[0]
        row_num = idx + 2  # +1 header, +1 gspread 1-indexed
        ws.update(f"A{row_num}", [[str(row.get(h,"")) for h in USER_HEADERS]])
    else:
        ws.append_row([str(row.get(h, "")) for h in USER_HEADERS])

def delete_usuario(uid):
    ws = get_sheet(SHEET_USUARIOS)
    df = load_usuarios()
    if df.empty:
        return
    matches = df[df["id"].astype(str) == str(uid)]
    if matches.empty:
        return
    row_num = matches.index[0] + 2
    ws.delete_rows(row_num)

def seed_admin():
    """Cria admin padrão se não houver nenhum usuário."""
    df = load_usuarios()
    if df.empty:
        save_usuario({"nome":"Administrador","usuario":"admin","senha":"admin123","perfil":"admin","ativo":"true"})


# ─────────────────────────────────────────
# OPERADORES
# ─────────────────────────────────────────
OP_HEADERS = ["id","nome","matricula","tier","canal","nota_geral","nota_mp","nota_interna","ativo","criado_em"]

def load_operadores() -> pd.DataFrame:
    ws = get_sheet(SHEET_OPERADORES)
    ensure_header(ws, OP_HEADERS)
    data = ws.get_all_records()
    if not data:
        return pd.DataFrame(columns=OP_HEADERS)
    return pd.DataFrame(data)

def save_operador(row: dict):
    ws = get_sheet(SHEET_OPERADORES)
    ensure_header(ws, OP_HEADERS)
    df = load_operadores()
    if "id" not in row or not row["id"]:
        row["id"] = int(datetime.now().timestamp() * 1000)
    if "criado_em" not in row or not row["criado_em"]:
        row["criado_em"] = datetime.now().strftime("%d/%m/%Y %H:%M")
    if not df.empty and str(row["id"]) in df["id"].astype(str).values:
        idx = df[df["id"].astype(str) == str(row["id"])].index[0]
        ws.update(f"A{idx+2}", [[str(row.get(h,"")) for h in OP_HEADERS]])
    else:
        ws.append_row([str(row.get(h,"")) for h in OP_HEADERS])

def delete_operador(oid):
    ws = get_sheet(SHEET_OPERADORES)
    df = load_operadores()
    if df.empty: return
    matches = df[df["id"].astype(str) == str(oid)]
    if matches.empty: return
    ws.delete_rows(matches.index[0] + 2)


# ─────────────────────────────────────────
# AVALIAÇÕES
# ─────────────────────────────────────────
AV_HEADERS = ["id","operador","data_chamada","tipo","nota_final","soft_skills","tecnico",
              "saudacao","empatia","resolucao","encerramento","parecer","auditor","criado_em"]

def load_avaliacoes() -> pd.DataFrame:
    ws = get_sheet(SHEET_AVALIACOES)
    ensure_header(ws, AV_HEADERS)
    data = ws.get_all_records()
    if not data:
        return pd.DataFrame(columns=AV_HEADERS)
    return pd.DataFrame(data)

def save_avaliacao(row: dict):
    ws = get_sheet(SHEET_AVALIACOES)
    ensure_header(ws, AV_HEADERS)
    if "id" not in row or not row["id"]:
        row["id"] = int(datetime.now().timestamp() * 1000)
    if "criado_em" not in row or not row["criado_em"]:
        row["criado_em"] = datetime.now().strftime("%d/%m/%Y %H:%M")
    ws.append_row([str(row.get(h, "")) for h in AV_HEADERS])


# ─────────────────────────────────────────
# FEEDBACKS
# ─────────────────────────────────────────
FB_HEADERS = ["id","operador","data","tipo","nota","positivo","melhoria","plano",
              "vis_operador","vis_gestor","notif_email","auditor","status","criado_em"]

def load_feedbacks() -> pd.DataFrame:
    ws = get_sheet(SHEET_FEEDBACKS)
    ensure_header(ws, FB_HEADERS)
    data = ws.get_all_records()
    if not data:
        return pd.DataFrame(columns=FB_HEADERS)
    return pd.DataFrame(data)

def save_feedback(row: dict):
    ws = get_sheet(SHEET_FEEDBACKS)
    ensure_header(ws, FB_HEADERS)
    if "id" not in row or not row["id"]:
        row["id"] = int(datetime.now().timestamp() * 1000)
    if "criado_em" not in row or not row["criado_em"]:
        row["criado_em"] = datetime.now().strftime("%d/%m/%Y %H:%M")
    ws.append_row([str(row.get(h, "")) for h in FB_HEADERS])


# ─────────────────────────────────────────
# BANCO DE ERROS
# ─────────────────────────────────────────
ERRO_HEADERS = ["id","horario","categoria","descricao","operador","severidade","status","criado_em"]

def load_erros() -> pd.DataFrame:
    ws = get_sheet(SHEET_ERROS)
    ensure_header(ws, ERRO_HEADERS)
    data = ws.get_all_records()
    if not data:
        return pd.DataFrame(columns=ERRO_HEADERS)
    return pd.DataFrame(data)

def save_erro(row: dict):
    ws = get_sheet(SHEET_ERROS)
    ensure_header(ws, ERRO_HEADERS)
    if "id" not in row or not row["id"]:
        row["id"] = int(datetime.now().timestamp() * 1000)
    if "criado_em" not in row or not row["criado_em"]:
        row["criado_em"] = datetime.now().strftime("%d/%m/%Y %H:%M")
    ws.append_row([str(row.get(h, "")) for h in ERRO_HEADERS])
