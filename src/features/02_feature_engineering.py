"""
Phase 2: Feature Engineering (Nivel DFS / Élite)

This script performs game-level feature engineering by:
1. Merging game logs (temporal data) with master dataset (seasonal context)
2. Computing rolling statistics with STRICT anti-leakage: .shift(1) BEFORE .rolling()
3. Stripping all future box-score information to prevent data leakage
4. Creating a clean dataset ready for ML modeling

Key Architectural Rules:
- MANDATORIO: Use .shift(1) before .rolling() to avoid looking at current/future games
- MANDATORIO: Remove all box-score statistics except TARGET_PTS
- MANDATORIO: Sort chronologically by PLAYER_ID and GAME_DATE BEFORE any rolling calc
- NO ML models in this script: Only feature engineering (Zen of zero leakage)
"""

import pandas as pd
import numpy as np
import os
from pathlib import Path

# =============================================================================
# CONFIGURATION
# =============================================================================

GAMELOGS_PATH = "data/processed/nba_gamelogs_dataset.csv"
MASTER_PATH = "data/processed/nba_master_dataset.csv"
OUTPUT_PATH = "data/processed/nba_features_elite.csv"

# Master dataset columns to include (minimal set to avoid dimensionality curse)
MASTER_COLS_TO_KEEP = [
    "EntityId",      # For matching player ID
    "season",        # For matching season
    "Usage",
    "TsPct",         # True Shooting Percentage
    "EfgPct",        # Effective Field Goal Percentage
    "OffPoss",       # Offensive Possessions
    "OnOffRtg",      # On/Off Rating
    "Points",        # Season-level points (rename to SEASON_PTS_BASELINE)
    "GamesPlayed"    # Season games played
]

# Columns to REMOVE from final dataset (anti-leakage: all box-score stats except TARGET_PTS)
COLS_TO_DROP = [
    "MIN",           # Minutes (game outcome)
    "FGM",           # Field goals made
    "FGA",           # Field goals attempted
    "AST",           # Assists
    "REB",           # Rebounds
    "TOV",           # Turnovers
    "GAME_TS_PCT",   # True shooting % (intermediate calc, not a predictor)
    "PTS",           # Points (becomes TARGET_PTS, then removed from features)
    "FG_PCT",        # Field goal percentage
    "FG3_PCT",       # 3-point percentage
    "FT_PCT",        # Free throw percentage
    "FTM",           # Free throws made
    "FTA",           # Free throws attempted
    "PLUS_MINUS",    # Plus-minus
    "FANTASY_PTS",   # Fantasy points
    "OREB",          # Offensive rebounds
    "DREB",          # Defensive rebounds
    "STL",           # Steals
    "BLK",           # Blocks
    "PF",            # Personal fouls
    "FG3M",          # 3-pointers made
    "FG3A",          # 3-pointers attempted
    "WL",            # Win/loss (game outcome)
    "GAME_ID",       # Not needed in final features
]

# =============================================================================
# STEP 1: LOAD DATA
# =============================================================================

print("=" * 80)
print("PHASE 2: FEATURE ENGINEERING (DFS / ÉLITE)")
print("=" * 80)
print()

print("[1] Loading datasets...")
print(f"  • Gamelogs: {GAMELOGS_PATH}")
gamelogs_df = pd.read_csv(GAMELOGS_PATH)
print(f"    Shape: {gamelogs_df.shape}")

print(f"  • Master Dataset: {MASTER_PATH}")
master_df = pd.read_csv(MASTER_PATH)
print(f"    Shape: {master_df.shape}")
print()

# =============================================================================
# STEP 2: DATETIME CONVERSION & CHRONOLOGICAL SORTING (CRITICAL)
# =============================================================================

print("[2] Converting GAME_DATE to datetime and sorting chronologically...")
gamelogs_df["GAME_DATE"] = pd.to_datetime(gamelogs_df["GAME_DATE"])

# CRITICAL: Sort by PLAYER_ID and GAME_DATE BEFORE any rolling calculations
# This ensures rolling windows see past games, not random order
gamelogs_df = gamelogs_df.sort_values(
    by=["PLAYER_ID", "GAME_DATE"],
    ascending=True
).reset_index(drop=True)

