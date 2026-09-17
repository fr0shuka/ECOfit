import re
import time
import streamlit as st
from models.user_model import UserModel


class AdminController:

    @staticmethod
    def validar_nome_registo(nome: str) -> tuple[bool, str]:
        """
        Função unificada de validação do nome de utilizador.
        Retorna um tuplo: (True/False, "Mensagem de feedback para o utilizador")
        """
        if not nome:
            return False, "O campo do nome não pode estar vazio."
            
        # 1. Validação de formato (sem espaços ou carateres especiais inapropriados)
        padrao = r"^[a-zA-Z0-9À-ÿ]+$"
        if not re.match(padrao, nome):
            return False, "O nome não pode conter espaços (nem no início/fim) nem carateres especiais!"
            
        # 2. Validação de unicidade na base de dados
        nome_limpo = nome.strip()
        utilizador_existente = UserModel.buscar_por_nome(nome_limpo)
        if utilizador_existente:
            return False, "Este nome já está registado na plataforma. Escolha outro ou faça login."
            
        return True, "Nome válido e disponível!"
    
    @staticmethod
    def solicitar_registo(nome: str, palavra_passe: str = None) -> bool:
        """Processa a inserção do utilizador pendente associando o perfil padrão de registo (Atleta Free)."""
        sucesso_validacao, mensagem = AdminController.validar_nome_registo(nome)
        
        if not sucesso_validacao:
            st.error(mensagem)
            return False
            
        sucesso = UserModel.criar_utilizador_pendente(nome, palavra_passe)
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
        """Rejeita (elimina) o pedido de acesso do atleta."""
        if UserModel.eliminar_utilizador(utilizador_id):
            st.warning("Pedido de acesso rejeitado e removido.")
            time.sleep(1.5)
            st.rerun()
        else:
            st.error("Erro ao rejeitar o pedido.")
            time.sleep(1.5)

    @staticmethod
    def listar_pendentes():
        """Retorna a lista de utilizadores com estado 'Pendente'."""
        return UserModel.obter_utilizadores_por_estado("Pendente")

    @staticmethod
    def listar_todos_utilizadores():
        """Retorna todos os utilizadores registados na plataforma."""
        return UserModel.obter_todos_utilizadores()

    @staticmethod
    def processar_decisao(utilizador_id: int, aprovado: bool) -> bool:
        """Processa a decisão administrativa de aprovação ou rejeição de um utilizador."""
        novo_estado = "Aprovado" if aprovado else "Rejeitado"
        return UserModel.atualizar_estado(utilizador_id, novo_estado)

    @staticmethod
    def alterar_perfil_utilizador(utilizador_id: int, perfil_id: int) -> bool:
        """Atualiza a Foreign Key do perfil/plano do utilizador na tabela bd_utilizadores."""
        if not perfil_id:
            st.error("Selecione um perfil de acesso válido.")
            return False

        if UserModel.atualizar_perfil(utilizador_id, perfil_id):
            st.success("Perfil do utilizador atualizado com sucesso!")
            time.sleep(1.5)
            return True
        else:
            st.error("Erro ao atualizar o perfil do utilizador na base de dados.")
            return False

    @staticmethod
    def obter_todos_perfis():
        """Obtém a lista completa de perfis de acesso disponíveis (bd_perfis_acesso)."""
        return UserModel.obter_perfis_acesso()