import streamlit as st
import pandas as pd
from models.activity_model import ActivityModel

class MyTrainingsView:
    @staticmethod
    def renderizar(utilizador_id, utilizador_nome="Atleta"):
        """
        Renderiza a vista de histórico, tabela e edição de treinos com mapeamento descritivo e dados completos.
        """
        st.subheader("Os Meus Treinos")

        # 1. Obter dados via ActivityModel
        atividades = ActivityModel.buscar_por_utilizador(utilizador_id)

        if not atividades:
            st.info("Ainda não registou nenhuma atividade. Utilize a aba 'Inserir Atividade' para começar!")
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

        # Dicionário de mapeamento para transformar IDs de tipo de atividade em nomes legíveis
        mapa_tipos_atividade = {
            1: "Corrida",
            2: "Ciclismo",
            3: "Caminhada",
            4: "Ginásio / Força",
            5: "Outro"
        }

        # Criar coluna descritiva legível para a atividade
        def obter_nome_atividade(row):
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

        # 3. Métricas
        total_registos = len(df_treinos)
        distancia_total = df_treinos[col_km].sum() if col_km in df_treinos.columns else 0.0
        duracao_total_min = int(df_treinos[col_min].sum()) if col_min in df_treinos.columns else 0

        h_sync = duracao_total_min // 60
        m_sync = duracao_total_min % 60
        tempo_total_str = f"{h_sync}h {m_sync}m" if h_sync > 0 else f"{m_sync} min"

        col1, col2, col3 = st.columns(3)
        col1.metric("Atividades", f"{total_registos}")
        col2.metric("Distância", f"{distancia_total:.2f} km")
        col3.metric("Tempo", tempo_total_str)

        st.markdown("<br>", unsafe_allow_html=True)
        st.divider()

        # 4. Tabela de Apresentação (Apenas Data sem horas e Nome legível)
        st.markdown("##### Listagem de Atividades")
        df_exibicao = df_treinos.copy()
        
        if col_data in df_exibicao.columns:
            df_exibicao['Data'] = df_exibicao[col_data].dt.strftime('%d/%m/%Y')  # Removidas as horas
            
        df_exibicao['Atividade'] = df_exibicao['nome_atividade_legivel']
        df_exibicao['Distância (km)'] = df_exibicao[col_km]
        df_exibicao['Duração (min)'] = df_exibicao[col_min]

        cols = [c for c in ['Data', 'Atividade', 'Distância (km)', 'Duração (min)'] if c in df_exibicao.columns]
        st.dataframe(df_exibicao[cols], width="stretch", hide_index=True)

        st.divider()

        # 5. Edição e Eliminação Individual (Com detalhes alargados: Temperatura, Água, Fruta, etc.)
        st.markdown("##### Gerir / Editar Registos")
        for _, treino in df_treinos.iterrows():
            t_id = treino.get(col_id)
            t_data_val = treino.get(col_data)
            t_data_str = t_data_val.strftime('%d/%m/%Y') if pd.notnull(t_data_val) else str(treino.get('data_registo', ''))[:10]
            t_tipo = treino.get('nome_atividade_legivel', 'Treino')
            t_km = float(treino.get(col_km, 0.0))
            
            t_min_raw = treino.get(col_min, 1)
            t_min = int(t_min_raw) if pd.notnull(t_min_raw) and int(t_min_raw) > 0 else 1

            # Informação extra para exibir no expander
            t_temp = treino.get('temperatura', 'N/D')
            t_agua = treino.get('copos_agua', 0)
            t_fruta = treino.get('pecas_fruta', 0)
            t_pontos = treino.get('pontos_ganhos', 0)

            titulo_expander = f"{t_data_str} — {t_tipo} ({t_km} km | {t_min} min)"

            with st.expander(titulo_expander, expanded=False):
                # Informações detalhadas do treino
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
        # EXPORTAR HISTÓRICO DE TREINOS (CSV)
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
                file_name=f"historico_treinos_utilizador_{utilizador_id}_{nome_limpo}.csv",
                mime="text/csv",
                width="stretch",
                key="btn_download_csv_trainings"
            )
        else:
            st.info("Sem registos de treinos disponíveis para exportação.")