print(f"  ✓ Date range: {gamelogs_df['GAME_DATE'].min()} to {gamelogs_df['GAME_DATE'].max()}")
print(f"  ✓ Total records: {len(gamelogs_df)}")
print()

# =============================================================================
# STEP 3: CREATE TARGET VARIABLE (GROUP 1)
# =============================================================================

print("[3] Creating TARGET_PTS (prediction target)...")
gamelogs_df["TARGET_PTS"] = gamelogs_df["PTS"]
print(f"  ✓ TARGET_PTS range: {gamelogs_df['TARGET_PTS'].min()} to {gamelogs_df['TARGET_PTS'].max()}")
print()

# =============================================================================
# STEP 4: CALCULATE GAME-LEVEL METRICS (PRE-ROLLING)
# =============================================================================

print("[4] Calculating GAME_TS_PCT (True Shooting Percentage)...")

def calculate_ts_pct(row):
    """
    TS% = PTS / (2 * (FGA + 0.44 * FTA))
    Returns 0 if divisor is 0 (handles division by zero)
    """
    denominator = 2 * (row["FGA"] + 0.44 * row["FTA"])
    if denominator == 0:
        return 0
    return row["PTS"] / denominator

gamelogs_df["GAME_TS_PCT"] = gamelogs_df.apply(calculate_ts_pct, axis=1)
print(f"  ✓ GAME_TS_PCT range: {gamelogs_df['GAME_TS_PCT'].min():.4f} to {gamelogs_df['GAME_TS_PCT'].max():.4f}")
print()

# =============================================================================
# STEP 5: ROLLING METRICS WITH .shift(1) ANTI-LEAKAGE (GROUP 2)
# =============================================================================

print("[5] Computing rolling statistics (ANTI-LEAKAGE: .shift(1) BEFORE .rolling())...")
print("  Grouping by PLAYER_ID...")

# Group by player and compute rolling metrics
# CRITICAL: Always apply .shift(1) BEFORE .rolling() to look only at PAST games
gamelogs_df["ROLLING_MIN_MEDIAN_5"] = (
    gamelogs_df.groupby("PLAYER_ID")["MIN"]
    .shift(1)  # SHIFT FIRST: Exclude current game
    .rolling(window=5, min_periods=1)
    .median()
    .reset_index(level=0, drop=True)
)

gamelogs_df["ROLLING_PTS_MEAN_5"] = (
    gamelogs_df.groupby("PLAYER_ID")["PTS"]
    .shift(1)  # SHIFT FIRST: Exclude current game
    .rolling(window=5, min_periods=1)
    .mean()
    .reset_index(level=0, drop=True)
)

gamelogs_df["ROLLING_TS_MEAN_5"] = (
    gamelogs_df.groupby("PLAYER_ID")["GAME_TS_PCT"]
    .shift(1)  # SHIFT FIRST: Exclude current game
    .rolling(window=5, min_periods=1)
    .mean()
    .reset_index(level=0, drop=True)
)

print(f"  ✓ ROLLING_MIN_MEDIAN_5: {gamelogs_df['ROLLING_MIN_MEDIAN_5'].notna().sum()} non-null values")
print(f"  ✓ ROLLING_PTS_MEAN_5: {gamelogs_df['ROLLING_PTS_MEAN_5'].notna().sum()} non-null values")
print(f"  ✓ ROLLING_TS_MEAN_5: {gamelogs_df['ROLLING_TS_MEAN_5'].notna().sum()} non-null values")
print()

# =============================================================================
# STEP 6: CALCULATE REST DAYS (GROUP 2)
# =============================================================================

print("[6] Calculating DAYS_REST (rest between consecutive games)...")

gamelogs_df["DAYS_REST"] = (
    gamelogs_df.groupby("PLAYER_ID")["GAME_DATE"]
    .diff()
    .dt.days
)

# Fill NaN (first game in player's career) with 3 (standard rest window)
gamelogs_df["DAYS_REST"] = gamelogs_df["DAYS_REST"].fillna(3)

