'''Serializer for our recipe app'''
from rest_framework import serializers
from core.models import Recipe, Tag, Ingredient

class TagSerializer(serializers.ModelSerializer):
    '''Serializer for tag objects'''

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']

class IngredientSerializer(serializers.ModelSerializer):
    '''Serializer for ingredient objects'''

    class Meta:
        model = Ingredient
        fields = ['id', 'name']
        read_only_fields = ['id']

class RecipeSerializer(serializers.ModelSerializer):
    '''Serializer for recipe objects'''

    tags = TagSerializer(many=True, required=False)
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = [
            'id', 'title', 'time_minutes', 'price',
            'link', 'tags', 'ingredients',
            ]
        read_only_fields = ['id']

    def _get_or_create_tags(self, instance, tags):
        '''Get or create tags for a recipe'''
        auth_user = self.context['request'].user
        for tag in tags:
            tag, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            instance.tags.add(tag)

    def _get_or_create_ingredients(self, instance, ingredients):
        '''Get or create ingredients for a recipe'''
        auth_user = self.context['request'].user
        for ingredient in ingredients:
            ingredient, created = Ingredient.objects.get_or_create(
                user=auth_user,
                **ingredient,
            )
            instance.ingredients.add(ingredient)

    def create(self, validated_data):
        '''Create a new recipe'''
        tags = validated_data.pop('tags', []) #remove the tags object from the validated data and store it in tags variable
        ingredients = validated_data.pop('ingredients', [])
        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(recipe, tags)
        self._get_or_create_ingredients(recipe, ingredients)

        return recipe

    def update(self, instance, validated_data):
        '''Update a recipe'''
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(instance, tags)

        if ingredients is not None:
            instance.ingredients.clear()
            self._get_or_create_ingredients(instance, ingredients)

        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()
        return instance

class RecipeDetailSerializer(RecipeSerializer):
    '''Serializer for recipe detail objects'''

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description', 'image']
        read_only_fields = ['id']

class RecipeImageSerializer(serializers.ModelSerializer):
    '''Serializer for uploading images to recipes'''

    class Meta:
        model = Recipe
        fields = ['id', 'image']
        read_only_fields = ['id']
        extra_kwargs = {'image': {'required': True}}

