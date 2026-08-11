import sys
import os
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.user_model import UserModel


class UserController:
    @staticmethod
    def obter_dados_ranking() -> pd.DataFrame:
        """Soma as atividades por utilizador mapeando os nomes exatos das colunas da BD."""
        users_data, atividades_data = UserModel.obter_utilizadores_e_atividades()
        
        if not users_data:
            return pd.DataFrame()
            
        df_users = pd.DataFrame(users_data)
        col_id_user = 'utilizador_id' if 'utilizador_id' in df_users.columns else 'id'

        # Mapeamento: 'coluna_na_bd': 'coluna_esperada_na_view'
        mapeamento_colunas = {
            'pontos_ganhos': 'pontos',
            'km_corridos': 'kms',
            'copos_agua': 'agua',
            'pecas_fruta': 'fruta'
        }

        colunas_view = list(mapeamento_colunas.values())

        # Caso não existam atividades registadas ainda
        if not atividades_data:
            for col in colunas_view:
                df_users[col] = 0
            return df_users

        df_atividades = pd.DataFrame(atividades_data)
        colunas_reais = list(mapeamento_colunas.keys())

        # Converter colunas numéricas da BD
        for col_real in colunas_reais:
            if col_real in df_atividades.columns:
                df_atividades[col_real] = pd.to_numeric(df_atividades[col_real], errors='coerce').fillna(0)
            else:
                df_atividades[col_real] = 0

        # Agrupar por utilizador_id e somar as métricas reais
        df_totais = df_atividades.groupby('utilizador_id')[colunas_reais].sum().reset_index()

        # Renomear as colunas somadas para os nomes que a View consome
        df_totais.rename(columns=mapeamento_colunas, inplace=True)

        # Cruzar a lista de utilizadores com os somatórios
        df_ranking = pd.merge(
            df_users, 
            df_totais, 
            left_on=col_id_user, 
            right_on='utilizador_id', 
            how='left'
        )

        # Preencher com 0 os utilizadores que ainda não têm atividades registadas
        df_ranking[colunas_view] = df_ranking[colunas_view].fillna(0)

        return df_ranking