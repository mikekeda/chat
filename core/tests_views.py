from unittest import mock

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.conf import settings
from django.test import TestCase


class ChatViewTest(TestCase):
    def setUp(self):
        # No need to set cache seen for tests users for testing views.
        view_patcher_cache = mock.patch('core.middleware.cache')
        self.mock_cache = view_patcher_cache.start()
        self.addCleanup(view_patcher_cache.stop)
        # Create usual user.
        test_user = User.objects.create_user(username='testuser',
                                             password='12345')
        test_user.save()
        test_user2 = User.objects.create_user(username='testuser2',
                                              password='12345')
        test_user2.save()

    # Pages available for anonymous.
    def test_views_user_list(self):
        resp = self.client.get(reverse('core:user_list'))
        self.assertRedirects(resp, '/login?next=/')
        self.client.login(username='testuser', password='12345')
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'user_list.html')

    def test_views_login(self):
        resp = self.client.get(reverse('core:login'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'login.html')

        # Try to login again (fail).
        self.client.login(username='testuser', password='12345')
        resp = self.client.get(reverse('core:login'))
        self.assertRedirects(resp, settings.LOGIN_REDIRECT_URL)

    def test_views_signup(self):
        resp = self.client.get(reverse('core:signup'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'signup.html')

        # Try to login again (fail).
        self.client.login(username='testuser', password='12345')
        resp = self.client.get(reverse('core:signup'))
        self.assertRedirects(resp, settings.LOGIN_REDIRECT_URL)

    def test_views_logout(self):
        resp = self.client.get(reverse('core:logout'))
        self.assertRedirects(resp, '/login?next=/logout')
        self.client.login(username='testuser', password='12345')
        resp = self.client.get(reverse('core:logout'))
        self.assertRedirects(resp, reverse('core:login'))

    # Pages available only for registered users.
    def test_views_user(self):
        resp = self.client.get(reverse('core:user',
                                       kwargs={'username': 'testuser'}))
        self.assertRedirects(resp, '/login?next=/user/testuser')
        self.client.login(username='testuser', password='12345')
        resp = self.client.get(reverse('core:user',
                                       kwargs={'username': 'testuser'}))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'profile.html')

    def test_views_update_profile(self):
        resp = self.client.post(
            reverse('core:update_profile'),
            {'first_name': 'test1'}
        )
        self.assertRedirects(resp, '/login?next=/update-profile')
        self.client.login(username='testuser', password='12345')
        # Need to create profile for the users.
        resp = self.client.get(reverse('core:user',
                                       kwargs={'username': 'testuser'}))
        self.assertEqual(resp.status_code, 200)

        # Change first name.
        resp = self.client.post(
            reverse('core:update_profile'),
            {'name': 'first_name', 'value': 'test name'}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertJSONEqual(
            str(resp.content, encoding='utf8'),
            {'success': True}
        )
        user = User.objects.get(username='testuser')
        self.assertEqual(user.first_name, 'test name')

        # Change last name.
        resp = self.client.post(
            reverse('core:update_profile'),
            {'name': 'last_name', 'value': 'test last name'}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertJSONEqual(
            str(resp.content, encoding='utf8'),
            {'success': True}
        )
        user = User.objects.get(username='testuser')
        self.assertEqual(user.last_name, 'test last name')

        # Change email.
        resp = self.client.post(
            reverse('core:update_profile'),
            {'name': 'email', 'value': 'myemail2@test.com'}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertJSONEqual(
            str(resp.content, encoding='utf8'),
            {'success': True}
        )
        user = User.objects.get(username='testuser')
        self.assertEqual(user.email, 'myemail2@test.com')

        # Change not existing field (fail).
        resp = self.client.post(
            reverse('core:update_profile'),
            {'name': 'dummy_field', 'value': 'dummy_value'}
        )
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(
            str(resp.content, encoding='utf8'),
            '"You can\'t change this field"'
        )

    def test_views_chat(self):
        resp = self.client.get(reverse('core:chat',
                                       kwargs={'username': 'testuser2'}))
        self.assertRedirects(resp, '/login?next=/chat/testuser2')

        # Go to chat page.
        self.client.login(username='testuser', password='12345')
        resp = self.client.get(reverse('core:chat',
                                       kwargs={'username': 'testuser2'}))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'thread.html')

        # Try to open the thread by id (our test tred have id 1)
        resp = self.client.get(reverse('core:thread',
                                       kwargs={'thread_id': '1'}))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'thread.html')

        # Tread with id 2 doesn't exists.
        resp = self.client.get(reverse('core:thread',
                                       kwargs={'thread_id': '2'}))
        self.assertEqual(resp.status_code, 404)

    def test_views_call(self):
        resp = self.client.get(reverse('core:call',
                                       kwargs={'username': 'testuser2'}))
        self.assertRedirects(resp, '/login?next=/call/testuser2')

        # Go to chat page.
        self.client.login(username='testuser', password='12345')
        resp = self.client.get(reverse('core:call',
                                       kwargs={'username': 'testuser2'}))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'call.html')
