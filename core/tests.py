from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase


class LoanedBookInstancesByUserListViewTest(TestCase):
    def setUp(self):
        # Create usual user.
        test_user = User.objects.create_user(username='testuser',
                                             password='12345')
        test_user.save()

    # Pages available for anonymous.
    def test_home_page(self):
        resp = self.client.get('/')
        self.assertRedirects(resp, '/login?next=/')
        self.client.login(username='testuser', password='12345')
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'user_list.html')

    def test_login_page(self):
        resp = self.client.get('/login')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'login.html')

    def test_signup_page(self):
        resp = self.client.get('/signup')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'signup.html')

    # Pages available only for registered users.
    def test_profile_page(self):
        resp = self.client.get(reverse('core:user',
                                       kwargs={'username': 'testuser'}))
        self.assertRedirects(resp, '/login?next=/user/testuser')
        self.client.login(username='testuser', password='12345')
        resp = self.client.get(reverse('core:user',
                                       kwargs={'username': 'testuser'}))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'profile.html')
