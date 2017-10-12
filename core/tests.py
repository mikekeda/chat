from django.test import TestCase
from django.contrib.auth.models import User


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
