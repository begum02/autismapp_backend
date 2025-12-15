from .auth_views import register_view, login_view, logout_view
from .profile_views import profile_view, update_profile_view
from .password_views import change_password_view
from .user_management_views import list_users_view, user_detail_view, delete_account_view

__all__ = [
    'register_view',
    'login_view',
    'logout_view',
    'profile_view',
    'update_profile_view',
    'change_password_view',
    'list_users_view',
    'user_detail_view',
    'delete_account_view',
]