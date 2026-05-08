# config/settings.py
"""
Configuración centralizada del modelo QuantBet WC26
"""
import os
from typing import Dict, Any

class Config:
    """Clase de configuración con valores por defecto y overrides de ambiente"""
    
    # API Configuration
    API_BASE_URL: str = "https://v3.football.api-sports.io"
    API_ENDPOINT: str = "/fixtures"
    API_RATE_LIMIT_DELAY: int = 2  # Segundos entre requests
    
    # Decaimiento Exponencial
    DECAY_LAMBDA: float = 0.0015  # Ajustado para mejor peso temporal
    MIN_MATCHES_REQUIRED: int = 3  # Mínimo de partidos por equipo
    
    # Modelo Poisson
    MAX_GOALS_PROJECTION: int = 10  # Aumentado de 8 a 10
    CONFIDENCE_THRESHOLD: float = 0.65  # Mínimo para value bets
    
    # Torneos Prioritarios
    TORNEOS: list = [
        {"league": "1", "season": "2022"},   # Qatar 2022
        {"league": "1", "season": "2026"},   # WC 2026
        {"league": "34", "season": "2023"},  # Eliminatorias CONMEBOL
        {"league": "34", "season": "2024"},
        {"league": "34", "season": "2025"},
        {"league": "5", "season": "2024"},   # Nations League UEFA
        {"league": "5", "season": "2025"},
        {"league": "13", "season": "2024"},  # Nations League CONCACAF
        {"league": "13", "season": "2025"},
    ]
    
    # Paths
    DATA_DIR: str = "data"
    LOGS_DIR: str = "logs"
    HISTORICAL_DATA_FILE: str = "historico_selecciones.json"
    PREDICTIONS_FILE: str = "predicciones.json"
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @classmethod
    def get_api_key(cls) -> str:
        """Obtiene la API key desde variables de ambiente"""
        key = os.getenv("API_SPORTS_KEY")
        if not key:
            raise ValueError("API_SPORTS_KEY no configurada en secretos")
        return key
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Exporta configuración como diccionario"""
        return {
            "decay_lambda": cls.DECAY_LAMBDA,
            "min_matches": cls.MIN_MATCHES_REQUIRED,
            "max_goals": cls.MAX_GOALS_PROJECTION,
            "confidence_threshold": cls.CONFIDENCE_THRESHOLD,
            "torneos": cls.TORNEOS,
        }
