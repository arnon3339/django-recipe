""" Test models module. """
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError

from core.models import Recipe, Tag, Ingredient
from core.models.recipe import recipe_image_file_path

from unittest.mock import patch


class UserModelTest(TestCase):
    """ Test user model class. """
    def test_create_user(self):
        """
            Test create a user.
        """
        user_data = {
            'email': 'arnon@example.com',
            'password': 'sample123'
        }
        user = get_user_model().objects.create_user(
            email=user_data['email'],
            password=user_data['password']
        )

        self.assertEqual(user.email, user_data['email'])
        self.assertTrue(user.check_password(user_data['password']))

    def test_user_email_nomalized(self):
        """ Test email normalization for user. """
        users_data = [
            ('test@Example.com', 'test@example.com'),
        ]

        for user_data in users_data:
            user = get_user_model().objects.create_user(email=user_data[0])
            user.refresh_from_db()
            self.assertEqual(user.email, user_data[1])

    def test_create_superuser(self):
        """ Test create a superuser """
        user_data = {
            'email': 'admin@example.com',
            'password': 'password123'
        }

        user = get_user_model().objects.create_superuser(
            email=user_data['email'],
            password=user_data['password']
            )

        self.assertEqual(user.email, user_data['email'])
        self.assertTrue(user.check_password(user_data['password']))


class RecipeModelTest(TestCase):
    """Test for Recipe model."""
    def setUp(self):
        """Mothod fixture."""
        self.user = get_user_model().objects.create_user(
            name='Test name',
            email='test@example.com',
            password='test1234567890'
        )

    def test_get_recipe(self):
        """Test to get a recipe."""
        payload = {
                'user': self.user,
                'title': 'Test title1',
                'description': 'Test description1',
                'time_minutes': 10,
                'price': 10.50,
                'link': 'www.recipe-test-1.com'
        }
        Recipe.objects.create(**payload)

        recipe = Recipe.objects.get(link=payload['link'])

        recipe_dict = {k: getattr(recipe, k) for k in payload.keys()}

        self.assertEqual(recipe_dict, payload)


class TageModelTest(TestCase):
    """Test for Tage model."""
    @classmethod
    def setUpClass(cls):
        """Setup for the calss test."""
        super().setUpClass()
        user_data = {
            'name': 'Test name',
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        cls.__user = get_user_model().objects.create_user(**user_data)

    def setUp(self):
        """Setup for each test."""
        super().setUp()
        self.__tag_data = {
            'user': self.__user,
            'name': 'Tag1',
        }

    def test_create_tag(self):
        """Test to create a tag."""
        tag = Tag.objects.create(**self.__tag_data)

        for k, v in self.__tag_data.items():
            self.assertEqual(getattr(tag, k), v)

    def test_get_tags(self):
        """Test to get tags."""
        Tag.objects.create(**self.__tag_data)

        tags = Tag.objects.all().order_by('-id')

        for k, v in self.__tag_data.items():
            self.assertEqual(getattr(tags[0], k), v)


class IngredientModelTest(TestCase):
    """TestCase for Ingredient model."""
    def setUp(self):
        super().setUp()
        self.__user = get_user_model().objects.create_user(
            name='Test name',
            email='testuser@exampl.com',
            password='testpass123'
        )
        payload = {
            'user': self.__user,
            'name': 'Salt'
        }
        self.__ingredient = Ingredient.objects.create(
            **payload
        )

    def test_get_no_exists(self):
        """Test get not exists."""
        has_sugar = Ingredient.objects.filter(name='Sugar').exists()
        self.assertFalse(has_sugar)

    def test_get_success(self):
        """Test get with success."""
        has_salt = Ingredient.objects.filter(name='Salt').exists()
        self.assertTrue(has_salt)

    def test_create_raise(self):
        """Test create raise an exception."""
        with self.assertRaises(IntegrityError):
            Ingredient.objects.create(name='Salt')

    def test_create_success(self):
        """Test create with success."""
        salt = Ingredient.objects.create(user=self.__user, name='New Salt')
        self.assertEqual(salt.name, 'New Salt')

    def test_update_raise(self):
        """Test update raise an exception."""
        with self.assertRaises(Ingredient.DoesNotExist):
            sugar = Ingredient.objects.get(name='Sugar')
            sugar.name = 'Sugar 2'
            sugar.save()

    def test_update_success(self):
        """Test update with sucess."""
        salt = Ingredient.objects.get(name='Salt')
        salt.name = 'Salt 2'
        salt.save()
        salt.refresh_from_db()
        self.assertEqual(salt.name, 'Salt 2')

    def test_delete_raise(self):
        """Test delete raise an exception."""
        with self.assertRaises(Ingredient.DoesNotExist):
            Ingredient.objects.get(name='Sugar').delete()

    def test_delete_success(self):
        """Test delete with success."""
        Ingredient.objects.get(name='Salt').delete()
        has_salt = Ingredient.objects.filter(name='Salt').exists()
        self.assertFalse(has_salt)

    @patch('core.models.recipe.uuid.uuid4')
    def test_upload_file_with_mock_success(self, mock_uuid):
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = recipe_image_file_path(None, 'example.jpg')

        self.assertEqual(file_path, 'uploads/recipe/{}.jpg'.format(uuid))
