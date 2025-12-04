from django.urls import path
from .views import (
    task_list,
    create_task,
    task_detail,
    update_task,
    delete_task,
    start_task,
    complete_task,
    cancel_task,
    task_statistics,
    user_statistics,
)

urlpatterns = [
    # Görev listesi
    path('', task_list, name='task-list'),
    
    # Görev CRUD
    path('create/', create_task, name='task-create'),
    path('<int:task_id>/', task_detail, name='task-detail'),
    path('<int:task_id>/update/', update_task, name='task-update'),
    path('<int:task_id>/delete/', delete_task, name='task-delete'),
    
    # Görev durumu değişiklikleri
    path('<int:task_id>/start/', start_task, name='task-start'),
    path('<int:task_id>/complete/', complete_task, name='task-complete'),
    path('<int:task_id>/cancel/', cancel_task, name='task-cancel'),
    
    # İstatistikler
    path('statistics/', task_statistics, name='task-statistics'),
    path('user-statistics/<int:user_id>/', user_statistics, name='user-statistics'),
]