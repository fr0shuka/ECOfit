import sys
import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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
                [data-testid="stMetric"] {
                    background-color: #1e222a;
                    border: 1px solid #2e3440;
                    padding: 14px 18px;
                    border-radius: 8px;
                }
                [data-testid="stMetricLabel"] {
                    font-size: 0.78rem !important;
                    color: #94a3b8 !important;
                    font-weight: 500;
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                }
                [data-testid="stMetricValue"] {
                    font-size: 1.35rem !important;
                    font-weight: 700;
                    color: #ffffff !important;
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
        st.caption("Este painel consolida o desempenho global da plataforma ecoFIT, monitorizando a adesão dos utilizadores, a dinâmica dos registos e a correlação entre as variáveis climatéricas e o volume de treino registado.")
        st.markdown("---")

        # 3. Obtenção dos Dados Globais via Model
        # Assumindo a função que recolhe os registos de todos os utilizadores
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

        # Cálculos de apoio para subtextos contextuais
        media_atividades_usr = total_atividades / utilizadores_ativos if utilizadores_ativos > 0 else 0
        media_km_usr = total_kms / utilizadores_ativos if utilizadores_ativos > 0 else 0

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            with st.container(border=True):
                st.caption("📋 Total Atividades")
                st.subheader(f"{total_atividades}")
                st.caption(f"~{media_atividades_usr:.1f} / utilizador")

        with col2:
            with st.container(border=True):
                st.caption("👥 Utilizadores Ativos")
                st.subheader(f"{utilizadores_ativos}")
                st.caption("Com registos efetuados")

        with col3:
            with st.container(border=True):
                st.caption("🏃 Volume Corrida")
                st.subheader(f"{total_kms:.1f} km")
                st.caption(f"~{media_km_usr:.1f} km / utilizador")

        with col4:
            with st.container(border=True):
                st.caption("⏱️ Horas de Treino")
                st.subheader(f"{total_horas:.1f} h")
                st.caption(f"{df['minutos_treino'].sum():.0f} min acumulados")

        with col5:
            with st.container(border=True):
                st.caption("🌡️ Temp. Média")
                st.subheader(f"{temp_media:.1f} °C")
                st.caption("Nos dias de treino")

        st.markdown("<br>", unsafe_allow_html=True)

        # SECÇÃO 2: ANÁLISE DE IMPACTO CLIMATÉRICO NOS TREINOS
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
        st.markdown("##### Métricas de utilização e hábitos")

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

        # SECÇÃO 3.1: ADESÃO E DISTRIBUIÇÃO DA PLATAFORMA
        st.markdown("##### Métricas de Utilização e Adesão")

        col_hab1, col_hab2 = st.columns(2)

        with col_hab1:
            # 1. Adesão de Utilizadores (Crescimento Acumulado de Utilizadores Ativos)
            if 'utilizador_id' in df.columns and 'data_registo' in df.columns:
                # Identifica a primeira atividade de cada utilizador
                primeiro_registo = df.groupby('utilizador_id')['data_registo'].min().reset_index()
                primeiro_registo['data_dia'] = primeiro_registo['data_registo'].dt.strftime('%Y-%m-%d')
                
                # Conta novos utilizadores por dia e calcula o acumulado
                novos_usrs = primeiro_registo.groupby('data_dia').size().reset_index(name='novos')
                novos_usrs = novos_usrs.sort_values('data_dia')
                novos_usrs['total_acumulado'] = novos_usrs['novos'].cumsum()

                fig_utilizadores = px.line(
                    novos_usrs,
                    x='data_dia',
                    y='total_acumulado',
                    markers=True,
                    title="Adesão de Utilizadores (Acumulado)",
                    labels={'data_dia': 'Data', 'total_acumulado': 'N.º Utilizadores'},
                    color_discrete_sequence=['#4da6ff']
                )
                fig_utilizadores.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(family="Inter, sans-serif", size=12, color="#94a3b8"),
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=True, gridcolor="#2e3440")
                )
                with st.container(border=True):
                    st.plotly_chart(fig_utilizadores, use_container_width=True)

        with col_hab2:
            # 2. Adesão de Atividades (Volume Diário por Método de Inserção)
            if 'data_registo' in df.columns:
                df['data_dia'] = df['data_registo'].dt.strftime('%Y-%m-%d')
                col_tipo = 'tipo_insercao' if 'tipo_insercao' in df.columns else None
                
                if col_tipo:
                    df_atividades = df.groupby(['data_dia', col_tipo]).size().reset_index(name='total_atividades')
                    fig_atividades = px.bar(
                        df_atividades,
                        x='data_dia',
                        y='total_atividades',
                        color=col_tipo,
                        title="Adesão de Atividades (Volume Diário)",
                        labels={'data_dia': 'Data', 'total_atividades': 'Total Atividades', col_tipo: 'Método'},
                        color_discrete_sequence=['#34d399', '#4da6ff', '#f59e0b']
                    )
                else:
                    df_atividades = df.groupby('data_dia').size().reset_index(name='total_atividades')
                    fig_atividades = px.bar(
                        df_atividades,
                        x='data_dia',
                        y='total_atividades',
                        title="Adesão de Atividades (Volume Diário)",
                        labels={'data_dia': 'Data', 'total_atividades': 'Total Atividades'},
                        color_discrete_sequence=['#34d399']
                    )

                fig_atividades.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(family="Inter, sans-serif", size=12, color="#94a3b8"),
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=True, gridcolor="#2e3440")
                )
                with st.container(border=True):
                    st.plotly_chart(fig_atividades, use_container_width=True)
                    

        st.markdown("---")


        # SECÇÃO 4: TABELA DETALHADA PARA AUDITORIA
        st.markdown("##### Registo Geral de Atividades")

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

        # Formatar a data para apenas Ano-Mês-Dia (sem horas)
        if 'data_registo' in df_auditoria.columns:
            df_auditoria['data_registo'] = df_auditoria['data_registo'].dt.strftime('%Y-%m-%d')

        df_auditoria.rename(columns=colunas_exibir, inplace=True)

        st.dataframe(
            df_auditoria.sort_values(by="Data", ascending=False),
            use_container_width=True,
            hide_index=True
        )