# Backend Project (Django + MySQL)

Django REST API backend with MySQL and a `users` app.

## Structure

```
backend_project
├── users
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── urls.py
│   └── ...
├── backend_project
│   ├── settings.py
│   ├── urls.py
│   └── ...
└── manage.py
```

## Setup

1. **Create a virtual environment and install dependencies:**

   ```bash
   python -m venv venv
   venv\Scripts\activate   # Windows (required before pip/python if you use plain "python")
   pip install -r requirements.txt
   ```

   **If you get "Couldn't import Django"**: you're not using the venv's Python. Either:
   - **Activate the venv** first: `venv\Scripts\activate` (Windows), then `python manage.py runserver`, or
   - **Use the venv Python directly**: `venv\Scripts\python.exe manage.py runserver`, or
   - **Double‑click `run.bat`** (or run `.\run.ps1`) from the project folder to start the server without activating.

2. **Create a MySQL database:**

   ```sql
   CREATE DATABASE backend_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

3. **Configure environment (optional):**

   Copy `.env.example` to `.env` and adjust, or set env vars:

   - `MYSQL_DATABASE` (default: `backend_db`)
   - `MYSQL_USER` (default: `root`)
   - `MYSQL_PASSWORD`
   - `MYSQL_HOST` (default: `localhost`)
   - `MYSQL_PORT` (default: `3306`)
   - `FRONTEND_URL` (default: `http://localhost:3000`) — for CORS when a frontend calls the API
   - `API_BASE_URL` (default: `http://localhost:8000`) — backend base URL (for frontend .env reference)

4. **Run migrations:**

   ```bash
   python manage.py migrate
   ```

5. **Create a superuser (optional):**

   ```bash
   python manage.py createsuperuser
   ```

6. **Run the server** (from the project folder, with venv activated or use the run script):

   ```bash
   python manage.py runserver
   ```
   Or without activating venv: `venv\Scripts\python.exe manage.py runserver`, or run **`run.bat`** / **`run.ps1`**.

## API

- **Users**
  - `GET /api/users/` — list users
  - `POST /api/users/` — create user (JSON: `username`, `email`, `password`, `first_name`, `last_name`)
  - `GET /api/users/<id>/` — user detail
  - `PUT /api/users/<id>/` — update user
  - `DELETE /api/users/<id>/` — delete user

- **Admin:** `http://127.0.0.1:8000/admin/`

## Connecting a frontend

The backend allows requests from your frontend origin (CORS) and supports cookie-based login.

1. **Backend `.env`** (or env vars):
   - `FRONTEND_URL` — origin of the frontend app, e.g. `http://localhost:3000` (React/Vite). Use comma-separated values for multiple origins.
   - `API_BASE_URL` — base URL of this API (e.g. `http://localhost:8000`) for documentation or frontend config.

2. **Frontend `.env`** (use the API base URL when calling the backend):
   - **React (Create React App):** `REACT_APP_API_URL=http://localhost:8000`
   - **Vite:** `VITE_API_URL=http://localhost:8000`
   - Then in code: `fetch(`${import.meta.env.VITE_API_URL}/api/users/owners/`)` or equivalent.

3. **Using the API from the frontend:**
   - Base URL: `http://localhost:8000` (or your `API_BASE_URL`).
   - Endpoints: `/api/users/`, `/api/users/owners/`, `/api/users/projects/`, `/api/users/login/`, `/api/users/logout/`, etc.
   - For login/logout with cookies, use `credentials: 'include'` in `fetch` so the session cookie is sent and stored.
