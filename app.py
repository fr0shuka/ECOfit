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
# Injeção de Estilos Globais para toda a aplicação EcoFit
st.markdown("""
    <style>
        /* 1. BOTÕES PRIMÁRIOS (Inserir / Submeter Atividades) */
        button[data-testid="baseButton-primary"],
        div.stButton > button[kind="primary"] {
            background-color: #10b981 !important;
            border-color: #10b981 !important;
            color: #ffffff !important;
            font-weight: 600;
        }

        button[data-testid="baseButton-primary"]:hover,
        div.stButton > button[kind="primary"]:hover {
            background-color: #059669 !important;
            border-color: #059669 !important;
        }

        /* 2. SEPARADORES (TABS) EM TOM VERDE */
        /* Texto da tab ativa */
        button[data-baseweb="tab"][aria-selected="true"] p {
            color: #10b981 !important;
            font-weight: 600 !important;
        }

        /* Linha inferior da tab ativa */
        div[data-baseweb="tab-highlight"] {
            background-color: #10b981 !important;
        }

        /* Tab ao passar o rato (hover) */
        button[data-baseweb="tab"]:hover p {
            color: #34d399 !important;
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