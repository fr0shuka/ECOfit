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

# Injeção de Estilos Globais para a EcoFit
st.markdown("""
    <style>
        /* 1. BOTÕES PRIMÁRIOS E SUBMIT DO FORMULÁRIO */
        button[data-testid="stFormSubmitButton"] > button,
        button[data-testid="stFormSubmitButton"] > button[kind="primary"],
        button[kind="primary"],
        button[data-testid="stBaseButton-primary"],
        .stButton > button[kind="primary"] {
            background-color: #10b981 !important;
            border-color: #10b981 !important;
            color: #ffffff !important;
            font-weight: 600 !important;
        }

        button[data-testid="stFormSubmitButton"] > button:hover,
        button[data-testid="stFormSubmitButton"] > button[kind="primary"]:hover,
        button[kind="primary"]:hover,
        button[data-testid="stBaseButton-primary"]:hover,
        .stButton > button[kind="primary"]:hover {
            background-color: #059669 !important;
            border-color: #059669 !important;
            color: #ffffff !important;
        }

        /* 2. ABAS (st.tabs) - VERDE ECOFIT */
        /* Cor do texto na Aba Selecionada */
        div[data-testid="stTabs"] button[aria-selected="true"],
        div[data-testid="stTabs"] button[aria-selected="true"] p,
        button[data-baseweb="tab"][aria-selected="true"],
        button[data-baseweb="tab"][aria-selected="true"] p {
            color: #10b981 !important;
            font-weight: 600 !important;
        }

        /* Linha inferior de destaque da Aba Ativa */
        div[data-testid="stTabs"] [data-baseweb="tab-highlight"],
        div[data-baseweb="tab-highlight"] {
            background-color: #10b981 !important;
        }

        /* Cor ao passar o rato (Hover) em qualquer aba */
        div[data-testid="stTabs"] button[aria-selected="false"]:hover,
        div[data-testid="stTabs"] button[aria-selected="false"]:hover p {
            color: #34d399 !important;
        }

        /* Border / Focus verde nos campos de entrada */
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