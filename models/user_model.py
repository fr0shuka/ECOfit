import sys
import os

# Garante que o Python encontra a pasta 'config'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.database import get_supabase_client

class UserModel:
    @staticmethod
    def buscar_por_nome(nome: str):
        """
        Consulta a tabela bd_utilizadores no Supabase pelo nome.
        Retorna o dicionário do utilizador se existir, ou None se não existir.
        """
        supabase = get_supabase_client()
        
        # Faz o SELECT * WHERE nome = nome
        resposta = supabase.table('bd_utilizadores').select('*').eq('nome', nome).execute()
        
        # O Supabase retorna os registos dentro de .data (que é uma lista)
        if resposta.data:
            return resposta.data[0] # Retorna o primeiro utilizador encontrado
        
        return None