import os
import json
import requests
import time

# Jalamos el token directo desde los secretos de GitHub
API_KEY = os.getenv("API_SPORTS_KEY")

def fetch_all_data():
    # Ligas clave: 1 (Mundial), 5 (Nations League UEFA), 34 (Eliminatorias CONMEBOL)
    # Metemos años recientes para que el modelo tenga carnita fresca
    torneos = [
        {"league": "1", "season": "2022"},  # Qatar 2022
        {"league": "34", "season": "2023"}, # Eliminatorias CONMEBOL
        {"league": "34", "season": "2024"}, 
        {"league": "5", "season": "2024"},  # Nations League UEFA
        {"league": "13", "season": "2024"}  # Nations League CONCACAF
    ]
    
    url = "https://v3.football.api-sports.io/fixtures"
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "v3.football.api-sports.io"
    }
    
    todos_los_partidos = []

    for torneo in torneos:
        print(f"Jalando datos de liga {torneo['league']} temporada {torneo['season']}...")
        try:
            response = requests.get(url, headers=headers, params=torneo)
            response.raise_for_status() 
            data = response.json()
            
            # Si la API nos responde chido, guardamos los partidos
            if "response" in data:
                todos_los_partidos.extend(data["response"])
                
            # Aguantamos un segundo para no saturar la API y que no nos bloqueen
            time.sleep(1)
        except Exception as e:
            print(f"Hubo un pedo al conectar con la liga {torneo['league']}: {e}")

    # Nos aseguramos de que la carpeta exista
    os.makedirs("data", exist_ok=True)
    
    # Metemos todo el desmadre en la misma estructura para que el otro script no se rompa
    json_final = {"response": todos_los_partidos}
    
    # Le cambiamos el nombre para que tenga más sentido
    with open("data/historico_selecciones.json", "w") as f:
        json.dump(json_final, f, indent=4)
        
    print(f"¡Al tiro! Se guardaron {len(todos_los_partidos)} partidos en data/historico_selecciones.json")

if __name__ == "__main__":
    if not API_KEY:
        print("¡Ojo! No se encontró la API Key. Revisa los Secrets en GitHub.")
    else:
        fetch_all_data()
