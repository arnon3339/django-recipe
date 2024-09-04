"""Test for Tag serializer module."""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.models import Tag

from rest_framework.test import APIClient
from rest_framework import status


from tag.serializer import TagSerializer


TAG_URL = reverse('tag:tag-list')


UNAUTHENICATED_USER, AUTHENTICATED_USER_1, AUTHENTICATED_USER_2 =\
    (None, None, None)


def setUpModule():
    global UNAUTHENICATED_USER, AUTHENTICATED_USER_1, AUTHENTICATED_USER_2
    """Setup for tag test module."""
    UNAUTHENICATED_USER = get_user_model().objects.create_user(
        name='Some user',
        email='some@example.com',
        password='somepass123'
    )
    AUTHENTICATED_USER_1 = get_user_model().objects.create_user(
        name='Auth user 1',
        email='authuser1@example.com',
        password='userpass123'
    )
    AUTHENTICATED_USER_2 = get_user_model().objects.create_user(
        name='Auth user 1',
        email='authuser2@example.com',
        password='userpass123'
    )


def get_tag_detail_url(tag_id):
    """Return tag detail url by providing tag id."""
    return reverse('tag:tag-detail', args=[tag_id])


class TagSerializerTest(TestCase):
    """Test class for an unauthenticated user."""
    def setUp(self):
        """Setup for Tag serializer test."""
        super().setUp()
        tag_data = {
            'name': 'Tag1',
            'user': AUTHENTICATED_USER_1
        }
        Tag.objects.create(**tag_data)
        self.__client = APIClient()

    def test_get_tag_with_unauthentication(self):
        """Get tag data with an unauthenticated user."""
        res = self.__client.get(TAG_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_with_unauthentication(self):
        """Create tag with an unauthenticated user."""
        res = self.__client.post(TAG_URL, {
            'user': AUTHENTICATED_USER_1,
            'name': 'Tag2',
        })

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagSerializerTest(TestCase):
    """Test class of Tag serializer with authenticated users."""
    def setUp(self):
        """Setup for the test methods."""
        super().setUp()
        self.__client_1 = APIClient()
        self.__client_2 = APIClient()
        self.__client_1.force_authenticate(AUTHENTICATED_USER_1)
        self.__client_2.force_authenticate(AUTHENTICATED_USER_2)

    def test_get_tags_without_user_data(self):
        """Test to get tags."""
        tag_data = {
            'user': AUTHENTICATED_USER_1,
            'name': 'Tag1'
        }
        Tag.objects.create(**tag_data)

        res = self.__client_1.get(TAG_URL)
        tag = Tag.objects.get(name=tag_data['name'])

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for k in tag_data.keys():
            if k != 'user':
                self.assertEqual(res.data[0][k], getattr(tag, k))

    def test_create_success(self):
        """Test successful creating a tag."""
        tag_data = {
            'name': 'Tag1'
        }
        res = self.__client_1.post(TAG_URL, tag_data)
        tag = Tag.objects.get(name=tag_data['name'])
        serializer = TagSerializer(tag)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data, serializer.data)

    def test_partial_update_success(self):
        """Test to update tag with partial data to be successful."""
        orig_tag_data = {
            'name': 'tag'
        }
        new_tag_data = {
            'name': 'new-tag'
        }

        res_create = self.__client_1.post(TAG_URL, orig_tag_data)
        res_update = self.__client_1.patch(get_tag_detail_url(
            res_create.data['id']), new_tag_data)

        get_old_tag = Tag.objects.filter(name=orig_tag_data['name']).exists()
        get_new_tag = Tag.objects.filter(name=new_tag_data['name']).exists()

        self.assertEqual(res_update.status_code, status.HTTP_200_OK)
        self.assertTrue(get_new_tag)
        self.assertFalse(get_old_tag)

    def test_full_update_success(self):
        """Test to update a tag with all data to be fail."""
        orig_tag_data = {
            'name': 'tag'
        }
        new_tag_data = {
            'name': 'new-tag'
        }

        res_create = self.__client_1.post(TAG_URL, orig_tag_data)
        res_update = self.__client_1.put(get_tag_detail_url(
            res_create.data['id']), new_tag_data)

        get_old_tag = Tag.objects.filter(name=orig_tag_data['name']).exists()
        get_new_tag = Tag.objects.filter(name=new_tag_data['name']).exists()

        self.assertEqual(res_update.status_code, status.HTTP_200_OK)
        self.assertTrue(get_new_tag)
        self.assertFalse(get_old_tag)

    def test_delete_success(self):
        """Test to delete a tag to be success."""
        tag_data = {
            'name': 'Tag1'
        }

        tag = Tag.objects.create(user=AUTHENTICATED_USER_1,
                                 name=tag_data['name'])
        res = self.__client_1.delete(get_tag_detail_url(tag.id))
        has_tag = Tag.objects.filter(name=tag_data['name'])

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(has_tag)
