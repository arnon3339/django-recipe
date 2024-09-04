"""Test for Recipe serializer API."""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from core.models import Recipe, Tag, Ingredient
from recipe.serializer import RecipeSerializer, RecipeDetailSerializer

from rest_framework.test import APIClient
from rest_framework import status


RECIPE_URL = reverse('recipe:recipe-list')


def get_detail_url(recipe_id: int) -> str:
    """Get a recipe detail url

    Args:
        recipe_id (int): pk of Recipe model

    Returns:
        str: recipe detail url
    """
    return reverse('recipe:recipe-detail', args=[recipe_id])


class RecipeSerializerTest(TestCase):
    """Test class of Recipe serializer."""

    @classmethod
    def setUpClass(cls):
        """Setup for the test class."""
        super().setUpClass()
        cls.__client = APIClient()
        cls.__user = get_user_model().objects.create_user(
            name='Test name',
            email='test@example.com',
            password='test1234567890'
        )

    def test_get_recipes_with_unauthentication(self):
        """Get a recipes with anauthenticated user."""
        res = self.__client.get(RECIPE_URL)
        Recipe.objects.bulk_create([
            Recipe(
                user=self.__user,
                title='Test title{}'.format(i + 1),
                description='Test description{}'.format(i + 1),
                time_minutes=10 * (i + 1),
                price=10 * (i + 1) + 0.50,
                link='www.recipe-test-{}.com'.format(i + 1)
            ) for i in range(3)
        ])

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateSerializerTest(TestCase):
    """Test class of Recipe serializer with an authenticated user."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.__client = APIClient()
        cls.__user = get_user_model().objects.create_user(
            name='Test name',
            email='test@example.com',
            password='test1234567890'
        )
        cls.__client.force_authenticate(cls.__user)

    def test_get_recipes(self):
        """Get a recipes."""
        recipes = Recipe.objects.bulk_create([
            Recipe(
                user=self.__user,
                title='Test title{}'.format(i + 1),
                description='Test description{}'.format(i + 1),
                time_minutes=10 * (i + 1),
                price=10 * (i + 1) + 0.50,
                link='www.recipe-test-{}.com'.format(i + 1)
            ) for i in range(3)
        ])

        res = self.__client.get(RECIPE_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe(self):
        """Test to get a recipe."""
        Recipe.objects.bulk_create([
            Recipe(
                user=self.__user,
                title='Test title{}'.format(i + 1),
                description='Test description{}'.format(i + 1),
                time_minutes=10 * (i + 1),
                price=10 * (i + 1) + 0.50,
                link='www.recipe-test-{}.com'.format(i + 1)
            ) for i in range(3)
        ])

        recipes = Recipe.objects.all().order_by('-id')
        res = self.__client.get(get_detail_url(recipes[0].id))
        serializer = RecipeDetailSerializer(recipes[0])

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Test to create a new recipe."""
        res = self.__client.post(RECIPE_URL, {
            'title': 'Test title0',
            'time_minutes': 10,
            'price': 10.50,
        })

        recipe = Recipe.objects.get(user=self.__user)
        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_with_tags_success(self):
        """Test to get a recipe with tags to be successfull."""
        recipe_data = {
            'user': self.__user,
            'title': 'Test title',
            'time_minutes': 10,
            'price': 10.50,
            'tags': ['Tag1', 'Tag2']
        }

        tags = Tag.objects.bulk_create([
            Tag(user=self.__user, name=i) for i in recipe_data['tags']
        ])

        recipe = Recipe.objects.create(**{k: v for k, v in
                                          recipe_data.items() if k != 'tags'})
        recipe.tags.set(tags)
        recipe.save()
        recipe = Recipe.objects.get(user=self.__user)
        serializer = RecipeDetailSerializer(recipe)

        res = self.__client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for k in res.data[0].keys():
            if k == 'tags':
                ser_tags = serializer.data['tags']
                for ser_tag, res_tag in zip(ser_tags, res.data[0]['tags']):
                    self.assertEqual(res_tag['id'], ser_tag['id'])
            self.assertEqual(res.data[0][k], serializer.data[k])

    def test_create_recipe_with_tags_success(self):
        """Test to create a new recipe with tags data to be successful."""
        recipe_data = {
            'title': 'Test title',
            'time_minutes': 10,
            'price': 10.50,
            'tags': ['Tag1', 'Tag2']
        }

        res = self.__client.post(RECIPE_URL, recipe_data)

        recipe = Recipe.objects.get(user=self.__user)
        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        for k in res.data.keys():
            if k == 'tags':
                ser_tags = serializer.data['tags']
                for ser_tag, res_tag in zip(ser_tags, res.data['tags']):
                    self.assertEqual(res_tag['id'], ser_tag['id'])
            self.assertEqual(res.data[k], serializer.data[k])

    def test_create_recipe_with_tags_fail(self):
        """Test to create a new recipe with tags data to be fail."""
        new_recipe_data = {
            'title': 'Test title',
            'time_minutes': 10,
            'price': 10.50,
            'tags': [{'name': 'Tag1'}, {'name': 'Tag2 new'}]
        }

        # res_old = self.__client.post(RECIPE_URL, recipe_data, format='json')
        res = self.__client.post(RECIPE_URL, new_recipe_data, format='json')
        recipe = Recipe.objects.get(user=self.__user)
        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        for k in res.data.keys():
            if k == 'tags':
                ser_tags = serializer.data['tags']
                for ser_tag, res_tag in zip(ser_tags, res.data['tags']):
                    self.assertEqual(res_tag['id'], ser_tag['id'])
            self.assertEqual(res.data[k], serializer.data[k])

    def test_update_recipe_with_new_tags_success(self):
        """Test to update recipe with tags data to be successful."""
        recipe_data = {
            'title': 'Test title',
            'time_minutes': 10,
            'price': 10.50,
            'tags': [{'name': 'Tag1'}, {'name': 'Tag2'}]
        }

        new_recipe_data = {
            'title': 'Test new title',
            'price': 11.50,
            'tags': [{'name': 'Tag1'}, {'name': 'Tag2 new'}]
        }

        check_recipe_data = {
            'title': 'Test new title check',
            'time_minutes': 10,
            'price': 11.50,
            'tags': [{'name': 'Tag1'}, {'name': 'Tag2'}, {'name': 'Tag2 new'}]
        }

        res_create = self.__client.post(RECIPE_URL, recipe_data, format='json')

        res_update = self.__client.patch(get_detail_url(res_create.data['id']),
                                         new_recipe_data, format='json')
        res_check = self.__client.post(RECIPE_URL, check_recipe_data,
                                       format='json')

        recipe = Recipe.objects.get(id=res_create.data['id'])
        serializer = RecipeDetailSerializer(recipe)
        recipe_check = Recipe.objects.get(id=res_check.data['id'])
        serializer_check = RecipeDetailSerializer(recipe_check)

        self.assertEqual(res_update.status_code, status.HTTP_200_OK)
        for k_orig, k_check in zip(serializer.data.keys(),
                                   serializer_check.data.keys()):
            if k_orig != 'id' and k_orig != 'title':
                self.assertEqual(serializer.data[k_orig],
                                 serializer_check.data[k_check])

    def test_update_full_recipe_with_new_tags_fail(self):
        """Test to update a recipe with full data to be fail."""
        recipe_data = {
            'title': 'Test title',
            'time_minutes': 10,
            'price': 10.50,
            'tags': [{'name': 'Tag1'}, {'name': 'Tag2'}]
        }

        new_recipe_data = {
            'title': 'Test new title',
            'price': 11.50,
            'tags': [{'name': 'Tag1'}, {'name': 'Tag2 new'}]
        }

        res_create = self.__client.post(RECIPE_URL, recipe_data, format='json')

        res_update = self.__client.put(get_detail_url(res_create.data['id']),
                                       new_recipe_data, format='json')

        self.assertEqual(res_update.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_full_recipe_with_new_tags_success(self):
        """Test to update a recipe with full data to be success."""
        recipe_data = {
            'title': 'Test title',
            'time_minutes': 10,
            'price': 10.50,
            'tags': [{'name': 'Tag1'}, {'name': 'Tag2'}]
        }

        new_recipe_data = {
            'title': 'Test new title',
            'time_minutes': 11,
            'price': 11.50,
            'tags': [{'name': 'Tag1'}, {'name': 'Tag2 new'}]
        }

        res_create = self.__client.post(RECIPE_URL, recipe_data, format='json')

        res_update = self.__client.put(get_detail_url(res_create.data['id']),
                                       new_recipe_data, format='json')

        recipe = Recipe.objects.get(id=res_create.data['id'])
        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res_update.status_code, status.HTTP_200_OK)
        for k in res_update.data.keys():
            if k == 'tags':
                ser_tags = serializer.data['tags']
                for ser_tag, res_tag in zip(ser_tags, res_update.data['tags']):
                    self.assertEqual(res_tag['id'], ser_tag['id'])
            self.assertEqual(res_update.data[k], serializer.data[k])

    def test_delete_recipe_success(self):
        """Test to delete recipe with success."""
        recipe_data = {
            'title': 'Test title',
            'time_minutes': 10,
            'price': 10.50,
            'tags': [{'name': 'Tag1'}, {'name': 'Tag2'}]
        }

        res_create = self.__client.post(RECIPE_URL, recipe_data, format='json')
        res_delete = self.__client.delete(
            get_detail_url(res_create.data['id'])
            )

        self.assertEqual(res_delete.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_recipe_with_ingredients_success(self):
        """Test to get recipes with ingredients with sucess."""
        recipe_data = {
            'title': 'Test title',
            'time_minutes': 10,
            'price': 10.50,
            'tags': [{'name': 'Tag1'}, {'name': 'Tag2'}],
            'ingredients': [{'name': 'Salt'}, {'name': 'Sugar'}]
        }

        tags = Tag.objects.bulk_create(
            Tag(user=self.__user, name=tag['name'])
            for tag in recipe_data['tags']
        )
        ingredients = Ingredient.objects.bulk_create(
            Ingredient(user=self.__user, name=ingredient['name'])
            for ingredient in recipe_data['ingredients']
        )
        recipe_data
        recipe = Recipe.objects.create(
            user=self.__user, **{k: v for k, v in recipe_data.items()
                                 if k != 'tags' and k != 'ingredients'})
        recipe.tags.set(tags)
        recipe.ingredients.set(ingredients)
        recipe.save()
        recipe.refresh_from_db()

        res = self.__client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        for k, v in recipe_data.items():
            if k != 'tags' and k != 'ingredients':
                self.assertEqual(res.data[0][k], v
                                 if not isinstance(v, float)
                                 else '{:.2f}'.format(v))
            else:
                for d_i in range(len(v)):
                    self.assertEqual(res.data[0][k][d_i]['name'],
                                     v[d_i]['name'])

    def test_create_recipe_with_ingredients_tags_success(self):
        """Test to create a recipe with ingredient and tag data
        to be successful."""
        recipe_data = {
            'title': 'Test title',
            'time_minutes': 10,
            'price': 10.50,
            'tags': [{'name': 'Tag1'}, {'name': 'Tag2'}],
            'ingredients': [{'name': 'Salt'}, {'name': 'Sugar'}]
        }
        res_create = self.__client.post(RECIPE_URL, recipe_data, format='json')
        res_get = self.__client.get(RECIPE_URL)

        self.assertEqual(res_create.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res_get.status_code, status.HTTP_200_OK)

        for k, v in recipe_data.items():
            if k != 'tags' and k != 'ingredients':
                self.assertEqual(res_get.data[0][k], v
                                 if not isinstance(v, float)
                                 else '{:.2f}'.format(v))
            else:
                for d_i in range(len(v)):
                    self.assertEqual(res_get.data[0][k][d_i]['name'],
                                     v[d_i]['name'])

    def test_udpate_recipe_with_ingredients_tags_success(self):
        """Test to update a recipe with new data."""
        old_recipe_data = {
            'title': 'Test title',
            'time_minutes': 10,
            'price': 10.50,
            'tags': [{'name': 'Tag1'}, {'name': 'Tag2'}],
            'ingredients': [{'name': 'Salt'}, {'name': 'Sugar'}]
        }
        new_recipe_data = {
            'title': 'Test title new',
            'time_minutes': 11,
            'price': 11.50,
            'tags': [{'name': 'Tag1'}, {'name': 'Tag2 new'}],
            'ingredients': [{'name': 'Salt'}, {'name': 'Sugar new'}]
        }

        new_tags_ingredients = {
            'tags':
                [{'name': 'Tag1'}, {'name': 'Tag2'}, {'name': 'Tag2 new'}],
            'ingredients':
                [{'name': 'Salt'}, {'name': 'Sugar'}, {'name': 'Sugar new'}],
        }

        res_create = self.__client.post(RECIPE_URL, old_recipe_data,
                                        format='json')
        res = self.__client.put(get_detail_url(res_create.data['id']),
                                new_recipe_data, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        for k, v in new_recipe_data.items():
            if k != 'tags' and k != 'ingredients':
                self.assertEqual(res.data[k], v
                                 if not isinstance(v, float)
                                 else '{:.2f}'.format(v))
            else:
                for d_i in range(len(v)):
                    self.assertEqual(res.data[k][d_i]['name'],
                                     new_tags_ingredients[k][d_i]['name'])

    def test_delete_recipe_with_ingredients_tags_success(self):
        """Test to delete a recipe with ingredients and tags
        to be successful."""
        recipe_data = {
            'title': 'Test title',
            'time_minutes': 10,
            'price': 10.50,
            'tags': [{'name': 'Tag1'}, {'name': 'Tag2'}],
            'ingredients': [{'name': 'Salt'}, {'name': 'Sugar'}]
        }
        res_create = self.__client.post(RECIPE_URL, recipe_data,
                                        format='json')
        res = self.__client.delete(get_detail_url(res_create.data['id']))

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
