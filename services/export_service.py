import pandas as pd
import io
import streamlit as st
from supabase import Client, create_client

def gerar_csv_completo_powerbi(atividades_globais, utilizadores_globais=None):
    """
    Processa todos os registos globais e mapeia o nome do utilizador 
    baseando-se estritamente na chave 'utilizador_id' e 'nome' da tabela bd_utilizadores.
    """
    if not atividades_globais:
        return None
    
    df = pd.DataFrame(atividades_globais)
    
    # Criar um dicionário de mapeamento exato: utilizador_id -> nome
    mapa_nomes = {}
    if utilizadores_globais:
        for u in utilizadores_globais:
            u_id = u.get('utilizador_id')
            u_nome = u.get('nome')
            
            if u_id is not None and u_nome:
                mapa_nomes[str(u_id)] = u_nome

    # Garantir que a coluna 'utilizador_id' existe e mapear diretamente para o campo 'nome'
    if 'utilizador_id' in df.columns and mapa_nomes:
        df['nome'] = df['utilizador_id'].astype(str).map(mapa_nomes).fillna('Desconhecido')
    else:
        # Fallback caso já venha preenchido ou não exista o mapa
        df['nome'] = df.get('nome', 'Desconhecido')

    # Conversões e normalizações de colunas numéricas
    df['distancia_km'] = pd.to_numeric(df.get('distancia_km', 0), errors='coerce').fillna(0.0)
    df['minutos_treino'] = pd.to_numeric(df.get('minutos_treino', 0), errors='coerce').fillna(0)
    df['pontos_ganhos'] = pd.to_numeric(df.get('pontos_ganhos', 0), errors='coerce').fillna(0)
    df['copos_agua'] = pd.to_numeric(df.get('copos_agua', 0), errors='coerce').fillna(0)
    df['pecas_fruta'] = pd.to_numeric(df.get('pecas_fruta', 0), errors='coerce').fillna(0)
    df['temperatura'] = pd.to_numeric(df.get('temperatura', 0), errors='coerce').fillna(0.0)
    
    # Garantir e tratar colunas de hábitos
    if 'copos_agua' not in df.columns:
        df['copos_agua'] = 0
    else:
        df['copos_agua'] = pd.to_numeric(df['copos_agua'], errors='coerce').fillna(0)
        
    if 'porcoes_fruta' not in df.columns and 'fruta' in df.columns:
        df['porcoes_fruta'] = df['fruta']
    elif 'porcoes_fruta' not in df.columns:
        df['porcoes_fruta'] = 0
    else:
        df['porcoes_fruta'] = pd.to_numeric(df['porcoes_fruta'], errors='coerce').fillna(0)

    # Classificação inteligente do tipo de registo
    def classificar_tipo(row):
        if row['distancia_km'] > 0 or row['minutos_treino'] > 0:
            return 'Treino / Atividade Física'
        else:
            return 'Hábito / Hidratação'
            
    df['tipo_registo'] = df.apply(classificar_tipo, axis=1)

    # Tratamento de datas e colunas auxiliares para DAX no Power BI (Ano, Mês, Dia da Semana)
    if 'data_registo' in df.columns:
        df['data_registo'] = pd.to_datetime(df['data_registo'], errors='coerce')
        df['Ano'] = df['data_registo'].dt.year
        df['Mes'] = df['data_registo'].dt.month
        df['Nome_Mes'] = df['data_registo'].dt.strftime('%B')
        df['Dia_Semana'] = df['data_registo'].dt.strftime('%A')

    # Retorna o CSV formatado em UTF-8 com BOM (suporta perfeitamente caracteres acentuados no Power BI)
    return df.to_csv(index=False, encoding='utf-8-sig')


def publicar_csv_online(csv_string, nome_ficheiro="ecofit_powerbi_dataset.csv"):
"""
Faz o upload ou substitui o ficheiro CSV no bucket do Supabase com upsert=True.
"""
try:
    # Obter credenciais de forma segura através do Streamlit Secrets
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    
    # Inicializar o cliente do Supabase
    supabase: Client = create_client(url, key)
    
    bucket_name = "export-powerbi"  
    file_bytes = csv_string.encode('utf-8-sig')
    
    # Tentar fazer o upload com upsert para substituir caso já exista
    try:
        supabase.storage.from_(bucket_name).upload(
            path=nome_ficheiro,
            file=file_bytes,
            file_options={"content-type": "text/csv; charset=utf-8", "upsert": "true"}
        )
    except Exception:
        # Se o upload falhar porque o ficheiro já existe, forçamos o update
        supabase.storage.from_(bucket_name).update(
            path=nome_ficheiro,
            file=file_bytes,
            file_options={"content-type": "text/csv; charset=utf-8", "upsert": "true"}
        )
    
    # Obter o URL público direto para a web
    public_url = supabase.storage.from_(bucket_name).get_public_url(nome_ficheiro)
    return public_url, None
    
except Exception as e:
    return None, str(e)