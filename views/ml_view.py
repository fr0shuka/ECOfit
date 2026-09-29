import streamlit as st
import pandas as pd
from models.activity_model import ActivityModel
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

def executar_modelo_nao_supervisionado(df_atividades):
    if df_atividades is None or len(df_atividades) < 3:
        return None, "Dados insuficientes para executar o clustering."
    features = ['distancia_km', 'minutos_treino', 'pontos_ganhos']
    X = df_atividades[features].fillna(0)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    df_atividades['cluster_id'] = kmeans.fit_predict(X_scaled)
    cluster_means = df_atividades.groupby('cluster_id')['pontos_ganhos'].mean().sort_values()
    sorted_ids = cluster_means.index.tolist()
    mapa_clusters = {
        sorted_ids[0]: "🟢 Baixa Intensidade / Recuperação",
        sorted_ids[1]: "🟡 Intensidade Moderada",
        sorted_ids[2]: "🔥 Alta Performance / Intensivo"
    }
    df_atividades['perfil_ia'] = df_atividades['cluster_id'].map(mapa_clusters)
    return df_atividades, None

def executar_modelo_supervisionado(df_atividades):
    if df_atividades is None or len(df_atividades) < 5:
        return None, None, "Dados insuficientes para treinar o modelo supervisionado (mínimo de 5 registos)."
    df_modelo = df_atividades[['distancia_km', 'minutos_treino', 'pontos_ganhos']].dropna().copy()
    if len(df_modelo) < 5:
        return None, None, "Dados limpos insuficientes para a regressão."
    X = df_modelo[['distancia_km', 'minutos_treino']]
    y = df_modelo['pontos_ganhos']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    modelo_regressao = LinearRegression()
    modelo_regressao.fit(X_train, y_train)
    y_pred = modelo_regressao.predict(X_test)
    r2 = r2_score(y_test, y_pred) if len(y_test) > 1 else 0.0
    mse = mean_squared_error(y_test, y_pred)
    metricas_modelo = {
        "r2_score": round(r2, 3),
        "mse": round(mse, 2),
        "coef_distancia": round(modelo_regressao.coef_[0], 2),
        "coef_minutos": round(modelo_regressao.coef_[1], 2),
        "intercept": round(modelo_regressao.intercept_, 2)
    }
    return modelo_regressao, metricas_modelo, None

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
                df_clusterizado['data_registo_dt'] = pd.to_datetime(df_clusterizado['data_registo'], errors='coerce')
                df_clusterizado = df_clusterizado.sort_values(by='data_registo_dt', ascending=False)
                cols_mostrar = [c for c in ['data_registo', 'distancia_km', 'minutos_treino', 'pontos_ganhos', 'perfil_ia'] if c in df_clusterizado.columns]
                
                # MOSTRAR TODOS OS REGISTOS (Removido o .head(10) para não ocultar treinos)
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