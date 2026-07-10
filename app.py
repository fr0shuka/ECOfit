import streamlit as st
from views.login_view import LoginView

# Se o utilizador não está logado, mostra o ecrã de login
if 'utilizador_logado' not in st.session_state:
    LoginView.renderizar_ecran()
else:
    # Se já estiver logado, mostra o conteúdo do MVP (vamos criar a seguir)
    utilizador = st.session_state['utilizador_logado']
    st.title(f"💪 Painel do Atleta: {utilizador['nome']}")
    st.info(f"Perfil: {utilizador['perfil']} | Estado: {utilizador['estado']}")
    
    if st.button("Sair"):
        from controllers.auth_controller import AuthController
        AuthController.logout()
        st.rerun()