import streamlit as st
import pandas as pd
import plotly.express as px
from models.activity_model import ActivityModel
from models.user_model import UserModel


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
        """Carrega os dados diretamente do Supabase através dos Models e renderiza o dashboard."""
        cls._injetar_estilos()

        st.title("📊 EcoFit - Analytics Administrativo")
        st.caption("Visão geral do envolvimento, utilizadores e volume global de hábitos.")

        # --- CARREGAMENTO DIRETO VIA SUPABASE ---
        # Procura todos os registos nas tabelas do Supabase
        dados_atividades = []
        dados_utilizadores = []

        try:
            if hasattr(ActivityModel, 'buscar_todas'):
                dados_atividades = ActivityModel.buscar_todas()
            elif hasattr(ActivityModel, 'buscar_todos'):
                dados_atividades = ActivityModel.buscar_todos()

            if hasattr(UserModel, 'buscar_todos'):
                dados_utilizadores = UserModel.buscar_todos()
            elif hasattr(UserModel, 'listar_todos'):
                dados_utilizadores = UserModel.listar_todos()
        except Exception as e:
            st.error(f"Erro ao ligar ao Supabase: {e}")
            return

        # Fallback de segurança se os registos vierem no session_state
        if not dados_atividades:
            dados_atividades = st.session_state.get('atividades', [])
        if not dados_utilizadores:
            dados_utilizadores = st.session_state.get('utilizadores', [])

        if not dados_atividades:
            st.warning("Sem registos de atividades encontrados na tabela do Supabase.")
            return

        df_act = pd.DataFrame(dados_atividades)
        df_usr = pd.DataFrame(dados_utilizadores) if dados_utilizadores else pd.DataFrame()

        # Higienização de campos numéricos do Supabase
        for col in ['pontos_ganhos', 'km_corridos', 'minutos_treino']:
            if col in df_act.columns:
                df_act[col] = pd.to_numeric(df_act[col], errors='coerce').fillna(0)
            else:
                df_act[col] = 0

        # Totais para os Cartões KPI
        total_utilizadores = len(df_usr) if not df_usr.empty else df_act.get('utilizador_id', pd.Series()).nunique()
        total_registos = len(df_act)
        total_pontos = f"{int(df_act['pontos_ganhos'].sum()):,}".replace(",", " ")
        total_km = f"{df_act['km_corridos'].sum():.1f} km"

        # --- CARTÕES KPI ---
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Utilizadores", str(total_utilizadores), help="Total de utilizadores registados na plataforma.")
        col2.metric("Atividades", str(total_registos), help="Número total de registos de hábitos efetuados.")
        col3.metric("Pontos Globais", total_pontos, help="Soma de todos os pontos atribuídos no Supabase.")
        col4.metric("Distância Total", total_km, help="Volume total de quilómetros acumulados.")

        st.markdown("---")

        # --- GRÁFICO DE EVOLUÇÃO ---
        campo_data = 'data_registo' if 'data_registo' in df_act.columns else 'created_at'
        if campo_data in df_act.columns:
            df_act[campo_data] = pd.to_datetime(df_act[campo_data])
            df_diario = df_act.groupby(df_act[campo_data].dt.strftime('%Y-%m-%d'))['pontos_ganhos'].sum().reset_index()

            fig = px.bar(
                df_diario,
                x=campo_data,
                y='pontos_ganhos',
                title="Pontuação Acumulada por Dia (Global)",
                labels={campo_data: 'Data', 'pontos_ganhos': 'Pontos'},
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