from django.urls import path
from .views.auth_views import register_view, login_view, logout_view
from .views.profile_views import profile_view, update_profile_view
from .views.password_views import change_password_view
from .views.user_management_views import list_users_view, user_detail_view, delete_account_view

app_name = 'users'

urlpatterns = [
    # Auth endpoints
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    
    # Profile endpoints
    path('profile/', profile_view, name='profile'),
    path('profile/update/', update_profile_view, name='update_profile'),
    
    # Password endpoints
    path('password/change/', change_password_view, name='change_password'),
    
    # User management endpoints
    path('list/', list_users_view, name='list_users'),
    path('<int:user_id>/', user_detail_view, name='user_detail'),
    path('account/delete/', delete_account_view, name='delete_account'),
]