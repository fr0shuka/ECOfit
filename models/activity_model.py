import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.database import get_supabase_client

class ActivityModel:
    @staticmethod
    def salvar_atividade(dados_atividade: dict) -> bool:
        """Insere um novo registo de treino na tabela bd_atividades do Supabase."""
        try:
            supabase = get_supabase_client()
            supabase.table('bd_atividades').insert(dados_atividade).execute()
            return True
        except Exception as e:
            print(f"Erro ao gravar atividade no Supabase: {e}")
            return False