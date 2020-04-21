from __future__ import unicode_literals

import unittest

import requests

from https_everywhere.adapter import (
    HTTPBlockAdapter,
    HTTPRedirectBlockAdapter,
    HTTPSEverywhereOnlyAdapter,
    ChromePreloadHSTSAdapter,
    MozillaPreloadHSTSAdapter,
    HTTPSEverywhereAdapter,
    ForceHTTPSAdapter,
    PreferHTTPSAdapter,
    UpgradeHTTPSAdapter,
    SafeUpgradeHTTPSAdapter,
    _REASON,
    _HTTP_BLOCK_CODE,
)

from tests.test_upstream import TestUpstreamAdapter

# Throughout _test_modwsgi_org refers to a scenario where the website
# has been fixed, an a similar scenario has not yet been found
# It may need to be mocked.


class TestBlockAdapter(unittest.TestCase):

    cls = HTTPBlockAdapter

    def test_freerangekitten_com(self):
        url = "http://freerangekitten.com/"
        s = requests.Session()
        self.assertEqual(len(s.adapters), 2)
        s.mount("http://", self.cls())
        self.assertEqual(len(s.adapters), 2)
        self.assertEqual(
            s.adapters["https://"].__class__, requests.adapters.HTTPAdapter
        )
        self.assertEqual(s.adapters["http://"].__class__, self.cls)
        r = s.get(url)
        self.assertEqual(r.url, url)
        self.assertEqual(r.history, [])
        self.assertEqual(r.status_code, _HTTP_BLOCK_CODE)

        url = "https://freerangekitten.com/"
        s.mount("https://", self.cls())
        r = s.get(url)
        self.assertEqual(r.url, url)
        self.assertEqual(r.status_code, 200)


class TestRedirectBlockAdapter(unittest.TestCase):

    cls = HTTPRedirectBlockAdapter

    def test_whisper_sh(self):
        url = "https://whisper.sh/"
        s = requests.Session()
        self.assertEqual(len(s.adapters), 2)
        s.mount("https://", self.cls())
        self.assertEqual(len(s.adapters), 2)
        self.assertEqual(s.adapters["http://"].__class__, requests.adapters.HTTPAdapter)
        self.assertEqual(s.adapters["https://"].__class__, self.cls)
        r = s.get(url)
        self.assertEqual(r.url, url)
        self.assertEqual(r.history, [])
        self.assertEqual(r.status_code, _HTTP_BLOCK_CODE)


class TestEverywhereOnlyAdapter(TestUpstreamAdapter):

    cls = HTTPSEverywhereOnlyAdapter

    def test_freerangekitten_com(self):
        url = "http://freerangekitten.com/"
        s = requests.Session()
        s.mount("http://", self.cls())
        r = s.get(url)
        r.raise_for_status()
        self.assertEqual(r.url, url.replace("http://", "https://"))
        self.assertEqual(len(r.history), 1)
        original = r.history[0]
        self.assertEqual(original.url, url)

    def _test_webhostinggeeks_com_science(self):
        # https://github.com/EFForg/https-everywhere/issues/18867
        # https has wrong cert, which is a quick failure, but an exception exists
        url = "http://science.webhostinggeeks.com/"
        # See super method

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
        self.assertEqual(original.status_code, 302)
        self.assertEqual(original.reason, _REASON)

    def test_01_org_www(self):
        url = "http://www.01.org/"
        s = requests.Session()
        s.mount("http://", self.cls())
        r = s.get(url)
        r.raise_for_status()
        self.assertEqual(r.url, "https://01.org/")
        self.assertEqual(len(r.history), 2)
        original = r.history[0]
        self.assertEqual(original.url, url)
        self.assertEqual(original.status_code, 302)
        self.assertEqual(original.reason, _REASON)
        self.assertEqual(r.history[-1].url, "https://www.01.org/")

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
        self.assertEqual(original.status_code, 302)
        self.assertEqual(original.reason, _REASON)
        self.assertEqual(r.history[1].url, url.replace("http://", "https://"))
        self.assertEqual(r.history[1].status_code, 301)
        self.assertEqual(r.history[1].reason, "Moved Permanently")


class TestChromePreloadAdapter(TestEverywhereOnlyAdapter):

    cls = ChromePreloadHSTSAdapter

    def test_freerangekitten_com(self):
        url = "http://freerangekitten.com/"
        s = requests.Session()
        s.mount("http://", self.cls())
        r = s.get(url)
        r.raise_for_status()
        self.assertEqual(r.url, url)
        self.assertEqual(len(r.history), 0)

    def test_medbank_mt(self):
        url = "http://business.medbank.com.mt/"
        s = requests.Session()
        s.mount("http://", self.cls())
        r = s.get(url)
        r.raise_for_status()
        self.assertEqual(r.url, "https://www.medirect.com.mt")
        self.assertEqual(len(r.history), 2)
        original = r.history[0]
        self.assertEqual(original.url, url)
        self.assertEqual(original.status_code, 302)
        self.assertEqual(original.reason, _REASON)
        self.assertEqual(r.history[1].url, url.replace("http://", "https://"))
        self.assertEqual(r.history[1].status_code, 301)
        self.assertEqual(r.history[1].reason, "Moved Permanently")

    test_python_org_packages = TestUpstreamAdapter.test_python_org_packages


