from django.urls import path

from .views.task_notifications import task_notifications_view
from .views.list_tasks import list_tasks_view
from .views.create_task import create_task_view
from .views.task_detail import task_detail_view
from .views.update_task import update_task_view
from .views.delete_task import delete_task_view
from .views.start_task import start_task_view
from .views.complete_task import complete_task_view
from .views.cancel_task import cancel_task_view
from .views.assign_user import assign_user_view
from .views.statistics import user_statistics_view, today_completed_count_view, assignable_users_view

app_name = 'tasks'

urlpatterns = [
    # Task CRUD
    path('', list_tasks_view, name='task-list'),
    path('create/', create_task_view, name='task-create'),
    path('<int:task_id>/', task_detail_view, name='task-detail'),
    path('<int:task_id>/update/', update_task_view, name='task-update'),
    path('<int:task_id>/delete/', delete_task_view, name='task-delete'),
    
    # Task actions
    path('<int:task_id>/start/', start_task_view, name='task-start'),
    path('<int:task_id>/complete/', complete_task_view, name='task-complete'),
    path('<int:task_id>/cancel/', cancel_task_view, name='task-cancel'),
    path('<int:task_id>/assign/', assign_user_view, name='task-assign'),
    
    # Statistics
    path('statistics/<int:user_id>/', user_statistics_view, name='user-statistics'),
    path('today-completed/', today_completed_count_view, name='today-completed'),
    path('assignable-users/', assignable_users_view, name='assignable-users'),
    #notifications
   path('notifications/', task_notifications_view, name='task-notifications'),  # ✅ Yeni
]