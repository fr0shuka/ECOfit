import streamlit as st
from views.login_view import LoginView
from views.dashboard_view import DashboardView
from views.admin_view import AdminView

st.set_page_config(page_title="EcoFIT", page_icon="🌱", layout="wide")

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
        
        if st.button("Terminar Sessão (Logout)", use_container_width=True):
            from controllers.auth_controller import AuthController
            AuthController.logout()
            st.rerun()

    st.title("💪 Painel de Performance EcoFit")
    
    # Se for Administrador, mostra a opção de gerir acessos na barra principal ou abas
    if utilizador['perfil'] == 'Admin':
        aba_app, aba_admin = st.tabs(["Inserir Atividade", "Gerir pedidos Pendentes"])
        with aba_app:
            DashboardView.renderizar_formulario()
        with aba_admin:
            AdminView.renderizar_painel_admin()
    else:
        # Atleta normal vê apenas o formulário de atividades
        DashboardView.renderizar_formulario()