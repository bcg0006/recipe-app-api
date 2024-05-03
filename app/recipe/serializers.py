'''Serializer for our recipe app'''
from rest_framework import serializers
from core.models import Recipe, Tag

class TagSerializer(serializers.ModelSerializer):
    '''Serializer for tag objects'''

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']

class RecipeSerializer(serializers.ModelSerializer):
    '''Serializer for recipe objects'''

    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = [
            'id', 'title', 'time_minutes', 'price',
            'link', 'tags'
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

    def create(self, validated_data):
        '''Create a new recipe'''
        tags = validated_data.pop('tags', []) #remove the tags object from the validated data and store it in tags variable
        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(recipe, tags)

        return recipe

    def update(self, instance, validated_data):
        '''Update a recipe'''
        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(instance, tags)

        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()
        return instance

class RecipeDetailSerializer(RecipeSerializer):
    '''Serializer for recipe detail objects'''

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']
        read_only_fields = ['id']

