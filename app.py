import streamlit as st
from views.login_view import LoginView
from views.dashboard_view import DashboardView
from views.admin_view import AdminView
from views.upload_view import UploadView
from views.users_view import UsersView
from views.admin_analytics_view import AdminAnalyticsView
from views.components import renderizar_meteo_sidebar
from services.news_service import renderizar_galeria_eventos

# Configuração da página
st.set_page_config(
    page_title="ecoFIT", 
    page_icon="🌱", 
    layout="centered"
)

# Injeção de Estilos Globais Reforçados para a EcoFit
st.markdown("""
    <style>
        /* 1. BOTÕES PRIMÁRIOS (Inserir / Submeter Atividades) */
        button[kind="primary"],
        button[data-testid="stBaseButton-primary"],
        .stButton > button[kind="primary"] {
            background-color: #10b981 !important;
            border-color: #10b981 !important;
            color: #ffffff !important;
            font-weight: 600 !important;
        }

        button[kind="primary"]:hover,
        button[data-testid="stBaseButton-primary"]:hover,
        .stButton > button[kind="primary"]:hover {
            background-color: #059669 !important;
            border-color: #059669 !important;
        }

        /* 2. SEPARADORES (TABS) - Texto e Linha Ativa */
        /* Selecionador de Tab Ativa */
        div[data-baseweb="tab-list"] button[aria-selected="true"],
        button[role="tab"][aria-selected="true"] {
            border-bottom-color: #10b981 !important;
        }

        /* Texto dentro da Tab Ativa */
        div[data-baseweb="tab-list"] button[aria-selected="true"] *,
        button[role="tab"][aria-selected="true"] * {
            color: #10b981 !important;
            font-weight: 600 !important;
        }

        /* Linha inferior de destaque das Tabs */
        div[data-baseweb="tab-highlight"],
        div[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
            background-color: #10b981 !important;
        }

        /* Hover nas Tabs */
        button[role="tab"]:hover * {
            color: #34d399 !important;
        }

        /* 3. BORDAS DE FOCO E INPUTS (Remove o contorno vermelho ao clicar) */
        div[data-baseweb="input"]:focus-within,
        div[data-baseweb="select"]:focus-within {
            border-color: #10b981 !important;
        }
    </style>
""", unsafe_allow_html=True)

# Fluxo de navegação baseado no estado da sessão
if 'utilizador_logado' not in st.session_state:
    LoginView.renderizar_ecran()
else:
    utilizador = st.session_state['utilizador_logado']
    
    # Barra Lateral
    with st.sidebar:
        st.markdown(f"### Olá, **{utilizador['nome']}**")
        st.caption(f"Perfil: {utilizador['perfil']} | Estado: {utilizador['estado']}")
        st.markdown("---")

        # Widget meteorológico
        renderizar_meteo_sidebar()

        if st.button("Terminar Sessão (Logout)", use_container_width=True):
            from controllers.auth_controller import AuthController
            AuthController.logout()
            st.rerun()

    # Cabeçalho Principal
    st.title("Plataforma ecoFIT")
    
    # Navegação por Perfil
    if utilizador['perfil'] == 'Admin':
        # Admin visualiza 5 abas (incluindo a Analítica Global)
        aba_app, aba_upload, aba_user, aba_analytics, aba_admin = st.tabs([
            "Inserir Atividade", 
            "Sincronizar Ficheiro", 
            "Ranking & Utilizadores", 
            "Analítica Global",
            "Gerir Pedidos Pendentes"
        ])
        
        with aba_app:
            DashboardView.renderizar_formulario()
        with aba_upload:
            UploadView.renderizar_zona_upload()
        with aba_user:
            UsersView.renderizar()
        with aba_analytics:
            AdminAnalyticsView.renderizar()
        with aba_admin:
            AdminView.renderizar_painel_admin()
            
    else:
        # Atleta visualiza 3 abas
        aba_app, aba_upload, aba_user = st.tabs([
            "Inserir Atividade", 
            "Sincronizar Ficheiro", 
            "Ranking & Utilizadores"
        ])
        
        with aba_app:
            DashboardView.renderizar_formulario()
        with aba_upload:
            UploadView.renderizar_zona_upload()
        with aba_user:
            UsersView.renderizar()  

    st.markdown("---")

    # Secção de Eventos Desportivos
    st.markdown("### Eventos Desportivos")
    termo = st.text_input("Pesquisar Eventos:", "próximos eventos desportivos em Portugal")

    if termo:
        renderizar_galeria_eventos(termo)