import streamlit as st
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.user_model import UserModel
from controllers.admin_controller import AdminController

class AdminView:
    @staticmethod
    def renderizar_formulario():
        """Ecrã provisório do atleta após o login."""
        st.markdown("### 💪 Área do Atleta - EcoFit")
        st.success("Sessão iniciada com sucesso! O teu acesso está ativo e validado.")
        st.write("Este é o teu painel principal. O ambiente de login e registo está operacional.")


    def login(nome_utilizador: str) -> bool:
        nome_limpo = nome_utilizador.strip()
        
        if not nome_limpo:
            st.warning("Por favor, introduz o teu nome.")
            return False
            
        # 1. Chamar o Modelo para procurar o utilizador na BD
        utilizador = UserModel.buscar_por_nome(nome_limpo)
        
        if not utilizador:
            st.error("Utilizador não encontrado. Solicita o teu acesso ao Administrador.")
            return False
            
        # 2. Aplicar a Regra de Segurança: Verificar o Estado de Acesso
        estado = utilizador.get('estado')

        if estado == 'Pendente':
            st.warning("⏳ O teu acesso ainda aguarda aprovação do Administrador.")
            return False

        if estado == 'Rejeitado':
            st.error("❌ O teu acesso foi recusado pela administração.")
            return False

        if estado != 'Aprovado':
            st.error("⚠️ Estado de conta inválido ou inativo.")
            return False

        # 3. Sessão autorizada
        st.session_state['utilizador_logado'] = utilizador
        st.success(f"Bem-vindo de volta, {utilizador['nome']}!")
        return True   