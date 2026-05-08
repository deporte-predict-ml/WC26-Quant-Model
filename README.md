# 🏆 QuantBet WC26 - Motor Cuantitativo Predictivo

[![Tests](https://github.com/deporte-predict-ml/WC26-Quant-Model/actions/workflows/bot_runner.yml/badge.svg)](https://github.com/deporte-predict-ml/WC26-Quant-Model/actions)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

> **Sistema automatizado de análisis cuantitativo para predicción de partidos internacionales, enfocado en la Copa del Mundo 2026.**

Este motor está diseñado bajo una arquitectura **Mobile-First / Cloud-Only**. No requiere terminal local ni computadora; todo el código, ejecución y extracción de datos vive y corre en GitHub Actions.

---

## 📑 Tabla de Contenidos

- [🧠 Lógica del Modelo](#-lógica-del-modelo)
- [📂 Estructura del Repositorio](#-estructura-del-repositorio)
- [🚀 Setup y Ejecución](#-setup-y-ejecución)
- [⚙️ Configuración](#-configuración)
- [📊 Output y Resultados](#-output-y-resultados)
- [🧪 Testing](#-testing)
- [📈 Monitoreo y Logs](#-monitoreo-y-logs)
- [⚠️ Notas de Mantenimiento](#-notas-de-mantenimiento)
- [🤝 Contribuciones](#-contribuciones)
- [📄 Licencia](#-licencia)

---

## 🧠 Lógica del Modelo

El núcleo matemático utiliza una **Distribución de Poisson Bivariada** para proyectar los marcadores exactos y probabilidades (1X2, Over/Under). Para evitar el sobreajuste (overfitting) y tener probabilidades reales, el modelo se alimenta de:

### 1. **Datos Históricos Pesados**
Se nutre de múltiples torneos internacionales:
| Torneo | Liga ID | Temporadas |
|--------|---------|------------|
| Copa del Mundo Qatar | 1 | 2022, 2026 |
| Eliminatorias CONMEBOL | 34 | 2023-2025 |
| Nations League UEFA | 5 | 2024-2025 |
| Nations League CONCACAF | 13 | 2024-2025 |

### 2. **Decaimiento Exponencial (Time-Weighting)**
Implementa la fórmula:

$$W = e^{-\lambda \times t}$$

Donde:
- `λ (lambda)` = 0.0015 (ajustado para mejor peso temporal)
- `t` = días transcurridos desde el partido

**Un gol de hace 3 años pesa mucho menos en el promedio de xG que un gol de la semana pasada.**

### 3. **Cálculo de xG (Expected Goals)**
Saca el promedio de ataque y defensa ponderado por tiempo para encontrar las **Value Bets** reales contra las casas de apuestas.

### 4. **Criterios de Value Bet**
 Una predicción se marca como Value Bet cuando:
- Probabilidad > 65%
- Confianza > 0.65 (basada en partidos ponderados)

---

## 📂 Estructura del Repositorio
WC26-Quant-Model/ ├── .github/ │ └── flows/ │ └── bot_runner.yml # Pipeline automatizado ├── config/ │ └── settings.py # Configuración centralizada ├── scripts/ │ ├── init .py │ ├── data_fetch.py ​​# Extracción de datos API │ ├── poisson_core.py # Núcleo del modelo │ └── report_generator.py # Generación de reportes ├── tests/ │ ├── inicio .py │ ├── test_poisson.py # Tests del modelo │ └── test_data_fetch.py ​​# Tests de extracción ├── data/ │ ├── historico_selecciones.json # Datos históricos │ └── predicciones.json # Resultados ├── logs/ │ └── *.log # Logs de ejecución ├── requisitos.txt # Dependencias ├── main.py # Orquestador principal └── README.md


### Descripción de Archivos Clave

| Archivo | Propósito |
|---------|-----------|
| `config/settings.py` | Parámetros configurables sin tocar código |
| `scripts/data_fetch.py` | Conexión a API-football con retry logic |
| `scripts/poisson_core.py` | Cálculo de probabilidades y xG |
| `main.py` | Orquesta el pipeline completo |
| `.github/workflows/bot_runner.yml` | Automatización en GitHub Actions |

---

## 🚀 Setup y Ejecución

### Requisitos Previos

1. **Cuenta de GitHub** (necesaria para GitHub Actions)
2. **API Key de API-football** (o proveedor similar)
3. **Python 3.11+** (solo para desarrollo local)

### Paso 1: Configurar Secrets

En la configuración del repo (**Settings > Secrets and variables > Actions**), agrega:

| Secret | Descripción | Ejemplo |
|--------|-------------|---------|
| `API_SPORTS_KEY` | Token del proveedor de datos | `abc123xyz...` |
| `LOG_LEVEL` (opcional) | Nivel de logging | `INFO`, `DEBUG`, `WARNING` |

![Secrets Configuration](https://docs.github.com/assets/cb-40633/images/help/repository/actions-secrets.webp)

### Paso 2: Primer Ejecución Manual

1. Ve a la pestaña **Actions** del repositorio
2. Selecciona **"🏆 WC2026 Quant Model Runner"**
3. Haz clic en **Run workflow**
4. Configura las opciones:
   - **Environment**: `production` o `staging`
   - **Run tests**: `true` (recomendado)
   - **Force refresh**: `false` (solo si necesitas actualizar todo)

![Run Workflow](https://docs.github.com/assets/cb-12345/images/help/repository/workflow-dispatch.png)

### Paso 3: Ejecución Automática

El bot está programado con un **cron** que se ejecuta:

```yaml
schedule:
  - cron: '0 0 * * *'  # Todos los días a las 00:00 UTC
También se activa automáticamente en:

Push a main(en archivos de scripts/config)
Solicitudes de extracciónmain
Ejecución manual desde la UI
Ejecución Local (Desarrollo)
intento

Copiar
# 1. Clonar el repositorio
git clone https://github.com/deporte-predict-ml/WC26-Quant-Model.git
cd WC26-Quant-Model

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
export API_SPORTS_KEY="tu_api_key"
export LOG_LEVEL="DEBUG"

# 5. Ejecutar tests
pytest tests/ -v

# 6. Ejecutar pipeline completo
python main.py
