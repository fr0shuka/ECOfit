import sys
import os
import time
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.user_model import UserModel

class AuthController:
    @staticmethod
    def login(nome_utilizador: str) -> bool:
        """Processa o login do utilizador com base no nome fornecido."""
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
            time.sleep(2)
            return False

        if estado == 'Rejeitado':
            st.error("❌ O teu acesso foi recusado pela administração.")
            time.sleep(2)
            return False

        if estado != 'Aprovado':
            st.error("⚠️ Estado de conta inválido ou inativo.")
            time.sleep(2)
            return False

        # 3. Sessão autorizada
        st.session_state['utilizador_logado'] = utilizador
        st.success(f"Bem-vindo de volta, {utilizador['nome']}!")
        time.sleep(2)
        return True

    @staticmethod
    def logout():
        """Limpa a sessão atual."""
        if 'utilizador_logado' in st.session_state:
            del st.session_state['utilizador_logado']


    @staticmethod
    def obter_nome_por_id(utilizador_id: int) -> str:
        """Procura o nome do utilizador na BD através do seu ID."""
        try:
            # Aceder à tabela bd_utilizadores no Supabase
            resposta = supabase.table("bd_utilizadores").select("nome").eq("id", utilizador_id).execute()
            
            if resposta.data and len(resposta.data) > 0:
                return resposta.data[0].get("nome", "Atleta")
        except Exception as e:
            print(f"⚠️ Erro ao procurar nome do utilizador: {e}")
            
        return "Atleta" 