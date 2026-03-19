from rest_framework import serializers
from .models import EmailUsers

class FileUploadSerializer(serializers.Serializer):
    images = serializers.ListField(child=serializers.ImageField(), allow_empty=False, required=False)
    file = serializers.FileField(required=False)

class emailserializer(serializers.ModelSerializer):
    class Meta:
        model = EmailUsers
        fields = '__all__'
        read_only_fields = ['created_at', 'id']