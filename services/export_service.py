import pandas as pd
import io

def gerar_csv_completo_powerbi(atividades_globais):
    """
    Processa todos os registos globais (incluindo treinos e hábitos) 
    para um formato tabular robusto pronto para o Power BI e DAX.
    """
    if not atividades_globais:
        return None
    
    df = pd.DataFrame(atividades_globais)
    
    # Normalização de colunas de distância
    if 'distancia_km' not in df.columns and 'km_corridos' in df.columns:
        df['distancia_km'] = df['km_corridos']
    elif 'distancia_km' not in df.columns:
        df['distancia_km'] = 0.0

    # Conversão de tipos seguros para métricas numéricas
    df['distancia_km'] = pd.to_numeric(df.get('distancia_km', 0), errors='coerce').fillna(0)
    df['minutos_treino'] = pd.to_numeric(df.get('minutos_treino', 0), errors='coerce').fillna(0)
    df['pontos_ganhos'] = pd.to_numeric(df.get('pontos_ganhos', 0), errors='coerce').fillna(0)
    
    # Garantir e tratar colunas de hábitos (copos de água, fruta, etc.)
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

    # Classificação inteligente do tipo de registo para filtros visuais no Power BI
    def classificar_tipo(row):
        if row['distancia_km'] > 0 or row['minutos_treino'] > 0:
            return 'Treino / Atividade Física'
        else:
            return 'Hábito / Hidratação'
            
    df['tipo_registo'] = df.apply(classificar_tipo, axis=1)

    # Formato de data e colunas auxiliares de suporte à Inteligência de Tempo (DAX)
    if 'data_registo' in df.columns:
        df['data_registo'] = pd.to_datetime(df['data_registo'], errors='coerce')
        df['Ano'] = df['data_registo'].dt.year
        df['Mes'] = df['data_registo'].dt.month
        df['Nome_Mes'] = df['data_registo'].dt.strftime('%B')
        df['Dia_Semana'] = df['data_registo'].dt.strftime('%A')

    # Devolve o CSV em formato texto (UTF-8 com BOM para compatibilidade total com Excel e Power BI)
    return df.to_csv(index=False, encoding='utf-8-sig')