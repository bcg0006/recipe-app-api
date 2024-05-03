'''test for recipe model'''
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPE_URL = reverse('recipe:recipe-list')

def detail_url(recipe_id):
    """Return recipe detail URL"""
    return reverse('recipe:recipe-detail', args=[recipe_id])

def create_recipe(user, **params):
    """Helper function to create a recipe"""
    defaults = {
        'title': 'Sample recipe',
        'time_minutes': 22,
        'price': Decimal('5.25'),
        'description': 'Sample description',
        'link': 'https://sample.com',
    }
    defaults.update(params)

    recipe = Recipe.objects.create(user= user, **defaults)
    return recipe

def create_user(**params):
    return get_user_model().objects.create_user(**params)

class PublicRecipeApiTests(TestCase):
    """Test unauthenticated recipe API access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateRecipeApiTests(TestCase):
    """Test authenticated recipe API access"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='user@example.com', password='test123')
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes"""
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """Test retrieving recipes for user"""
        user2 = create_user(email='other@example.com',password='testpass')
        create_recipe(user=user2)
        create_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_view_recipe_detail(self):
        """Test viewing a recipe detail"""
        recipe = create_recipe(user=self.user)
        #recipe.tags.add(create_tag(user=self.user))
        #recipe.ingredients.add(create_ingredient(user=self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        "Test creating a recipe"
        payload = {
            'title': 'Chocolate cheesecake',
            'time_minutes': 30,
            'price': Decimal('5.00'),
        }

        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for k,v in payload.items():
            self.assertEqual(v, getattr(recipe, k))
        self.assertEqual(recipe.user, self.user)

    def test_partial_update_recipe(self):
        """Test updating a recipe with patch"""
        original_link = 'https://sample.com/recipedetail'
        recipe = create_recipe(user=self.user, title= 'Sample recipe', link=original_link)

        payload = {'title': 'New recipe title'}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)

    def test_full_update_recipe(self):
        "Test full updated recipe"
        recipe = create_recipe(
            user=self.user, title='Pennes alla Norma',
            time_minutes=212,
            price=Decimal('50.25'),
            description='Sample description1',
            link='https://sample.com')

        payload = {
            'title': 'Spaghetti Carbonara',
            'time_minutes': 25,
            'price': Decimal('5.00'),
            'description': 'Sample description2',
            'link': 'https://sample2.com'
        }

        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        for k,v in payload.items():
            self.assertEqual(v, getattr(recipe, k))
        self.assertEqual(recipe.user, self.user)

    def test_update_recipe_by_other_user(self):
        """Test changing the recipe user result in an error"""
        user2 = create_user(email='user2@example2.com', password='testpass')
        recipe = create_recipe(user=self.user)

        payload = {'user': user2.id}
        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """Test deleting a recipe"""
        recipe = create_recipe(user=self.user)
        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Recipe.objects.filter(id=recipe.id).count(), 0)

    def test_delete_recipe_by_other_user(self):
        """Test deleting a recipe by other user"""
        user2 = create_user(email='user2@example.com', password='testpass')
        recipe = create_recipe(user=user2)
        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

    def test_create_recipe_with_new_tags(self):
        """Test create recipe with new tags"""
        payload = {
            'title': 'Avocado lime cheesecake',
            'time_minutes': 60,
            'price': Decimal('20.00'),
            'tags': [{'name': 'vegan'}, {'name': 'dessert'}]
        }
        res = self.client.post(RECIPE_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user = self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                user= self.user,
                ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_tags(self):
        """Test create recipe with existing tags"""
        tag_indian = Tag.objects.create(user=self.user, name='Indian')
        payload = {
            'title': 'Tandoori chicken',
            'time_minutes': 60,
            'price': Decimal('20.00'),
            'tags': [{'name':'Indian'}, {'name':'Dinner'}]
        }

        res =self.client.post(RECIPE_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(tag_indian, recipe.tags.all())
        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user,
                ).exists()
            self.assertTrue(exists)

    def test_create_tag_on_update(self):
        """Test creating a tag on update"""
        recipe = create_recipe(user=self.user)
        payload = {
            'tags': [{'name':'Dinner'}]
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(user=self.user, name='Dinner')
        self.assertIn(new_tag, recipe.tags.all())

    def test_update_recipe_assign_tag(self):
        """Test assignin an existing tag when updating a recipe"""
        breakfast = Tag.objects.create(user=self.user, name='Breakfast')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(breakfast)

        lunch = Tag.objects.create(user=self.user, name='Lunch')
        payload = {'tags':[{'name':'Lunch'}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(lunch, recipe.tags.all())
        self.assertNotIn(breakfast, recipe.tags.all())

    def test_clear_recipe_tags(self):
        tag = Tag.objects.create(user=self.user, name='Breakfast')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag)

        payload = {'tags':[]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)














