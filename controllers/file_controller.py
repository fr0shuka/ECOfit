import json
import time
import xml.etree.ElementTree as ET
from datetime import date
import pandas as pd
import streamlit as st
from models.activity_model import ActivityModel
from services.weather_service import WeatherService


class FileController:

    @staticmethod
    def pre_visualizar_ficheiro(ficheiro_carregado) -> dict:
        """Lê o ficheiro e devolve um dicionário com os dados extraídos (km, minutos, data, tipo detetado) sem gravar."""
        if ficheiro_carregado is None:
            return {"sucesso": False}

        nome_ficheiro = ficheiro_carregado.name.lower()
        km, minutos = 0.0, 0
        data_real = None
        tipo_detectado_id = None

        try:
            # GPX Parsing para Pré-visualização
            if nome_ficheiro.endswith('.gpx'):
                import gpxpy
                from geopy.distance import geodesic

                conteudo_gpx = ficheiro_carregado.read().decode('utf-8')
                gpx = gpxpy.parse(conteudo_gpx)

                # Detetar tipo na tag type ou extensões do track
                for track in gpx.tracks:
                    if hasattr(track, 'type') and track.type:
                        tipo_detectado_id = FileController._mapear_string_para_tipo_id(track.type)

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
                    # Fallback de tempo caso o GPX não tenha timestamps por ponto
                    km = round(total_metros / 1000.0, 2)
                    minutos = max(int(km * 4), 1) # Estimativa de 4 min/km se faltar tempo

                # Reposicionar o ponteiro do ficheiro para trás caso seja necessário relê-lo
                ficheiro_carregado.seek(0)

                return {
                    "sucesso": True,
                    "km": km,
                    "minutos": minutos,
                    "data_real": data_real or str(date.today()),
                    "tipo_sugerido_id": tipo_detectado_id
                }

            # (Lógica semelhante para outros formatos se necessário, focando agora no GPX)
            ficheiro_carregado.seek(0)
            return {"sucesso": False}

        except Exception as e:
            return {"sucesso": False, "erro": str(e)}

    @staticmethod
    def gravar_atividade_com_dados_ajustados(utilizador_id: int, km: float, minutos: int, tipo_atividade_id: int, nome_fonte: str, data_real: str = None) -> bool:
        """Grava definitivamente na BD a atividade com os valores validados/ajustados pelo utilizador."""
        tipos_atividade = ActivityModel.obter_tipos_atividade()
        tipo_escolhido = next((t for t in tipos_atividade if t['tipo_atividade_id'] == tipo_atividade_id), tipos_atividade[0])

        fator = float(tipo_escolhido.get("fator_pontuacao", 1.0))
        pontos = int(((km * 10) + (minutos * 1)) * fator)
        temp_atual = WeatherService.obter_temperatura_atual()

        payload = {
            "utilizador_id": utilizador_id,
            "tipo_atividade_id": tipo_escolhido["tipo_atividade_id"],
            "data_registo": data_real if data_real else str(date.today()),
            "distancia_km": km,
            "minutos_treino": minutos,
            "copos_agua": 0,
            "pecas_fruta": 0,
            "pontos_ganhos": pontos,
            "tipo_insercao": "Ficheiro",
            "temperatura": float(temp_atual) if temp_atual is not None else None,
            "condicao_clima": "Sincronizado"
        }

        return ActivityModel.salvar_atividade(payload)

    @staticmethod
    def _mapear_string_para_tipo_id(texto: str) -> int:
        tipos = ActivityModel.obter_tipos_atividade()
        if not tipos:
            return 1
        
        texto_lower = texto.lower()
        dicionario_conversao = {
            'running': 'corrida',
            'run': 'corrida',
            'biking': 'ciclismo',
            'cycling': 'ciclismo',
            'bike': 'ciclismo',
            'walking': 'caminhada',
            'walk': 'caminhada',
            'gym': 'ginásio',
            'strength': 'ginásio'
        }

        termo_procurado = dicionario_conversao.get(texto_lower, texto_lower)

        for t in tipos:
            nome_t = t.get('nome', '').lower()
            if termo_procurado in nome_t or nome_t in termo_procurado:
                return t['tipo_atividade_id']
        
        return tipos[0]['tipo_atividade_id']

    @staticmethod
    def obter_historico_atividades_ficheiro(utilizador_id: int) -> pd.DataFrame:
        registos = ActivityModel.obter_ficheiros_carregados(utilizador_id)
        if not registos:
            return pd.DataFrame()

        dados_flat = []
        for reg in registos:
            item = dict(reg)
            info_modalidade = item.get("bd_tipos_atividade") or {}
            item["modalidade"] = info_modalidade.get("nome", "N/A")
            dados_flat.append(item)

        df = pd.DataFrame(dados_flat)
        if 'tipo_insercao' in df.columns:
            df = df[df['tipo_insercao'].str.lower() == 'ficheiro']

        if df.empty:
            return pd.DataFrame()

        if 'distancia_km' not in df.columns:
            df['distancia_km'] = df.get('km_corridos', 0.0)

        if 'data_registo' in df.columns:
            df['data_registo'] = pd.to_datetime(df['data_registo'], errors='coerce').dt.strftime('%d/%m/%Y')

        return df