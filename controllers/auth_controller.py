import streamlit as st
from models.user_model import UserModel

class AuthController:
    @staticmethod
    def login(nome_utilizador: str) -> bool:
        """
        Processa a tentativa de login aplicando as regras de negócio do MVP.
        """
        if not nome_utilizador.strip():
            st.warning("Por favor, introduz o teu nome.")
            return False
            
        # 1. Chamar o Modelo para procurar o utilizador na BD
        utilizador = UserModel.buscar_por_nome(nome_utilizador.strip())
        
        if not utilizador:
            st.error("Utilizador não encontrado. Solicita o teu acesso ao Administrador.")
            return False
            
        # 2. Aplicar a Regra de Segurança: Verificar o Estado
        if utilizador['estado'] == 'Pendente':
            st.error("⏳ O teu acesso ainda aguarda aprovação do Administrador.")
            return False
            
        # 3. Se passou nas validações, guarda na sessão do Streamlit
        st.session_state['utilizador_logado'] = utilizador
        st.success(f"Bem-vindo de volta, {utilizador['nome']}!")
        return True

    @staticmethod
    def logout():
        """Limpa a sessão atual."""
        if 'utilizador_logado' in st.session_state:
            del st.session_state['utilizador_logado']