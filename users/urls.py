from django.urls import path
from .views import (
    register, login, logout, profile, update_profile,
    change_password, list_users, user_detail, delete_account
)

app_name = 'users'

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('profile/', profile, name='profile'),
    path('profile/update/', update_profile, name='update_profile'),
    path('password/change/', change_password, name='change_password'),
    path('users/', list_users, name='list_users'),
    path('users/<int:user_id>/', user_detail, name='user_detail'),
    path('account/delete/', delete_account, name='delete_account'),
]