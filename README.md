# RBAC FastAPI Demo

## Overview

This project demonstrates Role-Based Access Control (RBAC) using FastAPI.
Users have roles (admin, manager, user), and roles map to permissions.
Each API endpoint declares which permissions it requires.

## How to run

```bash
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/macOS: source venv/bin/activate

pip install -r requirements.txt

uvicorn app.main:app --reload
ow to test (Postman):

Base URL: http://127.0.0.1:8000

Header: X-User: one | two | three

Example calls:

GET /me

GET /items

POST /items (body {"name": "demo"})

DELETE /items/1

PUT /admin/roles

PUT /admin/users/role