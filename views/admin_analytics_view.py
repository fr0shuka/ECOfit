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
from services.export_service import gerar_csv_completo_powerbi, publicar_csv_online


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
        utilizadores_ativos = df['utilizador_id'].nunique() if 'utilizador_id' in df.columns else 1

        minutos_totais = int(df['minutos_treino'].sum())
        h = minutos_totais // 60
        m = minutos_totais % 60
        horas_treino_str = f"{h}h {m}m" if h > 0 else f"{m} min"
        temp_media = df[df['temperatura'] > 0]['temperatura'].mean() if (df['temperatura'] > 0).any() else 0

        col1, col2, col3, col4, col5 = st.columns(5)

        col1.metric(label="Atividades", value=f"{total_atividades}")
        col2.metric(label="Ativos", value=f"{utilizadores_ativos}")
        col3.metric(label="Distância", value=f"{total_kms:.1f} km")
        col4.metric(label="Tempo", value=horas_treino_str)
        col5.metric(label="Temp. Média", value=f"{temp_media:.1f} °C")

        st.markdown("<br>", unsafe_allow_html=True)

        # SECÇÃO 2: ANÁLISE DE IMPACTO CLIMATÉRICO
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
            fig_temp.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#94a3b8"))
            with st.container(border=True):
                st.plotly_chart(fig_temp, use_container_width=True)

        with col_clima2:
            df['faixa_temp'] = pd.cut(
                df['temperatura'], 
                bins=[-10, 10, 20, 30, 50], 
                labels=['Frio (<10°C)', 'Agradável (10-20°C)', 'Quente (20-30°C)', 'Muito Quente (>30°C)']
            )
            df_temp_group = df.groupby('faixa_temp', observed=False)['minutos_treino'].mean().reset_index()

            fig_faixas = px.bar(
                df_temp_group, x='faixa_temp', y='minutos_treino',
                title="Média de Minutos de Treino por Faixa de Temperatura",
                color_discrete_sequence=['#94a3b8']
            )
            fig_faixas.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#94a3b8"))
            with st.container(border=True):
                st.plotly_chart(fig_faixas, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # SECÇÃO 3: TABELA DETALHADA PARA AUDITORIA
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

        st.dataframe(df_auditoria.sort_values(by="Data", ascending=False), use_container_width=True, hide_index=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("---")

        # CHAMADA OBRIGATÓRIA DA SECÇÃO DE EXPORTAÇÃO
        AdminAnalyticsView.renderizar_exportador_dados(df)

    @staticmethod
    def renderizar_exportador_dados(df_atividades):
        st.markdown("### Exportação de Dados")
        st.caption("Descarrega o ficheiro consolidado para análise externa.")

        if df_atividades.empty:
            st.warning("Não existem dados disponíveis para exportação.")
            return

        # Converter o DataFrame para CSV local
        csv_data = df_atividades.to_csv(index=False).encode('utf-8-sig')

        st.download_button(
            label="📥 Descarregar dados (CSV Local)",
            data=csv_data,
            file_name="ecofit_dados_completos.csv",
            mime="text/csv",
            help="Clica para exportar todos os dados para análise externa."
        )
        
        st.markdown("### 🌐 Sincronização Automática para Power BI (CSV Online)")
        st.caption("Publica o dataset atualizado na cloud para que o Power BI possa consultar os dados diretamente via URL web.")

        if st.button("🚀 Sincronizar dados para a Nuvem", key="btn_sync_cloud"):
            with st.spinner("A gerar dataset completo com nomes e a atualizar o link online..."):
                # 1. Obter dados globais de atividades
                res_metricas = ActivityModel.obter_metricas_globais_admin() or {}
                dados_globais = res_metricas.get("dados_completos", [])
                
                # 2. Obter a lista de utilizadores para o cruzamento de nomes
                lista_utilizadores = UserModel.obter_todos_utilizadores() or []
                
                # 3. Gerar o CSV passando as atividades e os utilizadores
                csv_string = gerar_csv_completo_powerbi(dados_globais, lista_utilizadores)
                
                if csv_string:
                    # 4. Enviar para o Supabase Storage
                    url_publico, erro = publicar_csv_online(csv_string)
                    
                    if erro:
                        st.error(f"Erro ao publicar online: {erro}")
                    else:
                        st.success("Dataset sincronizado com sucesso na nuvem!")
                        st.info("Copia o link abaixo e usa-o no Power BI (**Obter Dados > Web**):")
                        st.code(url_publico, language="text")
                else:
                    st.warning("Não existem dados suficientes para publicar.")