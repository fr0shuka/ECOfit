import streamlit as st
from services.weather_service import WeatherService

try:
    from streamlit_js_eval import get_geolocation
    HAS_GEO = True
except ImportError:
    HAS_GEO = False


def renderizar_meteo_sidebar():
    """Renderiza o widget do tempo no fundo do menu lateral."""
    
    st.sidebar.markdown("### 🌡️ Meteorologia")

    loc = None
    if HAS_GEO:
        try:
            loc = get_geolocation()
        except Exception:
            loc = None

    # Se conseguiu coordenadas, passa ao serviço; se não, passa None (ativa o fallback de Espinho/Gaia)
    if loc and isinstance(loc, dict) and 'coords' in loc:
        meteo = WeatherService.obter_meteo(
            lat=loc['coords']['latitude'], 
            lon=loc['coords']['longitude']
        )
    else:
        meteo = WeatherService.obter_meteo()

    if meteo:
        st.sidebar.metric(
            label=f"({meteo['local']})", 
            value=f"{meteo['temp']} °C", 
            delta=f"Vento: {meteo['wind']} km/h"
        )
    else:
        st.sidebar.caption("Sem dados do tempo de momento.")