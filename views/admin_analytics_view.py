import sys
import os
import streamlit as st
import pandas as pd
import plotly.express as px

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.activity_model import ActivityModel


class AdminAnalyticsView:
    @staticmethod
    def _injetar_estilos():
        st.markdown("""
            <style>
                .main .block-container {
                    padding-top: 1.5rem;
                    max-width: 1200px;
                }
                /* Cartões KPI em Tons de Cinza Executivo com Bordo Verde Accent */
                [data-testid="stMetric"] {
                    background-color: #1e222a;
                    border: 1px solid #2e3440;
                    border-left: 3px solid #10b981;
                    padding: 14px 18px;
                    border-radius: 6px;
                }
                [data-testid="stMetricLabel"] {
                    font-size: 0.78rem !important;
                    color: #94a3b8 !important;
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                }
                [data-testid="stMetricValue"] {
                    font-size: 1.35rem !important;
                    font-weight: 700;
                    color: #ffffff !important;
                }
                /* Cor de destaque para os botões e seletores */
                div.stButton > button:first-child {
                    border-color: #10b981;
                }
            </style>
        """, unsafe_allow_html=True)

    @staticmethod
    def renderizar():
        AdminAnalyticsView._injetar_estilos()

        # 1. Controlo de Acesso
        utilizador = st.session_state.get('utilizador_logado')
        if not utilizador or utilizador.get('perfil') != 'Admin':
            st.error("Acesso restrito a administradores.")
            return

        # 2. Cabeçalho Executivo
        st.title("Painel de Analítica Global")
        st.caption("Métricas de adesão, impacto das condições climatéricas e volume de atividade da plataforma.")
        st.markdown("---")

        # 3. Obtenção dos Dados Globais via Supabase
        dados_brutos = ActivityModel.obter_metricas_globais_admin().get("dados_completos", [])

        if not dados_brutos:
            st.info("Não existem dados de atividades registados na plataforma para análise.")
            return

        # 4. Tratamento dos Dados com Pandas
        df = pd.DataFrame(dados_brutos)
        df['data_registo'] = pd.to_datetime(df['data_registo'])
        df['km_corridos'] = pd.to_numeric(df.get('km_corridos', 0), errors='coerce').fillna(0)
        df['minutos_treino'] = pd.to_numeric(df.get('minutos_treino', 0), errors='coerce').fillna(0)
        df['temperatura'] = pd.to_numeric(df.get('temperatura', 0), errors='coerce').fillna(0)
        df['copos_agua'] = pd.to_numeric(df.get('copos_agua', 0), errors='coerce').fillna(0)
        df['pecas_fruta'] = pd.to_numeric(df.get('pecas_fruta', 0), errors='coerce').fillna(0)
        df['pontos_ganhos'] = pd.to_numeric(df.get('pontos_ganhos', 0), errors='coerce').fillna(0)

        # SECÇÃO 1: METRICAS GLOBAIS DE PLATAFORMA (KPIs)
        total_atividades = len(df)
        total_kms = df['km_corridos'].sum()
        total_horas = df['minutos_treino'].sum() / 60
        temp_media = df[df['temperatura'] > 0]['temperatura'].mean() if (df['temperatura'] > 0).any() else 0
        utilizadores_ativos = df['utilizador_id'].nunique() if 'utilizador_id' in df.columns else 1

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Total Atividades", f"{total_atividades}")
        col2.metric("Utilizadores Ativos", f"{utilizadores_ativos}")
        col3.metric("Volume Corrida", f"{total_kms:.1f} km")
        col4.metric("Horas de Treino", f"{total_horas:.1f} h")
        col5.metric("Temp. Média Treinos", f"{temp_media:.1f} °C")

        st.markdown("<br>", unsafe_allow_html=True)

        # Paleta Executiva: Escala de Cinzas + Verde EcoFit (#10b981)
        VERDE_ECOFIT = "#10b981"
        VERDE_SUAVE = "#34d399"
        CINZA_TEXTO = "#94a3b8"
        CINZA_GRELHA = "#2e3440"

        # SECÇÃO 2: ANÁLISE DE IMPACTO CLIMATÉRICO NOS TREINOS
        st.markdown("##### Análise de Impacto Climatérico")
        
        col_clima1, col_clima2 = st.columns(2)

        with col_clima1:
            # Scatter Plot em Cinza e Verde
            fig_temp = px.scatter(
                df[df['temperatura'] > 0],
                x="temperatura",
                y="km_corridos",
                color="tipo_insercao" if "tipo_insercao" in df.columns else None,
                title="Relação: Temperatura (°C) vs. Distância Corrida (km)",
                labels={"temperatura": "Temperatura (°C)", "km_corridos": "Distância (km)"},
                color_discrete_sequence=[VERDE_ECOFIT, "#64748b"]
            )
            fig_temp.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Inter, sans-serif", size=12, color=CINZA_TEXTO),
                xaxis=dict(showgrid=True, gridcolor=CINZA_GRELHA),
                yaxis=dict(showgrid=True, gridcolor=CINZA_GRELHA)
            )
            with st.container(border=True):
                st.plotly_chart(fig_temp, use_container_width=True)

        with col_clima2:
            # Gráfico de Barras em Tons de Cinza com Bordo/Realce Verde
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
                color_discrete_sequence=[VERDE_ECOFIT]
            )
            fig_faixas.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Inter, sans-serif", size=12, color=CINZA_TEXTO),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor=CINZA_GRELHA)
            )
            with st.container(border=True):
                st.plotly_chart(fig_faixas, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # SECÇÃO 3: ADESÃO E DISTRIBUIÇÃO DA PLATAFORMA
        st.markdown("##### Métricas de Utilização e Hábitos")

        col_hab1, col_hab2 = st.columns(2)

        with col_hab1:
            # Donut Chart Verde EcoFit + Gradiente de Cinzas
            if 'tipo_insercao' in df.columns:
                df_metodo = df['tipo_insercao'].value_counts().reset_index()
                df_metodo.columns = ['Tipo', 'Quantidade']

                fig_pie = px.pie(
                    df_metodo,
                    names='Tipo',
                    values='Quantidade',
                    title="Origem dos Dados de Atividade",
                    hole=0.45,
                    color_discrete_sequence=[VERDE_ECOFIT, "#475569", "#94a3b8"]
                )
                fig_pie.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(family="Inter, sans-serif", size=12, color=CINZA_TEXTO)
                )
                with st.container(border=True):
                    st.plotly_chart(fig_pie, use_container_width=True)

        with col_hab2:
            # Gráfico de Linha em Verde EcoFit
            df_diario = df.groupby(df['data_registo'].dt.strftime('%Y-%m-%d'))['km_corridos'].sum().reset_index()

            fig_linha = px.line(
                df_diario,
                x='data_registo',
                y='km_corridos',
                title="Volume Diário Global de Quilómetros Percorridos",
                labels={'data_registo': 'Data', 'km_corridos': 'Total Km'},
                color_discrete_sequence=[VERDE_SUAVE]
            )
            fig_linha.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Inter, sans-serif", size=12, color=CINZA_TEXTO),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor=CINZA_GRELHA)
            )
            with st.container(border=True):
                st.plotly_chart(fig_linha, use_container_width=True)

        st.markdown("---")

        # SECÇÃO 4: TABELA DETALHADA PARA AUDITORIA
        st.markdown("##### Registo Geral de Atividades para Auditoria")

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