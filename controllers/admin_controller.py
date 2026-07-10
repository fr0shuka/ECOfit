import streamlit as st
from models.user_model import UserModel

class AdminController:
    @staticmethod
    def solicitar_registo(nome: str) -> bool:
        """Processa o pedido de um novo atleta para entrar no sistema."""
        if not nome.strip():
            st.warning("Introduz um nome válido para o registo.")
            return False
            
        # Verifica se o nome já existe
        existente = UserModel.buscar_por_nome(nome)
        if existente:
            st.error("Esse nome já se encontra registado no sistema. Tenta fazer login.")
            return False
            
        sucesso = UserModel.criar_utilizador_pendente(nome)
        if sucesso:
            st.success("🎉 Pedido submetido com sucesso! Aguarda a aprovação do Administrador.")
            return True
        else:
            st.error("Erro ao submeter o pedido. Tenta novamente.")
            return False

    @staticmethod
    def aprovar_atleta(utilizador_id: int):
        """Aprova o acesso de um atleta pendente."""
        if UserModel.atualizar_estado(utilizador_id, 'Aprovado'):
            st.success("Atleta aprovado com sucesso!")
            st.rerun()
        else:
            st.error("Erro ao aprovar o atleta.")

    @staticmethod
    def rejeitar_atleta(utilizador_id: int):
        """Rejeita (elimina) o pedido de acesso."""
        if UserModel.eliminar_utilizador(utilizador_id):
            st.warning("Pedido de acesso rejeitado e removido.")
            st.rerun()
        else:
            st.error("Erro ao rejeitar o pedido.")