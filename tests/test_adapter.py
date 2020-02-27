from __future__ import unicode_literals

import unittest

import requests

from https_everywhere.adapter import (
    HTTPBlockAdapter,
    HTTPRedirectBlockAdapter,
    HTTPSEverywhereOnlyAdapter,
    ChromePreloadHSTSAdapter,
    HTTPSEverywhereAdapter,
    ForceHTTPSAdapter,
    PreferHTTPSAdapter,
    UpgradeHTTPSAdapter,
    SafeUpgradeHTTPSAdapter,
    _REASON,
    _HTTP_BLOCK_CODE,
)

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


class TestEverywhereOnlyAdapter(unittest.TestCase):

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
        # https has wrong cert, which is a quick failure, but an exception exists
        url = "http://science.webhostinggeeks.com/"
        s = requests.Session()
        s.mount("http://", self.cls())
        r = s.get(url)
        r.raise_for_status()
        self.assertEqual(r.url, url)
        self.assertEqual(r.history, [])

    def test_fedmsg_com(self):
        # https://github.com/EFForg/https-everywhere/issues/18867
        # https redirects to http, but there are no rules to upgrade it to https
        url = "http://fedmsg.com/"
        s = requests.Session()
        s.mount("http://", self.cls())
        r = s.get(url)
        r.raise_for_status()
        self.assertEqual(r.url, url)
        self.assertEqual(r.history, [])

    def test_shopzilla(self):
        url = "http://www.shopzilla.com/"
        s = requests.Session()
        s.mount("http://", self.cls())
        r = s.get(url, timeout=5)
        r.raise_for_status()
        self.assertEqual(r.url, url)
        self.assertEqual(r.history, [])

    def test_whisper_sh(self):
        url = "http://whisper.sh/"
        s = requests.Session()
        s.mount("http://", self.cls())
        r = s.get(url, timeout=5)
        r.raise_for_status()
        self.assertEqual(r.url, url)
        self.assertEqual(r.history, [])

    def test_thesyriacampaign(self):
        url = "http://www.thesyriacampaign.org/"
        s = requests.Session()
        s.mount("http://", self.cls())
        r = s.get(url, timeout=5)
        self.assertEqual(r.url, url)
        self.assertEqual(r.status_code, 403)

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

    def test_medbank_mt(self):
        url = "http://business.medbank.com.mt/"
        s = requests.Session()
        s.mount("http://", self.cls())
        r = s.get(url)
        r.raise_for_status()
        self.assertEqual(r.url, "https://www.medirect.com.mt")
        # with self.assertRaises(requests.exceptions.ConnectionError):
        #    s.get(url)

    def test_my_vpnglobe(self):
        url = "http://my.vpnglobe.com/"
        s = requests.Session()
        s.mount("http://", self.cls())
        with self.assertRaises(requests.exceptions.SSLError):
            s.get(url)

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
        # 301 here vs 302
        self.assertEqual(original.status_code, 301)
        self.assertEqual(original.reason, "Moved Permanently")
        self.assertEqual(r.history[1].url, url.replace("http://", "https://"))
        self.assertEqual(r.history[1].status_code, 301)
        self.assertEqual(r.history[1].reason, "Moved Permanently")


class TestEverywhereAdapter(TestChromePreloadAdapter):

    cls = HTTPSEverywhereAdapter

    test_freerangekitten_com = TestEverywhereOnlyAdapter.test_freerangekitten_com

    test_python_org_packages = TestEverywhereOnlyAdapter.test_python_org_packages


class TestForceAdapter(unittest.TestCase):

    cls = ForceHTTPSAdapter

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

    def test_fedmsg_com(self):
        # https://github.com/EFForg/https-everywhere/issues/18867
        # https redirects to http, so a manual exclusion is needed
        url = "http://fedmsg.com/"
        s = requests.Session()
        s.mount("http://", self.cls())
        with self.assertRaises(requests.exceptions.TooManyRedirects):
            s.get(url)

        s.mount("http://", ForceHTTPSAdapter(https_exclusions=["fedmsg.com"]))
        s.mount("https://", ForceHTTPSAdapter(https_exclusions=["fedmsg.com"]))

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
        self.assertEqual(r.history[1].url, url.replace("http://", "https://"))
        self.assertEqual(r.history[1].status_code, 301)


