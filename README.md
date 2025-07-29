# pymrkt

`pymrkt` es un microservicio robusto y modular para la **recolección, almacenamiento y consulta de precios financieros**, pensado para correr en servidores livianos como una Raspberry Pi y servir como backend para plataformas como [Reflejo Capital](https://github.com/cttn/reflejocapital).

---

## 🧠 ¿Qué es pymrkt?

Es un sistema que:
1. Extrae precios desde múltiples fuentes públicas (APIs como yfinance o scrapers como Rava).
2. Guarda los datos en una base local (SQLite por defecto, extensible a PostgreSQL).
3. Expone esos datos mediante una API REST que puede ser consumida por cualquier cliente.

---

## ⚙️ Arquitectura del sistema

### 1. Extracción de datos

Cada fuente de precios está representada como un módulo `fetcher`, que implementa una interfaz común:

```python
class PriceFetcher:
    def get_price(self, ticker: str) -> Optional[float]: ...
    def get_history(self, ticker: str, start: date, end: date) -> List[Tuple[date, float]]: ...
```

Las fuentes posibles incluyen:
- `yfinance` (via API)
- `rava` (scraping autenticado)
- `bolsar` (scraping)
- `dólar blue`, `MEP`, `CCL` (webs públicas)
- Criptomonedas (Coinbase, Binance)

Los tickers y frecuencia se configuran desde un archivo YAML.

---

### 2. Almacenamiento

- Se utiliza **SQLite** por defecto, con esquema optimizado:
  - Tabla `tickers`: metadata del activo.
  - Tabla `precios`: valores con timestamp, fuente y ticker.
- Consultas rápidas: último precio, histórico, lote de tickers.
- Posibilidad futura de escalar a PostgreSQL.

---

### 3. Exposición vía API REST

Usamos FastAPI para exponer:

- `GET /precio/<ticker>`  
  Último precio disponible.

- `GET /historial/<ticker>?desde=YYYY-MM-DD&hasta=YYYY-MM-DD`  
  Histórico de precios.

- `GET /batch?ticker=YPF,AAPL`  
  Precios recientes de múltiples tickers.

- `GET /status`  
  Estado del sistema.

---

### 4. Automatización

- Cada `fetcher` puede tener su propia frecuencia (configurable).
- Se usa `APScheduler` para lanzar tareas periódicas.
- Logs y errores quedan registrados en consola o archivo.
- Modular: se pueden habilitar/deshabilitar fuentes desde YAML.

---

## 📦 Estructura del proyecto

```
pymrkt/
├── api/              # API REST con FastAPI
├── config/           # YAML de configuración y .env.example
├── fetchers/         # Módulos para cada fuente de datos
├── scheduler/        # Tareas automáticas
├── scripts/          # Inicialización, mantenimiento
├── storage/          # Lógica y esquema de base de datos
├── main.py           # Punto de entrada principal
├── requirements.txt
└── README.md
```

---

## 🚀 Cómo instalar y correr

1. Clonar el repo

```bash
git clone https://github.com/cttn/pymrkt.git
cd pymrkt
```

2. Crear entorno virtual

```bash
python -m venv venv
source venv/bin/activate
```

3. Instalar dependencias

```bash
pip install -r requirements.txt
```

4. Crear archivo `.env` con variables necesarias (ver `.env.example`):

```bash
export DOLAR_SCRAPER_API_KEY=clave123
export SECRET_API_KEY=clave321
```

5. Inicializar la base

```bash
python scripts/init_db.py
```

6. Ejecutar el servidor

```bash
python main.py
```

---

## 🔐 Seguridad

- Las credenciales se pasan vía variables de entorno.
- El archivo `.env.example` sirve como plantilla.
- Nunca incluyas secretos en los archivos versionados.

---

## 🛣️ Roadmap

- [ ] Fetchers por scraping (Rava, Bolsar)
- [ ] Scheduler real con retry/backoff
- [ ] Exportaciones programadas (CSV, JSON)
- [ ] Web UI local para debugging
- [ ] Logs y monitoreo

---

## 🤝 Contribuciones

¡Bienvenidas! Especialmente si querés sumar nuevas fuentes (`fetchers`) o endpoints útiles para consumo interno o externo.

---

## 📄 Licencia

MIT License.
