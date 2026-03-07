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
   venv\Scripts\activate   # Windows
   pip install -r requirements.txt
   ```

2. **Create a MySQL database:**

   ```sql
   CREATE DATABASE backend_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

3. **Configure environment (optional):**

   Set these env vars or edit `backend_project/settings.py` defaults:

   - `MYSQL_DATABASE` (default: `backend_db`)
   - `MYSQL_USER` (default: `root`)
   - `MYSQL_PASSWORD`
   - `MYSQL_HOST` (default: `localhost`)
   - `MYSQL_PORT` (default: `3306`)

4. **Run migrations:**

   ```bash
   python manage.py migrate
   ```

5. **Create a superuser (optional):**

   ```bash
   python manage.py createsuperuser
   ```

6. **Run the server:**

   ```bash
   python manage.py runserver
   ```

## API

- **Users**
  - `GET /api/users/` — list users
  - `POST /api/users/` — create user (JSON: `username`, `email`, `password`, `first_name`, `last_name`)
  - `GET /api/users/<id>/` — user detail
  - `PUT /api/users/<id>/` — update user
  - `DELETE /api/users/<id>/` — delete user

- **Admin:** `http://127.0.0.1:8000/admin/`
