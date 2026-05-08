# scripts/data_fetch.py
"""
Módulo de extracción de datos deportivos desde API
Maneja rate limiting, retries y validación de datos
"""
import os
import json
import time
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import requests
from requests.exceptions import RequestException, Timeout

# Configuración
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import Config

# Setup logging
logging.basicConfig(
    level=Config.LOG_LEVEL,
    format=Config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(f"{Config.LOGS_DIR}/data_fetch.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DataFetcher:
    """Clase para extracción robusta de datos deportivos"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = Config.API_BASE_URL
        self.endpoint = Config.API_ENDPOINT
        self.session = requests.Session()
        self.session.headers.update({
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": "v3.football.api-sports.io"
        })
        self.all_matches: List[Dict] = []
    
    def fetch_tournament_data(self, league: str, season: str) -> List[Dict]:
        """
        Extrae datos de un torneo específico con retry logic
        
        Args:
            league: ID de la liga
            season: Temporada
            
        Returns:
            Lista de partidos
        """
        url = f"{self.base_url}{self.endpoint}"
        params = {"league": league, "season": season}
        
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                logger.info(f"Extrayendo liga {league} temporada {season} (intento {retry_count + 1})")
                
                response = self.session.get(url, headers=self.session.headers, params=params, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                
                if "response" not in data:
                    logger.warning(f"No hay campo 'response' en liga {league}")
                    return []
                
                matches = data["response"]
                logger.info(f"✅ {len(matches)} partidos extraídos de liga {league}")
                
                # Rate limiting
                time.sleep(Config.API_RATE_LIMIT_DELAY)
                
                return matches
                
            except Timeout:
                retry_count += 1
                logger.warning(f"Timeout en liga {league}. Reintentando...")
                time.sleep(5 * retry_count)
                
            except RequestException as e:
                retry_count += 1
                logger.error(f"Error en liga {league}: {str(e)}")
                if response.status_code == 429:
                    logger.warning("Rate limit excedido. Esperando 60 segundos...")
                    time.sleep(60)
                else:
                    time.sleep(2 * retry_count)
                    
        logger.error(f"❌ Fallo después de {max_retries} intentos para liga {league}")
        return []
    
    def validate_match(self, match: Dict) -> bool:
        """
        Valida que un partido tenga datos completos
        
        Args:
            match: Diccionario de partido
            
        Returns:
            True si es válido
        """
        required_fields = [
            "fixture", "teams", "goals", "league", "season"
        ]
        
        for field in required_fields:
            if field not in match:
                return False
        
        # Validar que haya goles (partido jugado)
        if match["goals"]["home"] is None or match["goals"]["away"] is None:
            return False
        
        # Validar fecha
        if "date" not in match["fixture"]:
            return False
            
        return True
    
    def fetch_all_data(self) -> Dict[str, Any]:
        """
        Extrae todos los torneos configurados
        
        Returns:
            Diccionario con todos los partidos
        """
        self.all_matches = []
        successful_tournaments = 0
        
        for torneo in Config.TORNEOS:
            matches = self.fetch_tournament_data(
                torneo["league"], 
                torneo["season"]
            )
            
            # Validar y filtrar
            valid_matches = [m for m in matches if self.validate_match(m)]
            invalid_count = len(matches) - len(valid_matches)
            
            if invalid_count > 0:
                logger.warning(f"{invalid_count} partidos inválidos filtrados")
            
            self.all_matches.extend(valid_matches)
            
            if len(valid_matches) > 0:
                successful_tournaments += 1
        
        logger.info(f"✅ {successful_tournaments}/{len(Config.TORNEOS)} torneos exitosos")
        logger.info(f"📊 Total: {len(self.all_matches)} partidos válidos")
        
        return {"response": self.all_matches, "metadata": {
            "extraction_date": datetime.utcnow().isoformat(),
            "total_matches": len(self.all_matches),
            "tournaments_processed": successful_tournaments
        }}
    
    def save_data(self, data: Dict[str, Any]) -> str:
        """
        Guarda datos en archivo JSON
        
        Args:
            data: Datos a guardar
            
        Returns:
            Ruta del archivo guardado
        """
        os.makedirs(Config.DATA_DIR, exist_ok=True)
        filepath = os.path.join(Config.DATA_DIR, Config.HISTORICAL_DATA_FILE)
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Datos guardados en {filepath}")
        return filepath


def main():
    """Función principal para ejecución standalone"""
    logger.info("🚀 Iniciando DataFetcher de QuantBet WC26")
    
    try:
        api_key = Config.get_api_key()
    except ValueError as e:
        logger.error(str(e))
        return
    
    fetcher = DataFetcher(api_key)
    data = fetcher.fetch_all_data()
    
    if data["response"]:
        fetcher.save_data(data)
        logger.info("✅ Proceso completado exitosamente")
    else:
        logger.error("❌ No se extrajeron datos válidos")


if __name__ == "__main__":
    main()
