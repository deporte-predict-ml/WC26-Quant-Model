import json
import os
import numpy as np
from scipy.stats import poisson
from datetime import datetime, timezone

def cargar_datos():
    ruta = "data/historico_selecciones.json"
    if not os.path.exists(ruta):
        print("No hay datos todavía. Toca correr el data_fetch primero.")
        return None
    with open(ruta, "r") as f:
        return json.load(f)

def calcular_promedios_con_peso(data):
    stats_equipos = {}
    # Usamos UTC para no tener broncas al restar fechas en la nube
    hoy = datetime.now(timezone.utc) 
    
    partidos = data.get("response", [])
    for p in partidos:
        home = p["teams"]["home"]["name"]
        away = p["teams"]["away"]["name"]
        goles_h = p["goals"]["home"]
        goles_a = p["goals"]["away"]
        
        fecha_str = p["fixture"]["date"] 
        
        # Filtramos partidos no jugados o pospuestos para no meter basura al modelo
        if goles_h is None or goles_a is None: 
            continue

        # Convertimos la fecha al formato que entiende Python
        try:
            fecha_partido = datetime.fromisoformat(fecha_str.replace('Z', '+00:00'))
        except ValueError:
            continue
            
        dias_pasados = (hoy - fecha_partido).days
        
        # El castigo al tiempo (Decaimiento exponencial)
        peso = np.exp(-0.001 * dias_pasados)

        for equipo in [home, away]:
            if equipo not in stats_equipos:
                stats_equipos[equipo] = {"anotados_ponderados": 0, "partidos_ponderados": 0}
        
        # Sumamos los goles y partidos multiplicados por su peso temporal
        stats_equipos[home]["anotados_ponderados"] += goles_h * peso
        stats_equipos[home]["partidos_ponderados"] += peso
        
        stats_equipos[away]["anotados_ponderados"] += goles_a * peso
        stats_equipos[away]["partidos_ponderados"] += peso

    return stats_equipos

def poisson_model(home_team, away_team, stats):
    if home_team not in stats or away_team not in stats:
        return {"Error": f"Faltan datos en el historial para {home_team} o {away_team}"}
    
    # Cálculo de Expected Goals (Lambda) ajustado por tiempo
    exp_home = stats[home_team]["anotados_ponderados"] / stats[home_team]["partidos_ponderados"]
    exp_away = stats[away_team]["anotados_ponderados"] / stats[away_team]["partidos_ponderados"]
    
    max_goles = 8
    prob_h = [poisson.pmf(i, exp_home) for i in range(max_goles)]
    prob_a = [poisson.pmf(i, exp_away) for i in range(max_goles)]
    
    matriz = np.outer(prob_h, prob_a)
    
    return {
        "Local": round(np.sum(np.tril(matriz, -1)) * 100, 2),
        "Empate": round(np.sum(np.diag(matriz)) * 100, 2),
        "Visitante": round(np.sum(np.triu(matriz, 1)) * 100, 2),
        "xG_Local": round(exp_home, 2),
        "xG_Visitante": round(exp_away, 2)
    }

if __name__ == "__main__":
    print("--- Iniciando motor de QuantBet para Selecciones ---")
    data = cargar_datos()
    if data:
        stats = calcular_promedios_con_peso(data)
        
        # Prueba directa para ver si el script arranca al 100
        res = poisson_model("Mexico", "USA", stats)
        print(f"Proyección de prueba: {res}")
