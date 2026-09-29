import pandas as pd
import io
import streamlit as st
from supabase import Client, create_client

def gerar_csv_completo_powerbi(atividades_globais, utilizadores_globais=None):
    """
    Processa todos os registos globais e cruza com os utilizadores 
    para incluir o Nome e email, preparando um formato tabular rico para o Power BI.
    """
    if not atividades_globais:
        return None
    
    df = pd.DataFrame(atividades_globais)
    
    # Cruzamento (Merge) com a tabela de utilizadores para trazer o Nome
    if utilizadores_globais:
        df_users = pd.DataFrame(utilizadores_globais)
        
        # Identificar qual é a coluna de ID do utilizador em cada tabela (ex: 'user_id' ou 'id')
        coluna_id_atv = 'user_id' if 'user_id' in df.columns else ('id_utilizador' if 'id_utilizador' in df.columns else None)
        coluna_id_usr = 'id' if 'id' in df_users.columns else ('user_id' if 'user_id' in df_users.columns else None)
        
        if coluna_id_atv and coluna_id_usr:
            # Garantir que a coluna de nome existe (pode chamar-se 'nome', 'name' ou 'full_name')
            coluna_nome = next((c for c in ['nome', 'name', 'full_name', 'nome_completo'] if c in df_users.columns), None)
            coluna_email = next((c for c in ['email', 'mail'] if c in df_users.columns), None)
            
            colunas_para_trazer = [coluna_id_usr]
            if coluna_nome: colunas_para_trazer.append(coluna_nome)
            if coluna_email: colunas_para_trazer.append(coluna_email)
            
            df_users_subset = df_users[colunas_para_trazer].copy()
            
            # Normalizar nomes de colunas para o merge
            rename_map = {coluna_id_usr: coluna_id_atv}
            if coluna_nome and coluna_nome != 'nome':
                rename_map[coluna_nome] = 'nome'
            df_users_subset = df_users_subset.rename(columns=rename_map)
            
            if 'nome' not in df_users_subset.columns and coluna_nome:
                df_users_subset['nome'] = df_users_subset[coluna_nome]

            # Merge do tipo Left Join para não perder atividades
            df = pd.merge(df, df_users_subset, on=coluna_id_atv, how='left')

    # Garantir que a coluna 'nome' existe mesmo que o dicionário venha vazio
    if 'nome' not in df.columns:
        df['nome'] = 'Utilizador Desconhecido'

    # Normalização de colunas de distância
    if 'distancia_km' not in df.columns and 'km_corridos' in df.columns:
        df['distancia_km'] = df['km_corridos']
    elif 'distancia_km' not in df.columns:
        df['distancia_km'] = 0.0

    # Conversão de tipos seguros para métricas numéricas
    df['distancia_km'] = pd.to_numeric(df.get('distancia_km', 0), errors='coerce').fillna(0)
    df['minutos_treino'] = pd.to_numeric(df.get('minutos_treino', 0), errors='coerce').fillna(0)
    df['pontos_ganhos'] = pd.to_numeric(df.get('pontos_ganhos', 0), errors='coerce').fillna(0)
    
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

    # Formato de data e colunas auxiliares para suporte à Inteligência de Tempo (DAX)
    if 'data_registo' in df.columns:
        df['data_registo'] = pd.to_datetime(df['data_registo'], errors='coerce')
        df['Ano'] = df['data_registo'].dt.year
        df['Mes'] = df['data_registo'].dt.month
        df['Nome_Mes'] = df['data_registo'].dt.strftime('%B')
        df['Dia_Semana'] = df['data_registo'].dt.strftime('%A')

    # Devolve o CSV em formato texto (UTF-8 com BOM)
    return df.to_csv(index=False, encoding='utf-8-sig')


def publicar_csv_online(csv_string, nome_ficheiro="ecofit_powerbi_dataset.csv"):
    """
    Faz o upload do CSV unificado para o bucket do Supabase Storage
    e devolve o URL público direto para o Power BI.
    """
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        supabase: Client = create_client(url, key)
        
        bucket_name = "export-powerbi"  
        file_bytes = csv_string.encode('utf-8-sig')
        
        supabase.storage.from_(bucket_name).upload(
            path=nome_ficheiro,
            file=file_bytes,
            file_options={"content-type": "text/csv", "upsert": "true"}
        )
        
        public_url = supabase.storage.from_(bucket_name).get_public_url(nome_ficheiro)
        return public_url, None
        
    except Exception as e:
        return None, str(e)