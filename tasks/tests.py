from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from .models import Task

User = get_user_model()

class TaskAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)
        self.task = Task.objects.create(
            user=self.user,
            title='Test Task',
            description='This is a test task.',
            task_type='daily_routine',
            category='hygiene',
            date='2025-12-03',
            start_time='09:00',
            end_time='09:10',
            priority='high',
            difficulty_level='easy'
        )

    def test_create_task(self):
        response = self.client.post('/tasks/create/', {
            'title': 'New Task',
            'description': 'Description of new task',
            'task_type': 'daily_routine',
            'category': 'hygiene',
            'date': '2025-12-04',
            'start_time': '10:00',
            'end_time': '10:30',
            'priority': 'medium',
            'difficulty_level': 'medium'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 2)

    def test_list_my_tasks(self):
        response = self.client.get('/tasks/my-tasks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_task_detail(self):
        response = self.client.get(f'/tasks/{self.task.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.task.title)

    def test_update_task(self):
        response = self.client.put(f'/tasks/{self.task.id}/', {
            'title': 'Updated Task',
            'description': 'Updated description'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Updated Task')

    def test_delete_task(self):
        response = self.client.delete(f'/tasks/{self.task.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Task.objects.count(), 0)

    def test_cancel_task(self):
        response = self.client.post(f'/tasks/{self.task.id}/cancel/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'cancelled')

    def test_complete_task(self):
        response = self.client.post(f'/tasks/{self.task.id}/complete/', {
            'notes': 'Completed successfully',
            'rating': 5
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'completed')

    def test_start_task(self):
        response = self.client.post(f'/tasks/{self.task.id}/start/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'in_progress')

    def test_task_statistics(self):
        response = self.client.get('/tasks/statistics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_tasks', response.data)