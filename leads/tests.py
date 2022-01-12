from django.test import TestCase
from django.shortcuts import reverse


class LandingPagetest(TestCase):
    def test_status_code(self):
        # todo a test
        response = self.client.get(reverse ("landing-page"))
        self.assertEqual(response.status_code, 200)
        print(response.content)
        print(response.status_code)
        pass

