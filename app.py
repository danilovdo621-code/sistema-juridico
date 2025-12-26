import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime

# ==============================================================================
# 1. CONFIGURAÇÃO DA PÁGINA
# ==============================================================================
st.set_page_config(
    layout="wide", 
    page_title="Advocacia Digital",
    page_icon="⚖️",
    initial_sidebar_state="collapsed"
)

# ==============================================================================
# 2. CONEXÃO COM GOOGLE SHEETS
# ==============================================================================
try:
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets"]

    if "gcp_service_account" in st.secrets:
        creds_dict = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    else:
        creds = Credentials.from_service_account_file("credenciais.json", scopes=scope)

    client = gspread.authorize(creds)
    spreadsheet_id = "1f3iOOxcAdPY-ciswOGUkPVoyu90p0e1FeSYvSuHalmo"
    spreadsheet = client.open_by_key(spreadsheet_id)

    sheet_processos = spreadsheet.worksheet("ProcessosJuridicos")
    sheet_clientes = spreadsheet.worksheet("Clientes")
    try:
        sheet_historico = spreadsheet.worksheet("HistoricoProcessos")
    except:
        sheet_historico = None

    CONNECTION_STATUS = True
except Exception as e:
    st.error(f"⚠️ Erro de conexão: {e}")
    CONNECTION_STATUS = False

# ==============================================================================
# 3. ESTADO DA SESSÃO
# ==============================================================================
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'user_id' not in st.session_state: st.session_state['user_id'] = None
if 'user_name' not in st.session_state: st.session_state['user_name'] = None
if 'user_role' not in st.session_state: st.session_state['user_role'] = None

# ==============================================================================
# 4. FUNÇÕES AUXILIARES
# ==============================================================================
def authenticate_user(email, password):
    if not CONNECTION_STATUS: return None, None, None
    try:
        df = pd.DataFrame(sheet_clientes.get_all_records())
        df.columns = df.columns.str.strip()
        df['Email'] = df['Email'].astype(str).str.strip()
        df['Senha'] = df['Senha'].astype(str).str.strip()

        user = df[(df['Email'] == email.strip()) & (df['Senha'] == password.strip())]

        if not user.empty:
            role = user.iloc[0].get('Role', 'Cliente')
            return str(user.iloc[0]['IDCliente']), user.iloc[0]['NomeCompleto'], role
    except: pass
    return None, None, None

def load_data(sheet):
    if not CONNECTION_STATUS or sheet is None: return pd.DataFrame()
    try:
        data = sheet.get_all_records()
        return pd.DataFrame(data)
    except:
        return pd.DataFrame()

def logout():
    for key in ['logged_in', 'user_id', 'user_name', 'user_role']:
        st.session_state[key] = None
    st.session_state['logged_in'] = False
    st.rerun()

# ==============================================================================
# 5. LÓGICA DE EXIBIÇÃO
# ==============================================================================

