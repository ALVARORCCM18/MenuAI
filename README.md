# MenuIA 🍽️🤖

MVP de una aplicación que gestiona menús inteligentes, ofreciendo recomendaciones personalizadas mediante IA.

## 🚀 Estructura del Proyecto

```text
MenuIA/
├── backend/           # API FastAPI + SQLAlchemy + OpenAI
├── frontend/          # Next.js App Router con Tailwind CSS
├── docker-compose.yml # Configuración de PostgreSQL
├── .env.example       # Variables de entorno recomendadas
└── README.md          # Documentación del proyecto
```

## 🛠️ Tecnologías

- **Backend:** Python, FastAPI, SQLAlchemy, Pydantic.
- **Base de Datos:** PostgreSQL.
- **Frontend:** Next.js, TypeScript, Tailwind CSS.
- **IA:** OpenAI GPT-4o con Structured Outputs.

## ⚙️ Requisitos Previos

- Python 3.10+
- Docker + Docker Compose (para PostgreSQL local)
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

Y detener todos los servicios con:

```powershell
powershell -ExecutionPolicy Bypass -File .\stop-all.ps1
```

## 🔍 Endpoints disponibles

- `GET /menu?weather={clima}&time={hora}`
- `GET /admin/inventory`
- `PATCH /admin/inventory/{id}`

## 💡 Notas

- Las credenciales deben guardarse en `.env`, que ya está excluido en `.gitignore`.
- Si no hay clave de OpenAI configurada, el backend usa un ranking local de respaldo.
