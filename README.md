# NBA AI Prop Bet Predictor

Un sistema completo de **Machine Learning (MLOps)** diseñado para encontrar ventajas matemáticas (Edge) en las líneas de apuestas de la NBA (Player Props).

El sistema automatiza la extracción de estadísticas históricas, la ingeniería de características (cálculo de rachas, fatiga y matchups), y cruza las proyecciones de un modelo **XGBoost** contra las cuotas en vivo de las casas de apuestas para identificar apuestas de **Valor Esperado Positivo (EV+)**.

## ⚠️ Disclaimer

Este proyecto es **estrictamente para fines educativos y de investigación** en el ámbito de la Inteligencia Artificial.

⛔ **No es asesoría financiera.** Los modelos predictivos no garantizan resultados. **Apuesta con responsabilidad.**

## 🏗️ Arquitectura del Sistema

El pipeline diario se ejecuta en **cuatro fases secuenciales**:

| Fase                             | Descripción                                                           | Comando                                                                  |
| -------------------------------- | --------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| **1. ETL**                       | Extracción de Gamelogs oficiales mediante `nba_api`                   | `python src/data/etl_gamelogs.py`                                        |
| **2. Feature Engineering**       | Cálculo de promedios móviles, días de descanso y factores de contexto | `python src/features/02_feature_engineering.py`                          |
| **3. Context Features**          | Integración de factores contextuales (home/away, rest days, etc.)     | `python src/features/03_context_features.py`                             |
| **4. Odds Fetching & Inference** | Conexión a The Odds API y generación de proyecciones                  | `python src/data/04_fetch_odds.py` + `python src/models/06_inference.py` |

**Output final:** Archivo `.csv` con picks ordenados por Edge matemático.

## ⚙️ Requisitos Previos

## 🚀 Instalación y Configuración

### 1️⃣ Clonar el repositorio

```bash
git clone https://github.com/TU_USUARIO/nba-ai-predictor.git
cd nba-ai-predictor
```

### 2️⃣ Crear y activar el entorno virtual

⚠️ **No ejecutes este proyecto de forma global.** Aísla las dependencias en un `venv`.

**Windows (Git Bash/CMD):**

```bash
python -m venv .venv
.venv\Scripts\activate
```

**Mac/Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3️⃣ Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4️⃣ Configurar Variables de Entorno

Crea un archivo llamado `.env` en la **raíz del proyecto**:

```
ODDS_API_KEY=tu_clave_secreta_aqui
```

⚠️ **Nunca subas este archivo a GitHub.** Añádelo a `.gitignore`:

```bash
echo ".env" >> .gitignore
```

## 🔄 Ejecución: El Pipeline Diario (Operación)

Para que el modelo funcione con precisión, **el pipeline debe ejecutarse el mismo día de los partidos**, idealmente **un par de horas antes del tip-off** (cuando las casas de apuestas ya publicaron sus líneas).

### Ejecuta los comandos en este orden estricto:

#### **Fase 1: Actualizar el contexto histórico (Mañana/Tarde)**

```bash
python src/data/etl_gamelogs.py
python src/features/02_feature_engineering.py
python src/features/03_context_features.py
```

#### **Fase 2: Conectar con el mercado e Inferencia (Antes del partido)**

```bash
python src/data/04_fetch_odds.py
python src/models/06_inference.py
```

### 🤖 Automatización (Opcional)

Crea un script para ejecutar todo automáticamente:

**Windows (`run_pipeline.bat`):**

```batch
@echo off
cd /d %~dp0
call .venv\Scripts\activate
python src/data/etl_gamelogs.py
python src/features/02_feature_engineering.py
python src/features/03_context_features.py
python src/data/04_fetch_odds.py
python src/models/06_inference.py
pause
```

**Mac/Linux (`run_pipeline.sh`):**

```bash
#!/bin/bash
cd "$(dirname "$0")"
source .venv/bin/activate
python src/data/etl_gamelogs.py
python src/features/02_feature_engineering.py
python src/features/03_context_features.py
python src/data/04_fetch_odds.py
python src/models/06_inference.py
```

## 📊 Resultados Esperados

Al finalizar el script de inferencia, se generará un archivo en:

