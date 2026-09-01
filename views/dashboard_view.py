import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import date
from models.activity_model import ActivityModel
from services.weather_service import WeatherService


class DashboardView:
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
                
                /* Contentor principal dos cartões KPI */
                .kpi-container {
                    display: flex;
                    gap: 12px;
                    width: 100%;
                    margin-bottom: 20px;
                }
                
                /* Estilização do Cartão */
                .kpi-card {
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

                .kpi-card:hover {
                    background-color: #242933;
                    border-color: #10b981;
                }

                .kpi-title {
                    font-size: 0.75rem;
                    color: #94a3b8;
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                    margin-bottom: 4px;
                }

                .kpi-value {
                    font-size: 1.3rem;
                    font-weight: 700;
                    color: #ffffff;
                }

                /* Tooltip / Legenda em Hover */
                .kpi-card .tooltip-text {
                    visibility: hidden;
                    width: 180px;
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

                /* Seta do tooltip */
                .kpi-card .tooltip-text::after {
                    content: "";
                    position: absolute;
                    top: 100%;
                    left: 50%;
                    margin-left: -5px;
                    border-width: 5px;
                    border-style: solid;
                    border-color: #0f172a transparent transparent transparent;
                }

                /* Exibição no hover */
                .kpi-card:hover .tooltip-text {
                    visibility: visible;
                    opacity: 1;
                }

                div.stButton > button:first-child {
                    background-color: #10b981 !important;
                    color: #ffffff !important;
                    border: none !important;
                    font-weight: 600 !important;
                }
                div.stButton > button:first-child:hover {
                    background-color: #059669 !important;
                }
            </style>
        """, unsafe_allow_html=True)

    @staticmethod
    def renderizar_card_html(titulo: str, valor: str, legenda_tooltip: str) -> str:
        """Estrutura HTML do cartão individual com o balão de hover."""
        return f"""
        <div class="kpi-card">
            <div class="kpi-title">{titulo}</div>
            <div class="kpi-value">{valor}</div>
            <span class="tooltip-text">{legenda_tooltip}</span>
        </div>
        """

    @classmethod
    def renderizar_formulario(cls):
        """Ponto de entrada principal chamado no app.py"""
        cls._injetar_estilos()
        
        utilizador = st.session_state.get('utilizador_logado')
        if not utilizador:
            st.warning("Efetue login para visualizar o Dashboard.")
            return

        st.title("🌱 EcoFit - Painel do Utilizador")
        st.write(f"Bem-vindo(a), **{utilizador.get('nome', 'Utilizador')}**!")
        st.markdown("---")

        cls.renderizar_graficos_e_kpis()

    @classmethod
    def renderizar_graficos_e_kpis(cls):
        """Calcula métricas e renderiza os cartões KPI com legenda hover e gráfico."""
        st.markdown("##### Análise de Performance e Métricas")
        
        utilizador = st.session_state.get('utilizador_logado', {})
        id_utilizador = utilizador.get('utilizador_id')
        
        if not id_utilizador:
            st.warning("Identificador de utilizador não encontrado.")
            return

        registos_brutos = ActivityModel.buscar_por_utilizador(id_utilizador)
        
        if not registos_brutos:
            st.info("Ainda não existem atividades registadas para este utilizador.")
            return

        df = pd.DataFrame(registos_brutos)
        
        # Garante que as colunas essenciais existem mesmo que a BD retorne dados incompletos
        colunas_necessarias = ['km_corridos', 'minutos_treino', 'copos_agua', 'pecas_fruta', 'pontos_ganhos', 'data_registo']
        for col in colunas_necessarias:
            if col not in df.columns:
                df[col] = 0

        df['data_registo'] = pd.to_datetime(df['data_registo'])
        df['km_corridos'] = pd.to_numeric(df['km_corridos'], errors='coerce').fillna(0)
        df['minutos_treino'] = pd.to_numeric(df['minutos_treino'], errors='coerce').fillna(0)
        df['copos_agua'] = pd.to_numeric(df['copos_agua'], errors='coerce').fillna(0)
        df['pecas_fruta'] = pd.to_numeric(df['pecas_fruta'], errors='coerce').fillna(0)
        df['pontos_ganhos'] = pd.to_numeric(df['pontos_ganhos'], errors='coerce').fillna(0)
        df = df.sort_values(by='data_registo', ascending=True)

        # TotaisFormatados
        total_km = f"{df['km_corridos'].sum():.1f} km"
        total_min = f"{int(df['minutos_treino'].sum())} min"
        total_agua = f"{int(df['copos_agua'].sum())} copos"
        total_fruta = f"{int(df['pecas_fruta'].sum())} peças"
        total_pontos = f"{int(df['pontos_ganhos'].sum())} pts"

        # --- RENDERIZAÇÃO DOS CARTÕES COM TOOLTIP ---
        html_cards = f"""
        <div class="kpi-container">
            {cls.renderizar_card_html("Distância", total_km, "Total de quilómetros percorridos em corridas/caminhadas.")}
            {cls.renderizar_card_html("Tempo Total", total_min, "Tempo acumulado gasto em sessões de treino.")}
            {cls.renderizar_card_html("Hidratação", total_agua, "Quantidade total de copos de água ingeridos.")}
            {cls.renderizar_card_html("Fruta", total_fruta, "Doses de fruta consumidas durante o período.")}
            {cls.renderizar_card_html("Pontos", total_pontos, "Pontuação total acumulada com base nas atividades.")}
        </div>
        """
        st.markdown(html_cards, unsafe_allow_html=True)

        # --- GRÁFICO PLOTLY ---
        df_diario = df.groupby(df['data_registo'].dt.strftime('%Y-%m-%d'))['pontos_ganhos'].sum().reset_index()
        
        fig_bar = px.bar(
            df_diario,
            x='data_registo',
            y='pontos_ganhos',
            title="Evolução Diária de Pontuações",
            labels={'data_registo': 'Data', 'pontos_ganhos': 'Pontos'},
            color_discrete_sequence=[cls.VERDE_ECOFIT]
        )
        fig_bar.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=40, b=20),
            font=dict(family="Inter, sans-serif", size=12, color=cls.CINZA_TEXTO),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor=cls.CINZA_GRELHA)
        )
        
        with st.container(border=True):
            st.plotly_chart(fig_bar, use_container_width=True)