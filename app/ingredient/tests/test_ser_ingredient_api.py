from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from core.models import Ingredient
from ingredient.serializer import IngredientSerializer

from rest_framework.test import APIClient
from rest_framework import status

import random

INGREDIENT_URL = reverse('ingredient:ingredient-list')


def get_ingredient_detail(ingredient_id):
    return reverse('ingredient:ingredient-detail', args=[ingredient_id])


def create_new_ingredient(user, payload):
    """Create a new ingredient function."""
    return Ingredient.objects.create(user=user, **payload)


class IngredientTest(TestCase):
    """TestCase for Ingredient app."""
    def test_get_ingredient_list_with_unauthenticated_user(self):
        """Test to get a gredient list with invalid user."""
        client = APIClient()
        res = client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientTest(TestCase):
    """TestCase for Private Ingredient app."""
    def setUp(self):
        super().setUp()
        self.__user_1 = get_user_model().objects.create_user(
            name='Test name 1',
            email="testuser1@example.com",
            password='test1pass123'
        )
        self.__user_2 = get_user_model().objects.create_user(
            name='Test name 2',
            email="testuser2@example.com",
            password='test2pass123'
        )
        self.__client_1 = APIClient()
        self.__client_1.force_authenticate(self.__user_1)
        self.__client_2 = APIClient()
        self.__client_2.force_authenticate(self.__user_2)

    def test_get_ingredient_with_success(self):
        """Test to get ingredient list with success."""
        payload = {
            'name': 'Salt'
        }
        create_new_ingredient(self.__user_1, payload)

        res = self.__client_1.get(INGREDIENT_URL)

        ingredeints = Ingredient.objects.all().order_by('name')
        serializer = IngredientSerializer(ingredeints, many=True)

        for res_data, ingredient_data in zip(res.data, serializer.data):
            for k in res_data.keys():
                self.assertEqual(res_data[k], ingredient_data[k])

    def test_get_ingredient_belong_to_user_with_success(self):
        """Test to get ingredient list that belongs to specific user."""
        payload_user1 = {
            'name': 'Salt user 1'
        }
        payload_user2 = {
            'name': 'Salt user 2'
        }

        create_new_ingredient(self.__user_1, payload_user1)
        create_new_ingredient(self.__user_2, payload_user2)

        res_1 = self.__client_1.get(INGREDIENT_URL)
        res_2 = self.__client_2.get(INGREDIENT_URL)

        ingredeints_1 = Ingredient.objects.filter(user=self.__user_1)\
            .order_by('name')
        serializer_1 = IngredientSerializer(ingredeints_1, many=True)
        ingredeints_2 = Ingredient.objects.filter(user=self.__user_2)\
            .order_by('name')
        serializer_2 = IngredientSerializer(ingredeints_2, many=True)

        for res_data, ingredient_data in zip(res_1.data, serializer_1.data):
            for k in res_data.keys():
                self.assertEqual(res_data[k], ingredient_data[k])

        for res_data, ingredient_data in zip(res_2.data, serializer_2.data):
            for k in res_data.keys():
                self.assertEqual(res_data[k], ingredient_data[k])

    def test_create_ingredient_success(self):
        """Test to create an ingredient with success."""
        payload = {
            'name': 'Salt'
        }
        res = self.__client_1.post(INGREDIENT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        for k in payload.keys():
            if k == 'name':
                self.assertEqual(res.data[k], payload[k])

    def test_create_ingredient_icase_error(self):
        """Test to create the same object with fail."""
        payload_1 = {
            'name': 'Salt'
        }

        payload_2 = {
            'name': 'Salt'
        }
        self.__client_1.post(INGREDIENT_URL, payload_1)
        res = self.__client_1.post(INGREDIENT_URL, payload_2)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_ingredient_success(self):
        """Test to update an ingredeint."""
        ingredient = create_new_ingredient(self.__user_1, {
            'name': 'Salt'
        })

        res = self.__client_1.patch(get_ingredient_detail(ingredient.id), {
            'name': 'Sugar'
        })

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['name'], 'Sugar')

    def test_delete_ingredient_success(self):
        ingredient = create_new_ingredient(self.__user_1, {
            'name': 'Salt'
        })

        res = self.__client_1.delete(get_ingredient_detail(ingredient.id))

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_ingredients_with_ids_success(self):
        """Test to get ingredients by prividing ids parmas."""
        ingredient_data = [
            {
                'name': 'Ingredient{}'.format(i)
            }
            for i in range(10)
        ]
        res_list = [
            self.__client_1.post(INGREDIENT_URL, ingredient_data[i])
            for i in range(len(ingredient_data))
        ]

        ingredient_res_data_ids = random.sample([
            res_list[i].data['id'] for i in range(len(res_list))
        ], 3)

        ingredient_res_data_ids.sort()

        ingredients_serializers = [
            IngredientSerializer(Ingredient.objects.get(id=id_i))
            for id_i in ingredient_res_data_ids
        ]

        params = {'id': ','.join([str(id_i)
                                  for id_i in ingredient_res_data_ids])}

        res = self.__client_1.get(INGREDIENT_URL, params)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for i in range(len(res.data)):
            self.assertEqual(res.data[i], ingredients_serializers[i].data)

    def test_get_ingredients_with_name_success(self):
        """Test to get ingredients by prividing name parmas."""
        ingredient_data = [
            {
                'name': 'Ingredient{}'.format(i)
            }
            for i in range(10)
        ]
        res_list = [
            self.__client_1.post(INGREDIENT_URL, ingredient_data[i])
            for i in range(len(ingredient_data))
        ]

        ingredient_res_data_names = random.sample([
            res_list[i].data['name'] for i in range(len(res_list))
        ], 3)

        ingredient_res_data_names.sort()

        ingredients_serializers = [
            IngredientSerializer(Ingredient.objects.get(name=name_i))
            for name_i in ingredient_res_data_names
        ]

        params = {'name': ','.join(ingredient_res_data_names)}

        res = self.__client_1.get(INGREDIENT_URL, params)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for i in range(len(res.data)):
            self.assertEqual(res.data[i], ingredients_serializers[i].data)
