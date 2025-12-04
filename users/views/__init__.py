from .auth_views import register, login, logout
from .profile_views import profile, update_profile
from .password_views import change_password
from .user_management_views import list_users, user_detail, delete_account

__all__ = [
    'register',
    'login',
    'logout',
    'profile',
    'update_profile',
    'change_password',
    'list_users',
    'user_detail',
    'delete_account',
]