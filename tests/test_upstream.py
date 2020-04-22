from __future__ import unicode_literals

import unittest

import requests


class TestUpstreamAdapter(unittest.TestCase):

    cls = requests.adapters.HTTPAdapter

    def test_freerangekitten_com(self):
        url = "http://freerangekitten.com/"
        s = requests.Session()
        s.mount("http://", self.cls())
        r = s.get(url)
        r.raise_for_status()
        self.assertEqual(r.url, url)
        self.assertEqual(r.history, [])

    def test_example_com(self):
        url = "http://example.com/"
        s = requests.Session()
        s.mount("http://", self.cls())
        r = s.get(url)
        r.raise_for_status()
        self.assertEqual(r.url, url)
        self.assertEqual(r.history, [])

    def test_webhostinggeeks_com_science(self):
        # https://github.com/EFForg/https-everywhere/issues/18867
        # https has wrong cert for a quick failure
        url = "http://science.webhostinggeeks.com/"
        s = requests.Session()
        s.mount("http://", self.cls())
        r = s.get(url)
        r.raise_for_status()
        self.assertEqual(r.url, url)
        self.assertEqual(r.history, [])

    def test_fedmsg_com(self):
        # https://github.com/EFForg/https-everywhere/issues/18867
        # https redirects to http, so a manual exclusion is needed
        url = "http://fedmsg.com/"
        s = requests.Session()
        s.mount("http://", self.cls())
        r = s.get(url, timeout=60)
        r.raise_for_status()
        self.assertEqual(r.url, url)
        self.assertEqual(r.history, [])

    def test_shopzilla(self):
        url = "http://www.shopzilla.com/"
        s = requests.Session()
        s.mount("http://", self.cls())
        r = s.get(url)
        r.raise_for_status()
        self.assertEqual(r.url, url)
        self.assertEqual(r.history, [])

    def test_whisper_sh(self):
        url = "http://whisper.sh/"
        s = requests.Session()
        s.mount("http://", self.cls())
        r = s.get(url)
        r.raise_for_status()
        self.assertEqual(r.url, url)
        self.assertEqual(r.history, [])

    def test_thesyriacampaign(self):
        url = "http://www.thesyriacampaign.org/"
        s = requests.Session()
        s.mount("http://", self.cls())
        r = s.get(url)
        self.assertEqual(r.status_code, 403)

    def test_esncz_org(self):
        url = "http://www.isc.vutbr.cz/"
        s = requests.Session()
        s.mount("http://", self.cls())
        r = s.get(url)
        r.raise_for_status()
        self.assertEqual(r.url, "https://www.esncz.org")
        target = "https://www.esncz.org"
        self.assertEqual(r.url, target)
        self.assertEqual(len(r.history), 1)
        original = r.history[0]
        self.assertEqual(original.url, url)
        self.assertEqual(original.status_code, 302)
        self.assertEqual(original.reason, "Found")

    def test_01_org(self):
        url = "http://01.org/"
        s = requests.Session()
        s.mount("http://", self.cls())
        r = s.get(url)
        r.raise_for_status()
        self.assertEqual(r.url, url.replace("http://", "https://"))
        self.assertEqual(len(r.history), 1)
        original = r.history[0]
        self.assertEqual(original.url, url)
        self.assertEqual(original.status_code, 301)
        self.assertEqual(original.reason, "Moved Permanently")

    def test_01_org_www(self):
        url = "http://www.01.org/"
        s = requests.Session()
        s.mount("http://", self.cls())
        r = s.get(url)
        r.raise_for_status()
        self.assertEqual(r.url, "https://01.org/")
        self.assertEqual(len(r.history), 1)
        original = r.history[0]
        self.assertEqual(original.url, url)
        self.assertEqual(original.status_code, 301)
        self.assertEqual(original.reason, "Moved Permanently")

    def test_medbank_mt(self):
        url = "http://business.medbank.com.mt/"
        s = requests.Session()
        s.mount("http://", self.cls())
        r = s.get(url)
        r.raise_for_status()
        self.assertEqual(r.url, "https://www.medirect.com.mt")
        self.assertEqual(len(r.history), 1)
        original = r.history[0]
        self.assertEqual(original.url, url)
        self.assertEqual(original.status_code, 301)
        self.assertEqual(original.reason, "Moved Permanently")

    def test_my_vpnglobe(self):
        url = "http://my.vpnglobe.com/"
        s = requests.Session()
        s.mount("http://", self.cls())
        with self.assertRaises(requests.exceptions.SSLError):
            s.get(url)

    def _test_modwsgi_org(self):
        # https://github.com/EFForg/https-everywhere/issues/18867
        # http has a redirect to readthedocs; https fails
        url = "http://www.modwsgi.org/"
        s = requests.Session()
        s.mount("http://", self.cls())
        with self.assertRaises(requests.exceptions.Timeout):
            s.get(url, timeout=5)

    def test_python_org_packages(self):
        url = "http://packages.python.org/"
        s = requests.Session()
        s.mount("http://", self.cls())
        r = s.get(url)
        r.raise_for_status()
        self.assertEqual(r.url, "https://pythonhosted.org/")
        self.assertEqual(len(r.history), 2)
        original = r.history[0]
        self.assertEqual(original.url, url)
        self.assertEqual(original.status_code, 301)
        self.assertEqual(original.reason, "Moved Permanently")
        self.assertEqual(r.history[1].url, url.replace("http://", "https://"))
        self.assertEqual(r.history[1].status_code, 301)
        self.assertEqual(r.history[1].reason, "Moved Permanently")

    def test_ros_wiki(self):
        # https://github.com/jayvdb/pypidb/issues/115
        # Short-lived problem
        url = "http://wiki.ros.org/"
        s = requests.Session()
        s.mount("http://", self.cls())
        r = s.get(url)
        r.raise_for_status()
        self.assertEqual(r.url, url)
        self.assertEqual(r.history, [])
