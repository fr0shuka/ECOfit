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

    @staticmethod
    def obter_ficheiros_carregados(utilizador_id: int) -> list:
        """Procura os registos de atividades originados por ficheiro."""
        try:
            supabase = get_supabase_client()
            
            # Procura na bd_atividades apenas os registos onde tipo_insercao é 'ficheiro' ou 'upload'
            resposta = supabase.table("bd_atividades") \
                .select("data_registo, km_corridos, minutos_treino, pontos_ganhos, tipo_insercao") \
                .eq("utilizador_id", utilizador_id) \
                .order("data_registo", desc=True) \
                .execute()
                
            return resposta.data or []
        except Exception as e:
            print(f"❌ Erro ao procurar histórico de atividades/ficheiros: {e}")
            return []