from __future__ import unicode_literals

import unittest

from https_everywhere.session import HTTPSEverywhereSession


class TestRequestsSession(unittest.TestCase):
    def test_freerangekitten_com(self):
        url = "http://freerangekitten.com/"
        s = HTTPSEverywhereSession()
        r = s.get(url)
        r.raise_for_status()
        self.assertEqual(r.url, url.replace("http://", "https://"))
        self.assertEqual(len(r.history), 1)
        original = r.history[0]
        self.assertEqual(original.url, url)

    def test_example_com(self):
        url = "http://example.com/"
        s = HTTPSEverywhereSession()
        r = s.get(url)
        r.raise_for_status()
        self.assertEqual(r.url, url)
        self.assertEqual(r.history, [])

    def test_webhostinggeeks_com_science(self):
        # https://github.com/EFForg/https-everywhere/issues/18867
        # http has wrong cert for quick failure, but an exception exists
        url = "http://science.webhostinggeeks.com/"
        s = HTTPSEverywhereSession()
        r = s.get(url)
        r.raise_for_status()
        self.assertEqual(r.url, url)
        self.assertEqual(r.history, [])

    def test_fedmsg_com(self):
        # https://github.com/EFForg/https-everywhere/issues/18867
        # https redirects to http, but there are no rules to upgrade it to https
        url = "http://fedmsg.com/"
        s = HTTPSEverywhereSession()
        r = s.get(url)
        r.raise_for_status()
        self.assertEqual(r.url, url)
        self.assertEqual(r.history, [])

    def test_python_org_packages(self):
        # https://github.com/EFForg/https-everywhere/issues/18867
        # https redirects to http, but there are no rules to upgrade it to https
        url = "http://packages.python.org/"
        s = HTTPSEverywhereSession()
        r = s.get(url)
        r.raise_for_status()
        self.assertEqual(r.url, "https://pythonhosted.org/")
        self.assertEqual(len(r.history), 2)
        original = r.history[0]
        self.assertEqual(original.url, url)
        self.assertEqual(original.status_code, 302)
        self.assertEqual(r.history[1].url, url.replace("http://", "https://"))
        self.assertEqual(r.history[1].status_code, 301)
