import streamlit as st
from controllers.auth_controller import AuthController

class LoginView:
    @staticmethod
    def renderizar_ecran():
        """Desenha a interface visual do Login do EcoFit."""
        st.title("🌱 EcoFit - Plataforma de Atividade")
        st.subheader("Controlo de Acesso ao MVP")
        
        # Caixa de texto para o utilizador escrever o nome
        nome_introduzido = st.text_input("Nome do Atleta", placeholder="Ex: Miguel Borges")
        
        if st.button("Entrar na Plataforma", use_container_width=True):
            # Envia o dado para o Controller processar
            sucesso = AuthController.login(nome_introduzido)
            
            if sucesso:
                # Força o Streamlit a recarregar o ecrã para mostrar o painel principal
                st.rerun()