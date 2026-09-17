import sys
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

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
from controllers.auth_controller import AuthController

# Configuração da página
st.set_page_config(
    page_title="ecoFIT", 
    page_icon="🌱", 
    layout="centered"
)

# Fluxo de navegação baseado no estado da sessão
if 'utilizador_logado' not in st.session_state:
    LoginView.renderizar_ecran()
else:
    utilizador = st.session_state['utilizador_logado']
    
    # Barra Lateral
    with st.sidebar:
        st.markdown(f"### Olá, **{utilizador['nome']}**")
        st.caption(f"Perfil: {utilizador.get('perfil', 'Atleta')} | Estado: {utilizador.get('estado', 'Aprovado')}")
        st.markdown("---")

        menu_opcao = st.sidebar.radio(
            "Navegação",
            ["Painel Principal", "Os Meus Treinos"],
            index=0
        )
        
        st.markdown("---")
        
        # Expandir: Alterar Palavra-Passe
        with st.expander("🔑 Alterar Palavra-passe"):
            with st.form(key="form_alterar_passe_sidebar", clear_on_submit=True):
                p_atual = st.text_input("Palavra-passe Atual", type="password", key="p_atual")
                p_nova = st.text_input("Nova Palavra-passe", type="password", key="p_nova")
                p_conf = st.text_input("Confirmar Nova", type="password", key="p_conf")
                
                btn_guardar_passe = st.form_submit_button("Atualizar", use_container_width=True)
                
                if btn_guardar_passe:
                    u_id = utilizador.get('utilizador_id') or utilizador.get('id')
                    if AuthController.alterar_palavra_passe(u_id, p_atual, p_nova, p_conf):
                        st.rerun()

        # Expandir: Plano de Subscrição
        with st.expander("⭐ Plano de Subscrição"):
            perfil_atual = utilizador.get('perfil', 'Atleta')
            st.write(f"**Plano Atual:** `{perfil_atual}`")
            
            # Opções de subscrição
            opcoes_plano = ["Atleta Free", "Atleta Pro"]
            index_padrao = 1 if "Pro" in perfil_atual else 0
            
            novo_plano = st.selectbox(
                "Mudar de Plano:", 
                opcoes_plano, 
                index=index_padrao,
                key="select_plano_sub"
            )
            
            if st.button("Confirmar Alteração de Plano", use_container_width=True, key="btn_mudar_plano"):
                if novo_plano == perfil_atual:
                    st.info("Já se encontra neste plano.")
                else:
                    u_id = utilizador.get('utilizador_id') or utilizador.get('id')
                    if AuthController.alterar_plano_subscricao(u_id, novo_plano):
                        st.rerun()

        st.markdown("---")
            
        # Widget meteorológico
        renderizar_meteo_sidebar()

        if st.button("Terminar Sessão (Logout)", use_container_width=True):
            AuthController.logout()
            st.rerun()

    # Cabeçalho Principal
    st.title("Plataforma ecoFIT")

    if menu_opcao == "Os Meus Treinos":
        usr_id = utilizador.get('id') or utilizador.get('utilizador_id')
        usr_nome = utilizador.get('nome', 'Atleta')
        MyTrainingsView.renderizar(utilizador_id=usr_id, utilizador_nome=usr_nome)
        
    else:
        # Navegação por Perfil
        if utilizador.get('perfil') == 'Admin':
            # Admin visualiza 5 abas (incluindo a Analítica Global)
            aba_app, aba_upload, aba_user, aba_analytics, aba_admin = st.tabs([
                "Inserir Atividade", 
                "Sincronizar Ficheiro", 
                "Ranking & Utilizadores", 
                "Analítica Global",
                "Menu Admin"
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