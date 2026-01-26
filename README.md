# Library Management System (FastAPI + Vanilla JS)

A beginner-friendly Library Management System with:
- Password-based authentication
- Role-based access (admin, manager, user)
- CRUD operations for books
- Soft delete + undo delete
- Audit logging
- Frontend with toast notifications

---

## 📁 Project Structure


Passwordbased/
├── backend/
│ ├── main.py
│ └── requirements.txt
├── frontend/
│ └── index.html
└── README.md

## ⚙️ Backend Setup (FastAPI)

### 1️⃣ Create virtual environment (optional but recommended)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate

2️⃣ Install dependencies
pip install -r requirements.txt

3️⃣ Run backend server
uvicorn main:app --reload


Backend runs at:

http://127.0.0.1:8000

🌐 Frontend Setup

No build tools required.

1️⃣ Open frontend
cd frontend
xdg-open index.html


(or double-click index.html)

🔐 Default Users
Username	Password	Role
admin1	    admin123    admin
manager1	manager123	manager
user1	    user123	    user

📋 Features

Login / Logout

Role-based permissions

Add, view, update, delete books

Soft delete with undo

Audit logs (login, logout, CRUD)

Toast notifications

Clean UI flow

🧠 Notes

Data is stored in memory (no database)

Restarting backend resets data

Designed for learning purposes