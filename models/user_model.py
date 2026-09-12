import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.database import get_supabase_client

class UserModel:
    ############ 
    # READ 
    ############ 
    @staticmethod
    def buscar_por_nome(nome: str):
        """Busca um utilizador pelo nome exato."""
        try:
            supabase = get_supabase_client()
            resposta = supabase.table('bd_utilizadores').select('*').eq('nome', nome.strip()).execute()
            return resposta.data[0] if resposta.data else None
        except Exception as e:
            print(f"Erro ao buscar utilizador por nome: {e}")
            return None

    @staticmethod
    def obter_por_id(utilizador_id: int):
        """Busca os dados completos de um utilizador pelo seu ID (utilizador_id ou id)."""
        try:
            supabase = get_supabase_client()
            # Tenta filtrar primeiro por utilizador_id e faz fallback para id
            resposta = supabase.table('bd_utilizadores').select('*').eq('utilizador_id', utilizador_id).execute()
            if not resposta.data:
                resposta = supabase.table('bd_utilizadores').select('*').eq('id', utilizador_id).execute()
            return resposta.data[0] if resposta.data else None
        except Exception as e:
            print(f"Erro ao buscar utilizador por ID: {e}")
            return None

    @staticmethod
    def obter_nome_por_id(utilizador_id: int) -> str:
        """Devolve diretamente o nome do utilizador pelo ID para nomes de ficheiros ou relatórios."""
        utilizador = UserModel.obter_por_id(utilizador_id)
        if utilizador and 'nome' in utilizador:
            return utilizador['nome']
        return "Atleta"

    @staticmethod
    def listar_todos() -> list:
        """Retorna todos os utilizadores (aprovados, pendentes, etc.) para a Gestão de Admin."""
        try:
            supabase = get_supabase_client()
            resposta = supabase.table('bd_utilizadores').select('*').order('utilizador_id', desc=False).execute()
            return resposta.data or []
        except Exception as e:
            print(f"Erro ao listar todos os utilizadores: {e}")
            return []

    @staticmethod
    def obter_utilizadores_por_estado(estado: str = "Pendente") -> list:
        """Retorna utilizadores filtrados pelo estado (ex: 'Pendente', 'Aprovado')."""
        try:
            supabase = get_supabase_client()
            resposta = supabase.table("bd_utilizadores") \
                .select("*") \
                .ilike("estado", estado) \
                .execute()
            return resposta.data or []
        except Exception as e:
            print(f"Erro ao obter utilizadores por estado: {e}")
            return []

    @staticmethod
    def obter_utilizadores_e_atividades():
        """Procura utilizadores aprovados e todas as atividades para o ranking."""
        try:
            supabase = get_supabase_client()
            res_users = supabase.table("bd_utilizadores").select("*").ilike("estado", "aprovado").execute()
            res_atividades = supabase.table("bd_atividades").select("*").execute()
            
            users = res_users.data or []
            atividades = res_atividades.data or []
            return users, atividades
        except Exception as e:
            print(f"❌ ERRO SUPABASE AO OBTER DADOS DO RANKING: {e}")
            return [], []

    ###########
    # CREATE / UPDATE / DELETE
    ########### 
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
    def atualizar_estado(utilizador_id: int, novo_estado: str) -> bool:
        """Atualiza o estado de um utilizador (ex: 'Aprovado', 'Rejeitado', 'Pendente')."""
        try:
            supabase = get_supabase_client()
            supabase.table("bd_utilizadores").update({"estado": novo_estado}).eq("utilizador_id", utilizador_id).execute()
            return True
        except Exception as e:
            print(f"❌ ERRO AO ATUALIZAR ESTADO: {e}")
            return False

    @staticmethod
    def atualizar_perfil(utilizador_id: int, novo_perfil: str) -> bool:
        """Atualiza o perfil/role de um utilizador (ex: 'Atleta', 'Admin')."""
        try:
            supabase = get_supabase_client()
            supabase.table("bd_utilizadores").update({"perfil": novo_perfil}).eq("utilizador_id", utilizador_id).execute()
            return True
        except Exception as e:
            print(f"❌ ERRO AO ATUALIZAR PERFIL: {e}")
            return False

    @staticmethod
    def eliminar_utilizador(utilizador_id: int) -> bool:
        """Elimina um utilizador e remove as suas atividades associadas."""
        try:
            supabase = get_supabase_client()
            # 1. Limpa primeiro as atividades associadas (evita erros de FK)
            supabase.table('bd_atividades').delete().eq("utilizador_id", utilizador_id).execute()
            # 2. Elimina o utilizador
            supabase.table('bd_utilizadores').delete().eq("utilizador_id", utilizador_id).execute()
            return True
        except Exception as e:
            print(f"Erro ao eliminar utilizador: {e}")
            return False