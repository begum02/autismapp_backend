from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'

class TaskCompletionSerializer(serializers.Serializer):
    notes = serializers.CharField(required=False)
    rating = serializers.IntegerField(required=False, min_value=1, max_value=5)