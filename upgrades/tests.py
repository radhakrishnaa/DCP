"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.utils import override_settings
from pprint import pprint

# @override_settings(AUTHENTICATION_BACKENDS=
#                    ('django.contrib.auth.backends.ModelBackend',))
class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

    def test_defaultpollinginterval(self):
        """
        Test that you can get correct default polling interval 
        """
        response = self.client.get('/defaultpollinginterval/', follow=True)
        expected = '''{"Default Polling Interval in seconds": 3601}'''
        self.assertEqual(response.content, expected)

    def test_defaultpollinginterval_86400(self):
        """
        Test that you can get correct updated polling interval 
        """

        # Then override the LOGIN_URL setting
        with self.settings(DEFAULT_POLLING_INTERVAL=86400):
            response = self.client.get('/defaultpollinginterval/')
            expected = '''{"Default Polling Interval in seconds": 86400}'''
            self.assertEqual(response.content, expected)
