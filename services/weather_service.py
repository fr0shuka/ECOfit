import requests


class WeatherService:
    ESPINHO = {"lat": 41.0072, "lon": -8.6410, "nome": "Espinho"}
    GAIA = {"lat": 41.1336, "lon": -8.6174, "nome": "Vila Nova de Gaia"}

    @staticmethod
    def obter_meteo(lat: float = None, lon: float = None) -> dict | None:
        target_lat = lat if lat is not None else WeatherService.ESPINHO["lat"]
        target_lon = lon if lon is not None else WeatherService.ESPINHO["lon"]

        # 1. Tentativa principal
        try:
            # Formato JSON via wttr.in
            url = f"https://wttr.in/{target_lat},{target_lon}?format=j1"
            res = requests.get(url, timeout=4).json()

            current = res["current_condition"][0]
            area = res["nearest_area"][0]

            # Tenta extrair o nome da localidade detetada
            local_nome = area["areaName"][0]["value"] if area.get("areaName") else "Localização Atual"

            return {
                "temp": float(current["temp_C"]),
                "wind": float(current["windspeedKmph"]),
                "local": local_nome
            }
        except Exception as e:
            print(f"⚠️ Erro no pedido principal wttr.in: {e}")

        # 2. Fallback (VN Gaia)
        try:
            url_gaia = f"https://wttr.in/{WeatherService.GAIA['lat']},{WeatherService.GAIA['lon']}?format=j1"
            res_gaia = requests.get(url_gaia, timeout=4).json()
            current_gaia = res_gaia["current_condition"][0]

            return {
                "temp": float(current_gaia["temp_C"]),
                "wind": float(current_gaia["windspeedKmph"]),
                "local": WeatherService.GAIA["nome"]
            }
        except Exception as e:
            print(f"❌ Erro no fallback wttr.in: {e}")

        return None