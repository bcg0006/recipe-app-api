"""
Tests for models.
"""
from unittest.mock import patch
from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from core import models

def create_user(email='test@domain.com', password='testpass123'):
    """ Helper function to create a user """
    return get_user_model().objects.create_user(email, password)

class ModelTests(TestCase):
    """ Test the user model """

    def test_create_user_with_email_successful(self):
        """ Test creating a new user with an email is successful """
        email = 'test@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """ Test email is normalized for new users. """
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
        ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raise_error(self):
        """ Test creating user without email raises error """
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'sample123')

    def test_create_new_superuser(self):
        """ Test creating a new superuser """
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123',
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_creating_recipe(self):
        """ Test creating a recipe is successful """
        user = get_user_model().objects.create_user(
            'test@example.com',
            'test123',
            )

        recipe = models.Recipe.objects.create(
            user=user,
            title='Test Recipe',
            time_minutes=5,
            price=Decimal('5.10'),
            description='Test description',
        )

        self.assertEqual(str(recipe), recipe.title)

    def test_create_tag(self):
        """ Test creating a tag """
        tag = models.Tag.objects.create(
            user=create_user(),
            name='Test Tag',
        )

        self.assertEqual(str(tag), tag.name)

    def test_create_ingredient(self):
        """ Test creating an ingredient """
        ingredient = models.Ingredient.objects.create(
            user=create_user(),
            name='Test Ingredient',
        )

        self.assertEqual(str(ingredient), ingredient.name)

    @patch('core.models.uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        """ Test that image is saved in the correct location """
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, 'myimage.jpg')

        exp_path = f'uploads/recipe/{uuid}.jpg'
        self.assertEqual(file_path, exp_path)