class TestMozillaPreloadAdapter(TestChromePreloadAdapter):
    cls = MozillaPreloadHSTSAdapter

    test_medbank_mt = TestEverywhereOnlyAdapter.test_medbank_mt


class TestEverywhereAdapter(TestChromePreloadAdapter):

    cls = HTTPSEverywhereAdapter

    test_freerangekitten_com = TestEverywhereOnlyAdapter.test_freerangekitten_com

    test_python_org_packages = TestEverywhereOnlyAdapter.test_python_org_packages


class TestForceAdapter(TestEverywhereAdapter):

    cls = ForceHTTPSAdapter

    def test_ros_wiki(self):
        url = "http://wiki.ros.org/"
        s = requests.Session()
        s.mount("http://", self.cls())
        r = s.get(url)
        r.raise_for_status()
        self.assertEqual(r.url, url.replace("http://", "https://"))
        self.assertEqual(len(r.history), 1)
        original = r.history[0]
        self.assertEqual(original.url, url)

    def test_example_com(self):
        url = "http://example.com/"
        s = requests.Session()
        s.mount("http://", self.cls())
        r = s.get(url)
        r.raise_for_status()
        self.assertEqual(r.url, url.replace("http://", "https://"))
        self.assertEqual(len(r.history), 1)
        original = r.history[0]
        self.assertEqual(original.url, url)

    def test_webhostinggeeks_com_science(self):
        # https://github.com/EFForg/https-everywhere/issues/18867
        # https has wrong cert for a quick failure
        url = "http://science.webhostinggeeks.com/"
        s = requests.Session()
        s.mount("http://", self.cls())
        with self.assertRaises(requests.exceptions.SSLError):
            s.get(url)

        s.mount(
            "http://",
            ForceHTTPSAdapter(https_exclusions=["science.webhostinggeeks.com"]),
        )
        r = s.get(url)
        r.raise_for_status()
        self.assertEqual(r.url, url)
        self.assertEqual(r.history, [])

    def test_shopzilla(self):
        url = "http://www.shopzilla.com/"
        s = requests.Session()
        s.mount("http://", self.cls())
        with self.assertRaises(requests.exceptions.TooManyRedirects):
            s.get(url)

    def test_whisper_sh(self):
        url = "http://whisper.sh/"
        s = requests.Session()
        s.mount("http://", self.cls())
        with self.assertRaises(requests.exceptions.TooManyRedirects):
            s.get(url)

    def test_thesyriacampaign(self):
        url = "http://www.thesyriacampaign.org/"
        s = requests.Session()
        s.mount("http://", self.cls())
        with self.assertRaises(requests.exceptions.TooManyRedirects):
            s.get(url)

    def test_esncz_org(self):
        url = "http://www.isc.vutbr.cz/"
        s = requests.Session()
        s.mount("http://", self.cls())
        with self.assertRaises(requests.exceptions.SSLError):
            s.get(url)

        with self.assertRaises(requests.exceptions.SSLError):
            s.get(url, timeout=5)

    def _test_modwsgi_org(self):
        # https://github.com/EFForg/https-everywhere/issues/18867
        # http has a redirect to readthedocs; https fails
        url = "http://www.modwsgi.org/"
        s = requests.Session()
        s.mount("http://", self.cls())
        with self.assertRaises(requests.exceptions.Timeout):
            s.get(url, timeout=5)

    def test_fedmsg_com(self):
        # https://github.com/EFForg/https-everywhere/issues/18867
        # https redirects to http, so a manual exclusion is needed
        url = "http://fedmsg.com/"
        s = requests.Session()
        s.mount("http://", self.cls())
        with self.assertRaises(requests.exceptions.TooManyRedirects):
            s.get(url)

        s.mount("http://", self.cls(https_exclusions=["fedmsg.com"]))
        s.mount("https://", self.cls(https_exclusions=["fedmsg.com"]))

        r = s.get(url)
        r.raise_for_status()
        self.assertEqual(r.url, url)
        self.assertEqual(r.history, [])

        r = s.get(url.replace("http://", "https://"))
        r.raise_for_status()
        self.assertEqual(r.url, url)
        self.assertEqual(len(r.history), 1)
        original = r.history[0]
        self.assertEqual(original.url, url.replace("http://", "https://"))


