import re
import time
import streamlit as st
from models.user_model import UserModel

class AdminController:
    @staticmethod
    def validar_nome_registo(nome: str) -> tuple[bool, str]:
        """
        Função unificada de validação.
        Retorna um tuplo: (True/False, "Mensagem de feedback para o utilizador")
        """
        if not nome:
            return False, "O campo do nome não pode estar vazio."
            
        # 1. VALIDAÇÃO DE FORMATO DIRETA (Sem fazer strip primeiro)
        # Se houver um espaço no início ou fim, o Regex deteta e bloqueia logo aqui!
        padrao = r"^[a-zA-Z0-9À-ÿ]+$"
        if not re.match(padrao, nome):
            return False, "O nome não pode conter espaços (nem no início/fim) nem carateres especiais!"
            
        # 2. Validação de Existência na Base de Dados (Unicidade)
        nome_limpo = nome.strip()
        utilizador_existente = UserModel.buscar_por_nome(nome_limpo)
        if utilizador_existente:
            return False, "Este nome já está registado na plataforma. Escolha outro ou faça login."
            
        return True, "Nome válido e disponível!"
    
    @staticmethod
    def solicitar_registo(nome: str) -> bool:
        """Processa a inserção apenas se passar na validação de segurança final."""
        # 🛡️ BARREIRA DE SEGURANÇA FINAL: Revalida o dado antes de falar com a BD
        sucesso_validacao, mensagem = AdminController.validar_nome_registo(nome)
        
        if not sucesso_validacao:
            st.error(mensagem)
            return False
            
        sucesso = UserModel.criar_utilizador_pendente(nome)
        if sucesso:
            st.success("🎉 Pedido submetido! Aguarde a aprovação do Administrador.")
            time.sleep(1.5)
            return True
        else:
            st.error("Erro ao submeter o pedido. Tente novamente.")
            time.sleep(1.5)
            return False

    @staticmethod
    def aprovar_atleta(utilizador_id: int):
        """Aprova o acesso de um atleta pendente."""
        if UserModel.atualizar_estado(utilizador_id, 'Aprovado'):
            st.success("Atleta aprovado com sucesso!")
            time.sleep(1.5)
            st.rerun()
        else:
            st.error("Erro ao aprovar o atleta.")
            time.sleep(1.5)

    @staticmethod
    def rejeitar_atleta(utilizador_id: int):
        """Rejeita (elimina) o pedido de acesso."""
        if UserModel.eliminar_utilizador(utilizador_id):
            st.warning("Pedido de acesso rejeitado e removido.")
            time.sleep(1.5)
            st.rerun()
        else:
            st.error("Erro ao rejeitar o pedido.")
            time.sleep(1.5)


    @staticmethod
    def listar_pendentes():
        return UserModel.obter_utilizadores_por_estado("Pendente")

    @staticmethod
    def processar_decisao(utilizador_id: int, aprovado: bool) -> bool:
        novo_estado = "Aprovado" if aprovado else "Rejeitado"
        return UserModel.atualizar_estado_utilizador(utilizador_id, novo_estado)