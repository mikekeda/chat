from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from core.context_processors import unread_threads
from core.models import Thread, UnreadThread

User = get_user_model()


class ChatContextProcessorTest(TestCase):
    def setUp(self):
        # No need to set cache seen for test user.
        patcher_cache = mock.patch("core.middleware.cache")
        self.mock_cache = patcher_cache.start()
        self.addCleanup(patcher_cache.stop)
        # Create usual user.
        self.password = User.objects.make_random_password()
        self.test_user = User.objects.create_user(
            username="testuser", password=self.password
        )
        self.test_user.save()

    def test_context_processor_unread_threads(self):
        # Anonymous user.
        resp = self.client.get(reverse("core:user_list"))
        request = resp.wsgi_request
        result = unread_threads(request)
        self.assertEqual(result, {"threads": [], "unread_threads": 0})

        # Regular user.
        self.client.login(username="testuser", password=self.password)
        resp = self.client.get(reverse("core:user_list"))
        request = resp.wsgi_request
        result = unread_threads(request)
        self.assertEqual(result, {"threads": [], "unread_threads": 0})

        # Regular user with one unread thread.
        thread = Thread(name="Test thread")
        thread.save()
        thread.users.add(self.test_user)
        UnreadThread(thread=thread, user=self.test_user).save()
        request = resp.wsgi_request
        result = unread_threads(request)
        self.assertEqual(result["unread_threads"], 1)
        self.assertEqual(len(result["threads"]), 1)
