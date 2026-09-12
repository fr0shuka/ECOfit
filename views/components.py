import streamlit as st
from services.weather_service import WeatherService

try:
    from streamlit_js_eval import get_geolocation
    HAS_GEO = True
except ImportError:
    HAS_GEO = False


def renderizar_meteo_sidebar():
    """Card do tempo no menu lateral dentro de um cartão com borda."""
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("##### 🌡️ Meteorologia")

    loc = None
    if HAS_GEO:
        try:
            loc = get_geolocation()
        except Exception:
            loc = None

    if loc and isinstance(loc, dict) and 'coords' in loc:
        meteo = WeatherService.obter_meteo(
            lat=loc['coords']['latitude'], 
            lon=loc['coords']['longitude']
        )
    else:
        meteo = WeatherService.obter_meteo()

    if meteo:
        st.sidebar.markdown(
            """
            <style>
            div[data-testid="stSidebar"] div[data-testid="stMetric"] {
                border-left: 4px solid #FF4B4B !important;
                padding-left: 12px !important;
                background-color: rgba(255, 255, 255, 0.03);
                border-radius: 4px;
                padding-top: 8px;
                padding-bottom: 8px;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        with st.sidebar.container(border=True):
            st.metric(
                label=meteo['local'].upper(), 
                value=f"{meteo['temp']:.1f} °C", 
                delta=f"{meteo['wind']:.1f} km/h vento",
                delta_color="normal",
                help=f"Condições meteorológicas obtidas em tempo real para {meteo['local']}."
            )
    else:
        st.sidebar.caption("Sem dados do tempo de momento.")