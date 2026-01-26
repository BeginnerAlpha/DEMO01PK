from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- DATA ----------------
users_db = {
    "admin1": {"password": "admin123", "role": "admin"},
    "manager1": {"password": "manager123", "role": "manager"},
    "user1": {"password": "user123", "role": "user"},
}

books_db = []
audit_logs = []
book_id_counter = 1

# ---------------- MODELS ----------------
class AuthRequest(BaseModel):
    username: str
    password: str

class Book(BaseModel):
    title: str
    author: str

class BookRequest(Book, AuthRequest):
    pass

class RoleUpdateRequest(AuthRequest):
    target_user: str
    new_role: str

# ---------------- HELPERS ----------------
def authenticate(data: AuthRequest):
    if data.username not in users_db:
        raise HTTPException(status_code=401, detail="Invalid username")
    if users_db[data.username]["password"] != data.password:
        raise HTTPException(status_code=401, detail="Invalid password")
    return users_db[data.username]["role"]

def authorize(role, allowed):
    if role not in allowed:
        raise HTTPException(status_code=403, detail="Permission denied")

def log(action, user, details=""):
    audit_logs.append({
        "action": action,
        "user": user,
        "details": details,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

# ---------------- AUTH ----------------
@app.post("/login")
def login(data: AuthRequest):
    role = authenticate(data)
    log("LOGIN", data.username)
    return {"role": role}

@app.post("/logout")
def logout(data: AuthRequest):
    authenticate(data)
    log("LOGOUT", data.username)
    return {"message": "Logged out"}

# ---------------- BOOKS ----------------
@app.post("/books")
def get_books(data: AuthRequest):
    authenticate(data)
    visible = [b for b in books_db if not b["deleted"]]
    return {"books": visible}

@app.post("/books/add")
def add_book(data: BookRequest):
    global book_id_counter
    role = authenticate(data)
    authorize(role, ["admin", "manager"])

    book = {
        "id": book_id_counter,
        "title": data.title,
        "author": data.author,
        "deleted": False
    }
    books_db.append(book)
    log("BOOK_CREATED", data.username, f"Book ID {book_id_counter}")
    book_id_counter += 1
    return {"message": "Book added"}

@app.put("/books/{book_id}")
def update_book(book_id: int, data: BookRequest):
    role = authenticate(data)
    authorize(role, ["admin", "manager"])

    for b in books_db:
        if b["id"] == book_id and not b["deleted"]:
            b["title"] = data.title
            b["author"] = data.author
            log("BOOK_UPDATED", data.username, f"Book ID {book_id}")
            return {"message": "Book updated"}

    raise HTTPException(status_code=404, detail="Book not found")

@app.delete("/books/{book_id}")
def delete_book(book_id: int, data: AuthRequest):
    role = authenticate(data)
    authorize(role, ["admin"])

    for b in books_db:
        if b["id"] == book_id and not b["deleted"]:
            b["deleted"] = True
            log("BOOK_DELETED", data.username, f"Book ID {book_id}")
            return {"message": "Book deleted"}

    raise HTTPException(status_code=404, detail="Book not found")

@app.post("/books/undo/{book_id}")
def undo_delete(book_id: int, data: AuthRequest):
    role = authenticate(data)
    authorize(role, ["admin"])

    for b in books_db:
        if b["id"] == book_id and b["deleted"]:
            b["deleted"] = False
            log("BOOK_RESTORED", data.username, f"Book ID {book_id}")
            return {"message": "Book restored"}

    raise HTTPException(status_code=404, detail="Book not found or not deleted")

# ---------------- ROLES ----------------
@app.put("/users/role")
def change_role(data: RoleUpdateRequest):
    role = authenticate(data)
    authorize(role, ["admin"])

    if data.target_user not in users_db:
        raise HTTPException(status_code=404, detail="User not found")

    old = users_db[data.target_user]["role"]
    users_db[data.target_user]["role"] = data.new_role
    log("ROLE_CHANGED", data.username, f"{data.target_user}: {old} → {data.new_role}")
    return {"message": "Role updated"}

# ---------------- AUDIT ----------------
@app.post("/audit-logs")
def get_logs(data: AuthRequest):
    role = authenticate(data)
    authorize(role, ["admin"])
    return {"logs": audit_logs}
