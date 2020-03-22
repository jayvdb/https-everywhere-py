from __future__ import unicode_literals

import unittest

from https_everywhere._util import _check_in, _reverse_host


class TestReverseHost(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(_reverse_host("appspot.com"), "com.appspot.")
        self.assertEqual(_reverse_host("www.appspot.com"), "com.appspot.www.")
        self.assertIn(_reverse_host("appspot.com"), _reverse_host("www.appspot.com"))

    def test_google(self):
        self.assertEqual(_reverse_host("google"), "google.")
        self.assertEqual(_reverse_host("www.google"), "google.www.")
        self.assertIn(_reverse_host("google"), _reverse_host("www.google"))


class TestLookup(unittest.TestCase):
    def test_single_label_domain_names(self):
        self.assertTrue(_check_in(["gmail"], "www.gmail"))
        self.assertTrue(_check_in(["google"], "www.google"))
        # Single label domain names are not legal in DNS
        self.assertFalse(_check_in(["gmail"], "gmail"))
        self.assertFalse(_check_in(["google"], "google"))
