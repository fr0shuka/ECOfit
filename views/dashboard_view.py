import pandas as pd
import plotly.express as px
import streamlit as st
from models.activity_model import ActivityModel

class DashboardView:
    @staticmethod
    def renderizar_dashboard():
        """Renderiza o painel principal de métricas e gráficos analíticos."""
        st.markdown("### 📊 Análise de Performance e Métricas")
        
        id_utilizador = st.session_state['utilizador_logado']['utilizador_id']
        
        # 1. Procurar registos brutos via Model
        registos_brutos = ActivityModel.buscar_por_utilizador(id_utilizador)
        
        if not registos_brutos:
            st.info("🌱 Ainda não tens atividades registadas. Insere o teu primeiro treino para veres a análise de dados!")
            return

        # 2. Processar dados com Pandas
        df = pd.DataFrame(registos_brutos)
        df['data_registo'] = pd.to_datetime(df['data_registo'])
        df['km_corridos'] = pd.to_numeric(df['km_corridos'], errors='coerce').fillna(0)
        df['minutos_treino'] = pd.to_numeric(df['minutos_treino'], errors='coerce').fillna(0)
        df['copos_agua'] = pd.to_numeric(df['copos_agua'], errors='coerce').fillna(0)
        df['pontos_ganhos'] = pd.to_numeric(df['pontos_ganhos'], errors='coerce').fillna(0)
        df = df.sort_values(by='data_registo', ascending=True)

        # 3. Exibir Cartões KPI
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🏃 Distância", f"{df['km_corridos'].sum():.1f} km")
        col2.metric("⏱️ Tempo", f"{int(df['minutos_treino'].sum())} min")
        col3.metric("💧 Hidratação", f"{int(df['copos_agua'].sum())} copos")
        col4.metric("🌱 Pontos", f"{int(df['pontos_ganhos'].sum())} pts")

        st.markdown("---")

        # 4. Renderizar Gráfico de Barras Plotly (Pontos Diários)
        df_diario = df.groupby(df['data_registo'].dt.strftime('%Y-%m-%d'))['pontos_ganhos'].sum().reset_index()
        
        fig_bar = px.bar(
            df_diario,
            x='data_registo',
            y='pontos_ganhos',
            title="📈 Evolução Diária de Pontuações",
            labels={'data_registo': 'Data', 'pontos_ganhos': 'Pontos'},
            color_discrete_sequence=['#2E7D32']
        )
        fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        
        st.plotly_chart(fig_bar, use_container_width=True)