class TestPreferAdapter(TestForceAdapter):

    cls = PreferHTTPSAdapter

    test_01_org = TestUpstreamAdapter.test_01_org
    test_01_org_www = TestUpstreamAdapter.test_01_org
    test_medbank_mt = TestUpstreamAdapter.test_medbank_mt
    test_python_org_packages = TestUpstreamAdapter.test_python_org_packages

    def test_esncz_org(self):
        url = "http://www.isc.vutbr.cz/"
        s = requests.Session()
        s.mount("http://", self.cls())
        r = s.get(url, timeout=5)
        r.raise_for_status()
        target = "https://www.esncz.org"
        self.assertEqual(r.url, target)
        self.assertEqual(len(r.history), 1)
        original = r.history[0]
        self.assertEqual(original.url, url)
        self.assertEqual(r.url, "https://www.esncz.org")

    def _test_modwsgi_org(self):
        # https://github.com/EFForg/https-everywhere/issues/18867
        # http has a redirect to readthedocs; https fails
        url = "http://www.modwsgi.org/"
        s = requests.Session()
        s.mount("http://", self.cls())
        r = s.get(url)
        r.raise_for_status()
        original = r.history[0]
        # The original url is lost, as part of a request which was skipped
        self.assertEqual(original.url, "http://modwsgi.readthedocs.io/")
        self.assertEqual(r.url, "https://modwsgi.readthedocs.io/en/develop/")
        self.assertEqual(len(r.history), 2)
        self.assertEqual(r.history[1].url, "https://modwsgi.readthedocs.io/")


class TestSafeUpgradeAdapter(TestEverywhereAdapter):

    cls = SafeUpgradeHTTPSAdapter

    def test_freerangekitten_com(self):
        url = "http://freerangekitten.com/"
        s = requests.Session()
        s.mount("http://", self.cls())
        r = s.get(url)
        r.raise_for_status()
        self.assertEqual(r.url, url.replace("http://", "https://"))
        self.assertEqual(r.history, [])

    def test_example_com(self):
        url = "http://example.com/"
        s = requests.Session()
        s.mount("http://", self.cls())
        r = s.get(url)
        r.raise_for_status()
        self.assertEqual(r.url, url.replace("http://", "https://"))
        self.assertEqual(r.history, [])

    def _test_my_vpnglobe(self):
        url = "http://my.vpnglobe.com/"
        s = requests.Session()
        s.mount("http://", self.cls())
        # FIXME: this is 'unsafe'
        with self.assertRaises(requests.exceptions.SSLError):
            s.get(url)

    def _test_modwsgi_org(self):
        # https://github.com/EFForg/https-everywhere/issues/18867
        # http has a redirect to readthedocs; https fails
        url = "http://www.modwsgi.org/"
        s = requests.Session()
        s.mount("http://", self.cls())
        r = s.get(url, timeout=5)
        r.raise_for_status()
        self.assertEqual(r.url, "https://modwsgi.readthedocs.io/en/develop/")
        self.assertEqual(len(r.history), 2)
        original = r.history[0]
        self.assertEqual(original.url, "http://www.modwsgi.org/")
        source_redirect = r.history[1]
        self.assertEqual(source_redirect.url, "https://modwsgi.readthedocs.io/")

    def test_python_org_packages(self):
        url = "http://packages.python.org/"
        s = requests.Session()
        s.mount("http://", self.cls())
        r = s.get(url)
        r.raise_for_status()
        self.assertEqual(r.url, "https://pythonhosted.org/")
        self.assertEqual(len(r.history), 1)
        original = r.history[0]
        self.assertEqual(original.url, url.replace("http://", "https://"))
        # This adapter provides the real response, with code of 301
        self.assertEqual(original.status_code, 301)

    def test_ros_wiki(self):
        # https://github.com/jayvdb/pypidb/issues/115
        # Short-lived problem
        url = "http://wiki.ros.org/"
        s = requests.Session()
        s.mount("http://", self.cls())
        r = s.get(url)
        r.raise_for_status()
        self.assertEqual(r.url, url.replace("http://", "https://"))
        self.assertEqual(r.history, [])

    def test_01_org(self):
        url = "http://01.org/"
        s = requests.Session()
        s.mount("http://", self.cls())
        r = s.get(url)
        r.raise_for_status()
        self.assertEqual(r.url, url.replace("http://", "https://"))
        self.assertEqual(r.history, [])

    def test_01_org_www(self):
        url = "http://www.01.org/"
        s = requests.Session()
        s.mount("http://", self.cls())
        r = s.get(url)
        r.raise_for_status()
        self.assertEqual(r.url, "https://01.org/")
        self.assertEqual(len(r.history), 1)
        original = r.history[0]
        # Here is where it differs from upstream, with an unusual
        # original url which differs from the real original
        self.assertEqual(original.url, url.replace("http://", "https://"))
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
        # Here is where it differs from upstream, with an unusual
        # original url which differs from the real original
        self.assertEqual(original.url, url.replace("http://", "https://"))
        self.assertEqual(original.status_code, 301)
        self.assertEqual(original.reason, "Moved Permanently")


class TestUpgradeAdapter(TestForceAdapter):

    cls = UpgradeHTTPSAdapter
