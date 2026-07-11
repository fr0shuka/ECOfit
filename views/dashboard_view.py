import streamlit as st

class DashboardView:
    @staticmethod
    def renderizar_formulario():
        """Ecrã provisório do atleta após o login."""
        st.markdown("### 💪 Área do Atleta - EcoFit")
        st.success("Sessão iniciada com sucesso! O teu acesso está ativo e validado.")
        st.write("Este é o teu painel principal. O ambiente de login e registo está operacional.")