class TestPreferAdapter(unittest.TestCase):

    cls = PreferHTTPSAdapter

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
        # https has wrong cert for quick failure.
        url = "http://science.webhostinggeeks.com/"
        s = requests.Session()
        s.mount("http://", self.cls())
        with self.assertRaises(requests.exceptions.SSLError):
            s.get(url)

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
        r = s.get(url, timeout=5)
        r.raise_for_status()
        target = "https://www.esncz.org"
        self.assertEqual(r.url, target)
        self.assertEqual(len(r.history), 1)
        original = r.history[0]
        self.assertEqual(original.url, url)
        self.assertEqual(r.url, "https://www.esncz.org")

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
        r = s.get(url)
        r.raise_for_status()
        original = r.history[0]
        # The original url is lost, as part of a request which was skipped
        self.assertEqual(original.url, "http://modwsgi.readthedocs.io/")
        self.assertEqual(r.url, "https://modwsgi.readthedocs.io/en/develop/")
        self.assertEqual(len(r.history), 2)
        self.assertEqual(r.history[1].url, "https://modwsgi.readthedocs.io/")

    def test_fedmsg_com(self):
        # https://github.com/EFForg/https-everywhere/issues/18867
        # https redirects to http, but there are no rules to upgrade it to https
        url = "http://fedmsg.com/"
        s = requests.Session()
        s.mount("http://", self.cls())
        with self.assertRaises(requests.exceptions.TooManyRedirects):
            s.get(url)

        # It can be solved with an explicit manual exclusion, but cant
        # be managed in an adapter because the TooManyRedirects is raised
        # in the session
        s.mount("http://", self.cls(https_exclusions=["fedmsg.com"]))
        r = s.get(url)
        r.raise_for_status()
        self.assertEqual(r.url, url)
        self.assertEqual(r.history, [])

        s.mount("https://", self.cls(https_exclusions=["fedmsg.com"]))
        r = s.get(url.replace("http://", "https://"))
        r.raise_for_status()
        self.assertEqual(r.url, url)
        self.assertEqual(len(r.history), 1)
        original = r.history[0]
        self.assertEqual(original.url, url.replace("http://", "https://"))

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
        # This adapter provides the real response, with code of 301
        self.assertEqual(original.status_code, 301)
        self.assertEqual(r.history[1].url, url.replace("http://", "https://"))
        self.assertEqual(r.history[1].status_code, 301)


class TestUpgradeAdapter(unittest.TestCase):

    cls = UpgradeHTTPSAdapter

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
        # https has wrong cert for quick failure.
        url = "http://science.webhostinggeeks.com/"
        s = requests.Session()
        s.mount("http://", self.cls())
        s.mount("https://", self.cls())
        r = s.get(url, timeout=5)
        r.raise_for_status()
        # There is an extra history item, with a redirect, but
        # the final request has disregarded that redirect
        self.assertEqual(r.url, url)
        self.assertEqual(len(r.history), 1)
        original = r.history[0]
        self.assertEqual(original.url, url)
        self.assertEqual(
            original.headers["location"], url.replace("http://", "https://")
        )

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
        s.mount("https://", self.cls())
        r = s.get(url, timeout=5)
        r.raise_for_status()
        self.assertEqual(r.url, "https://modwsgi.readthedocs.io/en/develop/")
        self.assertEqual(len(r.history), 4)
        original = r.history[0]
        self.assertEqual(original.url, "http://www.modwsgi.org/")
        injected_failed_upgrade = r.history[1]
        self.assertEqual(injected_failed_upgrade.url, "http://www.modwsgi.org/")
        source_redirect = r.history[2]
        self.assertEqual(source_redirect.url, "http://modwsgi.readthedocs.io/")

    def test_fedmsg_com(self):
        # https://github.com/EFForg/https-everywhere/issues/18867
        # https redirects to http, but there are no rules to upgrade it to https
        url = "http://fedmsg.com/"
        s = requests.Session()
        s.mount("http://", self.cls())
        s.mount("https://", self.cls())
        with self.assertRaises(requests.exceptions.TooManyRedirects):
            s.get(url)

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
        # This adapter provides the real response, with code of 301
        self.assertEqual(original.status_code, 302)
        self.assertEqual(r.history[1].url, url.replace("http://", "https://"))
        self.assertEqual(r.history[1].status_code, 301)


class TestSafeUpgradeAdapter(unittest.TestCase):

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

    def test_webhostinggeeks_com_science(self):
        # https://github.com/EFForg/https-everywhere/issues/18867
        # https has wrong cert for quick failure.
        url = "http://science.webhostinggeeks.com/"
        s = requests.Session()
        s.mount("http://", self.cls())
        r = s.get(url, timeout=5)
        r.raise_for_status()
        self.assertEqual(r.url, url)
        self.assertEqual(r.history, [])

    def test_shopzilla(self):
        url = "http://www.shopzilla.com/"
        s = requests.Session()
        s.mount("http://", self.cls())
        r = s.get(url, timeout=5)
        r.raise_for_status()
        self.assertEqual(r.url, url)

    def test_whisper_sh(self):
        url = "http://whisper.sh/"
        s = requests.Session()
        s.mount("http://", self.cls())
        r = s.get(url, timeout=5)
        r.raise_for_status()
        self.assertEqual(r.url, url)

    def test_thesyriacampaign(self):
        url = "http://www.thesyriacampaign.org/"
        s = requests.Session()
        s.mount("http://", self.cls())
        r = s.get(url, timeout=5)
        self.assertEqual(r.url, url)
        # FIXME: this should redirect to 'https://thesyriacampaign.org/'
        self.assertEqual(r.status_code, 403)

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
        self.assertEqual(original.url, "http://www.isc.vutbr.cz/")

    def test_my_vpnglobe(self):
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

    def test_fedmsg_com(self):
        # https://github.com/EFForg/https-everywhere/issues/18867
        # https redirects to http, but there are no rules to upgrade it to https
        url = "http://fedmsg.com/"
        s = requests.Session()
        s.mount("http://", self.cls())

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
