import pandas as pd
import time
import json
import xml.etree.ElementTree as ET
import streamlit as st
from datetime import date
from models.activity_model import ActivityModel
from services.weather_service import WeatherService


class FileController:

    @staticmethod
    def processar_ficheiro(ficheiro_carregado, utilizador_id: int = None) -> bool:
        """Deteta o tipo de ficheiro (CSV, Excel, JSON, GPX, TCX) e extrai a telemetria."""
        if ficheiro_carregado is None:
            return False

        nome_ficheiro = ficheiro_carregado.name.lower()
        km, minutos = 0.0, 0
        data_real = None

        try:
            # --- CASO 1: Exportação em CSV ou TXT ---
            if nome_ficheiro.endswith(('.csv', '.txt')):
                try:
                    df = pd.read_csv(ficheiro_carregado)
                except Exception:
                    ficheiro_carregado.seek(0)
                    df = pd.read_csv(ficheiro_carregado, sep=";")

                df.columns = df.columns.str.lower()
                col_distancia = next((c for c in df.columns if 'distance' in c or 'km' in c or 'distancia' in c), None)
                col_tempo = next((c for c in df.columns if 'duration' in c or 'time' in c or 'min' in c or 'duracao' in c), None)

                if col_distancia and col_tempo:
                    km = float(df[col_distancia].sum())
                    total_tempo = df[col_tempo].sum()
                    minutos = int(total_tempo / 60) if total_tempo > 500 else int(total_tempo)
                else:
                    st.error("❌ CSV inválido. Não foram encontradas colunas de 'distância' ou 'tempo'.")
                    time.sleep(1.5)
                    return False

            # --- CASO 2: Excel (.xlsx, .xls) ---
            elif nome_ficheiro.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(ficheiro_carregado)
                df.columns = df.columns.str.lower()
                col_distancia = next((c for c in df.columns if 'distance' in c or 'km' in c or 'distancia' in c), None)
                col_tempo = next((c for c in df.columns if 'duration' in c or 'time' in c or 'min' in c or 'duracao' in c), None)

                if col_distancia and col_tempo:
                    km = float(df[col_distancia].sum())
                    total_tempo = df[col_tempo].sum()
                    minutos = int(total_tempo / 60) if total_tempo > 500 else int(total_tempo)
                else:
                    st.error("❌ Ficheiro Excel sem colunas identificáveis de distância e tempo.")
                    time.sleep(1.5)
                    return False

            # --- CASO 3: Ficheiro JSON ---
            elif nome_ficheiro.endswith('.json'):
                dados = json.load(ficheiro_carregado)
                df = pd.DataFrame(dados if isinstance(dados, list) else [dados])
                df.columns = df.columns.str.lower()
                col_distancia = next((c for c in df.columns if 'distance' in c or 'km' in c or 'distancia' in c), None)
                col_tempo = next((c for c in df.columns if 'duration' in c or 'time' in c or 'min' in c or 'duracao' in c), None)

                if col_distancia and col_tempo:
                    km = float(df[col_distancia].sum())
                    total_tempo = df[col_tempo].sum()
                    minutos = int(total_tempo / 60) if total_tempo > 500 else int(total_tempo)

            # --- CASO 4: Atividade Individual em GPX ---
            elif nome_ficheiro.endswith('.gpx'):
                import gpxpy
                from geopy.distance import geodesic

                conteudo_gpx = ficheiro_carregado.read().decode('utf-8')
                gpx = gpxpy.parse(conteudo_gpx)

                total_metros = 0.0
                primeiro_tempo = None
                ultimo_tempo = None
                ponto_anterior = None

                for track in gpx.tracks:
                    for segment in track.segments:
                        for point in segment.points:
                            if point.time:
                                if primeiro_tempo is None:
                                    primeiro_tempo = point.time
                                ultimo_tempo = point.time

                            if ponto_anterior is not None:
                                coord1 = (ponto_anterior.latitude, ponto_anterior.longitude)
                                coord2 = (point.latitude, point.longitude)
                                total_metros += geodesic(coord1, coord2).meters

                            ponto_anterior = point

                if primeiro_tempo and ultimo_tempo:
                    duracao_segundos = (ultimo_tempo - primeiro_tempo).total_seconds()
                    minutos = int(duracao_segundos / 60)
                    km = round(total_metros / 1000.0, 2)
                    data_real = primeiro_tempo.strftime('%Y-%m-%d')
                else:
                    st.error("❌ O ficheiro GPX não contém marcas temporais válidas.")
                    time.sleep(1.5)
                    return False

            # --- CASO 5: Atividade Individual em TCX (Garmin/Strava) ---
            elif nome_ficheiro.endswith('.tcx'):
                tree = ET.parse(ficheiro_carregado)
                root = tree.getroot()

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

                if total_metros > 0 or total_segundos > 0:
                    km = round(total_metros / 1000.0, 2)
                    minutos = int(total_segundos / 60)
                else:
                    trackpoints = root.findall('.//{*}Trackpoint')
                    if trackpoints:
                        minutos = int(len(trackpoints) / 4)
                        km = round((len(trackpoints) * 0.005), 2)
                    else:
                        st.error("❌ Ficheiro TCX sem dados de telemetria legíveis.")
                        time.sleep(1.5)
                        return False

            # Gravação final se houver dados extraídos com sucesso
            if km > 0 or minutos > 0:
                return FileController._gravar_atividade_importada(km, minutos, nome_ficheiro, data_real)

            st.error("Não foi possível extrair métricas válidas deste ficheiro.")
            return False

        except Exception as e:
            st.error(f"Erro ao processar a estrutura do ficheiro: {str(e)}")
            return False

    @staticmethod
    def _gravar_atividade_importada(km: float, minutos: int, nome_fonte: str, data_real: str = None) -> bool:
        """Aplica a regra de pontos do EcoFit e envia para a Base de Dados."""
        id_utilizador = st.session_state['utilizador_logado']['utilizador_id']
        pontos = int((km * 10) + (minutos * 1))

        temp_atual = WeatherService.obter_temperatura_atual()

        payload = {
            "utilizador_id": id_utilizador,
            "data_registo": data_real if data_real else str(date.today()),
            "km_corridos": km,
            "minutos_treino": minutos,
            "copos_agua": 0,
            "pecas_fruta": 0,
            "pontos_ganhos": pontos,
            "tipo_insercao": "Ficheiro",
            "temperatura": temp_atual,
            "condicao_clima": "Sincronizado"
        }

        return ActivityModel.salvar_atividade(payload)

    @staticmethod
    def obter_historico_atividades_ficheiro(utilizador_id: int) -> pd.DataFrame:
        """Obtém as atividades carregadas e organiza-as para a vista."""
        registos = ActivityModel.obter_ficheiros_carregados(utilizador_id)

        if not registos:
            return pd.DataFrame()

        df = pd.DataFrame(registos)

        if 'tipo_insercao' in df.columns:
            df = df[df['tipo_insercao'].str.lower() == 'ficheiro']

        if df.empty:
            return pd.DataFrame()

        if 'data_registo' in df.columns:
            df['data_registo'] = pd.to_datetime(df['data_registo']).dt.strftime('%d/%m/%Y')

        return df