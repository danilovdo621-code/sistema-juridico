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
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

        /* Limpa margens */
        .block-container { padding: 0 !important; max-width: 100% !important; }
        header, footer { display: none !important; }

        /* Imagem Esquerda Fixa */
        .split-bg {
            position: fixed; top: 0; left: 0; width: 60%; height: 100vh;
            background-image: url('https://i.postimg.cc/50dwcw8Z/close-up-law-statue.jpg');
            background-size: cover; background-position: center; z-index: 0;
        }

        /* Fundo Branco Direita */
        .right-bg {
            position: fixed; top: 0; right: 0; width: 40%; height: 100vh;
            background-color: #ffffff; z-index: -1;
        }

        /* Estilo dos Inputs */
        div[data-testid="stTextInput"] input { 
            border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; 
            font-family: 'Inter', sans-serif; background-color: #f8fafc; color: #334155;
        }
        div[data-testid="stTextInput"] input:focus { 
            border-color: #1e40af; background-color: #fff;
            box-shadow: 0 0 0 2px rgba(30, 64, 175, 0.1); 
        }

        /* Botão */
        div[data-testid="stButton"] button { 
            width: 100%; background-color: #1e40af; color: white; 
            border: none; padding: 14px; font-weight: 600; border-radius: 8px; 
            margin-top: 10px;
        }
        div[data-testid="stButton"] button:hover { background-color: #1e3a8a; }

        /* MOBILE */
        @media only screen and (max-width: 768px) {
            .split-bg { display: none !important; }
            .right-bg { width: 100% !important; }
            div[data-testid="column"]:nth-of-type(1) { display: none !important; }
            div[data-testid="column"]:nth-of-type(2) { width: 100% !important; padding: 20px !important; }
        }
        </style>
        <div class="split-bg"></div>
        <div class="right-bg"></div>
    """, unsafe_allow_html=True)

    # Colunas Principais: 60% Imagem | 40% Login
    c_img, c_login = st.columns([6, 4])

    with c_img:
        st.write("") # Vazio (Imagem de fundo)

    with c_login:
        # 1. Espaçador Vertical
        st.markdown("""
            <div style="height: 25vh;" class="desktop-spacer"></div>
            <style>
                @media (max-width: 768px) { .desktop-spacer { height: 5vh !important; } }
            </style>
        """, unsafe_allow_html=True)

        # 2. Colunas Internas para Centralizar
        _, col_form, _ = st.columns([1, 4, 1])

        with col_form:
            # --- AQUI ESTÁ A LOGO ---
            # Troque o link dentro de src="" pelo link da sua logo
            st.markdown("""
                <div style="text-align: center; margin-bottom: 15px;">
                    <img src="https://cdn-icons-png.flaticon.com/512/924/924915.png" style="width: 80px;">
                </div>
                <h1 style='text-align: center; color: #1e3a8a; font-family: Inter; font-size: 32px; margin-top: 0;'>Jurídico Pro</h1>
                <p style='text-align: center; color: #64748b; margin-bottom: 30px;'>Acesso ao Portal do Cliente</p>
            """, unsafe_allow_html=True)

            email = st.text_input("E-mail", placeholder="seu@email.com")
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
                        st.error("Dados incorretos.")
                else:
                    st.error("Erro de conexão.")

            st.markdown("<div style='text-align: center; color: #cbd5e1; font-size: 11px; margin-top: 40px;'>Ambiente Seguro SSL</div>", unsafe_allow_html=True)

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
