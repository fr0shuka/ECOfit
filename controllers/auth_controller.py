import sys
import os
import time
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.user_model import UserModel
from controllers.admin_controller import AdminController

class AuthController:
    @staticmethod
    def login(nome_utilizador: str, palavra_passe: str) -> bool:
        """Processa o login do utilizador validando nome e palavra-passe."""
        nome_limpo = nome_utilizador.strip()
        passe_limpa = palavra_passe.strip()
        
        if not nome_limpo or not passe_limpa:
            st.warning("Por favor, preenche o nome e a palavra-passe.")
            return False
            
        # 1. Procurar utilizador por nome na BD
        utilizador = UserModel.buscar_por_nome(nome_limpo)
        
        if not utilizador:
            st.error("Utilizador não encontrado. Solicita o teu acesso ao Administrador.")
            return False
            
        # 2. Validar a Palavra-passe
        # Suporta contas antigas sem palavra-passe definida ou valida a correspondência exata
        pwd_guardada = utilizador.get('palavra_passe')
        if pwd_guardada and pwd_guardada != passe_limpa:
            st.error("🔒 Palavra-passe incorreta.")
            return False

        # 3. Verificar o Estado de Acesso
        estado = utilizador.get('estado')

        if estado == 'Pendente':
            st.warning("⏳ O teu acesso ainda aguarda aprovação do Administrador.")
            time.sleep(1.5)
            return False

        if estado == 'Rejeitado':
            st.error("❌ O teu acesso foi recusado pela administração.")
            time.sleep(1.5)
            return False

        if estado != 'Aprovado':
            st.error("⚠️ Estado de conta inválido ou inativo.")
            time.sleep(1.5)
            return False

        # 4. Sessão autorizada
        st.session_state['utilizador_logado'] = utilizador
        st.success(f"Bem-vindo de volta, {utilizador['nome']}!")
        time.sleep(1)
        return True

    @staticmethod
    def logout():
        """Limpa a sessão atual."""
        if 'utilizador_logado' in st.session_state:
            del st.session_state['utilizador_logado']

    @staticmethod
    def solicitar_registo(nome: str, palavra_passe: str) -> bool:
        """Processa o registo do atleta com palavra-passe."""
        if not palavra_passe or len(palavra_passe.strip()) < 4:
            st.error("A palavra-passe deve ter pelo menos 4 carateres.")
            return False

        sucesso_validacao, mensagem = AdminController.validar_nome_registo(nome)
        
        if not sucesso_validacao:
            st.error(mensagem)
            return False
            
        sucesso = UserModel.criar_utilizador_pendente(nome, palavra_passe)
        if sucesso:
            st.success("🎉 Pedido submetido com sucesso! Aguarde a aprovação do Administrador.")
            time.sleep(1.5)
            return True
        else:
            st.error("Erro ao submeter o pedido. Tente novamente.")
            time.sleep(1.5)
            return False