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
            # --- CASO 1: Exportação em CSV ---
            if nome_ficheiro.endswith('.csv'):
                df = pd.read_csv(ficheiro_carregado)
                df.columns = df.columns.str.lower()
                
                col_distancia = next((c for c in df.columns if 'distance' in c or 'km' in c), None)
                col_tempo = next((c for c in df.columns if 'duration' in c or 'time' in c or 'min' in c), None)
                
                if col_distancia and col_tempo:
                    km = float(df[col_distancia].sum())
                    total_tempo = df[col_tempo].sum()
                    minutos = int(total_tempo / 60) if total_tempo > 500 else int(total_tempo)
                else:
                    st.error("❌ CSV inválido. Não encontrámos colunas de 'distância' ou 'tempo'.")
                    return False

            # --- CASO 2: Atividade Individual em GPX ---
            elif nome_ficheiro.endswith('.gpx'):
                tree = ET.parse(ficheiro_carregado)
                root = tree.getroot()
                namespaces = {'gpx': 'http://www.topografix.com/GPX/1/1'}
                
                trackpoints = root.findall('.//gpx:trkpt', namespaces)
                if trackpoints:
                    minutos = int(len(trackpoints) / 4)
                    km = round((len(trackpoints) * 0.005), 2)
                else:
                    st.error("❌ Ficheiro GPX vazio ou sem pontos válidos.")
                    return False

            # --- CASO 3: Atividade Individual em TCX (Garmin/Strava) ---
            elif nome_ficheiro.endswith('.tcx'):
                tree = ET.parse(ficheiro_carregado)
                root = tree.getroot()
                
                # Procura todos os blocos de Lap (Volta) ignorando a versão do namespace do fabricante
                laps = root.findall('.//{*}Lap')
                total_metros = 0.0
                total_segundos = 0.0
                
                for lap in laps:
                    dist_node = lap.find('.//{*}DistanceMeters')
                    time_node = lap.find('.//{*}TotalTimeSeconds')
                    
                    if dist_node is not None and dist_node.text:
                        total_metros += float(dist_node.text)
                    if time_node is not None and time_node.text:
                        total_segundos += float(time_node.text)
                
                # Se encontrou dados válidos nos resumos das Laps
                if total_metros > 0 or total_segundos > 0:
                    km = round(total_metros / 1000.0, 2) # Converte metros para Km
                    minutos = int(total_segundos / 60)   # Converte segundos para minutos
                else:
                    # Fallback: se o ficheiro não tiver resumo de laps, conta os pontos brutos de Trackpoint
                    trackpoints = root.findall('.//{*}Trackpoint')
                    if trackpoints:
                        minutos = int(len(trackpoints) / 4)
                        km = round((len(trackpoints) * 0.005), 2)
                    else:
                        st.error("❌ Ficheiro TCX sem dados de telemetria legíveis.")
                        return False

            # Gravação final se houver dados extraídos com sucesso
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
        pontos = int((km * 10) + (minutos * 1))

        payload = {
            "utilizador_id": id_utilizador,
            "data_registo": str(date.today()),
            "km_corridos": km,
            "minutos_treino": minutos,
            "copos_agua": 0,
            "pecas_fruta": 0,
            "pontos_ganhos": pontos,
            "tipo_insercao": f"Importado ({nome_fonte.split('.')[-1].upper()})",
            "temperatura": 20.0,
            "condicao_clima": "Sincronizado"
        }

        return ActivityModel.salvar_atividade(payload)