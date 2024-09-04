"""Serializer module for ingredient app."""
from django.db import IntegrityError

from core.models import Ingredient

from rest_framework import serializers


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer class for ingredient app."""
    class Meta:
        model = Ingredient
        fields = ['id', 'name']
        read_only_fields = ['id']

    def create(self, validated_data):
        """Overried a create method."""
        try:
            validated_data['user'] = self.context['request'].user
            return super().create(validated_data)
        except IntegrityError:
            raise serializers.ValidationError({'error': 'Bad Request -\
                Integrity constraint violation'})
