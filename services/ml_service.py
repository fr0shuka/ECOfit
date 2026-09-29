import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

def executar_modelo_nao_supervisionado(df_atividades):
    """
    Modelo de Aprendizagem Não Supervisionada (K-Means Clustering).
    Segmenta os treinos em 3 clusters de intensidade baseados em dados reais.
    """
    if df_atividades is None or len(df_atividades) < 3:
        return None, "Dados insuficientes para executar o clustering."

    features = ['distancia_km', 'minutos_treino', 'pontos_ganhos']
    X = df_atividades[features].fillna(0)

    # Normalização estatística das features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Algoritmo K-Means
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    df_atividades['cluster_id'] = kmeans.fit_predict(X_scaled)

    # Mapeamento descritivo dos grupos detetados automaticamente
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
    """
    Modelo de Aprendizagem Supervisionada (Regressão Linear).
    Treina um modelo para prever a pontuação com base na distância e minutos de treino.
    """
    if df_atividades is None or len(df_atividades) < 5:
        return None, None, "Dados insuficientes para treinar o modelo supervisionado (mínimo de 5 registos)."

    # Preparar as variáveis independentes (X) e a variável alvo / target (y)
    df_modelo = df_atividades[['distancia_km', 'minutos_treino', 'pontos_ganhos']].dropna().copy()
    
    if len(df_modelo) < 5:
        return None, None, "Dados limpos insuficientes para a regressão."

    X = df_modelo[['distancia_km', 'minutos_treino']]
    y = df_modelo['pontos_ganhos']

    # Divisão dos dados em treino (80%) e teste (20%)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Instanciar e treinar o modelo de Regressão Linear
    modelo_regressao = LinearRegression()
    modelo_regressao.fit(X_train, y_train)

    # Avaliação da performance do modelo
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