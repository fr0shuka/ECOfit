import sys
import os
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.user_model import UserModel


class UserController:
    @staticmethod
    def obter_dados_ranking() -> pd.DataFrame:
        """Agrega as atividades por utilizador e calcula o ranking total."""
        users_data, atividades_data = UserModel.obter_utilizadores_e_atividades()
        
        if not users_data:
            return pd.DataFrame()
            
        df_users = pd.DataFrame(users_data)
        
        # Se não houver atividades registadas ainda, retorna utilizadores com zeros
        if not atividades_data:
            for col in ['pontos', 'kms', 'agua', 'fruta']:
                df_users[col] = 0
            return df_users

        df_atividades = pd.DataFrame(atividades_data)

        # Converter colunas métricas para numérico
        metricas = ['pontos', 'kms', 'agua', 'fruta']
        for col in metricas:
            if col in df_atividades.columns:
                df_atividades[col] = pd.to_numeric(df_atividades[col], errors='coerce').fillna(0)
            else:
                df_atividades[col] = 0

        # Agrupar atividades por utilizador_id e somar as métricas
        df_totais = df_atividades.groupby('utilizador_id')[metricas].sum().reset_index()

        # Cruzar (MERGE) os nomes dos utilizadores com os totais calculados
        df_ranking = pd.merge(df_users, df_totais, on='utilizador_id', how='left')

        # Substituir valores nulos (utilizadores sem atividades) por 0
        df_ranking[metricas] = df_ranking[metricas].fillna(0)

        return df_ranking