# backend/tasks/views/today_completed_count.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ..models import Task
from datetime import date

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def today_completed_count_view(request):
    user = request.user
    today = date.today()
    count = Task.objects.filter(
        assigned_to=user,
        scheduled_date=today,
        status='completed'
    ).count()
    return Response({'count': count})