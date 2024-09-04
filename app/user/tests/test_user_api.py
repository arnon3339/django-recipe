"""Test create user module."""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient


CREATE_USER_URL = reverse('user:create')
TOKEN_USER_URL = reverse('user:token')
ME_USER_URL = reverse('user:me')


def create_user(**params):
    """Create a user function, returning a user."""
    user = get_user_model().objects.create_user(**params)
    return user


class TestCreateUser(TestCase):
    """Test for create user class."""
    def setUp(self):
        self.client = APIClient()

    # @unittest.skip("")
    def test_create_user_success(self):
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test name'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertEqual(user.email, payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_with_email_exists_error(self):
        """Test if existing email."""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test name'
        }
        get_user_model().objects.create(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test if password to short."""
        payload = {
            'email': 'test@example.com',
            'password': '123',
            'name': 'Test name'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Create Token for a user"""
        user_data = {
            'name': "Test name",
            'email': 'test@example.com',
            'password': 'test-user-password123'
        }
        create_user(**user_data)

        payload = {
            'email': 'test@example.com',
            'password': 'test-user-password123'
        }

        res = self.client.post(TOKEN_USER_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_for_invalid_user(self):
        """Create a token for invalid user."""
        user_data = {
            'name': "Test name",
            'email': 'test@example.com',
            'password': 'test-user-password123'
        }
        create_user(**user_data)

        payload = {
            'email': 'test@example.com',
            'password': 'password123'
        }

        res = self.client.post(TOKEN_USER_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_for_nonpassword_user(self):
        """Create a token for empty password user."""
        user_data = {
            'name': "Test name",
            'email': 'test@example.com',
            'password': 'test-user-password123'
        }
        create_user(**user_data)

        payload = {
            'email': 'test@example.com',
            'password': ''
        }

        res = self.client.post(TOKEN_USER_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test authentication is required for users."""
        res = self.client.get(ME_USER_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTest(TestCase):
    """Test API requests that require authentication."""

    def setUp(self):
        self.user = create_user(
            name="Test name",
            email='test@example.com',
            password='test-user-password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user."""
        res = self.client.get(ME_USER_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email
        })

    def test_post_me_not_allowed(self):
        """Test not allowed post method in ME endpoints."""
        res = self.client.post(ME_USER_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test udpating the user."""
        update_payload = {
            'name': 'Updated name',
            'email': 'updated@example.com',
            'password': 'newpass123'
        }

        res = self.client.patch(ME_USER_URL, update_payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, update_payload['name'])
        self.assertEqual(self.user.email, update_payload['email'])
        self.assertTrue(self.user.check_password(update_payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_update_user_confict_email(self):
        """Test updating the user with conficting email."""
        create_user(
            name="Test name2",
            email='test@example2.com',
            password='test-user-password123'
        )
        update_payload = {
            'name': 'Updated name',
            'email': 'test@example2.com',
            'password': 'newpass123'
        }

        res = self.client.patch(ME_USER_URL, update_payload)

        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
