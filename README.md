# MenuIA 🍽️🤖

Aplicación de menú inteligente para restaurante con inventario por ingredientes, recetas con composición, ventas atómicas y recomendaciones por IA.

## 🚀 Estructura del Proyecto

```text
MenuIA/
├── backend/           # API FastAPI + SQLAlchemy + OpenAI
├── frontend/          # Next.js App Router con Tailwind CSS
├── docker-compose.yml # PostgreSQL local
├── start-all.ps1      # Arranque guiado en Windows
├── stop-all.ps1       # Parada guiada en Windows
└── README.md          # Documentación del proyecto
```

## 🛠️ Tecnologías

- **Backend:** Python, FastAPI, SQLAlchemy, Pydantic.
- **Base de Datos:** PostgreSQL.
- **Frontend:** Next.js, TypeScript, Tailwind CSS.
- **IA:** OpenAI GPT-4o con Structured Outputs.
- **Dominio actual:** ingredientes, platos, recetas, transacciones de stock y ventas atómicas.

## ⚙️ Requisitos Previos

- Python 3.10+
- PostgreSQL local o Docker + Docker Compose
- Node.js y npm (para la interfaz frontend)

## 📦 Configuración del Entorno

1. Copia el archivo de ejemplo:

   ```bash
   copy .env.example .env
   ```

2. Ajusta las credenciales en `.env`:
   - `DATABASE_URL`
   - `OPENAI_API_KEY`
   - `NEXT_PUBLIC_API_BASE_URL`

Si no usas Docker, puedes apuntar `DATABASE_URL` a una instancia local de PostgreSQL.

## 🧱 Levantar los servicios con Docker

```bash
docker compose up -d
```

Esto levantará:

- PostgreSQL en el servicio `db`
- Backend FastAPI en el servicio `backend`

## 🥣 Poblar datos de ejemplo

```bash
python -m backend.seed
```

El seed actual crea datos legacy y v2:
- Productos legacy para compatibilidad con `/menu` y `/admin/inventory`
- Ingredientes, platos y recetas para `/v2/*`

## 🗃️ Migraciones de base de datos (Alembic)

Desde la raiz del proyecto:

```bash
pip install -r backend/requirements.txt
alembic -c backend/alembic.ini upgrade head
```

Para revertir la ultima migracion:

```bash
alembic -c backend/alembic.ini downgrade -1
```

Nota: el backend ya no depende de `create_all` por defecto. Si quieres habilitarlo temporalmente en desarrollo, define `AUTO_CREATE_SCHEMA=true`.

## ✅ Test de migraciones

Usa una base de datos de pruebas dedicada para no afectar datos reales:

```bash
set MIGRATION_TEST_DATABASE_URL=postgresql://user:password@localhost:5432/menuai_db_test
python -m unittest backend.tests.test_migrations
```

## 🚀 Ejecutar el backend

```bash
python -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```

## 🌐 Ejecutar el frontend

```bash
cd frontend
npm install
npm run dev
```

## ⚡ Arranque rapido (Windows)

Desde la raiz del proyecto puedes arrancar todo con un solo comando:

```powershell
powershell -ExecutionPolicy Bypass -File .\start-all.ps1
```

Ese script hace esto:

- levanta PostgreSQL portable desde `.local-postgres` en `127.0.0.1:55432`
- crea `.env` si no existe, con la URL local de la base de datos
- arranca el backend en `http://127.0.0.1:8000`
- arranca el frontend en `http://127.0.0.1:3000`

Y detener todos los servicios con:

```powershell
powershell -ExecutionPolicy Bypass -File .\stop-all.ps1
```

Si prefieres usar Docker para la base de datos:

```bash
docker compose up -d
```

En ese caso el servicio expone PostgreSQL en `127.0.0.1:55432`.

Nota práctica:

- `start-all.ps1` usa el entorno portable del propio proyecto y es la forma recomendada para trabajar en Windows sin depender de Docker.
- `docker compose up -d` solo levanta la base de datos; después debes arrancar backend y frontend por separado si no usas `start-all.ps1`.

## 🔍 Endpoints disponibles

- `GET /menu?weather={clima}&time={hora}`
- `GET /admin/inventory`
- `PATCH /admin/inventory/{id}`
- `GET /v2/ingredients`
- `POST /v2/ingredients`
- `PATCH /v2/ingredients/{ingredient_id}`
- `GET /v2/dishes`
- `POST /v2/dishes`
- `POST /v2/sales`
- `GET /v2/stock-transactions`

## 🧭 Estado actual de la interfaz

- `/admin` muestra inventario de ingredientes, editor de recetas y ventas atómicas de platos.
- `/` consume `/menu` y muestra la carta legacy priorizada por IA.
- El sistema v2 convive con el flujo legacy para no romper compatibilidad.

## 🏗️ Arquitectura del sistema

- **Frontend público:** `/` consume `GET /menu` y pinta la carta ordenada por IA.
- **Panel admin:** `/admin` permite crear ingredientes, definir recetas y vender platos.
- **Backend legacy:** mantiene `/menu` y `/admin/inventory` para no romper el flujo anterior.
- **Backend v2:** expone ingredientes, platos, ventas atómicas y transacciones de stock.
- **Persistencia:** PostgreSQL guarda tanto el inventario legacy como el modelo v2 basado en ingredientes.
- **IA:** si existe `OPENAI_API_KEY`, el backend usa OpenAI; si no, aplica ranking local de respaldo.

## 👀 Guía rápida de uso

1. Abre `http://127.0.0.1:3000/admin`.
2. Crea ingredientes base con stock inicial y unidad de medida.
3. Usa el editor de recetas para construir un plato a partir de esos ingredientes.
4. Revisa la tabla de platos y vende una unidad para comprobar el descuento atómico de stock.
5. Abre `http://127.0.0.1:3000/` para ver la carta priorizada por IA.
6. Cambia clima y hora desde el simulador para observar cómo varía la recomendación.

## 💡 Notas

- Las credenciales deben guardarse en `.env`, que ya está excluido en `.gitignore`.
- Si no hay clave de OpenAI configurada, el backend usa un ranking local de respaldo.
- En Windows, si `npm` falla por políticas de PowerShell, ejecuta los scripts desde `cmd /c`.

## 🛠️ Resolución de problemas

- Si `/admin` muestra un error extraño tras cambios de UI, cierra el servidor, borra `frontend/.next` y vuelve a ejecutar `npm run dev`.
- Si Next.js no levanta por un cache corrupto, limpia `.next` y reinicia el frontend.
- Si el puerto `3000` o `8000` está ocupado, detén el proceso anterior antes de volver a arrancar.
- Si cambias la base de datos local, revisa `DATABASE_URL` y vuelve a lanzar `start-all.ps1`.
