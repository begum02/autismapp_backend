from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from tasks.models import Task
from tasks.serializers import TaskSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_task(request):
    """
    Yeni görev oluşturma
    """
    serializer = TaskSerializer(data=request.data)
    
    if serializer.is_valid():
        # Eğer assigned_to belirtilmemişse, mevcut kullanıcıya ata
        if 'assigned_to' not in request.data:
            serializer.save(created_by=request.user, assigned_to=request.user)
        else:
            serializer.save(created_by=request.user)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)