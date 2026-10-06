# ROADMAP - NBA POINTS PREDICTOR v2.0

## Arquitectura de Machine Learning para Predicción de Puntos Partido-a-Partido

---

## 1. VISIÓN GENERAL Y OBJETIVO CORE

### 1.1 Problema

Predecir cuántos puntos anotará un jugador en su **próximo partido** (Next_Game_PTS) con precisión competitiva, eliminando completamente:

- **Data Leakage**: No usar métricas de la temporada actual para predecir esa misma temporada
- **Estimaciones falsas**: Usar valores reales de play-by-play, nunca aproximaciones
- **Validación circular**: Prohibido random split en datos temporales

### 1.2 Solución Técnica

Pasado: SGDRegressor lineal + promedios de temporada (R² = 0.94 falso)
↓
Presente: XGBoost/LightGBM + rolling averages (últimos 5 juegos) + contexto pre-juego
↓
Resultado: R² realista = 0.55-0.68 (validación temporal honesta)

### 1.3 Diferencial del Modelo

| Aspecto    | Anterior                 | Nuevo                        |
| ---------- | ------------------------ | ---------------------------- |
| Target     | Promedio de temporada    | Puntos en SIGUIENTE partido  |
| Features   | Stats de misma temporada | Rolling avg + contexto rival |
| Modelo     | Regresión lineal         | Tree-based (XGBoost)         |
| Leakage    | Máximo (circular)        | Cero (causalidad respetada)  |
| Validación | Random split (inválido)  | Time-Series Split (válido)   |

## 2. ARQUITECTURA DE DIRECTORIOS

NBA_Predictor/
│
├── data/
│ ├── raw/
│ │ ├── nba_master_dataset.csv # ADN: métricas avanzadas por jugador/temporada
│ │ └── nba_gamelogs_dataset.csv # Línea de tiempo: 80k partidos elemento a elemento
│ │
│ └── processed/
│ ├── nba_features_ready.csv # Features engineered (rolling avg + contexto)
│ ├── nba_train_set.csv # Train: 2022-2025
│ └── nba_test_set.csv # Test: últimas 4 semanas 2026
│
├── src/
│ ├── init.py
│ │
│ ├── data/
│ │ ├── init.py
│ │ ├── loader.py # Carga nba_master_dataset + nba_gamelogs
│ │ └── merger.py # Une ADN + Línea de tiempo sin leakage
│ │
│ ├── features/
│ │ ├── init.py
│ │ ├── rolling_stats.py # Calcula rolling avg (últimos N juegos)
│ │ ├── context_features.py # Opponent defense, home/away, rest_days
│ │ └── feature_selection.py # Elimina features colineales
│ │
│ ├── models/
│ │ ├── init.py
│ │ ├── train.py # Entrena XGBoost con Time-Series Split
│ │ ├── evaluate.py # Métricas (MAE, RMSE, R2, SHAP)
│ │ └── inference.py # Predicción en batch
│ │
│ └── utils/
│ ├── init.py
│ ├── logger.py # Logging centralizado
│ └── validators.py # Chequeos de leakage, nulls, etc.
│
├── notebooks/
│ ├── 01_eda.ipynb # Exploración de datos
│ ├── 02_feature_engineering.ipynb # Desarrollo de features
│ ├── 03_model_training.ipynb # Ajuste de hiperparámetros
│ └── 04_inference_demo.ipynb # Demo de predicciones
│
├── models/
│ ├── xgboost_v1.pkl # Modelo entrenado serializado
│ └── feature_scaler.pkl # StandardScaler (si aplica)
│
├── config/
│ ├── constants.py # Constantes: SEASONS, FEATURES_TO_USE, etc.
│ └── hyperparams.py # Hiperparámetros XGBoost
│
├── orchestration/
│ ├── etl_historico.py # Sprint 1.1: Carga histórica (pbpstats API)
│ ├── etl_gamelogs.py # Sprint 1.2: Game logs (nba_api)
│ ├── 02_feature_engineering.py # Sprint 2: Feature eng
│ ├── 03_train_model.py # Sprint 3: Entrenamiento
│ └── 04_daily_inference.py # Sprint 4: Predicción diaria en producción
│
├── tests/
│ ├── test_leakage.py # Valida cero data leakage
│ ├── test_features.py # Chequea features no nulas
│ └── test_model.py # Validación del modelo
│
├── requirements.txt
├── README.md
└── ROADMAP.md

## 3. FASES DEL PROYECTO (SPRINT ROADMAP)

### FASE 1: INGESTA DE DATOS ✅ COMPLETADA

**Objetivo:** Descargar métricas reales (sin estimaciones) desde fuentes autoritativas.

**Sprint 1.1 - Carga Histórica (pbpstats API)**

- ✅ Descargó `nba_master_dataset.csv` desde https://api.pbpstats.com/get-totals/nba
- ✅ 3 temporadas: 2022-23, 2023-24, 2024-25
- ✅ 251 columnas: Puntos, Posesiones (reales, no estimadas), Off_Rating, Usage, TS%, etc.
- ✅ Arquitectura: 1 call HTTP por temporada (O(1) efficiency)

**Sprint 1.2 - Game Logs (nba_api)**

- ✅ Descargó `nba_gamelogs_dataset.csv` con LeagueGameLog endpoint
- ✅ ~80,000 registros (partidos individuales)
- ✅ Columnas: PLAYER_NAME, GAME_DATE, TEAM_ABBREVIATION, MIN, FGM, FGA, PTS, +/-, etc.
- ✅ 3 llamadas API (O(1) efficiency)

