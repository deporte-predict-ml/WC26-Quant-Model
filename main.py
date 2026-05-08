# main.py
"""
Orquestador principal de QuantBet WC26
Ejecuta el flujo completo: fetch -> process -> predict -> export
"""
import os
import sys
import logging
from datetime import datetime, timezone

# Configurar paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config.settings import Config
from scripts.data_fetch import DataFetcher
from scripts.poisson_core import PoissonModel

# Setup logging
os.makedirs(Config.LOGS_DIR, exist_ok=True)
logging.basicConfig(
    level=Config.LOG_LEVEL,
    format=Config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(f"{Config.LOGS_DIR}/main_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def run_full_pipeline():
    """Ejecuta el pipeline completo"""
    logger.info("=" * 60)
    logger.info("🏆 QUANTBET WC26 - Pipeline Completo")
    logger.info("=" * 60)
    
    try:
        # Paso 1: Extraer datos
        logger.info("\n📥 FASE 1: Extracción de datos")
        api_key = Config.get_api_key()
        fetcher = DataFetcher(api_key)
        data = fetcher.fetch_all_data()
        fetcher.save_data(data)
        
        if not data["response"]:
            logger.error("❌ No hay datos para procesar")
            return False
        
        # Paso 2: Calcular estadísticas
        logger.info("\n📊 FASE 2: Cálculo de estadísticas")
        model = PoissonModel()
        model.load_data()
        model.calculate_weighted_stats(data)
        
        logger.info(f"✅ {len(model.team_stats)} equipos procesados")
        
        # Paso 3: Generar predicciones
        logger.info("\n🔮 FASE 3: Generando predicciones")
        
        # Aquí podrías cargar partidos próximos desde otra API
        upcoming_matches = [
            ("Mexico", "USA"),
            ("Argentina", "Brazil"),
            ("Spain", "Germany"),
            ("France", "England"),
            ("Italy", "Netherlands"),
        ]
        
        predictions = model.predict_multiple_matches(upcoming_matches)
        
        # Paso 4: Exportar resultados
        logger.info("\n💾 FASE 4: Exportando resultados")
        model.export_predictions(predictions)
        
        # Resumen
        value_bets = [p for p in predictions if p.value_bet]
        logger.info("\n" + "=" * 60)
        logger.info("📋 RESUMEN")
        logger.info("=" * 60)
        logger.info(f"Total predicciones: {len(predictions)}")
        logger.info(f"Value Bets encontradas: {len(value_bets)}")
        
        if value_bets:
            logger.info("\n🎯 VALUE BETS DESTACADAS:")
            for vb in value_bets[:3]:
                logger.info(f"   • {vb.home_team} vs {vb.away_team}")
                logger.info(f"     Confianza: {vb.confidence*100:.0f}%")
        
        logger.info("\n✅ Pipeline completado exitosamente")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en pipeline: {str(e)}", exc_info=True)
        return False


if __name__ == "__main__":
    success = run_full_pipeline()
    sys.exit(0 if success else 1)
