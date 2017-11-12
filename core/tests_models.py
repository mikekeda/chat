from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.conf import settings
from django.test import TestCase

from .models import Profile


class ChatModelTest(TestCase):
    def setUp(self):
        # Create usual user.
        test_user = User.objects.create_user(username='test_model_user1',
                                             password='12345')
        test_user.save()
        test_user = User.objects.create_user(username='test_model_user2',
                                             password='12345')
        test_user.save()

    # Pages available for anonymous.
    def test_models_profile(self):
        result = Profile.get_online_users()
        self.assertEqual(result, [])

        # Go to any page to trigger active_user_middleware middleware.
        self.client.login(username='test_model_user1', password='12345')
        self.client.get(reverse('core:user_list'))

        # Check if test_model_user1 are online.
        test_user = User.objects.get(username='test_model_user1')
        profile, _ = Profile.objects.get_or_create(user=test_user)
        self.assertEqual(bool(profile.online()), True)

        # Check a list of online users.
        result = Profile.get_online_users()
        self.assertEqual(result, ['test_model_user1'])

        # Go to any page to trigger active_user_middleware middleware.
        self.client.login(username='test_model_user2', password='12345')
        self.client.get(reverse('core:user_list'))

        # Check if user are online.
        test_user = User.objects.get(username='test_model_user2')
        profile, _ = Profile.objects.get_or_create(user=test_user)
        self.assertEqual(bool(profile.online()), True)

        # Check a list of online users.
        result = Profile.get_online_users()
        self.assertEqual(len(result), 2)

        # Clean up the cache.
        cache.delete('seen_{}'.format('test_model_user1'))
        cache.delete('seen_{}'.format('test_model_user2'))
