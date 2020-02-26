from __future__ import unicode_literals

import unittest

from https_everywhere._chrome_preload_hsts import _preload_including_subdomains

from https_everywhere._util import _check_in


class TestPreload(unittest.TestCase):
    def test_01(self):
        domains = _preload_including_subdomains()
        self.assertTrue(_check_in(domains, "01.org"))

    def test_01_www(self):
        domains = _preload_including_subdomains()
        self.assertTrue(_check_in(domains, "www.01.org"))

    def test_longest(self):
        domains = _preload_including_subdomains()
        self.assertTrue(_check_in(domains, "business.medbank.com.mt"))
        self.assertTrue(_check_in(domains, "foo.business.medbank.com.mt"))
        self.assertFalse(_check_in(domains, "business2.medbank.com.mt"))
        self.assertFalse(_check_in(domains, "foo.business2.medbank.com.mt"))

        self.assertTrue(_check_in(domains, "pinning-test.badssl.com"))
        self.assertTrue(_check_in(domains, "foo.pinning-test.badssl.com"))
        self.assertFalse(_check_in(domains, "foo.pinning-test2.badssl.com"))
        self.assertFalse(_check_in(domains, "pinning-test2.badssl.com"))

    def test_include_subdomains(self):
        domains = _preload_including_subdomains()
        self.assertIn("pinningtest.appspot.com", domains)
        self.assertNotIn("at.search.yahoo.com", domains)