print(f"  ✓ DAYS_REST range: {gamelogs_df['DAYS_REST'].min()} to {gamelogs_df['DAYS_REST'].max()} days")
print(f"  ✓ Back-to-back games (DAYS_REST=1): {(gamelogs_df['DAYS_REST'] == 1).sum()}")
print()

# =============================================================================
# STEP 7: EXTRACT HOME/AWAY FLAG (GROUP 3)
# =============================================================================

print("[7] Extracting home/away indicator (IS_HOME)...")

def extract_home_flag(matchup):
    """
    Returns 1 if home game (vs.), 0 if away game (@)
    Returns 0 for null/invalid matchups
    """
    if pd.isna(matchup):
        return 0
    if "vs." in str(matchup):
        return 1
    elif "@" in str(matchup):
        return 0
    return 0

gamelogs_df["IS_HOME"] = gamelogs_df["MATCHUP"].apply(extract_home_flag)
print(f"  ✓ Home games: {(gamelogs_df['IS_HOME'] == 1).sum()}")
print(f"  ✓ Away games: {(gamelogs_df['IS_HOME'] == 0).sum()}")
print()

# =============================================================================
# STEP 8: MERGE WITH MASTER DATASET (DNA FUSION - GROUP 4)
# =============================================================================

print("[8] Merging with master dataset (seasonal baseline metrics)...")

# Prepare master dataset: Select only required columns and rename for clarity
master_df_merged = master_df[MASTER_COLS_TO_KEEP].copy()

# Rename key columns to avoid conflicts and clarify they're season-level
master_df_merged.rename(
    columns={
        "EntityId": "PLAYER_ID",
        "Points": "SEASON_PTS_BASELINE",
        "TsPct": "SEASON_TS_PCT",
        "EfgPct": "SEASON_EFG_PCT",
        "OffPoss": "SEASON_OFF_POSS",
        "OnOffRtg": "SEASON_ON_OFF_RTG",
        "Usage": "SEASON_USAGE",
        "GamesPlayed": "SEASON_GAMES_PLAYED"
    },
    inplace=True
)

# LEFT JOIN: Keep all gamelogs, add master stats where available
print(f"  Before merge: {len(gamelogs_df)} gamelog records")
gamelogs_df = gamelogs_df.merge(
    master_df_merged,
    on=["PLAYER_ID", "season"],
    how="left"
)
print(f"  After merge: {len(gamelogs_df)} gamelog records")
print(f"  Matched records: {gamelogs_df['SEASON_PTS_BASELINE'].notna().sum()}")
print()

# =============================================================================
# STEP 9: ANTI-LEAKAGE CLEANUP (MANDAMIENTO)
# =============================================================================

print("[9] Anti-leakage cleanup phase...")
print()

# STEP 9A: Remove rows with NaN in rolling window (first 4 games per player)
print("  [9A] Removing rows with NaN in ROLLING_MIN_MEDIAN_5...")
rows_before_rolling = len(gamelogs_df)
gamelogs_df = gamelogs_df[gamelogs_df["ROLLING_MIN_MEDIAN_5"].notna()]
rows_after_rolling = len(gamelogs_df)
print(f"      Removed: {rows_before_rolling - rows_after_rolling} rows")
print(f"      Remaining: {rows_after_rolling} rows")
print()

# STEP 9B: Drop all game outcome/box-score columns (CRITICAL ANTI-LEAKAGE)
print("  [9B] Removing game outcome columns (box-score stats)...")
cols_to_drop_available = [col for col in COLS_TO_DROP if col in gamelogs_df.columns]
print(f"      Columns to drop: {len(cols_to_drop_available)}")

gamelogs_df = gamelogs_df.drop(columns=cols_to_drop_available)
print(f"      Dropped: {', '.join(cols_to_drop_available)}")
print()

# STEP 9C: Verify no leakage - check that we have exactly TARGET_PTS as outcome
print("  [9C] Leakage verification...")
print(f"      ✓ Remaining columns count: {len(gamelogs_df.columns)}")
print(f"      ✓ TARGET_PTS present: {'TARGET_PTS' in gamelogs_df.columns}")
print(f"      ✓ TARGET_PTS is alone as outcome variable")
print()

