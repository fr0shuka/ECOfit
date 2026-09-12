import streamlit as st
from services.weather_service import WeatherService

try:
    from streamlit_js_eval import get_geolocation
    HAS_GEO = True
except ImportError:
    HAS_GEO = False


def renderizar_meteo_sidebar():
    """Renderiza o widget do tempo no fundo do menu lateral como um cartão KPI."""
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("##### 🌡️ Meteorologia")

    loc = None
    if HAS_GEO:
        try:
            loc = get_geolocation()
        except Exception:
            loc = None

    # Se obteve coordenadas, passa ao serviço; caso contrário, ativa o fallback (Espinho/Gaia)
    if loc and isinstance(loc, dict) and 'coords' in loc:
        meteo = WeatherService.obter_meteo(
            lat=loc['coords']['latitude'], 
            lon=loc['coords']['longitude']
        )
    else:
        meteo = WeatherService.obter_meteo()

    if meteo:
        st.sidebar.metric(
            label=meteo['local'], 
            value=f"{meteo['temp']:.1f} °C", 
            delta=f"{meteo['wind']:.1f} km/h vento",
            delta_color="normal",
            help=f"Condições meteorológicas obtidas em tempo real para {meteo['local']}."
        )
    else:
        st.sidebar.caption("Sem dados do tempo de momento.")