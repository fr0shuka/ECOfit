import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.database import get_supabase_client

class UserModel:
    @staticmethod
    def buscar_por_nome(nome: str):
        """Busca um utilizador pelo nome exato."""
        supabase = get_supabase_client()
        resposta = supabase.table('bd_utilizadores').select('*').eq('nome', nome).execute()
        if resposta.data:
            return resposta.data[0]
        return None

    @staticmethod
    def criar_utilizador_pendente(nome: str) -> bool:
        """Regista um novo atleta com estado Pendente e perfil Atleta."""
        try:
            supabase = get_supabase_client()
            payload = {
                "nome": nome.strip(),
                "estado": "Pendente",
                "perfil": "Atleta"
            }
            supabase.table('bd_utilizadores').insert(payload).execute()
            return True
        except Exception as e:
            print(f"Erro ao criar utilizador pendente: {e}")
            return False

    @staticmethod
    def listar_pendentes():
        """Retorna uma lista com todos os utilizadores em estado Pendente."""
        try:
            supabase = get_supabase_client()
            resposta = supabase.table('bd_utilizadores').select('*').eq('estado', 'Pendente').execute()
            return resposta.data or []
        except Exception as e:
            print(f"Erro ao listar pendentes: {e}")
            return []

    @staticmethod
    def atualizar_estado(utilizador_id: int, novo_estado: str) -> bool:
        """Atualiza o estado de um utilizador (ex: para 'Aprovado')."""
        try:
            supabase = get_supabase_client()
            supabase.table('bd_utilizadores').update({"estado": novo_estado}).eq("utilizador_id", utilizador_id).execute()
            return True
        except Exception as e:
            print(f"Erro ao atualizar estado: {e}")
            return False

    @staticmethod
    def eliminar_utilizador(utilizador_id: int) -> bool:
        """Remove um pedido de registo da base de dados."""
        try:
            supabase = get_supabase_client()
            supabase.table('bd_utilizadores').delete().eq("utilizador_id", utilizador_id).execute()
            return True
        except Exception as e:
            print(f"Erro ao eliminar utilizador: {e}")
            return False