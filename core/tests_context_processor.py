from unittest import mock

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .context_processors import unread_threads


class ChatContextProcessorTest(TestCase):
    def setUp(self):
        # No need to set cache seen for test user.
        patcher_cache = mock.patch('core.middleware.cache')
        self.mock_cache = patcher_cache.start()
        self.addCleanup(patcher_cache.stop)
        # Create usual user.
        test_user = User.objects.create_user(username='testuser',
                                             password='12345')
        test_user.save()

    def test_context_processor_unread_threads(self):
        resp = self.client.get(reverse('core:user_list'))
        request = resp.wsgi_request
        result = unread_threads(request)
        self.assertEqual(result, {'threads': [], 'unread_threads': 0})

        self.client.login(username='testuser', password='12345')
        resp = self.client.get(reverse('core:user_list'))
        request = resp.wsgi_request
        result = unread_threads(request)
        self.assertEqual(result, {'threads': [], 'unread_threads': 0})