# --- TELA DE LOGIN ---
if not st.session_state['logged_in']:

    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

        /* REMOVE MARGENS PADRÃO DO STREAMLIT */
        .block-container { padding-top: 0rem !important; padding-bottom: 0rem !important; }
        header { display: none !important; }
        footer { display: none !important; }

        /* --- DESKTOP --- */
        .split-bg {
            position: fixed; top: 0; left: 0; width: 60%; height: 100vh;
            background-image: url('https://i.postimg.cc/50dwcw8Z/close-up-law-statue.jpg');
            background-size: cover; background-position: center; z-index: 0;
        }

        .login-title {
            font-family: 'Inter', sans-serif;
            color: #1e3a8a;
            text-align: center;
            font-size: 2.5rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }

        .login-subtitle {
            font-family: 'Inter', sans-serif;
            color: #64748b;
            text-align: center;
            font-size: 1rem;
            margin-bottom: 2rem;
        }

        /* --- MOBILE (Telas menores que 768px) --- */
        @media only screen and (max-width: 768px) {
            /* Esconde a coluna da imagem no celular */
            div[data-testid="column"]:nth-of-type(1) {
                display: none !important;
            }
            /* Força a coluna do login a ocupar 100% */
            div[data-testid="column"]:nth-of-type(2) {
                width: 100% !important;
                min-width: 100% !important;
                margin: 0 !important;
                padding: 20px !important;
            }

            /* Ajustes visuais para celular */
            .split-bg { display: none !important; }

            .stApp {
                background-color: #ffffff; /* Fundo branco limpo */
            }

            .login-title { font-size: 1.8rem !important; margin-top: 2rem !important; }
        }

        /* INPUTS E BOTÕES */
        div[data-testid="stTextInput"] input { 
            border: 1px solid #e2e8f0; 
            border-radius: 12px; 
            padding: 15px; 
            font-size: 16px; /* Evita zoom no iPhone */
        }
        div[data-testid="stTextInput"] input:focus { 
            border-color: #1e40af; 
            box-shadow: 0 0 0 3px rgba(30, 64, 175, 0.1); 
        }
        div[data-testid="stButton"] button { 
            width: 100%; 
            background-color: #1e40af; 
            color: white; 
            border: none; 
            padding: 16px; 
            font-weight: 600; 
            border-radius: 12px; 
            font-size: 16px;
            margin-top: 10px;
        }
        div[data-testid="stButton"] button:hover { background-color: #1e3a8a; }

        </style>
        <div class="split-bg"></div>
    """, unsafe_allow_html=True)

    # Layout de colunas
    c1, c2 = st.columns([6, 4])

    # Coluna 1: Vazia (Imagem de fundo cobre ela no desktop, some no mobile)
    with c1:
        st.write("") 

    # Coluna 2: Login
    with c2:
        # Espaçamento vertical apenas no desktop
        st.markdown("""
            <style>
            @media (min-width: 769px) {
                div[data-testid="column"]:nth-of-type(2) {
                    padding-top: 15vh !important;
                    padding-left: 3rem !important;
                    padding-right: 3rem !important;
                }
            }
            </style>
        """, unsafe_allow_html=True)

        st.markdown('<div class="login-title">⚖️ Jurídico Pro</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-subtitle">Acesso Restrito ao Cliente</div>', unsafe_allow_html=True)

        email = st.text_input("E-mail", placeholder="exemplo@email.com")
        password = st.text_input("Senha", type="password", placeholder="••••••••")

        if st.button("ENTRAR"):
            if CONNECTION_STATUS:
                uid, uname, urole = authenticate_user(email, password)
                if uid:
                    st.session_state['logged_in'] = True
                    st.session_state['user_id'] = uid
                    st.session_state['user_name'] = uname
                    st.session_state['user_role'] = urole
                    st.rerun()
                else:
                    st.error("Dados inválidos.")
            else:
                st.error("Erro de conexão.")

        st.markdown("<div style='text-align: center; color: #cbd5e1; font-size: 12px; margin-top: 40px;'>Sistema Seguro v2.0</div>", unsafe_allow_html=True)

# --- ÁREA LOGADA ---
else:
    st.markdown("""
        <style>
        .block-container { padding: 2rem 1rem !important; max-width: 100% !important; }
        header { visibility: visible !important; }
        </style>
    """, unsafe_allow_html=True)

    opcoes_menu = ["Meus Processos"]
    if st.session_state['user_role'] == 'Advogado':
        opcoes_menu.append("Configurações")

    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state['user_name']}")
        st.caption(f"Perfil: {st.session_state['user_role']}")
        st.divider()

        if len(opcoes_menu) > 1:
            menu_opcao = st.radio("Menu", opcoes_menu)
        else:
            menu_opcao = "Meus Processos"

        st.divider()
        if st.button("Sair"):
            logout()

    # --- CONTEÚDO ---
    if menu_opcao == "Meus Processos":
        st.title("📂 Detalhes do Processo")
        st.markdown("---")

        df_processos = load_data(sheet_processos)
        df_historico = load_data(sheet_historico)

        if not df_processos.empty:
            df_processos.columns = df_processos.columns.str.strip()
            if not df_historico.empty:
                df_historico.columns = df_historico.columns.str.strip()

            if 'IDCliente' in df_processos.columns:
                df_processos['IDCliente'] = df_processos['IDCliente'].astype(str).str.strip()
                user_id_logado = str(st.session_state['user_id']).strip()

                if st.session_state['user_role'] != 'Advogado':
                    df_filtrado = df_processos[df_processos['IDCliente'] == user_id_logado]
                else:
                    df_filtrado = df_processos

                if not df_filtrado.empty:
                    processos_opcoes = df_filtrado['NumeroProcesso'].tolist()
                    processos_opcoes.insert(0, "Selecione...")

                    selected_process = st.selectbox("Escolha o processo para ver detalhes:", processos_opcoes)

                    if selected_process != "Selecione...":
                        dados = df_filtrado[df_filtrado['NumeroProcesso'] == selected_process].iloc[0]

                        with st.container():
                            st.subheader(f"📌 Processo: {dados['NumeroProcesso']}")
                            c1, c2, c3 = st.columns(3)
                            c1.markdown(f"**Tipo:** {dados.get('TipoProcesso', '-')}")
                            c2.markdown(f"**Status:** {dados.get('Status', '-')}")
                            c3.markdown(f"**Início:** {dados.get('DataInicio', '-')}")
                            st.markdown(f"**Descrição:** {dados.get('DescricaoDetalhada', '-')}")
                            st.markdown(f"**Próximo Prazo:** {dados.get('Próximo Prazo', '-')}")

                        st.markdown("---")
                        st.subheader("📜 Histórico de Movimentações")

                        if not df_historico.empty and 'NumeroProcesso' in df_historico.columns:
                            hist_filtrado = df_historico[df_historico['NumeroProcesso'] == selected_process]
                            if not hist_filtrado.empty:
                                if 'DataAtualizacao' in hist_filtrado.columns:
                                    hist_filtrado['DataAtualizacao'] = pd.to_datetime(hist_filtrado['DataAtualizacao'], dayfirst=True, errors='coerce')
                                    hist_filtrado = hist_filtrado.sort_values(by='DataAtualizacao', ascending=False)
                                for _, row in hist_filtrado.iterrows():
                                    data_hist = row.get('DataAtualizacao', '-')
                                    if isinstance(data_hist, pd.Timestamp):
                                        data_hist = data_hist.strftime('%d/%m/%Y')
                                    st.info(f"**{data_hist}** | {row.get('DescricaoHistorico', '-')}")
                            else:
                                st.warning("Nenhuma movimentação registrada.")
                        else:
                            st.warning("Histórico vazio.")
                    else:
                        st.info("👆 Selecione um processo acima.")
                else:
                    st.warning("Nenhum processo vinculado.")
            else:
                st.error("Erro: Coluna 'IDCliente' não encontrada.")
        else:
            st.info("Nenhum processo carregado.")

    elif menu_opcao == "Configurações":
        st.title("⚙️ Configurações")
        st.write("Área restrita para advogados.")