**Entregables:**

data/processed/
├── nba_master_dataset.csv (ADN del jugador: métricas resumen-carrera)
└── nba_gamelogs_dataset.csv (Línea de tiempo: partido a partido)

### FASE 2: FEATURE ENGINEERING (PRÓXIMO SPRINT)

**Objetivo:** Unir ADN + Línea de tiempo respetando causalidad temporal (CERO LEAKAGE).

**Arquitectura de Unión (CRITICAL):**

```python
# CORRECTO (Causal, Sin Leakage):
for game_date in sorted(unique_dates):
    # Obtener histórico del jugador ANTES de game_date
    history = gamelogs[gamelogs['GAME_DATE'] < game_date]
    # Calcular rolling average de ÚLTIMOS 5 JUEGOS
    rolling_5 = history.tail(5)[['PTS', 'MIN', 'AST']].mean()
    # Target: Puntos en game_date
    target = gamelogs[gamelogs['GAME_DATE'] == game_date]['PTS']
    # ✓ No hay fuga: usamos info previa para predecir línea de tiempo futura

# INCORRECTO (Data Leakage):
rolling_5 = gamelogs[gamelogs['season'] == '2023-24'][['PTS']].mean()
# ✗ Usaste stats DE LA MISMA TEMPORADA para predecir esa temporada

Features a Calcular:

# .shift(1) = desplaza 1 fila hacia adelante = ve PASADO, no futuro
rolling_pts_5 = df_gamelogs['PTS'].rolling(5).mean().shift(1)
rolling_min_5 = df_gamelogs['MIN'].rolling(5).mean().shift(1)
rolling_usage_5 = df_gamelogs['USAGE'].rolling(5).mean().shift(1)
rolling_ts_pct_5 = df_gamelogs['TS_PCT'].rolling(5).mean().shift(1)

Contexto Pre-Juego:

opponent = gamelogs['OPPONENT_TEAM']
opponent_defense_rtg = merge_con(nba_master, opponent)  # Defensa del rival
home_away = (gamelogs['GAME_LOCATION'] == '@').astype(int)  # 0=Local, 1=Visitante
rest_days = (gamelogs['GAME_DATE'].diff()).dt.days  # Días desde último juego
back_to_back = (rest_days == 1).astype(int)  # Flag para juegos consecutivos

Trend Features:

# ¿Jugador en racha o decayendo?
pts_trend = (rolling_pts_5.iloc[-1] - rolling_pts_5.iloc[-3]) / rolling_pts_5.iloc[-3]

Output:

data/processed/nba_features_ready.csv
├─ player_id, game_date
├─ rolling_pts_5, rolling_min_5, rolling_usage_5, rolling_ts_pct_5
├─ opponent, opponent_def_rtg, home_away, rest_days, back_to_back
├─ pts_trend, injury_status (si disponible)
└─ TARGET: next_game_pts (puntos que anotará en el siguiente partido)

Mandamiento

PROHIBIDO: df['rolling_avg'] = df['PTS'].rolling(5).mean()
         ↓
         Ves el futuro (leakage)

OBLIGATORIO: df['rolling_avg'] = df['PTS'].rolling(5).mean().shift(1)
            ↓
            Ves solo el pasado (correcto)

FASE 3: MODELADO Y VALIDACIÓN
Objetivo: Entrenar modelo con Time-Series Split (validación temporal honesta).

Split Strategy (PROHIBITION: random split):

Timeline: 2022-2025 -------------------- Últimos 30 días 2026
          ↓                              ↓
         TRAIN                          TEST
         (3+ años de historia)    (validación futura)

Incorrecta (RECHAZADA):
train_set, test_set = train_test_split(df, test_size=0.2, random_state=42)
                      ↓
                      Mezcla pasado/futuro = predicción falsa

ROADMAP DE EJECUCIÓN

SEMANA 1:
  ├─ Sprint 1.1 ✅ (Historico)
  └─ Sprint 1.2 ✅ (Gamelogs)

SEMANA 2:
  ├─ Sprint 2.1 (Feature Engineering: Rolling Avgs)
  ├─ Sprint 2.2 (Context Features: Opponent, Home/Away)
  └─ Sprint 2.3 (Validación de Leakage: test_leakage.py)

SEMANA 3:
  ├─ Sprint 3.1 (Entrenamiento: XGBoost con Time-Series Split)
  ├─ Sprint 3.2 (Evaluación: SHAP, Feature Importance)
  └─ Sprint 3.3 (Tuning de Hiperparámetros)

SEMANA 4:
  ├─ Sprint 4.1 (Daily Inference Pipeline)
  ├─ Sprint 4.2 (API REST para web frontend)
  └─ Sprint 4.3 (Deployment + Monitoreo)

PRODUCCIÓN:
  └─ Predicciones diarias: nba_predictions.json


8. REFERENCIAS TÉCNICAS

Librerías Core:

pandas: Manipulación de datos
xgboost: Modelo predictivo
nba_api: Descarga de stats en directo
scikit-learn: Métricas, procesamiento
shap: Feature importance, explicabilidad
Fuentes de Datos:

pbpstats API: https://api.pbpstats.com/get-totals/nba (métricas reales)
nba_api: Endpoints de NBA oficial (game logs)
```
