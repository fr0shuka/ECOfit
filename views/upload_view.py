import streamlit as st
from controllers.file_controller import FileController

class UploadView:
    @staticmethod
    def renderizar_zona_upload():
        """Desenha o ecrã de importação de dados externos (Strava, Garmin, Fitbit)."""
        st.markdown("### 📥 Sincronização Externa (Módulos Wearables)")
        st.caption("Carrega as tuas atividades diretamente a partir dos ficheiros exportados pelas tuas plataformas de treino.")
        
        # Componente oficial do Streamlit para captura de ficheiros
        ficheiro = st.file_uploader(
            "Seleciona o ficheiro de treino", 
            type=["csv", "gpx", "tcx"],
            help="Aceita CSV para relatórios mensais, ou GPX/TCX para treinos individuais."
        )
        
        if ficheiro is not None:
            st.info(f"📋 Ficheiro detetado: **{ficheiro.name}** ({round(ficheiro.size/1024, 2)} KB)")
            
            if st.button("Processar e Sincronizar Atividade", use_container_width=True, key="btn_upload_fit"):
                with st.spinner("A analisar métricas do ficheiro..."):
                    sucesso = FileController.processar_ficheiro_treino(ficheiro)
                    if sucesso:
                        st.success("🎯 Sincronização concluída! Os teus pontos foram atualizados no ranking.")