import sys
import os
import streamlit as st

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
            st.error(f"Erro ao gravar atividade no Supabase: {e}")
            return False

    @staticmethod
    def buscar_por_utilizador(utilizador_id: int) -> list:
        """Recupera todas as atividades registadas para um utilizador específico no Supabase."""
        try:
            supabase = get_supabase_client()
            resposta = supabase.table('bd_atividades').select('*').eq('utilizador_id', utilizador_id).execute()
            return resposta.data or []
        except Exception as e:
            st.error(f"Erro ao procurar atividades no Supabase: {e}")
            return []