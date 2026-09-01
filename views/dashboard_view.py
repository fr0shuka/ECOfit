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
                .admin-kpi-container {
                    display: flex;
                    gap: 12px;
                    width: 100%;
                    margin-bottom: 24px;
                }
                .admin-kpi-card {
                    flex: 1;
                    position: relative;
                    background-color: #1e222a;
                    border: 1px solid #2e3440;
                    border-left: 3px solid #10b981;
                    padding: 12px 14px;
                    border-radius: 6px;
                    cursor: help;
                    transition: background-color 0.2s ease, border-color 0.2s ease;
                }
                .admin-kpi-card:hover {
                    background-color: #242933;
                    border-color: #10b981;
                }
                .admin-kpi-title {
                    font-size: 0.75rem;
                    color: #94a3b8;
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                    margin-bottom: 4px;
                }
                .admin-kpi-value {
                    font-size: 1.3rem;
                    font-weight: 700;
                    color: #ffffff;
                }
                .admin-kpi-card .tooltip-text {
                    visibility: hidden;
                    width: 190px;
                    background-color: #0f172a;
                    color: #cbd5e1;
                    text-align: center;
                    border-radius: 6px;
                    padding: 8px 10px;
                    position: absolute;
                    z-index: 99;
                    bottom: 115%;
                    left: 50%;
                    transform: translateX(-50%);
                    opacity: 0;
                    transition: opacity 0.2s ease-in-out, visibility 0.2s;
                    font-size: 0.75rem;
                    font-weight: normal;
                    border: 1px solid #334155;
                    box-shadow: 0px 4px 12px rgba(0,0,0,0.4);
                    pointer-events: none;
                }
                .admin-kpi-card .tooltip-text::after {
                    content: "";
                    position: absolute;
                    top: 100%;
                    left: 50%;
                    margin-left: -5px;
                    border-width: 5px;
                    border-style: solid;
                    border-color: #0f172a transparent transparent transparent;
                }
                .admin-kpi-card:hover .tooltip-text {
                    visibility: visible;
                    opacity: 1;
                }
            </style>
        """, unsafe_allow_html=True)

    @staticmethod
    def _renderizar_card_kpi(titulo: str, valor: str, legenda: str) -> str:
        return f"""
        <div class="admin-kpi-card">
            <div class="admin-kpi-title">{titulo}</div>
            <div class="admin-kpi-value">{valor}</div>
            <span class="tooltip-text">{legenda}</span>
        </div>
        """

    @classmethod
    def renderizar_view(cls, dados_atividades: list, dados_utilizadores: list):
        cls._injetar_estilos()

        st.title("📊 EcoFit - Analytics Administrativo")
        st.caption("Visão geral do envolvimento, utilizadores e volume global de hábitos.")

        if not dados_atividades or not dados_utilizadores:
            st.warning("Dados insuficientes para gerar a análise global.")
            return

        df_act = pd.DataFrame(dados_atividades)
        df_usr = pd.DataFrame(dados_utilizadores)

        # Higienização de dados
        df_act['pontos_ganhos'] = pd.to_numeric(df_act.get('pontos_ganhos', 0), errors='coerce').fillna(0)
        df_act['km_corridos'] = pd.to_numeric(df_act.get('km_corridos', 0), errors='coerce').fillna(0)
        df_act['minutos_treino'] = pd.to_numeric(df_act.get('minutos_treino', 0), errors='coerce').fillna(0)

        # Totais para KPIs
        total_utilizadores = len(df_usr)
        total_registos = len(df_act)
        total_pontos = f"{int(df_act['pontos_ganhos'].sum()):,}".replace(",", " ")
        total_km = f"{df_act['km_corridos'].sum():.1f} km"

        # Renderização dos Cartões KPI
        html_kpis = f"""
        <div class="admin-kpi-container">
            {cls._renderizar_card_kpi("Utilizadores", str(total_utilizadores), "Total de utilizadores registados na plataforma.")}
            {cls._renderizar_card_kpi("Atividades", str(total_registos), "Número total de registos de hábitos efetuados.")}
            {cls._renderizar_card_kpi("Pontos Globais", total_pontos, "Soma de todos os pontos atribuídos na plataforma.")}
            {cls._renderizar_card_kpi("Distância Total", total_km, "Volume total de quilómetros acumulados por todos os alunos.")}
        </div>
        """
        st.markdown(html_kpis, unsafe_allow_html=True)

        # Gráfico de Atividade por Dia
        if 'data_registo' in df_act.columns:
            df_act['data_registo'] = pd.to_datetime(df_act['data_registo'])
            df_diario = df_act.groupby(df_act['data_registo'].dt.strftime('%Y-%m-%d'))['pontos_ganhos'].sum().reset_index()

            fig = px.bar(
                df_diario,
                x='data_registo',
                y='pontos_ganhos',
                title="Pontuação Acumulada por Dia (Global)",
                labels={'data_registo': 'Data', 'pontos_ganhos': 'Pontos Ganho'},
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