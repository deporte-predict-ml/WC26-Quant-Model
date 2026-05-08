# 🏆 QuantBet WC26 - Motor Cuantitativo Predictivo

Sistema automatizado de análisis cuantitativo y Machine Learning para predicción de partidos internacionales, enfocado en reventar las cuotas de la Copa del Mundo 2026. 

Este motor está diseñado bajo una arquitectura **Mobile-First / Cloud-Only**. No requiere terminal local ni computadora; todo el código, ejecución y extracción de datos vive y corre en GitHub Actions.

## 🧠 Lógica del Modelo

El núcleo matemático utiliza una **Distribución de Poisson Bivariada** para proyectar los marcadores exactos y probabilidades (1X2, Over/Under). Para evitar el sobreajuste (overfitting) y tener probabilidades reales, el modelo se alimenta de:

1. **Datos Históricos Pesados:** Se nutre de Qatar 2022, Eliminatorias de CONMEBOL, Nations League (UEFA/CONCACAF) y amistosos clase A.
2. **Decaimiento Exponencial (Time-Weighting):** Implementa la fórmula $W = e^{-\lambda \times t}$ para castigar los resultados viejos. Un gol de hace 3 años pesa mucho menos en el promedio de xG que un gol de la semana pasada.
3. **Cálculo de xG (Expected Goals):** Saca el promedio de ataque y defensa ponderado por tiempo para encontrar las *Value Bets* reales contra las casas de apuestas.

## 📂 Estructura del Repositorio

El jale está organizado así para que no haya pedos al correr en la nube:

* `scripts/data_fetch.py`: El script que se conecta a la API deportiva, extrae los cientos de partidos y los formatea.
* `scripts/poisson_core.py`: El cerebro. Lee el JSON, aplica la matemática y escupe las proyecciones.
* `data/`: Aquí se guardan los JSON crudos automáticamente. No se toca a mano.
* `.github/workflows/bot_runner.yml`: El cronograma. Despierta al bot en las madrugadas para que actualice la base de datos y corra el modelo.
* `requirements.txt`: Dependencias pesadas (`numpy`, `scipy`, `requests`).

## 🚀 Setup y Ejecución (Flujo en la nube)

Como la tirada es manejar todo desde el cel, la configuración es puro *plug-and-play* en GitHub:

1. **Claves de Seguridad:** En la configuración del repo (Settings > Secrets and variables > Actions), necesitas agregar:
   * `API_SPORTS_KEY`: Tu token del proveedor de datos (ej. API-football).
2. **Arranque Manual:** Ve a la pestaña **Actions**, selecciona "WC2026 Model Runner" y dale a *Run workflow* para la primera extracción masiva.
3. **Arranque Automático:** El bot ya está programado con un *cron* para jalar datos nuevos todos los días a las 00:00 UTC.

## ⚠️ Notas de Mantenimiento

* Si la API batea las peticiones, el script tiene un `time.sleep` para evitar bloqueos por saturación.
* Al ser un entorno automatizado, cualquier ajuste a la fórmula matemática se hace directo en el archivo `poisson_core.py` desde el editor web de GitHub.
