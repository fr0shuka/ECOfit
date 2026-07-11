import streamlit as st
from controllers.auth_controller import AuthController
from controllers.admin_controller import AdminController

class LoginView:
    @staticmethod
    def renderizar_ecran():
        """Desenha a interface de autenticação e pedidos de registo do EcoFit."""
        st.title("EcoFIT - Plataforma de análise de atividades")
        
        # Abas para separar o login do pedido de novo registo
        aba_login, aba_registo = st.tabs(["🔑 Iniciar Sessão", "📝 Novo Registo"])
        
        with aba_login:
            st.subheader("Acesso à Plataforma")
            nome_login = st.text_input("Nome do Atleta", placeholder="Ex: MiguelBorges", key="input_login")
            
            if st.button("Entrar", use_container_width=True, key="btn_login"):
                if AuthController.login(nome_login):
                    st.rerun()
                    
        with aba_registo:
            st.subheader("Solicitar conta de atleta")
            st.caption("O teu acesso ficará pendente de validação por parte do Administrador.")
            nome_input = st.text_input("O teu Nome", placeholder="Ex: AnaSilva", key="input_registo")
            
            nome_valido = False
            
            # Se o utilizador começou a escrever, o Controlador entra em ação
            if nome_input:
                # O Controlador assume a responsabilidade de testar o input
                sucesso_validacao, mensagem = AdminController.validar_nome_registo(nome_input)
                
                if not sucesso_validacao:
                    st.error(mensagem)
                else:
                    st.success(mensagem)
                    nome_valido = True

            if st.button("Submeter Pedido de Acesso", use_container_width=True, key="btn_registo"):
                if nome_valido:
                    AdminController.solicitar_registo(nome_input)
                    # Pequeno truque para limpar a tela após o sucesso
                    st.rerun()
                else:
                    st.error("Não é possível submeter. Resolva os avisos no nome antes de avançar.")