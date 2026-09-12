import streamlit as st
from supabase import create_client, Client

def get_supabase_client() -> Client:
    """
    Estabelece e retorna uma conexão segura com o Supabase
    suportando chaves diretas ou aninhadas em st.secrets.
    """
    try:
        supabase_url = None
        supabase_key = None

        # 1. Tentar obter da raiz do st.secrets
        if "SUPABASE_URL" in st.secrets and "SUPABASE_KEY" in st.secrets:
            supabase_url = st.secrets["SUPABASE_URL"]
            supabase_key = st.secrets["SUPABASE_KEY"]

        # 2. Tentar obter de dentro do bloco [config]
        elif "config" in st.secrets:
            supabase_url = st.secrets["config"].get("SUPABASE_URL")
            supabase_key = st.secrets["config"].get("SUPABASE_KEY")

        # 3. Tentar obter de dentro do bloco [supabase]
        elif "supabase" in st.secrets:
            supabase_url = st.secrets["supabase"].get("SUPABASE_URL")
            supabase_key = st.secrets["supabase"].get("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            raise KeyError("As chaves 'SUPABASE_URL' e 'SUPABASE_KEY' não foram encontradas em st.secrets.")

        # Criação do cliente de comunicação seguro via HTTPS
        supabase: Client = create_client(supabase_url, supabase_key)
        return supabase

    except Exception as e:
        st.error(f"Erro crítico de infraestrutura: Não foi possível ligar à Cloud. Detalhes: {e}")
        raise e