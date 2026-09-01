# views/admin_analytics_view.py

import streamlit as st
import pandas as pd
import plotly.express as px

class AdminAnalyticsView:
    VERDE_ECOFIT = "#10b981"
    CINZA_TEXTO = "#94a3b8"
    CINZA_GRELHA = "#2e3440"

    @staticmethod
    def _injetar_estilos():
        st.markdown("""
            <style>
                .main .block-container {
                    padding-top: 1.5rem;
                    max-width: 1100px;
                }
                
                [data-testid="stMetric"] {
                    background-color: #1e222a !important;
                    border: 1px solid #2e3440 !important;
                    border-left: 4px solid #10b981 !important;
                    padding: 12px 14px !important;
                    border-radius: 6px !important;
                    transition: all 0.2s ease-in-out !important;
                }

                [data-testid="stMetric"]:hover {
                    background-color: #242933 !important;
                    border-color: #10b981 !important;
                    transform: translateY(-2px);
                }

                [data-testid="stMetricLabel"] {
                    font-size: 0.75rem !important;
                    color: #94a3b8 !important;
                    font-weight: 600 !important;
                    text-transform: uppercase !important;
                    letter-spacing: 0.05em !important;
                }

                [data-testid="stMetricValue"] {
                    font-size: 1.3rem !important;
                    font-weight: 700 !important;
                    color: #ffffff !important;
                }
            </style>
        """, unsafe_allow_html=True)

    @classmethod
    def renderizar(cls):
        """Ponto de entrada chamado diretamente pela aba no app.py"""
        cls._injetar_estilos()

        st.title("📊 EcoFit - Analytics Administrativo")
        st.caption("Visão geral do envolvimento, utilizadores e volume global de hábitos.")

        # Exemplo de obtenção dos dados (ajusta conforme a tua estrutura/models):
        # dados_atividades = ActivityModel.buscar_todas()
        # dados_utilizadores = UserModel.buscar_todos()
        
        # Ou se os dados estiverem no st.session_state / passados via lista:
        dados_atividades = st.session_state.get('atividades', [])
        dados_utilizadores = st.session_state.get('utilizadores', [])

        if not dados_atividades or not dados_utilizadores:
            st.warning("Dados insuficientes para gerar a análise global.")
            return

        df_act = pd.DataFrame(dados_atividades)
        df_usr = pd.DataFrame(dados_utilizadores)

        # Higienização e conversão numérica
        df_act['pontos_ganhos'] = pd.to_numeric(df_act.get('pontos_ganhos', 0), errors='coerce').fillna(0)
        df_act['km_corridos'] = pd.to_numeric(df_act.get('km_corridos', 0), errors='coerce').fillna(0)

        # Métricas
        total_utilizadores = len(df_usr)
        total_registos = len(df_act)
        total_pontos = f"{int(df_act['pontos_ganhos'].sum()):,}".replace(",", " ")
        total_km = f"{df_act['km_corridos'].sum():.1f} km"

        # Cartões KPI em linha
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Utilizadores", str(total_utilizadores), help="Total de utilizadores registados.")
        col2.metric("Atividades", str(total_registos), help="Número total de registos efetuados.")
        col3.metric("Pontos", total_pontos, help="Soma global de pontos acumulados.")
        col4.metric("Distância", total_km, help="Volume total de quilómetros acumulados.")

        st.markdown("---")

        # Gráfico
        if 'data_registo' in df_act.columns:
            df_act['data_registo'] = pd.to_datetime(df_act['data_registo'])
            df_diario = df_act.groupby(df_act['data_registo'].dt.strftime('%Y-%m-%d'))['pontos_ganhos'].sum().reset_index()

            fig = px.bar(
                df_diario,
                x='data_registo',
                y='pontos_ganhos',
                title="Pontuação Acumulada por Dia (Global)",
                labels={'data_registo': 'Data', 'pontos_ganhos': 'Pontos'},
                color_discrete_sequence=[cls.VERDE_ECOFIT]
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=40, b=20),
                font=dict(family="Inter, sans-serif", size=12, color=cls.CINZA_TEXTO),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor=cls.CINZA_GRELHA)
            )

            with st.container(border=True):
                st.plotly_chart(fig, use_container_width=True)