# Backend FastAPI con JWT

Aplicación Web API en Python con FastAPI que implementa autenticación JWT.

## Requisitos

- Python 3.11+
- Poetry
- Docker (opcional)

## Configuración con Poetry

```bash
cd backend
poetry install
```

## Ejecutar localmente

```bash
cd backend
poetry run uvicorn app.main:app --reload
```

API disponible en `http://127.0.0.1:8000`.

## Endpoints

### 1. Generar token

**POST** `/token`

Body JSON:

```json
{
  "username": "admin",
  "password": "admin123"
}
```

También se acepta el campo `user` en lugar de `username`.
Respuesta:

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer",
  "expires_in": 300,
  "refresh_token": "<jwt_refresh>"
}
```

### 2. Refrescar token

**POST** `/refresh`

Body JSON:

```json
{
  "refresh_token": "<jwt_refresh>"
}
```

Devuelve un nuevo `access_token` (300 segundos) y un nuevo `refresh_token`.

### 3. Health check

**GET** `/health`

## Uso con Docker

Desde la carpeta `backend`:

```bash
docker compose up --build
```

Luego consumir la API en `http://localhost:8000`.
