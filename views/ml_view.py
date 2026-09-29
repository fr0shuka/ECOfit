import streamlit as st
import pandas as pd
from models.activity_model import ActivityModel
from services.ml_service import executar_modelo_nao_supervisionado, executar_modelo_supervisionado

class MLLabView:
    @staticmethod
    def renderizar():
        st.markdown("### Laboratório de Machine Learning")
        st.caption("Implementação prática de algoritmos de aprendizagem supervisionada e não supervisionada.")

        # 1. Consulta live ao Supabase
        res_metricas = ActivityModel.obter_metricas_globais_admin() or {}
        atividades_globais = res_metricas.get("dados_completos", [])

        if not atividades_globais:
            st.info("Não existem dados suficientes na base de dados para treinar os modelos de Machine Learning.")
            return

        # 2. Tratamento e Sanitização de Dados no Pandas
        df_ml_global = pd.DataFrame(atividades_globais)
        
        # Normalização de colunas de distância
        if 'distancia_km' not in df_ml_global.columns and 'km_corridos' in df_ml_global.columns:
            df_ml_global['distancia_km'] = df_ml_global['km_corridos']
        elif 'distancia_km' not in df_ml_global.columns:
            df_ml_global['distancia_km'] = 0.0

        # Conversão de tipos numéricos
        df_ml_global['distancia_km'] = pd.to_numeric(df_ml_global.get('distancia_km', 0), errors='coerce').fillna(0)
        df_ml_global['minutos_treino'] = pd.to_numeric(df_ml_global.get('minutos_treino', 0), errors='coerce').fillna(0)
        df_ml_global['pontos_ganhos'] = pd.to_numeric(df_ml_global.get('pontos_ganhos', 0), errors='coerce').fillna(0)

        # FILTRO: Excluir registos que tenham 0 km E 0 minutos (ex: hábitos) 
        df_ml_global = df_ml_global[(df_ml_global['distancia_km'] > 0) | (df_ml_global['minutos_treino'] > 0)].copy()
        if df_ml_global.empty:
            st.info("Não existem treinos registados com atividade física (distância ou duração) para treinar os modelos.")
            return

        # 3. Interface por Abas (Tabs)
        aba_nao_sup, aba_sup = st.tabs(["Não Supervisionada", "Supervisionada"])

        with aba_nao_sup:
            st.markdown("#### Segmentação de atividades por K-Means")
            df_clusterizado, erro_ns = executar_modelo_nao_supervisionado(df_ml_global)
            
            if erro_ns:
                st.warning(erro_ns)
            else:
                st.success("Modelo não supervisionado treinado com sucesso!")
                # ORDENAÇÃO POR DATA (+ recente primeiro)
                df_clusterizado['data_registo_dt'] = pd.to_datetime(df_clusterizado['data_registo'], errors='coerce')
                df_clusterizado = df_clusterizado.sort_values(by='data_registo_dt', ascending=False)

                cols_mostrar = [c for c in ['data_registo', 'distancia_km', 'minutos_treino', 'pontos_ganhos', 'perfil_ia'] if c in df_clusterizado.columns]
                
                # MOSTRAR TODOS OS REGISTOS
                st.dataframe(df_clusterizado[cols_mostrar], hide_index=True, use_container_width=True)

        with aba_sup:
            st.markdown("#### Previsão de Pontuação")
            modelo, metricas, erro_s = executar_modelo_supervisionado(df_ml_global)
            
            if erro_s:
                st.warning(erro_s)
            else:
                st.success("Modelo supervisionado treinado com sucesso com base no histórico!")
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Coeficiente de Determinação (R²)", f"{metricas['r2_score']}")
                c2.metric("Impacto por KM", f"+{metricas['coef_distancia']} pts/km")
                c3.metric("Impacto por MINUTO", f"+{metricas['coef_minutos']} pts/min")

                st.markdown("##### Simular Previsão")
                km_input = st.number_input("Distância para previsão (km)", 0.0, 100.0, 10.0)
                min_input = st.number_input("Duração para previsão (min)", 1, 600, 30)
                
                pontos_previstos = modelo.predict([[km_input, min_input]])[0]
                st.info(f"O modelo supervisionado prevê que esta atividade valerá exatamente **{max(0, int(pontos_previstos))} pontos**.")