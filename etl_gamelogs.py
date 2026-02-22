"""
ETL GAME LOGS NBA - LEAGUE LEVEL (O(1) Efficiency)
Descarga stats de TODOS los partidos por temporada en 3 llamadas (no 14k).
Output: data/processed/nba_gamelogs_dataset.csv
"""

import time
import logging
from pathlib import Path
import pandas as pd
from nba_api.stats.endpoints import leaguegamelog

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SEASONS = ["2022-23", "2023-24", "2024-25", "2025-26"]
OUTPUT_DIR = Path("data/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def fetch_league_gamelogs(season):
    """
    Descarga TODOS los game logs de la liga en una temporada.
    
    Args:
        season: str, ej "2023-24"
    
    Returns:
        DataFrame con todos los partidos de todos los jugadores o None
    """
    try:
        logger.info(f"📥 Descargando {season}...")
        
        logs = leaguegamelog.LeagueGameLog(
            season=season,
            season_type_all_star='Regular Season',
            player_or_team_abbreviation='P' 
        ).get_data_frames()[0]
        
        if logs is not None and not logs.empty:
            logs['season'] = season
            logger.info(f"✓ {season}: {len(logs):,} partidos")
            return logs
        
        logger.warning(f"⚠ {season}: DataFrame vacío")
        return None
    
    except Exception as e:
        logger.error(f"✗ Error en {season}: {e}")
        return None

def main():
    logger.info("="*70)
    logger.info("ETL GAME LOGS - LEAGUE LEVEL (3 CALLS)")
    logger.info("="*70 + "\n")
    
    all_gamelogs = []
    
    for i, season in enumerate(SEASONS):
        logs = fetch_league_gamelogs(season)
        if logs is not None:
            all_gamelogs.append(logs)
        
        # Rate limiting entre llamadas
        if i < len(SEASONS) - 1:
            logger.info("⏳ Esperando 2 segundos...\n")
            time.sleep(2)
    
    if not all_gamelogs:
        logger.error("✗ No se descargaron game logs. Abortando.")
        return
    
    # Consolidar
    logger.info("📦 Consolidando temporadas...")
    df_gamelogs = pd.concat(all_gamelogs, ignore_index=True)
    
    # Limpiar duplicados
    logger.info("🧹 Limpiando duplicados...")
    df_gamelogs = df_gamelogs.drop_duplicates()
    
    # Guardar
    output_file = OUTPUT_DIR / "nba_gamelogs_dataset.csv"
    logger.info(f"💾 Guardando en {output_file}...\n")
    
    try:
        df_gamelogs.to_csv(output_file, index=False)
        
        logger.info("="*70)
        logger.info("✅ ETL GAME LOGS COMPLETADO")
        logger.info("="*70)
        logger.info(f"Registros totales: {len(df_gamelogs):,} partidos")
        logger.info(f"Columnas: {len(df_gamelogs.columns)}")
        logger.info(f"Temporadas: {sorted(df_gamelogs['season'].unique().tolist())}")
        logger.info(f"Output: {output_file}")
        logger.info("="*70)
        
    except Exception as e:
        logger.error(f"✗ Error guardando: {e}")

if __name__ == "__main__":
    main()