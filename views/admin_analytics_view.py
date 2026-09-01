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
        """Carrega os dados diretamente do Supabase através dos métodos reais do ActivityModel/UserModel."""
        cls._injetar_estilos()

        st.caption("Visão geral do envolvimento, utilizadores e volume global de hábitos.")

        # --- CARREGAMENTO DOS DADOS VIA SUPABASE ---
        # Chama a função exata que tens definida no ActivityModel
        metricas_res = ActivityModel.obter_metricas_globais_admin()
        dados_atividades = metricas_res.get("dados_completos", [])

        # Procura utilizadores no UserModel
        dados_utilizadores = []
        try:
            if hasattr(UserModel, 'buscar_todos'):
                dados_utilizadores = UserModel.buscar_todos()
            elif hasattr(UserModel, 'listar_todos'):
                dados_utilizadores = UserModel.listar_todos()
            elif hasattr(UserModel, 'obter_todos'):
                dados_utilizadores = UserModel.obter_todos()
        except Exception:
            dados_utilizadores = []

        if not dados_atividades:
            st.warning("Nenhum registo de atividade encontrado na tabela bd_atividades do Supabase.")
            return

        df_act = pd.DataFrame(dados_atividades)
        df_usr = pd.DataFrame(dados_utilizadores) if dados_utilizadores else pd.DataFrame()

        # Conversão numérica defensiva
        for col in ['pontos_ganhos', 'km_corridos', 'minutos_treino']:
            if col in df_act.columns:
                df_act[col] = pd.to_numeric(df_act[col], errors='coerce').fillna(0)
            else:
                df_act[col] = 0

        # Totais para os Cartões KPI
        if not df_usr.empty:
            total_utilizadores = len(df_usr)
        elif 'utilizador_id' in df_act.columns:
            total_utilizadores = df_act['utilizador_id'].nunique()
        else:
            total_utilizadores = 0

        total_registos = len(df_act)
        total_pontos = f"{int(df_act['pontos_ganhos'].sum()):,}".replace(",", " ")
        total_km = f"{df_act['km_corridos'].sum():.1f} km"

        # --- CARTÕES KPI (Design System EcoFit) ---
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Utilizadores", str(total_utilizadores), help="Total de utilizadores registados na plataforma.")
        col2.metric("Atividades", str(total_registos), help="Número total de registos de hábitos no Supabase.")
        col3.metric("Pontos Globais", total_pontos, help="Soma total de pontos acumulados.")
        col4.metric("Distância Total", total_km, help="Volume total de quilómetros acumulados.")

        st.markdown("---")

        # --- GRÁFICO DE EVOLUÇÃO ---
        st.markdown("##### Análise de evolução diária")

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


        st.markdown("##### Análise de impacto Climatérico")
        
        col_clima1, col_clima2 = st.columns(2)

        with col_clima1:
            # Gráfico de Dispersão: Temperatura vs Quilómetros Corridos
            fig_temp = px.scatter(
                df[df['temperatura'] > 0],
                x="temperatura",
                y="km_corridos",
                color="tipo_insercao" if "tipo_insercao" in df.columns else None,
                title="Relação: Temperatura (°C) vs. Distância Corrida (km)",
                labels={"temperatura": "Temperatura (°C)", "km_corridos": "Distância (km)"},
                color_discrete_sequence=["#4da6ff", "#00e676"]
            )
            fig_temp.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Inter, sans-serif", size=12, color="#94a3b8"),
                xaxis=dict(showgrid=True, gridcolor="#2e3440"),
                yaxis=dict(showgrid=True, gridcolor="#2e3440")
            )
            with st.container(border=True):
                st.plotly_chart(fig_temp, use_container_width=True)

        with col_clima2:
            # Agrupamento de Atividade por Condição Climatérica ou Faixa de Temperatura
            df['faixa_temp'] = pd.cut(
                df['temperatura'], 
                bins=[-10, 10, 20, 30, 50], 
                labels=['Frio (<10°C)', 'Agradável (10-20°C)', 'Quente (20-30°C)', 'Muito Quente (>30°C)']
            )
            df_temp_group = df.groupby('faixa_temp', observed=False)['minutos_treino'].mean().reset_index()

            fig_faixas = px.bar(
                df_temp_group,
                x='faixa_temp',
                y='minutos_treino',
                title="Média de Minutos de Treino por Faixa de Temperatura",
                labels={'faixa_temp': 'Faixa Climatérica', 'minutos_treino': 'Média de Minutos'},
                color_discrete_sequence=['#94a3b8']
            )
            fig_faixas.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Inter, sans-serif", size=12, color="#94a3b8"),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="#2e3440")
            )
            with st.container(border=True):
                st.plotly_chart(fig_faixas, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # SECÇÃO 3: ADESÃO E DISTRIBUIÇÃO DA PLATAFORMA
        st.markdown("##### Análise de utilização e hábitos")

        col_hab1, col_hab2 = st.columns(2)

        with col_hab1:
            # Distribuição dos Métodos de Inserção (Manual vs Ficheiro GPX/CSV)
            if 'tipo_insercao' in df.columns:
                df_metodo = df['tipo_insercao'].value_counts().reset_index()
                df_metodo.columns = ['Tipo', 'Quantidade']

                fig_pie = px.pie(
                    df_metodo,
                    names='Tipo',
                    values='Quantidade',
                    title="Origem dos Dados de Atividade",
                    hole=0.4,
                    color_discrete_sequence=['#4da6ff', "#34d399", "#f59e0b"]
                )
                fig_pie.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(family="Inter, sans-serif", size=12, color="#94a3b8")
                )
                with st.container(border=True):
                    st.plotly_chart(fig_pie, use_container_width=True)

        with col_hab2:
            # Volume Diário Combinado de Atividades na Plataforma
            df_diario = df.groupby(df['data_registo'].dt.strftime('%Y-%m-%d'))['km_corridos'].sum().reset_index()

            fig_linha = px.line(
                df_diario,
                x='data_registo',
                y='km_corridos',
                title="Volume Diário Global de Quilómetros Percorridos",
                labels={'data_registo': 'Data', 'km_corridos': 'Total Km'},
                color_discrete_sequence=['#34d399']
            )
            fig_linha.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Inter, sans-serif", size=12, color="#94a3b8"),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="#2e3440")
            )
            with st.container(border=True):
                st.plotly_chart(fig_linha, use_container_width=True)

        st.markdown("---")

        # SECÇÃO 4: TABELA DETALHADA PARA AUDITORIA
        st.markdown("##### Registo Geral de atividades")

        colunas_exibir = {
            'data_registo': 'Data',
            'utilizador_id': 'ID Utilizador',
            'km_corridos': 'Distância (km)',
            'minutos_treino': 'Duração (min)',
            'temperatura': 'Temp. (°C)',
            'tipo_insercao': 'Método',
            'pontos_ganhos': 'Pontos'
        }

        cols_presentes = [c for c in colunas_exibir.keys() if c in df.columns]
        df_auditoria = df[cols_presentes].copy()
        df_auditoria.rename(columns=colunas_exibir, inplace=True)

        st.dataframe(
            df_auditoria.sort_values(by="Data", ascending=False),
            use_container_width=True,
            hide_index=True
        )