```
data/processed/nba_betting_picks.csv
```

### Contenido del archivo:

- 🟢 **OVER ⬆️ (Valor Fuerte)** → Probabilidad de sobre estimada vs. las odds
- 🔴 **UNDER ⬇️** → Probabilidad de bajo estimada vs. las odds
- ⚪ **NO BET ⚠️** → Sin ventaja matemática clara

### Columnas principales del CSV:

```
player_name | team | matchup | stat_line | model_projection |
odds_line | sportsbook | edge_percentage | ev_value | recommendation
```

## 📁 Estructura del Proyecto

```
nba-ai-predictor/
├── src/
│   ├── data/
│   │   ├── etl_gamelogs.py          # Extracción de datos
│   │   └── 04_fetch_odds.py         # Conexión a The Odds API
│   ├── features/
│   │   ├── 02_feature_engineering.py # Promedios móviles, fatiga
│   │   └── 03_context_features.py    # Factores contextuales
│   └── models/
│       └── 06_inference.py           # Predicción y cálculo de Edge
├── data/
│   ├── raw/                          # Datos sin procesar
│   └── processed/                    # Output (nba_betting_picks.csv)
├── models/
│   └── xgboost_model.pkl            # Modelo entrenado
├── .env                              # Variables de entorno (no subir)
├── .gitignore                        # Archivos a ignorar
├── requirements.txt                  # Dependencias
└── README.md                         # Este archivo
```

## 🛠️ Stack Tecnológico

| Componente              | Herramientas                 |
| ----------------------- | ---------------------------- |
| **Data Pipeline**       | `nba_api`, `pandas`, `numpy` |
| **Feature Engineering** | `pandas`, `scikit-learn`     |
| **Modelado**            | `XGBoost`, `scikit-learn`    |
| **APIs Externas**       | The Odds API                 |
| **Environment**         | `python-dotenv`              |

## 📝 Guía Rápida de Debugging

### Error: `ODDS_API_KEY not found`

✅ Verifica que el archivo `.env` existe en la raíz y contiene la clave correcta.

### Error: `ModuleNotFoundError`

✅ Asegúrate de haber activado el `venv` e instalado `pip install -r requirements.txt`

### El CSV está vacío

✅ Verifica que hay partidos de NBA programados para hoy en The Odds API.

### Las odds no se cargan

✅ Confirma que tu API Key es válida y tienes plan gratuito activado.

# Cuy Apostador

Aplicación web educativa para analizar líneas de puntos de jugadores de la NBA a partir de predicciones previamente generadas. La interfaz permite seleccionar dos equipos, introducir la línea propuesta para cada jugador y obtener una recomendación `OVER`, `UNDER` o de riesgo.

> Este proyecto es únicamente educativo y experimental. No constituye asesoría financiera ni garantiza resultados. Apuesta con responsabilidad.

## Estado actual

La versión actual es un frontend construido con React, TypeScript, Vite y Tailwind CSS.

- Las predicciones se cargan localmente desde `src/data/nba_predictions.json`.
- El análisis se realiza en el navegador; no existe una API backend conectada a la interfaz.
- La aplicación no consulta cuotas en vivo ni The Odds API.
- La carpeta `backend/` contiene datasets y un notebook de apoyo para el trabajo de datos, pero no un servidor web.
- La conexión con Supabase está declarada como dependencia, aunque actualmente no se utiliza en la interfaz.

## Funcionalidades

1. Selección de un equipo local y un equipo visitante.
2. Listado de los jugadores disponibles para cada equipo.
3. Visualización de la predicción de puntos por jugador.
4. Registro de una línea de puntos para los jugadores que se desean analizar.
5. Clasificación de cada resultado:

- `OVER`: la línea está por debajo del piso estimado.
- `UNDER`: la línea está por encima del techo estimado.
- `OVER (Riesgo)` o `UNDER (Riesgo)`: la línea se encuentra dentro del rango de incertidumbre.

6. Ordenamiento de los resultados, mostrando primero los análisis clasificados como `SAFE`.
7. Reinicio de la selección para realizar otro análisis.

## Cómo funciona el análisis

Cada registro de predicción contiene:

