from rest_framework import serializers
from .models import Process

class ProcessSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Process
        fields = ['process_type', 'is_public', 'access_password_hash']
        extra_kwargs = {
            'access_password_hash': {'write_only': True, 'required': False},
        }

    def validate(self, data):
        if not data.get('is_public', True) and not data.get('access_password_hash'):
            raise serializers.ValidationError("Private process must have a password.")
        return data
 