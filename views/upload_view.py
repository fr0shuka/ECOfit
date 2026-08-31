import time
import streamlit as st
import pandas as pd
from controllers.file_controller import FileController


class UploadView:
    @staticmethod
    def renderizar_zona_upload():
        st.title("Sincronização de Ficheiro")
        st.caption("Importação de dados de atividades via CSV ou Excel.")
        
        utilizador = st.session_state.get('utilizador_logado')
        if not utilizador:
            return

        utilizador_id = utilizador['utilizador_id']

        # --- SECÇÃO 1: UPLOAD ---
        with st.container(border=True):
            ficheiro = st.file_uploader(
                "Ficheiro de atividades (CSV ou XLSX)", 
                type=["csv", "xlsx"]
            )

            if ficheiro is not None:
                if st.button("Processar e Sincronizar", type="primary", use_container_width=True):
                    with st.spinner("A processar dados..."):
                        sucesso = FileController.processar_ficheiro(ficheiro, utilizador_id)

                    if sucesso:
                        st.toast(f"Ficheiro '{ficheiro.name}' processado com sucesso.", icon=None)
                        time.sleep(0.8)
                        st.rerun()
                    else:
                        st.error("Falha ao processar o ficheiro.")

        st.markdown("---")

        # --- SECÇÃO 2: HISTÓRICO ---
        st.markdown("##### Histórico de Ficheiros Sincronizados")

        df_historico = FileController.obter_historico_atividades_ficheiro(utilizador_id)

        if df_historico.empty:
            st.info("Não existem atividades registadas via ficheiro.")
            return

        colunas_exibir = {
            'data_registo': 'Data da Atividade',
            'km_corridos': 'Distância (km)',
            'minutos_treino': 'Duração (min)',
            'pontos_ganhos': 'Pontos Obtidos'
        }

        cols_presentes = [c for c in colunas_exibir.keys() if c in df_historico.columns]
        df_exibicao = df_historico[cols_presentes].copy()
        df_exibicao.rename(columns=colunas_exibir, inplace=True)

        st.dataframe(
            df_exibicao,
            use_container_width=True,
            hide_index=True
        )