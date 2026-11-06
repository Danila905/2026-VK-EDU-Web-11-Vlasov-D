from django.test import RequestFactory, SimpleTestCase
from django.urls import reverse
from .pagination import paginate


class PagesTests(SimpleTestCase):
    def test_routes(self):
        for address in ('/', '/hot/', '/tag/css/', '/tag/blablabla/', '/question/35/', '/ask/', '/login/', '/signup/', '/profile/'):
            with self.subTest(address=address):
                self.assertEqual(self.client.get(address).status_code, 200)

    def test_named_urls(self):
        self.assertEqual(reverse('questions:question', args=[35]), '/question/35/')
        self.assertEqual(reverse('core:signup'), '/signup/')

    def test_pagination(self):
        for number in ('abc', '999', '-5'):
            request = RequestFactory().get('/', {'page': number})
            self.assertEqual(paginate(list(range(30)), request).number, 1)
        self.assertEqual(self.client.get('/?page=2').status_code, 200)
        self.assertEqual(self.client.get('/question/35/?page=2').status_code, 200)
