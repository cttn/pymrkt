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
    supported_ticker_types: Tuple[Optional[str], ...]
    def get_price(self, ticker: str, ticker_type: Optional[str] = None) -> Optional[float]: ...
    def get_history(self, ticker: str, start: date, end: date) -> List[Tuple[date, float]]: ...
```

Las fuentes posibles incluyen:
- `yfinance` (via API)
- `rava` (scraping autenticado)
- `bolsar` (scraping)
- `dólar blue`, `MEP`, `CCL` (webs públicas)
- Criptomonedas (Coinbase, Binance)

Los tickers, su frecuencia y el valor de `lock_minutes` se configuran desde un
archivo YAML (`config/config.yaml`).

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

5. (Opcional) Inicializar la base manualmente

El servidor crea las tablas automáticamente al iniciar, por lo que este paso es
generalmente innecesario.

```bash
python scripts/init_db.py
```

6. Ejecutar el servidor

```bash
python main.py
```

Si querés ver mensajes de depuración durante la ejecución, podés agregar la
bandera `--debug`:

```bash
python main.py --debug
```

7. Levantar la API local

```bash
python -m api.server
```
Al iniciarse, el servidor crea automáticamente las tablas necesarias en las bases de datos, por lo que no es obligatorio ejecutar `scripts/init_db.py` de forma previa. El host y el puerto utilizados por la API se pueden ajustar en `config/config.yaml`.

8. Consultar la API

Una vez levantado el servidor (la dirección y el puerto se definen en
`config/config.yaml`, por defecto `http://127.0.0.1:8000`), podés obtener el
precio de un ticker usando `curl`:

```bash
# Por defecto
curl http://127.0.0.1:8000/price/AAPL
# Con tipo de ticker (por ejemplo "acciones")
curl http://127.0.0.1:8000/price/acciones/AAPL
```

La respuesta será un JSON similar a:

```json
{"ticker": "AAPL", "price": 123.45, "updated_at": "2023-01-01T12:00:00Z"}
```

### Uso de la lógica de fetching

Luego de inicializar las bases de datos, podés obtener precios de forma manual
llamando a la función `get_live_price` junto con el *fetcher* que prefieras. Por
ejemplo, utilizando el `DummyFetcher` incluido:

```python
from fetchers import DummyFetcher
from api.live import get_live_price
from scripts.init_db import main as init_db

init_db()
fetcher = DummyFetcher()
price, updated_at = get_live_price("AAPL", fetcher, ticker_type="acciones")
print(price, updated_at)
```

El resultado queda almacenado en `storage/live.acciones.db`. Si solicitás nuevamente el
precio antes de que pasen 15 minutos (valor configurable con `lock_minutes` en
`config/config.yaml`), se devolverá el último precio guardado sin contactar al
*fetcher*.

### Configuración del tiempo de *lock*

`get_live_price` acepta un parámetro opcional `lock_minutes` que define cuántos
minutos deben transcurrir antes de volver a consultar a la fuente de datos. Por
defecto este valor se obtiene desde `config/config.yaml`. Si establecés
`lock_minutes=0`, el servicio buscará siempre un precio nuevo en lugar de usar
el almacenado en la base. Podés ajustarlo a tus necesidades:

```python
price, updated_at = get_live_price(
    "AAPL", fetcher, lock_minutes=5, ticker_type="acciones"
)
```

En el archivo `main.py` se muestra un ejemplo que utiliza el valor definido en
`config/config.yaml` para reducir la cantidad de llamadas externas.

### Uso simultáneo de varios fetchers

`get_live_price` también acepta una lista de *fetchers*. Podés activar varios a
la vez y el sistema usará solo aquellos que soporten el tipo de ticker
solicitado. Por ejemplo, combinando `YFinanceFetcher` con `BancoPianoFetcher`:

```python
from fetchers import YFinanceFetcher, BancoPianoFetcher
from api.live import get_live_price

fetchers = [YFinanceFetcher(), BancoPianoFetcher()]
price, updated_at = get_live_price("AL30", fetchers, ticker_type="bonos")
```

La función filtrará automáticamente los *fetchers* para que cada consulta se
realice solo a las fuentes adecuadas.

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
