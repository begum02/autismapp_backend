from .list_tasks import list_my_tasks_view
from .list_tasks import list_managed_tasks_view
from .create_task import create_task_view
from .task_detail import task_detail_view
from .update_task import update_task_view
from .delete_task import delete_task_view
from .start_task import start_task_view
from .complete_task import complete_task_view
from .cancel_task import cancel_task_view
from .assign_user import assign_user_view
from .statistics import (
    user_statistics_view,
    today_completed_count_view,
    assignable_users_view
)

__all__ = [
    'list_my_tasks_view',
    'list_managed_tasks_view',
    'create_task_view',
    'task_detail_view',
    'update_task_view',
    'delete_task_view',
    'start_task_view',
    'complete_task_view',
    'cancel_task_view',
    'assign_user_view',
    'user_statistics_view',
    'today_completed_count_view',
    'assignable_users_view',
]