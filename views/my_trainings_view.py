import streamlit as st
import pandas as pd
from datetime import datetime

class MyTrainingsView:
    @staticmethod
    def renderizar(utilizador_id, activity_model):
        """
        Renderiza a vista de histórico e edição de treinos do utilizador.
        """
        st.subheader("Os Meus Treinos")
        
        # 1. Obter atividades através do model injetado
        atividades = []
        if hasattr(activity_model, 'obter_por_utilizador'):
            atividades = activity_model.obter_por_utilizador(utilizador_id)
        elif hasattr(activity_model, 'obter_atividades_por_utilizador'):
            atividades = activity_model.obter_atividades_por_utilizador(utilizador_id)
        
        if not atividades or len(atividades) == 0:
            st.info("Ainda não registou nenhuma atividade. Utilize a aba 'Inserir Atividade' para começar!")
            return

        df_treinos = pd.DataFrame(atividades)
        
        # Garantir ordenação por data mais recente
        if 'data_registo' in df_treinos.columns:
            df_treinos['data_registo'] = pd.to_datetime(df_treinos['data_registo'])
            df_treinos = df_treinos.sort_values('data_registo', ascending=False)

        # 2. Métrica resumo rápida
        total_treinos = len(df_treinos)
        total_distancia = df_treinos['distancia_km'].sum() if 'distancia_km' in df_treinos.columns else 0.0
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total de Registos", f"{total_treinos}")
        with col2:
            st.metric("Distância Acumulada", f"{total_distancia:.1f} km")

        st.divider()

        # 3. Lista de Treinos com Ações (Editar / Eliminar)
        st.markdown("##### Histórico de Registos")

        for idx, treino in df_treinos.iterrows():
            treino_id = treino.get('id', idx)
            data_str = treino['data_registo'].strftime('%d/%m/%Y %H:%M') if isinstance(treino['data_registo'], pd.Timestamp) else str(treino.get('data_registo', ''))
            modalidade = treino.get('modalidade', 'Atividade')
            distancia = treino.get('distancia_km', 0.0)
            duracao = treino.get('duracao_min', 0)

            titulo_expander = f"{data_str} — {modalidade} ({distancia} km | {duracao} min)"
            
            with st.expander(titulo_expander, expanded=False):
                with st.form(key=f"form_editar_treino_{treino_id}"):
                    st.markdown("**Editar Detalhes do Treino**")
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        nova_distancia = st.number_input(
                            "Distância (km)", 
                            min_value=0.0, 
                            max_value=500.0, 
                            value=float(distancia), 
                            step=0.1,
                            key=f"dist_{treino_id}"
                        )
                    with c2:
                        nova_duracao = st.number_input(
                            "Duração (minutos)", 
                            min_value=1, 
                            max_value=1440, 
                            value=int(duracao), 
                            step=1,
                            key=f"dur_{treino_id}"
                        )
                    
                    col_salvar, col_eliminar = st.columns([1, 1])
                    
                    with col_salvar:
                        btn_salvar = st.form_submit_button("Salvar Alterações", type="primary", width="stretch")
                    with col_eliminar:
                        btn_eliminar = st.form_submit_button("Eliminar Treino", width="stretch")

                    if btn_salvar:
                        if hasattr(activity_model, 'atualizar_atividade'):
                            sucesso = activity_model.atualizar_atividade(
                                atividade_id=treino_id,
                                novos_dados={
                                    'distancia_km': nova_distancia,
                                    'duracao_min': nova_duracao
                                }
                            )
                            if sucesso:
                                st.success("Treino atualizado com sucesso!")
                                st.rerun()
                            else:
                                st.error("Erro ao atualizar o treino.")
                        else:
                            st.warning("Função de atualização pendente no ActivityModel.")

                    if btn_eliminar:
                        if hasattr(activity_model, 'eliminar_atividade'):
                            sucesso = activity_model.eliminar_atividade(atividade_id=treino_id)
                            if sucesso:
                                st.warning("Treino eliminado.")
                                st.rerun()
                            else:
                                st.error("Erro ao eliminar o treino.")
                        else:
                            st.warning("Função de eliminação pendente no ActivityModel.")