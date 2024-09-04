"""Tag serializer module."""
from django.db import IntegrityError

from rest_framework import serializers

from core.models import Tag


class TagSerializer(serializers.ModelSerializer):
    """Tag serializer class."""
    class Meta:
        """Meta class for Tag serializer."""
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']

    def create(self, validated_data):
        """Override create method."""
        try:
            tag = Tag.objects.create(user=self.context['request'].user,
                                     **validated_data)
            return tag
        except IntegrityError:
            raise serializers.ValidationError({'error': 'Bad Request -\
                Integrity constraint violation'})

    def update(self, instance, validated_data):
        validated_data['user'] = self.context['request'].user
        new_instance = super().update(instance, validated_data)
        return new_instance
