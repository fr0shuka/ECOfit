import streamlit as st
from controllers.auth_controller import AuthController
from controllers.admin_controller import AdminController

class LoginView:
    @staticmethod
    def renderizar_ecran():
        """Desenha a interface de autenticação e pedidos de registo do EcoFit."""
        st.title("🌱 EcoFit - Plataforma de Atividade")
        
        # Abas para separar o login do pedido de novo registo
        aba_login, aba_registo = st.tabs(["🔑 Iniciar Sessão", "📝 Pedir Novo Registo"])
        
        with aba_login:
            st.subheader("Acesso à Plataforma")
            nome_login = st.text_input("Nome do Atleta", placeholder="Ex: Miguel Borges", key="input_login")
            
            if st.button("Entrar", use_container_width=True, key="btn_login"):
                if AuthController.login(nome_login):
                    st.rerun()
                    
        with aba_registo:
            st.subheader("Solicitar Conta de Atleta")
            st.caption("O teu acesso ficará pendente de validação por parte do Administrador.")
            nome_novo = st.text_input("O teu Nome Completo", placeholder="Ex: Ana Silva", key="input_registo")
            
            if st.button("Submeter Pedido de Acesso", use_container_width=True, key="btn_registo"):
                AdminController.solicitar_registo(nome_novo)