# Copilot - Backend + Frontend

Proyecto con autenticación JWT compuesto por:

- `backend/`: API en FastAPI con endpoint de login.
- `frontend/`: aplicación React con login y página de bienvenida protegida.

## Requisitos

- Python 3.11+
- Poetry
- Node.js 20+

## 1) Ejecutar backend

```bash
cd backend
poetry install
export JWT_SECRET="change-this-in-production-32-byte-secret"
export ADMIN_USERNAME="admin"
export ADMIN_PASSWORD="admin123"
poetry run uvicorn app.main:app --reload
```

Backend disponible en `http://127.0.0.1:8000`.

## 2) Ejecutar frontend

En una nueva terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend disponible en `http://127.0.0.1:5173`.

> El frontend usa proxy de Vite (`/api`) para comunicarse con el backend.

## Flujo funcional

1. Ingresar usuario y contraseña en `/login`.
2. El frontend llama `POST /token` del backend.
3. Si es exitoso, guarda `access_token` en `sessionStorage` y redirige a `/welcome`.
4. La ruta `/welcome` está protegida: si no hay sesión activa, redirige a `/login`.
5. El botón **Cerrar sesión** limpia la sesión y vuelve al login.

## Credenciales de ejemplo

Si usas los valores del ejemplo de entorno:

- Usuario: `admin`
- Contraseña: `admin123`
