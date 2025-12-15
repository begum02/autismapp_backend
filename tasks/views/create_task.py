from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..models import Task
from ..serializers import TaskSerializer
from django.core.cache import cache
from django.contrib.auth import get_user_model  # ✅ Django'nun standart yolu
import json
import traceback

User = get_user_model()  # ✅ CustomUser modelini al

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_task_view(request):
    """
    Yeni görev oluşturma
    """
    try:
        print("📥 Gelen veri:", request.data)  # ✅ Debug
        
        # ✅ assigned_to kontrolü
        assigned_to_id = request.data.get('assigned_to')
        if not assigned_to_id:
            return Response(
                {'error': 'assigned_to alanı zorunludur'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # ✅ Kullanıcının varlığını kontrol et
        try:
            assigned_user = User.objects.get(id=assigned_to_id)
        except User.DoesNotExist:
            return Response(
                {'error': f'ID {assigned_to_id} ile kullanıcı bulunamadı'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # ✅ created_by'ı manuel ekle (request.data'yı değiştir)
        task_data = request.data.copy()
        task_data['created_by'] = request.user.id
        
        print("📝 İşlenmiş veri:", task_data)  # ✅ Debug
        
        serializer = TaskSerializer(data=task_data)
        
        if serializer.is_valid():
            # ✅ created_by ve assigned_to'yu manuel set et
            task = serializer.save(
                created_by=request.user,
                assigned_to=assigned_user
            )
            
            print(f"✅ Görev oluşturuldu: {task.id}")  # ✅ Debug
            
            # ✅ Redis'e yeni task notification gönder
            cache_key = f'new_task_{task.assigned_to.id}'
            cache.set(cache_key, {
                'task_id': task.id,
                'title': task.title,
                'scheduled_date': str(task.scheduled_date),
                'start_time': str(task.start_time) if task.start_time else None,
                'lottie_animation': task.lottie_animation,
                'created_at': task.created_at.isoformat()
            }, timeout=300)  # 5 dakika
            
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        
        print("❌ Validation hataları:", serializer.errors)  # ✅ Debug
        return Response(
            {
                'errors': serializer.errors,
                'detail': 'Geçersiz veri'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    except Exception as e:
        print(f"❌ Hata: {str(e)}")  # ✅ Debug
        traceback.print_exc()
        
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )