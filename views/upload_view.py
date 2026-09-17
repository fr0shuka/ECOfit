import time
import streamlit as st
import pandas as pd
from controllers.file_controller import FileController


class UploadView:
    @staticmethod
    def renderizar_zona_upload():
        st.markdown("### Sincronização de Ficheiro")
        st.caption("Importação de dados de atividades via ficheiro (CSV, GPX, FIT, etc.)")
        
        utilizador = st.session_state.get('utilizador_logado')
        if not utilizador:
            st.error("Utilizador não autenticado.")
            return

        utilizador_id = utilizador.get('utilizador_id') or utilizador.get('id')

        # --- SECÇÃO 1: UPLOAD ---
        with st.container(border=True):
            ficheiro = st.file_uploader(
                "Selecione o ficheiro de atividades", 
                type=["csv", "xlsx", "xls", "json", "gpx", "fit", "txt", "xml", "tcx"]
            )

            if ficheiro is not None:
                if st.button("Processar e Sincronizar", type="primary", width="stretch"):
                    with st.spinner("A processar dados do ficheiro..."):
                        sucesso = FileController.processar_ficheiro(ficheiro, utilizador_id)

                    if sucesso:
                        st.toast(f"Ficheiro '{ficheiro.name}' processado com sucesso!")
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

        # Normalização do nome da coluna de distância para 3NF
        if 'distancia_km' not in df_historico.columns and 'km_corridos' in df_historico.columns:
            df_historico['distancia_km'] = df_historico['km_corridos']

        colunas_exibir = {
            'data_registo': 'Data da Atividade',
            'distancia_km': 'Distância (km)',
            'minutos_treino': 'Duração (min)',
            'pontos_ganhos': 'Pontos Obtidos'
        }

        cols_presentes = [c for c in colunas_exibir.keys() if c in df_historico.columns]
        df_exibicao = df_historico[cols_presentes].copy()
        
        # Formatar datas se presentes
        if 'data_registo' in df_exibicao.columns:
            df_exibicao['data_registo'] = pd.to_datetime(df_exibicao['data_registo'], errors='coerce').dt.strftime('%Y-%m-%d %H:%M')

        df_exibicao.rename(columns=colunas_exibir, inplace=True)

        st.dataframe(
            df_exibicao,
            width="stretch",
            hide_index=True
        )