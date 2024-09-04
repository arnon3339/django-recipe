"""Recipe serializer module."""
from django.db.utils import IntegrityError

from rest_framework import serializers

from core.models import Recipe, Tag, Ingredient
from tag.serializer import TagSerializer
from ingredient.serializer import IngredientSerializer


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer of Recipe Model without a decription field."""
    tags = TagSerializer(many=True, required=False)
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        """Meta class for RecipeSerializer."""
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link',
                  'tags', 'ingredients']
        read_only_fields = ['id']


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer of Recipe Model."""
    class Meta(RecipeSerializer.Meta):
        """Meta class for RecipeDetailSerializer."""
        fields = RecipeSerializer.Meta.fields + ['description', 'image']

    def create(self, validated_data):
        """Override a create method."""
        try:
            user = self.context['request'].user
            tag_list = validated_data.pop('tags', [])
            ingredient_list = validated_data.pop('ingredients', [])
            recipe = Recipe.objects.create(user=user, **validated_data)
            if tag_list:
                for tag in tag_list:
                    tag_obj, _ = Tag.objects.get_or_create(
                        user=user, **tag)
                    recipe.tags.add(tag_obj)
                recipe.save()

            if ingredient_list:
                for ingredient in ingredient_list:
                    ingredient_obj, _ = Ingredient.objects.get_or_create(
                        user=user,
                        **ingredient
                        )
                    recipe.ingredients.add(ingredient_obj)
                recipe.save()
            return recipe
        except IntegrityError:
            raise serializers.ValidationError({'error': 'Bad Request -\
                Integrity constraint violation'})

    def update(self, instance, validated_data):
        user = self.context['request'].user
        tags = validated_data.pop('tags', [])
        ingredeints = validated_data.pop('ingredients', [])
        recipe = super().update(instance, validated_data)
        if tags:
            for tag in tags:
                tag_obj, _ = Tag.objects.get_or_create(user=user,
                                                       **tag)
                recipe.tags.add(tag_obj)
            recipe.save()
        if ingredeints:
            for ingredient in ingredeints:
                ingredient_obj, _ = Ingredient.\
                    objects.get_or_create(user=user, **ingredient)
                recipe.ingredients.add(ingredient_obj)
            recipe.save()
        return recipe


class ImageSerializer(serializers.ModelSerializer):
    """Image serializer class."""
    class Meta:
        """Meta class for ImageSerializer."""
        model = Recipe
        fields = ['id', 'image']
        read_only_fields = ['id']
        extra_kwargs = {'image': {'required': 'True'}}
