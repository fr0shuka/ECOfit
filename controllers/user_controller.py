import sys
import os
import pandas as pd

# Assegura a resolução da raiz do projeto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.user_model import UserModel


class UserController:
    @staticmethod
    def obter_dados_ranking() -> pd.DataFrame:
        """Procura todos os utilizadores aprovados e devolve como DataFrame."""
        try:
            utilizadores = UserModel.obter_todos_aprovados()
            
            if not utilizadores:
                return pd.DataFrame()
                
            return pd.DataFrame(utilizadores)
        except Exception as e:
            print(f"Erro ao obter dados para o ranking: {e}")
            return pd.DataFrame()