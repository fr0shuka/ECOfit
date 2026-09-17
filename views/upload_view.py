import time
import streamlit as st
import pandas as pd
from controllers.file_controller import FileController
from models.activity_model import ActivityModel


class UploadView:
    @staticmethod
    def renderizar_zona_upload():
        st.markdown("### Sincronização de Ficheiro")
        st.caption("Importação de dados de atividades via ficheiro (CSV, GPX, FIT, TCX, JSON, etc.)")
        
        utilizador = st.session_state.get('utilizador_logado')
        if not utilizador:
            st.error("Utilizador não autenticado.")
            return

        utilizador_id = utilizador.get('utilizador_id') or utilizador.get('id')

        # Obter os tipos de atividade disponíveis na BD para o seletor manual (fallback)
        tipos_disponiveis = ActivityModel.obter_tipos_atividade()
        mapa_tipos = {t['nome']: t['tipo_atividade_id'] for t in tipos_disponiveis} if tipos_disponiveis else {"Corrida": 1}
        nomes_opcoes = list(mapa_tipos.keys())

        # --- SECÇÃO 1: UPLOAD ---
        with st.container(border=True):
            ficheiro = st.file_uploader(
                "Selecione o ficheiro de atividades", 
                type=["csv", "xlsx", "xls", "json", "gpx", "fit", "txt", "xml", "tcx"]
            )

            # Seletor opcional caso o ficheiro não traga a modalidade embutida
            idx_corrida = nomes_opcoes.index("Corrida") if "Corrida" in nomes_opcoes else 0
            tipo_selecionado_nome = st.selectbox(
                "Modalidade predefinida (utilizada se o ficheiro não especificar o desporto):",
                options=nomes_opcoes,
                index=idx_corrida,
                key="select_tipo_upload_ficheiro"
            )
            tipo_selecionado_id = mapa_tipos[tipo_selecionado_nome]

            if ficheiro is not None:
                if st.button("Processar e Sincronizar", type="primary", width="stretch"):
                    with st.spinner("A processar dados do ficheiro e a detetar desporto..."):
                        # O FileController deteta automaticamente do ficheiro, ou usa o tipo_selecionado_id como fallback
                        sucesso = FileController.processar_ficheiro(
                            ficheiro, 
                            utilizador_id, 
                            tipo_atividade_escolhido_id=tipo_selecionado_id
                        )

                    if sucesso:
                        st.toast(f"Ficheiro '{ficheiro.name}' processado e sincronizado com sucesso!")
                        time.sleep(0.8)
                        st.rerun()
                    else:
                        st.error("Falha ao processar o ficheiro. Verifique o formato dos dados.")

        st.markdown("---")

        # --- SECÇÃO 2: HISTÓRICO ---
        st.markdown("##### Histórico de Ficheiros Sincronizados")

        df_historico = FileController.obter_historico_atividades_ficheiro(utilizador_id)

        if df_historico is None or df_historico.empty:
            st.info("Não existem atividades registadas via ficheiro de momento.")
            return

        if 'distancia_km' not in df_historico.columns and 'km_corridos' in df_historico.columns:
            df_historico['distancia_km'] = df_historico['km_corridos']

        colunas_exibir = {
            'data_registo': 'Data da Atividade',
            'modalidade': 'Modalidade',
            'distancia_km': 'Distância (km)',
            'minutos_treino': 'Duração (min)',
            'pontos_ganhos': 'Pontos Obtidos'
        }

        cols_presentes = [c for c in colunas_exibir.keys() if c in df_historico.columns]
        df_exibicao = df_historico[cols_presentes].copy()
        
        if 'data_registo' in df_exibicao.columns:
            df_exibicao['data_registo'] = pd.to_datetime(df_exibicao['data_registo'], errors='coerce').dt.strftime('%Y-%m-%d %H:%M')

        df_exibicao.rename(columns=colunas_exibir, inplace=True)

        st.dataframe(
            df_exibicao,
            width="stretch",
            hide_index=True
        )