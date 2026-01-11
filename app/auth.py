from typing import Set
from fastapi import Request, HTTPException

from .rbac_data import ROLE_PERMISSIONS, USER_ROLES


class User:
    def __init__(self, username: str, role: str, permissions: Set[str]):
        self.username = username
        self.role = role
        self.permissions = permissions


async def auth_middleware(request: Request, call_next):
    """
    Authentication middleware:
    - Read username from header X-User
    - Look up role and permissions
    - Attach User object to request.state.user
    """
    username = request.headers.get("X-User")
    if not username or username not in USER_ROLES:
        raise HTTPException(status_code=401, detail="Unauthorized: invalid or missing user")

    role = USER_ROLES[username]
    permissions = ROLE_PERMISSIONS.get(role, set())
    request.state.user = User(username, role, permissions)

    response = await call_next(request)
    return response


def require_permissions(*required_permissions: str):
    """
    Authorization dependency:
    - Check that current user has all required_permissions
    """
    def dependency(request: Request):
        user: User = request.state.user
        missing = [p for p in required_permissions if p not in user.permissions]
        if missing:
            raise HTTPException(
                status_code=403,
                detail=f"Forbidden: missing permissions {missing} for user {user.username}",
            )
        return user

    return dependency
