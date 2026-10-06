"""
ETL HISTÓRICO NBA - API PBPSTATS
Descarga datos de 3 temporadas desde https://api.pbpstats.com/get-totals/nba
Output: data/processed/nba_master_dataset.csv
"""
import time
import requests
import pandas as pd
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuración
ENDPOINT = "https://api.pbpstats.com/get-totals/nba"
SEASONS = ["2022-23", "2023-24", "2024-25", "2025-26"]
OUTPUT_DIR = Path("data/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def fetch_season_data(season):
    """
    Descarga datos de una temporada desde pbpstats API.
    
    Args:
        season: str, ej "2023-24"
    
    Returns:
        DataFrame con stats de jugadores o None si falla
    """
    params = {
        "Season": season,
        "SeasonType": "Regular Season",
        "Type": "Player"
    }
    
    try:
        logger.info(f"📥 Descargando {season}...")
        response = requests.get(ENDPOINT, params=params, timeout=150)
        response.raise_for_status()
        
        data = response.json()
        
        if "multi_row_table_data" not in data:
            logger.warning(f"⚠ {season}: No 'multi_row_table_data' en respuesta")
            return None
        
        df = pd.DataFrame(data["multi_row_table_data"])
        df["season"] = season
        
        logger.info(f"✓ {season}: {len(df)} jugadores descargados")
        return df
    
    except requests.exceptions.RequestException as e:
        logger.error(f"✗ Error en {season}: {e}")
        return None
    except Exception as e:
        logger.error(f"✗ Error parseando {season}: {e}")
        return None


def main():
    logger.info("="*70)
    logger.info("ETL HISTÓRICO NBA - PBPSTATS API")
    logger.info("="*70)
    
    all_seasons = []
    
    # Descargar cada temporada
    for season in SEASONS:
        df = fetch_season_data(season)
        if df is not None:
            all_seasons.append(df)
            logger.info("⏳ Esperando 10 segundos para no saturar el servidor...")
            time.sleep(10)
    
    if not all_seasons:
        logger.error("✗ No se descargó ningún dato. Abortando.")
        return
    
    # Consolidar
    logger.info("\n📦 Consolidando temporadas...")
    df_master = pd.concat(all_seasons, ignore_index=True)
    
    # Limpiar
    logger.info("🧹 Limpiando duplicados...")
    initial_rows = len(df_master)
    df_master = df_master.drop_duplicates()
    removed = initial_rows - len(df_master)
    logger.info(f"Removidos {removed} duplicados")
    
    # Guardar
    output_file = OUTPUT_DIR / "nba_master_dataset.csv"
    logger.info(f"\n💾 Guardando en {output_file}...")
    
    try:
        df_master.to_csv(output_file, index=False)
        
        logger.info("\n" + "="*70)
        logger.info("✅ ETL COMPLETADO")
        logger.info("="*70)
        logger.info(f"Registros: {len(df_master):,}")
        logger.info(f"Columnas: {len(df_master.columns)}")
        logger.info(f"Temporadas: {sorted(df_master['season'].unique().tolist())}")
        logger.info(f"Output: {output_file}")
        logger.info("="*70)
        
    except Exception as e:
        logger.error(f"✗ Error guardando: {e}")


if __name__ == "__main__":
    main()