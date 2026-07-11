import streamlit as st
from models.user_model import UserModel

class AdminController:
    @staticmethod
    def validar_nome_registo(nome: str) -> tuple[bool, str]:
        """
        Função unificada de validação.
        Retorna um tuplo: (True/False, "Mensagem de feedback para o utilizador")
        """
        nome_limpo = nome.strip()
        
        if not nome_limpo:
            return False, "O campo do nome não pode estar vazio."
            
        # 1. Validação de Formato (Regex)
        padrao = r"^[a-zA-Z0-9À-ÿ]+$"
        if not re.match(padrao, nome_limpo):
            return False, "O nome não pode conter espaços nem carateres especiais!"
            
        # 2. Validação de Existência na Base de Dados (Unicidade)
        utilizador_existente = UserModel.buscar_por_nome(nome_limpo)
        if utilizador_existente:
            return False, "Este nome já está registado na plataforma. Escolha outro ou faça login."
            
        # Se passou em ambos os testes
        return True, "Nome válido e disponível!"
    
    @staticmethod
    def solicitar_registo(nome: str) -> bool:
        """Processa a inserção após validação bem-sucedida."""
        sucesso = UserModel.criar_utilizador_pendente(nome)
        if sucesso:
            st.success("🎉 Pedido submetido! Aguarde a aprovação do Administrador.")
            return True
        else:
            st.error("Erro ao submeter o pedido. Tente novamente.")
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