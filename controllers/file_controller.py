import pandas as pd
import xml.etree.ElementTree as ET
import streamlit as st
from datetime import date
from models.activity_model import ActivityModel

class FileController:
    @staticmethod
    def processar_ficheiro_treino(ficheiro_carregado) -> bool:
        """Deteta o tipo de ficheiro (CSV, GPX, TCX) e extrai a telemetria."""
        nome_ficheiro = ficheiro_carregado.name.lower()
        km, minutos = 0.0, 0
        
        try:
            # --- CASO 1: Exportação Mensal / Histórico em CSV (Strava/Fitbit) ---
            if nome_ficheiro.endswith('.csv'):
                df = pd.read_csv(ficheiro_carregado)
                # Normaliza o nome das colunas para evitar erros de maiúsculas
                df.columns = df.columns.str.lower()
                
                # Tenta mapear colunas comuns de plataformas fitness
                col_distancia = next((c for c in df.columns if 'distance' in c or 'km' in c), None)
                col_tempo = next((c for c in df.columns if 'duration' in c or 'time' in c or 'min' in c), None)
                
                if col_distancia and col_tempo:
                    # Se for um ficheiro mensal com várias linhas, soma o total
                    km = float(df[col_distancia].sum())
                    # Se o tempo estiver em segundos (comum no Strava), converte para minutos
                    total_tempo = df[col_tempo].sum()
                    minutos = int(total_tempo / 60) if total_tempo > 500 else int(total_tempo)
                else:
                    st.error("❌ CSV inválido. Não encontrámos colunas de 'distância' ou 'tempo'.")
                    return False

            # --- CASO 2: Atividade Individual em GPX (Garmin/Strava) ---
            elif nome_ficheiro.endswith('.gpx'):
                tree = ET.parse(ficheiro_carregado)
                root = tree.getroot()
                # Remove namespaces do XML para facilitar a leitura
                namespaces = {'gpx': 'http://www.topografix.com/GPX/1/1'}
                
                # Procura por extensões de treino ou conta pontos de track para simular
                trackpoints = root.findall('.//gpx:trkpt', namespaces)
                if trackpoints:
                    # Simulação de cálculo por pontos GPX para fins de MVP
                    minutos = int(len(trackpoints) / 4) # Estimativa de tempo baseado nos registos
                    km = round((len(trackpoints) * 0.005), 2) # Estimativa de distância entre pontos
                else:
                    st.error("❌ Ficheiro GPX vazio ou sem pontos de rota válidos.")
                    return False

            # Se a extração correu bem e gerou dados
            if km > 0 or minutos > 0:
                return FileController._gravar_atividade_importada(km, minutos, nome_ficheiro)
            
            st.error("Não foi possível extrair métricas válidas deste ficheiro.")
            return False

        except Exception as e:
            st.error(f"Erro ao processar a estrutura do ficheiro: {str(e)}")
            return False

    @staticmethod
    def _gravar_atividade_importada(km: float, minutos: int, nome_fonte: str) -> bool:
        """Aplica a regra de pontos do EcoFit e envia para a Base de Dados."""
        id_utilizador = st.session_state['utilizador_logado']['utilizador_id']
        
        # Fórmula de pontos padrão do EcoFit
        pontos = int((km * 10) + (minutos * 1))

        payload = {
            "utilizador_id": id_utilizador,
            "data_registo": str(date.today()),
            "km_corridos": km,
            "minutos_treino": minutos,
            "copos_agua": 0, # Trackers não medem água
            "pecas_fruta": 0, # Trackers não medem nutrição
            "pontos_ganhos": pontos,
            "tipo_insercao": f"Importado ({nome_fonte.split('.')[-1].upper()})",
            "temperatura": 20.0, # Valor neutro padrão
            "condicao_clima": "Sincronizado"
        }

        from models.activity_model import ActivityModel
        return ActivityModel.salvar_atividade(payload)