"""
PyLedger Core - Security
Role-based access control for accounting operations
"""

from enum import Enum
from datetime import datetime
from typing import Optional, List


class Role(Enum):
    ADMIN = 'admin'
    ACCOUNTANT = 'accountant'
    AUDITOR = 'auditor'
    VIEWER = 'viewer'
    MANAGER = 'manager'


class Permission(Enum):
    VIEW_ACCOUNTS = 'view_accounts'
    CREATE_ACCOUNTS = 'create_accounts'
    EDIT_ACCOUNTS = 'edit_accounts'
    DELETE_ACCOUNTS = 'delete_accounts'
    POST_ENTRIES = 'post_entries'
    APPROVE_ENTRIES = 'approve_entries'
    VIEW_REPORTS = 'view_reports'
    CLOSE_PERIOD = 'close_period'
    MANAGE_USERS = 'manage_users'
    MANAGE_SETTINGS = 'manage_settings'
    EXPORT_DATA = 'export_data'
    DELETE_ENTRIES = 'delete_entries'


ROLE_PERMISSIONS = {
    Role.ADMIN: list(Permission),
    Role.ACCOUNTANT: [
        Permission.VIEW_ACCOUNTS, Permission.CREATE_ACCOUNTS,
        Permission.EDIT_ACCOUNTS, Permission.POST_ENTRIES,
        Permission.VIEW_REPORTS, Permission.EXPORT_DATA,
    ],
    Role.AUDITOR: [
        Permission.VIEW_ACCOUNTS, Permission.VIEW_REPORTS,
        Permission.EXPORT_DATA,
    ],
    Role.MANAGER: [
        Permission.VIEW_ACCOUNTS, Permission.VIEW_REPORTS,
        Permission.APPROVE_ENTRIES, Permission.EXPORT_DATA,
    ],
    Role.VIEWER: [
        Permission.VIEW_ACCOUNTS, Permission.VIEW_REPORTS,
    ],
}


class User:
    def __init__(self, username: str, role: Role = Role.VIEWER,
                 full_name: str = '', email: str = '',
                 password: str = None, password_hash: str = None):
        self.username = username
        self.role = role
        self.full_name = full_name or username
        self.email = email
        self.created_at = datetime.now()
        self.last_login = None
        self.password_hash = password_hash
        if password is not None:
            self.set_password(password)

    def set_password(self, password: str):
        from pyledger.security.passwords import hash_password
        self.password_hash = hash_password(password)

    def check_password(self, password: str) -> bool:
        if not self.password_hash:
            return True  # backward compat: accounts without password
        from pyledger.security.passwords import verify_password
        return verify_password(password, self.password_hash)

    def has_permission(self, permission: Permission) -> bool:
        return permission in ROLE_PERMISSIONS.get(self.role, [])

    def has_any_permission(self, *permissions: Permission) -> bool:
        return any(self.has_permission(p) for p in permissions)

    def has_all_permissions(self, *permissions: Permission) -> bool:
        return all(self.has_permission(p) for p in permissions)

    def to_dict(self) -> dict:
        return {
            'username': self.username,
            'role': self.role.value,
            'full_name': self.full_name,
            'email': self.email,
        }


class SecurityManager:
    """Central security and access control"""

    def __init__(self):
        self._users = {}
        self._current_user = None
        self._audit_log = []

    def register_user(self, username: str, role: Role = Role.VIEWER,
                      full_name: str = '', email: str = '',
                      password: str = None) -> User:
        if username in self._users:
            raise ValueError(f"User '{username}' already exists")
        user = User(username, role, full_name, email, password=password)
        self._users[username] = user
        return user

    def authenticate(self, username: str, password: str = None) -> Optional[User]:
        user = self._users.get(username)
        if user and password is not None and user.password_hash:
            if not user.check_password(password):
                self._log('DENIED', f"Bad password for '{username}'")
                return None
        if user:
            user.last_login = datetime.now()
            self._current_user = user
            self._log('LOGIN', f"User '{username}' logged in")
        return user

    def get_current_user(self) -> Optional[User]:
        return self._current_user

    def require_permission(self, permission: Permission) -> bool:
        if not self._current_user:
            raise PermissionError("No authenticated user")
        if not self._current_user.has_permission(permission):
            self._log('DENIED', f"User '{self._current_user.username}' denied {permission.value}")
            raise PermissionError(
                f"User '{self._current_user.username}' lacks permission: {permission.value}")
        return True

    def check_permission(self, permission: Permission) -> bool:
        if not self._current_user:
            return False
        return self._current_user.has_permission(permission)

    def get_users_by_role(self, role: Role) -> List[User]:
        return [u for u in self._users.values() if u.role == role]

    def _log(self, action: str, detail: str = ''):
        self._audit_log.append({
            'timestamp': datetime.now().isoformat(),
            'user': self._current_user.username if self._current_user else 'system',
            'action': action,
            'detail': detail,
        })

    def get_audit_log(self) -> list:
        return list(self._audit_log)

    def to_dict(self) -> dict:
        return {
            'users': {k: v.to_dict() for k, v in self._users.items()},
            'current_user': self._current_user.username if self._current_user else None,
        }
