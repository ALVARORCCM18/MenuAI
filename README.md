# MenuIA 🍽️🤖

MVP de una aplicación que gestiona menús inteligentes, ofreciendo recomendaciones personalizadas mediante IA.

## 🚀 Estructura del Proyecto

```
MenuIA/
├── backend/          # API construida con FastAPI y SQLAlchemy
│   └── database.py   # Configuración de la base de datos y modelos
├── frontend/         # Interfaz de usuario (En desarrollo)
├── docker-compose.yml # Configuración de servicios (DB, Backend, etc.)
└── README.md         # Documentación del proyecto
```

## 🛠️ Tecnologías

- **Backend:** Python, FastAPI, SQLAlchemy.
- **Base de Datos:** PostgreSQL (v15).
- **Despliegue:** Docker & Docker Compose.

## ⚙️ Requisitos Previos

- [Docker](https://www.docker.com/get-started) y Docker Compose instalados.
- Python 3.10+ (para desarrollo local).

## 🏃 Guía de Inicio Rápido

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd MenuIA
```

### 2. Levantar los servicios con Docker
Actualmente, puedes levantar la base de datos PostgreSQL configurada:

```bash
docker-compose up -d
```

### 3. Configuración del Backend (Local)
Si deseas ejecutar el backend localmente:

1. Crea un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```
2. Instala las dependencias (se recomienda crear un `requirements.txt`):
   ```bash
   pip install fastapi sqlalchemy psycopg2-binary uvicorn
   ```
3. Configura la variable de entorno `DATABASE_URL` o usa el valor por defecto en `database.py`.

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.
