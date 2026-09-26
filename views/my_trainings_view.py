import streamlit as st
import pandas as pd
from models.activity_model import ActivityModel

class MyTrainingsView:
    @staticmethod
    def renderizar(utilizador_id, utilizador_nome="Atleta"):
        """
        Renderiza a vista de histórico, tabela, edição e Análise Exploratória de Dados (EDA),
        distinguindo treinos físicos de registos exclusivos de hábitos.
        """
        st.subheader("Os Meus Registos e Treinos")

        # 1. Obter dados via ActivityModel
        atividades = ActivityModel.buscar_por_utilizador(utilizador_id)

        if not atividades:
            st.info("Ainda não registou nenhuma atividade ou hábito. Utilize as abas de inserção para começar!")
            return

        df_treinos = pd.DataFrame(atividades)

        col_id = 'atividade_id' if 'atividade_id' in df_treinos.columns else 'id'
        col_data = 'data_registo' if 'data_registo' in df_treinos.columns else ('data' if 'data' in df_treinos.columns else 'created_at')
        
        if 'distancia_km' in df_treinos.columns:
            col_km = 'distancia_km'
        elif 'km_corridos' in df_treinos.columns:
            col_km = 'km_corridos'
        else:
            df_treinos['distancia_km'] = 0.0
            col_km = 'distancia_km'

        col_min = 'minutos_treino' if 'minutos_treino' in df_treinos.columns else ('minutos' if 'minutos' in df_treinos.columns else 'duracao_min')

        mapa_tipos_atividade = {
            1: "Corrida",
            2: "Ciclismo",
            3: "Caminhada",
            4: "Ginásio / Força",
            5: "Outro"
        }

        # Função para detetar se é um registo exclusivo de hábitos saudáveis
        def obter_nome_atividade(row):
            km = float(row.get(col_km, 0.0) or 0.0)
            mins = int(row.get(col_min, 0) or 0)
            agua = int(row.get('copos_agua', 0) or 0)
            fruta = int(row.get('pecas_fruta', 0) or 0)

            if km == 0 and mins == 0 and (agua > 0 or fruta > 0):
                return "Hábitos Saudáveis"

            for c_tipo in ['tipo_atividade', 'modalidade', 'tipo_atividade_id', 'atividade_id_tipo']:
                if c_tipo in row and pd.notnull(row[c_tipo]):
                    val = row[c_tipo]
                    if isinstance(val, (int, float)) or str(val).isdigit():
                        return mapa_tipos_atividade.get(int(val), f"Atividade #{val}")
                    return str(val)
            
            return "Sessão de Treino"

        df_treinos['nome_atividade_legivel'] = df_treinos.apply(obter_nome_atividade, axis=1)

        # Ordenar por data mais recente
        if col_data in df_treinos.columns:
            df_treinos[col_data] = pd.to_datetime(df_treinos[col_data], errors='coerce')
            df_treinos = df_treinos.sort_values(by=col_data, ascending=False)

        # 3. Métricas globais
        total_registos = len(df_treinos)
        distancia_total = df_treinos[col_km].sum() if col_km in df_treinos.columns else 0.0
        duracao_total_min = int(df_treinos[col_min].sum()) if col_min in df_treinos.columns else 0

        h_sync = duracao_total_min // 60
        m_sync = duracao_total_min % 60
        tempo_total_str = f"{h_sync}h {m_sync}m" if h_sync > 0 else f"{m_sync} min"

        col1, col2, col3 = st.columns(3)
        col1.metric("Registos Totais", f"{total_registos}")
        col2.metric("Distância Acumulada", f"{distancia_total:.2f} km")
        col3.metric("Tempo Total", tempo_total_str)

        st.markdown("<br>", unsafe_allow_html=True)
        st.divider()

        # 4. Tabela de Apresentação
        st.markdown("##### Histórico Geral")
        df_exibicao = df_treinos.copy()
        
        if col_data in df_exibicao.columns:
            df_exibicao['Data'] = df_exibicao[col_data].dt.strftime('%d/%m/%Y')
            
        df_exibicao['Registo / Atividade'] = df_exibicao['nome_atividade_legivel']
        df_exibicao['Distância (km)'] = df_exibicao[col_km]
        df_exibicao['Duração (min)'] = df_exibicao[col_min]

        cols = [c for c in ['Data', 'Registo / Atividade', 'Distância (km)', 'Duração (min)'] if c in df_exibicao.columns]
        st.dataframe(df_exibicao[cols], width="stretch", hide_index=True)

        st.divider()

        #################################################################
        # 5. ANÁLISE
        #################################################################
        st.markdown("##### Análise Exploratória de Dados")
        st.caption("Resumo estatístico rigoroso das métricas de desempenho para avaliação analítica.")

        df_fisico = df_treinos[(df_treinos[col_km] > 0) | (df_treinos[col_min] > 0)]

        if not df_fisico.empty:
            stats_km = df_fisico[col_km].describe()
            stats_min = df_fisico[col_min].describe()

            # Funções auxiliares de formatação de tempo para o utilizador
            def formatar_minutos_para_horas(total_minutos):
                if pd.isna(total_minutos) or total_minutos <= 0:
                    return "0 min"
                h = int(total_minutos // 60)
                m = int(round(total_minutos % 60))
                if h > 0:
                    return f"{h}h {m}m"
                return f"{m} min"

            aba_eda_km, aba_eda_min, aba_eda_tabela, aba_eda_explicacao = st.tabs([
                "🏃‍♂️ Distância (km)", 
                "⏱️ Duração (Tempo)", 
                "📋 Relatório Completo", 
                "💡 O que significam estas medidas?"
            ])

            with aba_eda_km:
                e1, e2, e3, e4 = st.columns(4)
                e1.metric("Média (Mean)", f"{stats_km['mean']:.2f} km")
                e2.metric("Mediana (Q2)", f"{stats_km['50%']:.2f} km")
                e3.metric("Desvio Padrão", f"{stats_km['std']:.2f} km")
                e4.metric("Máximo (Pico)", f"{stats_km['max']:.2f} km")

            with aba_eda_min:
                e1, e2, e3, e4 = st.columns(4)
                e1.metric("Média de Tempo", formatar_minutos_para_horas(stats_min['mean']))
                e2.metric("Mediana (Q2)", formatar_minutos_para_horas(stats_min['50%']))
                e3.metric("Desvio Padrão", f"{stats_min['std']:.1f} min")
                e4.metric("Sessão Mais Longa", formatar_minutos_para_horas(stats_min['max']))

            with aba_eda_tabela:
                # Criar dataframe com tempos formatados para legibilidade humana
                df_descritivo = pd.DataFrame({
                    "Medida Estatística": ["Média (Média Aritmética)", "Desvio Padrão (Dispersão)", "Mínimo", "1º Quartil (Q1 - 25%)", "Mediana (Q2 - 50%)", "3º Quartil (Q3 - 75%)", "Máximo"],
                    "Distância (km)": [
                        f"{stats_km['mean']:.2f}", f"{stats_km['std']:.2f}", f"{stats_km['min']:.2f}",
                        f"{stats_km['25%']:.2f}", f"{stats_km['50%']:.2f}", f"{stats_km['75%']:.2f}", f"{stats_km['max']:.2f}"
                    ],
                    "Duração": [
                        formatar_minutos_para_horas(stats_min['mean']), 
                        f"{stats_min['std']:.1f} min", 
                        formatar_minutos_para_horas(stats_min['min']),
                        formatar_minutos_para_horas(stats_min['25%']), 
                        formatar_minutos_para_horas(stats_min['50%']), 
                        formatar_minutos_para_horas(stats_min['75%']), 
                        formatar_minutos_para_horas(stats_min['max'])
                    ]
                })
                st.dataframe(df_descritivo, width="stretch", hide_index=True)

            with aba_eda_explicacao:
                st.markdown("""
                ### Guia Prático das Medidas Estatísticas
                Utilizam-se os seguintes indicadores:

                * **Média (Tendência Central):** O valor obtido somando todas as observações e dividindo pelo número total. Representa o desempenho médio típico por sessão de treino.
                * **Mediana / Q2 (Posição Central):** O valor exato que se encontra a meio do conjunto de dados ordenado. Ao contrário da média, **não é afetada por valores extremos** (como um treino excecionalmente longo ou curto).
                * **Desvio Padrão (Dispersão):** Mede o quão dispersos estão os treinos em relação à média. Um desvio padrão baixo indica consistência e regularidade; um valor alto indica grande variabilidade nos hábitos de treino.
                * **Quartis (Q1 e Q3):** O 1º Quartil (25%) e o 3º Quartil (75%) dividem a distribuição dos dados, permitindo perceber, por exemplo, qual é o patamar de distância ou tempo que separa os 25% de treinos mais curtos dos restantes.
                """)
        else:
            st.info("Registe atividades físicas (com distância ou duração) para calcular as medidas estatísticas descritivas.")

        st.divider()
        # #################################################################
        # 5.1 AltaPerformance 
        # #################################################################
        from sklearn.cluster import KMeans
        from sklearn.preprocessing import StandardScaler
        import plotly.express as px

        st.markdown("##### Classificação Inteligente do Atleta (IA)")
        st.caption("Segmentação automática do seu histórico com base na distância, duração e pontos acumulados por sessão.")

        df_ml = df_treinos[(df_treinos[col_km] > 0) | (df_treinos[col_min] > 0)].copy()

        if len(df_ml) >= 3 and 'pontos_ganhos' in df_ml.columns:
            features_ml = [col_km, col_min, 'pontos_ganhos']
            X_ml = df_ml[features_ml].fillna(0)

            # Normalização e K-Means
            scaler_ml = StandardScaler()
            X_scaled_ml = scaler_ml.fit_transform(X_ml)

            kmeans_ml = KMeans(n_clusters=3, random_state=42, n_init=10)
            df_ml['cluster_treino'] = kmeans_ml.fit_predict(X_scaled_ml)

            # Mapear os clusters pelo volume médio de pontos
            cluster_means_ml = df_ml.groupby('cluster_treino')['pontos_ganhos'].mean().sort_values()
            sorted_ids_ml = cluster_means_ml.index.tolist()

            mapa_perfis_ml = {
                sorted_ids_ml[0]: "🟢 Sessão Leve / Recuperação",
                sorted_ids_ml[1]: "🟡 Sessão Moderada",
                sorted_ids_ml[2]: "🔥 Sessão de Alta Intensidade"
            }
            df_ml['perfil_sessao'] = df_ml['cluster_treino'].map(mapa_perfis_ml)

            # Gráfico de dispersão interativo individual
            fig_ml = px.scatter(
                df_ml,
                x=col_km,
                y='pontos_ganhos',
                color='perfil_sessao',
                size=col_min,
                hover_data=[col_data, col_min],
                title="Distribuição das Suas Sessões de Treino por Perfil de Intensidade",
                labels={col_km: "Distância (km)", "pontos_ganhos": "Pontos Ganhos", "perfil_sessao": "Perfil"},
                color_discrete_sequence=['#4da6ff', '#f59e0b', '#34d399']
            )
            fig_ml.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Inter, sans-serif", size=12, color="#94a3b8"),
                xaxis=dict(showgrid=True, gridcolor="#2e3440"),
                yaxis=dict(showgrid=True, gridcolor="#2e3440")
            )
            with st.container(border=True):
                st.plotly_chart(fig_ml, width="stretch")
        else:
            st.info("Registe pelo menos 3 atividades físicas consistentes para ativar a segmentação inteligente de sessões por Inteligência Artificial.")

        st.divider()

        # 6. Edição e Eliminação Individual
        st.markdown("##### Gerir / Editar Registos")
        for _, treino in df_treinos.iterrows():
            t_id = treino.get(col_id)
            t_data_val = treino.get(col_data)
            t_data_str = t_data_val.strftime('%d/%m/%Y') if pd.notnull(t_data_val) else str(treino.get('data_registo', ''))[:10]
            t_tipo = treino.get('nome_atividade_legivel', 'Registo')
            t_km = float(treino.get(col_km, 0.0))
            
            t_min_raw = treino.get(col_min, 1)
            t_min = int(t_min_raw) if pd.notnull(t_min_raw) and int(t_min_raw) > 0 else 1

            t_temp = treino.get('temperatura', 'N/D')
            t_agua = int(treino.get('copos_agua', 0) or 0)
            t_fruta = int(treino.get('pecas_fruta', 0) or 0)
            t_pontos = treino.get('pontos_ganhos', 0)

            if t_tipo == "Hábitos Saudáveis":
                titulo_expander = f"{t_data_str} — Hábitos Saudáveis"
            else:
                titulo_expander = f"{t_data_str} — {t_tipo} ({t_km} km | {t_min} min)"

            with st.expander(titulo_expander, expanded=False):
                st.caption(f"🌡️ **Temperatura:** {t_temp} °C | 💧 **Água:** {t_agua} copos | 🍎 **Fruta:** {t_fruta} peças | ⭐ **Pontos:** {t_pontos}")
                
                with st.form(key=f"form_edit_{t_id}"):
                    c1, c2 = st.columns(2)
                    with c1:
                        novo_km = st.number_input("Distância (km)", min_value=0.0, max_value=500.0, value=t_km, step=0.1, key=f"km_{t_id}")
                    with c2:
                        novo_min = st.number_input("Duração (min)", min_value=1, max_value=1440, value=t_min, step=1, key=f"min_{t_id}")

                    c_salvar, c_eliminar = st.columns([1, 1])
                    with c_salvar:
                        btn_salvar = st.form_submit_button("Atualizar", type="primary", width="stretch")
                    with c_eliminar:
                        btn_eliminar = st.form_submit_button("Eliminar", width="stretch")

                    if btn_salvar:
                        sucesso = ActivityModel.atualizar_atividade(t_id, {col_km: novo_km, col_min: novo_min})
                        if sucesso:
                            st.success("Registo atualizado!")
                            st.rerun()

                    if btn_eliminar:
                        sucesso = ActivityModel.eliminar_atividade(t_id)
                        if sucesso:
                            st.warning("Registo eliminado!")
                            st.rerun()

        #######
        # EXPORTAR HISTÓRICO (CSV)
        #######
        st.divider()
        st.markdown("##### 📥 Exportar Histórico")

        df_para_exportar = df_treinos

        if df_para_exportar is not None and not df_para_exportar.empty:
            df_export = df_para_exportar.copy()
            
            if col_data in df_export.columns and pd.api.types.is_datetime64_any_dtype(df_export[col_data]):
                df_export[col_data] = df_export[col_data].dt.strftime('%Y-%m-%d')

            csv_data = df_export.to_csv(index=False, encoding='utf-8-sig')
            nome_limpo = str(utilizador_nome).lower().strip().replace(" ", "_")

            st.download_button(
                label="Descarregar Histórico em CSV",
                data=csv_data,
                file_name=f"historico_registos_utilizador_{utilizador_id}_{nome_limpo}.csv",
                mime="text/csv",
                width="stretch",
                key="btn_download_csv_trainings"
            )
        else:
            st.info("Sem registos disponíveis para exportação!")