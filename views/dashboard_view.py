import streamlit as st
from controllers.activity_controller import ActivityController

class DashboardView:
    @staticmethod
    def renderizar_formulario():
        """Desenha a interface de registo diário do atleta."""
        st.markdown("### 📝 Registo de Atividade Diária")
        st.caption("Insira os seus dados de hoje para atualizar os rankings do EcoFit.")
        
        # Criação do formulário isolado do Streamlit
        with st.form("form_atividade"):
            col1, col2 = st.columns(2)
            
            with col1:
                km = st.number_input("Quilómetros Corridos (Km)", min_value=0.0, step=0.1, value=0.0)
                minutos = st.number_input("Tempo de Treino (Minutos)", min_value=0, step=1, value=0)
            
            with col2:
                agua = st.number_input("Copos de Água (Unidades)", min_value=0, step=1, value=0)
                fruta = st.number_input("Peças de Fruta (Unidades)", min_value=0, step=1, value=0)
            
            st.markdown("---")
            st.markdown("##### 🌤️ Telemetria Ambiental (Simulação de API)")
            col3, col4 = st.columns(2)
            with col3:
                temp = st.number_input("Temperatura Atual (°C)", min_value=-10.0, max_value=50.0, step=0.5, value=22.0)
            with col4:
                clima = st.selectbox("Condição do Tempo", ["Ensolarado", "Nublado", "Chuva", "Vento"])
            
            submetido = st.form_submit_button("Submeter Atividade", use_container_width=True)
            
          