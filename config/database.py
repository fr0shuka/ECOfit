import streamlit as st
from supabase import create_client, Client

def get_supabase_client() -> Client:
    """
    Estabelece e retorna uma conexão segura com a base de dados online (Supabase)
    utilizando as credenciais protegidas do ecossistema Streamlit.
    """
    try:
        # O Streamlit vai buscar estas chaves ao secrets.toml (localmente)
        # ou às configurações de ambiente do painel web (quando estiver LIVE)
        supabase_url = st.secrets["SUPABASE_URL"]
        supabase_key = st.secrets["SUPABASE_KEY"]
        
        # Criação do cliente de comunicação seguro via HTTPS
        supabase: Client = create_client(supabase_url, supabase_key)
        return supabase
        
    except Exception as e:
        st.error(f"Erro crítico de infraestrutura: Não foi possível ligar à Cloud. Detalhes: {e}")
        raise e