| Campo      | Descripción                       |
| ---------- | --------------------------------- |
| `player`   | Nombre del jugador                |
| `team`     | Código del equipo                 |
| `points`   | Puntos proyectados por el sistema |
| `floor`    | Piso estimado                     |
| `ceiling`  | Techo estimado                    |
| `real_pts` | Referencia de puntos reales       |

Para una línea introducida por el usuario:

- Si `línea < floor`, se recomienda `OVER` y se marca como `SAFE`.
- Si `línea > ceiling`, se recomienda `UNDER` y se marca como `SAFE`.
- En cualquier otro caso, se compara la línea con `points` y se marca como `RISKY`.

Esta lógica está implementada en `src/components/NbaPredictor.tsx`.

## Requisitos

- Node.js 18 o una versión posterior.
- npm.
- Python 3.10 o posterior únicamente si se desean ejecutar los scripts ETL.

## Instalación y ejecución de la aplicación

Desde la raíz del proyecto:

```bash
npm install
npm run dev
```

Vite mostrará en la terminal la URL local de la aplicación, normalmente `http://localhost:5173`.

Para crear una versión de producción:

```bash
npm run build
npm run preview
```

## Comandos disponibles

| Comando             | Uso                                             |
| ------------------- | ----------------------------------------------- |
| `npm run dev`       | Inicia el servidor de desarrollo de Vite        |
| `npm run build`     | Comprueba tipos y genera el build de producción |
| `npm run typecheck` | Ejecuta TypeScript sin emitir archivos          |
| `npm run lint`      | Ejecuta ESLint                                  |
| `npm run preview`   | Sirve localmente el build generado              |

## Preparación de datos con Python

Los scripts de la raíz descargan y consolidan datos históricos en `data/processed/`:

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Instalar las dependencias usadas por los scripts ETL
pip install pandas requests nba_api
```

### Game logs de la NBA

```bash
python etl_gamelogs.py
```

Consulta `nba_api` para las temporadas configuradas en el script y genera:

```text
data/processed/nba_gamelogs_dataset.csv
```

### Datos históricos de PBP Stats

```bash
python etl_historico.py
```

Consulta la API pública de PBP Stats y genera:

```text
data/processed/nba_master_dataset.csv
```

Los scripts incluyen pausas entre peticiones para reducir la carga sobre las APIs. Las temporadas procesadas están definidas directamente en cada archivo.

## Estructura del proyecto

```text
project/
├── backend/
│   ├── nba_datos_limpios.csv
│   ├── nba_predictions.json
│   └── ProyectoIA.ipynb
├── data/
│   └── processed/
│       ├── nba_features_elite.csv
│       ├── nba_gamelogs_dataset.csv
│       └── nba_master_dataset.csv
├── src/
│   ├── components/
│   │   └── NbaPredictor.tsx
│   ├── data/
│   │   ├── mockPredictions.ts
│   │   └── nba_predictions.json
│   ├── features/
│   │   └── 02_feature_engineering.py
│   ├── types/
│   │   └── predictions.ts
│   ├── App.tsx
│   ├── index.css
│   └── main.tsx
├── etl_gamelogs.py
├── etl_historico.py
├── package.json
├── tailwind.config.js
└── vite.config.ts
```

## Tecnologías

- **Frontend:** React 18, TypeScript y Vite.
- **Estilos:** Tailwind CSS y PostCSS.
- **Iconos:** `lucide-react`.
- **Datos y ETL:** Python, pandas, requests y `nba_api`.
- **Fuentes de datos:** NBA API y PBP Stats para la preparación de datasets.

## Limitaciones conocidas

- Las predicciones mostradas dependen del archivo JSON incluido en el repositorio.
- No se actualizan automáticamente los partidos, jugadores, lesiones ni cuotas.
- No se calculan probabilidades implícitas, valor esperado ni gestión real de stake.
- La recomendación debe interpretarse como una clasificación experimental, no como una apuesta garantizada.

## Próximos pasos posibles

- Conectar la interfaz con un backend o servicio de predicción.
- Automatizar la generación de `nba_predictions.json` a partir de los datasets procesados.
- Incorporar cuotas reales, probabilidades, valor esperado y validación histórica.
- Añadir pruebas automatizadas para la lógica de clasificación.
