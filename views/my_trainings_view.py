import streamlit as st
import pandas as pd
from models.activity_model import ActivityModel

class MyTrainingsView:
    @staticmethod
    def renderizar(utilizador_id):
        """
        Renderiza a vista de histórico, tabela e edição de treinos usando o ActivityModel.
        """
        st.subheader("Os Meus Treinos")

        # 1. Obter dados via ActivityModel
        atividades = ActivityModel.buscar_por_utilizador(utilizador_id)

        if not atividades:
            st.info("Ainda não registou nenhuma atividade. Utilize a aba 'Inserir Atividade' para começar!")
            return

        # 2. DataFrame e Mapeamento de Colunas da tua bd_atividades
        df_treinos = pd.DataFrame(atividades)

        col_id = 'atividade_id' if 'atividade_id' in df_treinos.columns else 'id'
        col_data = 'data_registo' if 'data_registo' in df_treinos.columns else 'data'
        col_km = 'km_corridos' if 'km_corridos' in df_treinos.columns else 'distancia_km'
        col_min = 'minutos_treino' if 'minutos_treino' in df_treinos.columns else ('minutos' if 'minutos' in df_treinos.columns else 'duracao_min')
        col_tipo = 'modalidade' if 'modalidade' in df_treinos.columns else 'tipo_atividade'

        # Ordenar por data mais recente
        if col_data in df_treinos.columns:
            df_treinos[col_data] = pd.to_datetime(df_treinos[col_data])
            df_treinos = df_treinos.sort_values(by=col_data, ascending=False)

        # 3. Métricas
        total_registos = len(df_treinos)
        distancia_total = df_treinos[col_km].sum() if col_km in df_treinos.columns else 0.0
        duracao_total_min = int(df_treinos[col_min].sum()) if col_min in df_treinos.columns else 0

        # Conversão e Formatação do Tempo (Minutos -> Horas e Minutos)
        h_sync = duracao_total_min // 60
        m_sync = duracao_total_min % 60
        tempo_total_str = f"{h_sync}h {m_sync}m" if h_sync > 0 else f"{m_sync} min"

        # Cartões KPI em Linha (3 Colunas)
        col1, col2, col3 = st.columns(3)

        col1.metric(
            label="Atividades", 
            value=f"{total_registos}",
            help="Número total de registos de treino importados do ficheiro."
        )

        col2.metric(
            label="Distância", 
            value=f"{distancia_total:.2f} km",
            help="Quilómetros acumulados presentes no ficheiro sincronizado."
        )

        col3.metric(
            label="Tempo", 
            value=tempo_total_str,
            help="Tempo acumulado gasto em sessões de treino importadas."
        )

        st.markdown("<br>", unsafe_allow_html=True)

        st.divider()

        # 4. Tabela de Apresentação
        st.markdown("##### Listagem de Atividades")
        df_exibicao = df_treinos.copy()
        if col_data in df_exibicao.columns:
            df_exibicao['Data'] = df_exibicao[col_data].dt.strftime('%d/%m/%Y %H:%M')
        if col_tipo in df_exibicao.columns:
            df_exibicao['Atividade'] = df_exibicao[col_tipo]
        if col_km in df_exibicao.columns:
            df_exibicao['Distância (km)'] = df_exibicao[col_km]
        if col_min in df_exibicao.columns:
            df_exibicao['Duração (min)'] = df_exibicao[col_min]

        cols = [c for c in ['Data', 'Atividade', 'Distância (km)', 'Duração (min)'] if c in df_exibicao.columns]
        st.dataframe(df_exibicao[cols], width="stretch", hide_index=True)

        st.divider()

        # 5. Edição e Eliminação Individual
        st.markdown("##### Gerir / Editar Registos")
        for _, treino in df_treinos.iterrows():
            t_id = treino.get(col_id)
            t_data = treino[col_data].strftime('%d/%m/%Y %H:%M') if isinstance(treino[col_data], pd.Timestamp) else str(treino.get(col_data, ''))
            t_tipo = treino.get(col_tipo, 'Treino')
            t_km = treino.get(col_km, 0.0)
            t_min = treino.get(col_min, 0)

            with st.expander(f"{t_data} — {t_tipo} ({t_km} km | {t_min} min)", expanded=False):
                with st.form(key=f"form_edit_{t_id}"):
                    c1, c2 = st.columns(2)
                    with c1:
                        novo_km = st.number_input("Distância (km)", min_value=0.0, max_value=500.0, value=float(t_km), step=0.1, key=f"km_{t_id}")
                    with c2:
                        novo_min = st.number_input("Duração (min)", min_value=1, max_value=1440, value=int(t_min), step=1, key=f"min_{t_id}")

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



    @staticmethod
    def renderizar(utilizador_id, utilizador_nome="Atleta"):
        # ... (código existente da view até à secção do download) ...

        # 6. EXPORTAR HISTÓRICO DE TREINOS (CSV)
        st.divider()
        st.markdown("##### 📥 Exportar Histórico")

        # Preparar dados para o ficheiro CSV
        df_export = df_treinos.copy()
        
        if col_data in df_export.columns and pd.api.types.is_datetime64_any_dtype(df_export[col_data]):
            df_export[col_data] = df_export[col_data].dt.strftime('%Y-%m-%d %H:%M:%S')

        csv_data = df_export.to_csv(index=False, encoding='utf-8-sig')

        # Tratamento e formatação do nome para o ficheiro
        nome_limpo = str(utilizador_nome).lower().strip().replace(" ", "_")

        st.download_button(
            label="Descarregar Histórico em CSV",
            data=csv_data,
            file_name=f"historico_treinos_utilizador_{utilizador_id}_{nome_limpo}.csv",
            mime="text/csv",
            width="stretch",
            key="btn_download_csv_trainings"
        )