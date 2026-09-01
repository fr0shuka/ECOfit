import streamlit as st
from views.login_view import LoginView
from views.dashboard_view import DashboardView
from views.admin_view import AdminView
from views.upload_view import UploadView
from views.users_view import UsersView
from views.admin_analytics_view import AdminAnalyticsView
from views.my_trainings_view import MyTrainingsView
from views.components import renderizar_meteo_sidebar
from services.news_service import renderizar_galeria_eventos
from controllers.activity_controller import ActivityController

# Configuração da página
st.set_page_config(
    page_title="ecoFIT", 
    page_icon="🌱", 
    layout="centered"
)

def inicializar_estado():
    """Garante que todos os controladores e estado inicial existem no session_state."""
    if 'controller_atividades' not in st.session_state:
        st.session_state.controller_atividades = ActivityController()


inicializar_estado()

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

        menu_opcao = st.sidebar.radio(
            "Navegação",
            ["Painel Principal", "Os Meus Treinos"],
            index=0
        )
            
        # Widget meteorológico
        renderizar_meteo_sidebar()

        if st.button("Terminar Sessão (Logout)", use_container_width=True):
            from controllers.auth_controller import AuthController
            AuthController.logout()
            st.rerun()

    # Cabeçalho Principal
    st.title("Plataforma ecoFIT")

    if menu_opcao == "Os Meus Treinos":
        # Procura por 'id', 'utilizador_id' ou 'id_utilizador'
        usr_id = utilizador.get('id') or utilizador.get('utilizador_id') or utilizador.get('id_utilizador')
        
        MyTrainingsView.renderizar(
            utilizador_id=usr_id, 
            controller_atividades=st.session_state.get('controller_atividades')
        )
    else:
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