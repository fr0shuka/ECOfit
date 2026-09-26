import sys
import os
import streamlit as st
import pandas as pd
import plotly.express as px

# Resolver caminho para a raiz
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from controllers.admin_controller import AdminController
from models.activity_model import ActivityModel
from models.user_model import UserModel


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
                    border: 1px solid #FF4B4B;
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
    def _e_admin(utilizador: dict) -> bool:
        """Verifica se o utilizador tem permissões de administrador de forma resiliente."""
        if not utilizador:
            return False
        if utilizador.get('tipo_id') == 4:
            return True
        info_tipo = utilizador.get('bd_tipos_utilizador') or {}
        nome_tipo = info_tipo.get('nome') or info_tipo.get('descricao') or ''
        if str(nome_tipo).lower() == 'admin':
            return True
        if str(utilizador.get('perfil', '')).lower() == 'admin':
            return True
        return False

    @staticmethod
    def renderizar():
        AdminAnalyticsView._injetar_estilos()

        # 1. Controlo de Acesso Resiliente
        utilizador = st.session_state.get('utilizador_logado')
        if not AdminAnalyticsView._e_admin(utilizador):
            st.error("Acesso restrito a administradores.")
            return

        # 2. Cabeçalho Executivo
        st.caption("Este painel consolida o desempenho global da plataforma ecoFIT, monitorizando a adesão dos utilizadores, a dinâmica dos registos e a correlação entre as variáveis climatéricas e o volume de treino registado.")
        st.markdown("---")

        # 3. Obtenção dos Dados Globais via Model
        res_metricas = ActivityModel.obter_metricas_globais_admin() or {}
        dados_brutos = res_metricas.get("dados_completos", [])

        if not dados_brutos:
            st.info("Não existem dados de atividades registados na plataforma para análise.")
            return

        # Obter todos os utilizadores para mapear o nome através do UserModel
        lista_utilizadores = UserModel.obter_todos_utilizadores() or []
        mapa_utilizadores = {
            u.get('utilizador_id'): u.get('nome', 'Atleta Desconhecido') 
            for u in lista_utilizadores
        }

        # 4. Tratamento dos Dados com Pandas
        df = pd.DataFrame(dados_brutos)
        
        # Injetar a coluna 'nome_utilizador' usando o ID
        if 'utilizador_id' in df.columns:
            df['nome_utilizador'] = df['utilizador_id'].map(mapa_utilizadores).fillna('Desconhecido')
        else:
            df['nome_utilizador'] = 'Desconhecido'

        # Compatibilidade de colunas (distancia_km vs km_corridos)
        if 'distancia_km' in df.columns:
            df['distancia_km'] = pd.to_numeric(df['distancia_km'], errors='coerce').fillna(0)
        elif 'km_corridos' in df.columns:
            df['distancia_km'] = pd.to_numeric(df['km_corridos'], errors='coerce').fillna(0)
        else:
            df['distancia_km'] = 0.0

        df['data_registo'] = pd.to_datetime(df['data_registo'])
        df['minutos_treino'] = pd.to_numeric(df.get('minutos_treino', 0), errors='coerce').fillna(0)
        df['temperatura'] = pd.to_numeric(df.get('temperatura', 0), errors='coerce').fillna(0)
        df['copos_agua'] = pd.to_numeric(df.get('copos_agua', 0), errors='coerce').fillna(0)
        df['pecas_fruta'] = pd.to_numeric(df.get('pecas_fruta', 0), errors='coerce').fillna(0)
        df['pontos_ganhos'] = pd.to_numeric(df.get('pontos_ganhos', 0), errors='coerce').fillna(0)

        # SECÇÃO 1: METRICAS GLOBAIS DE PLATAFORMA (KPIs)
        total_atividades = len(df)
        total_kms = df['distancia_km'].sum()
        total_horas = df['minutos_treino'].sum() / 60
        temp_media = df[df['temperatura'] > 0]['temperatura'].mean() if (df['temperatura'] > 0).any() else 0
        utilizadores_ativos = df['utilizador_id'].nunique() if 'utilizador_id' in df.columns else 1

        # Cálculo da string do tempo
        minutos_totais = int(df['minutos_treino'].sum())
        h = minutos_totais // 60
        m = minutos_totais % 60
        horas_treino_str = f"{h}h {m}m" if h > 0 else f"{m} min"

        col1, col2, col3, col4, col5 = st.columns(5)

        col1.metric(
            label="Atividades", 
            value=f"{total_atividades}",
            help="Número total de atividades registadas por todos os utilizadores."
        )

        col2.metric(
            label="Ativos", 
            value=f"{utilizadores_ativos}",
            help="Quantidade de utilizadores com pelo menos uma atividade registada."
        )

        col3.metric(
            label="Distância", 
            value=f"{total_kms:.1f} km",
            help="Volume total de quilómetros acumulados na plataforma."
        )

        col4.metric(
            label="Tempo", 
            value=horas_treino_str,
            help="Total de tempo acumulado em treinos."
        )

        col5.metric(
            label="Temp. Média", 
            value=f"{temp_media:.1f} °C",
            help="Temperatura média registada durante as sessões de treino."
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # SECÇÃO 2: ANÁLISE DE IMPACTO CLIMATÉRICO NOS TREINOS
        st.markdown("##### Análise de impacto Climatérico")
        
        col_clima1, col_clima2 = st.columns(2)

        with col_clima1:
            fig_temp = px.scatter(
                df[df['temperatura'] > 0],
                x="temperatura",
                y="distancia_km",
                color="tipo_insercao" if "tipo_insercao" in df.columns else None,
                title="Relação: Temperatura (°C) vs. Distância Corrida (km)",
                labels={"temperatura": "Temperatura (°C)", "distancia_km": "Distância (km)"},
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
                st.plotly_chart(fig_temp, width="stretch")

        with col_clima2:
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
                st.plotly_chart(fig_faixas, width="stretch")

        st.markdown("<br>", unsafe_allow_html=True)

        # SECÇÃO 3: ADESÃO E DISTRIBUIÇÃO DA PLATAFORMA
        st.markdown("##### Métricas de utilização e hábitos")

        col_hab1, col_hab2 = st.columns(2)

        with col_hab1:
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
                    st.plotly_chart(fig_pie, width="stretch")

        with col_hab2:
            df_diario = df.groupby(df['data_registo'].dt.strftime('%Y-%m-%d'))['distancia_km'].sum().reset_index()

            fig_linha = px.line(
                df_diario,
                x='data_registo',
                y='distancia_km',
                title="Volume Diário Global de Quilómetros Percorridos",
                labels={'data_registo': 'Data', 'distancia_km': 'Total Km'},
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
                st.plotly_chart(fig_linha, width="stretch")

        st.markdown("---")

        # SECÇÃO 3.1: ADESÃO E DISTRIBUIÇÃO DA PLATAFORMA
        st.markdown("##### Métricas de Utilização e Adesão")

        col_hab1, col_hab2 = st.columns(2)

        with col_hab1:
            if 'utilizador_id' in df.columns and 'data_registo' in df.columns:
                primeiro_registo = df.groupby('utilizador_id')['data_registo'].min().reset_index()
                primeiro_registo['data_dia'] = primeiro_registo['data_registo'].dt.strftime('%Y-%m-%d')
                
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
                    st.plotly_chart(fig_utilizadores, width="stretch")

        with col_hab2:
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
                    st.plotly_chart(fig_atividades, width="stretch")

        st.markdown("---")

        # SECÇÃO 4: TABELA DETALHADA PARA AUDITORIA
        st.markdown("##### Registo Geral de Atividades")

        colunas_exibir = {
            'data_registo': 'Data',
            'nome_utilizador': 'Atleta',
            'distancia_km': 'Distância (km)',
            'minutos_treino': 'Duração (min)',
            'temperatura': 'Temp. (°C)',
            'tipo_insercao': 'Método',
            'pontos_ganhos': 'Pontos'
        }

        cols_presentes = [c for c in colunas_exibir.keys() if c in df.columns]
        df_auditoria = df[cols_presentes].copy()

        if 'data_registo' in df_auditoria.columns:
            df_auditoria['data_registo'] = df_auditoria['data_registo'].dt.strftime('%Y-%m-%d')

        df_auditoria.rename(columns=colunas_exibir, inplace=True)

        st.dataframe(
            df_auditoria.sort_values(by="Data", ascending=False),
            width="stretch",
            hide_index=True
        )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("---")

        AdminAnalyticsView.renderizar_exportador_dados(df)

    @staticmethod
    def renderizar_exportador_dados(df_atividades):
        st.markdown("### Exportação de Dados")
        st.caption("Descarrega o ficheiro consolidado para análise externa.")

        if df_atividades.empty:
            st.warning("Não existem dados disponíveis para exportação.")
            return

        # Converter o DataFrame para CSV
        csv_data = df_atividades.to_csv(index=False).encode('utf-8')

        st.download_button(
            label="📥 Descarregar dados (CSV)",
            data=csv_data,
            file_name="ecofit_dados_completos.csv",
            mime="text/csv",
            help="Clica para exportar todos os dados para análise externa."
        )