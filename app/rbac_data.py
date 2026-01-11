# app/rbac_data.py

# Role -> permissions mapping
ROLE_PERMISSIONS = {
    "admin": {"read_items", "create_items", "delete_items", "manage_permissions"},
    "manager": {"read_items", "create_items"},
    "user": {"read_items"},
}

# Simple user store: username -> role
USER_ROLES = {
    "one": "admin",
    "two": "manager",
    "three": "user",
}