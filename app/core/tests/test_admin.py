""" Test for admin page. """
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminTest(TestCase):
    """ Admin test class. """
    def setUp(self) -> None:
        self.client = Client()
        admin = {
            'email': 'arnon@example.com',
            'password': '123'
        }
        self.admin = get_user_model().objects.create_superuser(
            email=admin['email'],
            password=admin['password']
        )

        self.client.force_login(self.admin)

        user = {
            'email': 'arnon3339@example.com',
            'password': '123',
            'name': 'Test user'
        }
        self.user = get_user_model().objects.create_user(
            email=user['email'],
            password=user['password'],
            name=user['name']
        )

        return super().setUp()

    def test_users_list(self):
        """ Test that uses are listed on a page. """
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_edit_admin_page(self):
        """Test that edit page of admin work"""
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """Test the create user page works."""
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
