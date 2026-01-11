from typing import Set
from fastapi import FastAPI, Request, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .auth import auth_middleware, require_permissions, User
from .rbac_data import ROLE_PERMISSIONS, USER_ROLES


app = FastAPI(
    title="RBAC FastAPI Demo",
    description="Simple role-based access control with admin-managed roles",
)

# Register middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware("http")(auth_middleware)


# -------- Public/user routes --------

@app.get("/me")
def read_me(request: Request):
    """
    Return current user's identity and permissions.
    """
    user: User = request.state.user
    return {"username": user.username, "role": user.role, "permissions": list(user.permissions)}


@app.get("/items")
def list_items(user: User = Depends(require_permissions("read_items"))):
    """
    Any user with 'read_items' permission can call this.
    """
    return {"items": ["item1", "item2"], "user": user.username}


@app.post("/items")
def create_item(
    name: str = Body(..., embed=True),
    user: User = Depends(require_permissions("create_items")),
):
    """
    Only users with 'create_items' permission (admin, manager) can call this.
    """
    return {"message": f"Item '{name}' created by {user.username}"}


@app.delete("/items/{item_id}")
def delete_item(
    item_id: int,
    user: User = Depends(require_permissions("delete_items")),
):
    """
    Only users with 'delete_items' permission (admin by default) can call this.
    """
    return {"message": f"Item {item_id} deleted by {user.username}"}


# -------- Admin routes --------

class RoleUpdate(BaseModel):
    role: str
    permissions: list[str]


@app.put("/admin/roles")
def update_role_permissions(
    data: RoleUpdate,
    user: User = Depends(require_permissions("manage_permissions")),
):
    """
    Admin can overwrite permissions for a role.
    """
    ROLE_PERMISSIONS[data.role] = set(data.permissions)
    return {
        "message": f"Updated permissions for role '{data.role}'",
        "role_permissions": {r: list(p) for r, p in ROLE_PERMISSIONS.items()},
    }


class UserRoleUpdate(BaseModel):
    username: str
    role: str


@app.put("/admin/users/role")
def update_user_role(
    data: UserRoleUpdate,
    user: User = Depends(require_permissions("manage_permissions")),
):
    """
    Admin can change which role a user has.
    """
    USER_ROLES[data.username] = data.role
    return {"message": f"User '{data.username}' now has role '{data.role}'", "user_roles": USER_ROLES}
