import streamlit as st
from views.login_view import LoginView
from views.dashboard_view import DashboardView
from views.admin_view import AdminView
from views.upload_view import UploadView

# Configuração centrada e aplicação do Logotipo no separador do navegador
st.set_page_config(
    page_title="EcoFIT", 
    page_icon="🌱", 
    layout="centered"             # Força o layout a ficar centrado e compacto
)

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
    
    if utilizador['perfil'] == 'Admin':
        # Admin vê 3 abas agora
        aba_app, aba_upload, aba_admin = st.tabs(["🚀 Inserir Atividade", "📥 Sincronizar Ficheiro", "🛡️ Gerir Pedidos Pendentes"])
        with aba_app:
            DashboardView.renderizar_formulario()
        with aba_upload:
            UploadView.renderizar_zona_upload()
        with aba_admin:
            AdminView.renderizar_painel_admin()
    else:
        # Atleta normal vê 2 abas
        aba_app, aba_upload = st.tabs(["🚀 Inserir Atividade", "📥 Sincronizar Ficheiro"])
        with aba_app:
            DashboardView.renderizar_formulario()
        with aba_upload:
            UploadView.renderizar_zona_upload()