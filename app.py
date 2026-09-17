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
from models.user_model import UserModel

# Configuração da página
st.set_page_config(
    page_title="ecoFIT", 
    page_icon="🌱", 
    layout="centered"
)

# Auxiliar para obter o nome do perfil relacional
def obter_nome_perfil(u: dict) -> str:
    if not u:
        return "Atleta Free"
    info_tipo = u.get('bd_tipos_utilizador') or {}
    return info_tipo.get('nome') or info_tipo.get('descricao') or u.get('perfil') or "Atleta Free"

# Auxiliar para verificar permissão de Admin
def e_administrador(u: dict) -> bool:
    if not u:
        return False
    if u.get('tipo_id') == 4:
        return True
    nome_perfil = str(obter_nome_perfil(u)).lower()
    return nome_perfil == 'admin'


# Fluxo de navegação baseado no estado da sessão
if 'utilizador_logado' not in st.session_state:
    LoginView.renderizar_ecran()
else:
    # Recarregar utilizador da BD para garantir a sessão sincronizada
    u_sessao = st.session_state['utilizador_logado']
    u_id = u_sessao.get('utilizador_id') or u_sessao.get('id')
    
    utilizador_fresco = UserModel.obter_por_id(u_id)
    if utilizador_fresco:
        st.session_state['utilizador_logado'] = utilizador_fresco
        utilizador = utilizador_fresco
    else:
        utilizador = u_sessao

    perfil_nome_exibicao = obter_nome_perfil(utilizador)
    is_admin = e_administrador(utilizador)
    
    # Barra Lateral
    with st.sidebar:
        st.markdown(f"### Olá, **{utilizador['nome']}**")
        st.caption(f"Perfil: **{perfil_nome_exibicao}** | Estado: {utilizador.get('estado', 'Aprovado')}")
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
                
                btn_guardar_passe = st.form_submit_button("Atualizar", width="stretch")
                
                if btn_guardar_passe:
                    if AuthController.alterar_palavra_passe(u_id, p_atual, p_nova, p_conf):
                        st.rerun()

        # Expandir: Plano de Subscrição
        with st.expander("⭐ Plano de Subscrição"):
            st.write(f"**Plano Atual:** `{perfil_nome_exibicao}`")
            
            opcoes_plano = ["Atleta Free", "Atleta Pro"]
            index_padrao = 1 if "pro" in perfil_nome_exibicao.lower() else 0
            
            novo_plano = st.selectbox(
                "Mudar de Plano:", 
                opcoes_plano, 
                index=index_padrao,
                key="select_plano_sub"
            )
            
            if st.button("Confirmar Alteração de Plano", width="stretch", key="btn_mudar_plano"):
                if novo_plano == perfil_nome_exibicao:
                    st.info("Já se encontra neste plano.")
                else:
                    tipo_id_alvo = 2 if "pro" in novo_plano.lower() else 1
                    if AuthController.alterar_plano_subscricao(u_id, tipo_id_alvo):
                        st.rerun()

        # Widget meteorológico
        renderizar_meteo_sidebar()

        if st.button("Terminar Sessão (Logout)", width="stretch"):
            AuthController.logout()
            st.rerun()

    # Cabeçalho Principal
    st.title("Plataforma ecoFIT")

    if menu_opcao == "Os Meus Treinos":
        usr_nome = utilizador.get('nome', 'Atleta')
        MyTrainingsView.renderizar(utilizador_id=u_id, utilizador_nome=usr_nome)
        
    else:
        # Navegação por Perfil
        if is_admin:
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