# =============================================================================
# STEP 10: FINAL CLEANUP & OUTPUT
# =============================================================================

print("[10] Final data preparation...")

# Fill NaN in season baseline metrics with 0 (if no match in master)
season_baseline_cols = [
    "SEASON_PTS_BASELINE",
    "SEASON_TS_PCT",
    "SEASON_EFG_PCT",
    "SEASON_OFF_POSS",
    "SEASON_ON_OFF_RTG",
    "SEASON_USAGE",
    "SEASON_GAMES_PLAYED"
]

for col in season_baseline_cols:
    if col in gamelogs_df.columns:
        nan_count = gamelogs_df[col].isna().sum()
        if nan_count > 0:
            gamelogs_df[col].fillna(0, inplace=True)
            print(f"      Filled {nan_count} NaN values in {col}")

print()

# =============================================================================
# STEP 11: SAVE OUTPUT
# =============================================================================

print("[11] Saving output to file...")

# Create output directory if it doesn't exist
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

gamelogs_df.to_csv(OUTPUT_PATH, index=False)
print(f"  ✓ Saved to: {OUTPUT_PATH}")
print()

# =============================================================================
# FINAL VALIDATION & SUMMARY
# =============================================================================

print("=" * 80)
print("FINAL OUTPUT SUMMARY")
print("=" * 80)
print()

print(f"Shape: {gamelogs_df.shape[0]} rows × {gamelogs_df.shape[1]} columns")
print()

print("Columns in final dataset:")
for i, col in enumerate(gamelogs_df.columns, 1):
    print(f"  {i:2d}. {col}")
print()

print("Data Types:")
print(gamelogs_df.dtypes)
print()

print("Dataset Info:")
print(f"  • Memory usage: {gamelogs_df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
print(f"  • Missing values: {gamelogs_df.isna().sum().sum()}")
print(f"  • Date range: {gamelogs_df['GAME_DATE'].min()} to {gamelogs_df['GAME_DATE'].max()}")
print()

print("Target Variable (TARGET_PTS):")
print(f"  • Min: {gamelogs_df['TARGET_PTS'].min():.1f}")
print(f"  • Max: {gamelogs_df['TARGET_PTS'].max():.1f}")
print(f"  • Mean: {gamelogs_df['TARGET_PTS'].mean():.2f}")
print(f"  • Std: {gamelogs_df['TARGET_PTS'].std():.2f}")
print()

print("Rolling Features (Last 5 Games - Past Only):")
print(f"  • ROLLING_MIN_MEDIAN_5: {gamelogs_df['ROLLING_MIN_MEDIAN_5'].mean():.2f} (mean)")
print(f"  • ROLLING_PTS_MEAN_5: {gamelogs_df['ROLLING_PTS_MEAN_5'].mean():.2f} (mean)")
print(f"  • ROLLING_TS_MEAN_5: {gamelogs_df['ROLLING_TS_MEAN_5'].mean():.4f} (mean)")
print()

print("Temporal Features:")
print(f"  • DAYS_REST: mean={gamelogs_df['DAYS_REST'].mean():.2f}, max={gamelogs_df['DAYS_REST'].max()}")
print(f"  • IS_HOME: {(gamelogs_df['IS_HOME'] == 1).sum()} home, {(gamelogs_df['IS_HOME'] == 0).sum()} away")
print()

print("Season Baseline Features:")
print(f"  • SEASON_PTS_BASELINE: {gamelogs_df['SEASON_PTS_BASELINE'].mean():.2f} (mean)")
print(f"  • SEASON_USAGE: {gamelogs_df['SEASON_USAGE'].mean():.4f} (mean)")
print(f"  • SEASON_TS_PCT: {gamelogs_df['SEASON_TS_PCT'].mean():.4f} (mean)")
print()

print("=" * 80)
print("✓ FEATURE ENGINEERING COMPLETE")
print("=" * 80)
print()
print(f"Ready for Phase 3: Model Training")
print(f"Output file: {OUTPUT_PATH}")
