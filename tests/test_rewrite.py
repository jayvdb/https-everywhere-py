from __future__ import unicode_literals

import unittest

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

import urllib3.util

from https_everywhere._rules import https_url_rewrite

PY2 = str != "".__class__
if PY2:
    str = "".__class__


class TestRewrite(unittest.TestCase):
    def _check_https(self, url):
        self.assertIsNotNone(url)
        self.assertIsInstance(url, str)
        self.assertTrue(url.startswith("https://"))

    def _check_no_https(self, url):
        self.assertIsNotNone(url)
        self.assertIsInstance(url, str)
        self.assertTrue(url.startswith("http://"))

    def test_urlparse_stdlib_urlparse(self):
        url = urlparse("http://packages.python.org/foo")
        rv = https_url_rewrite(url)
        self._check_https(rv)

    def test_urlparse_urllib3(self):
        url = urllib3.util.url.parse_url("http://packages.python.org/foo")
        rv = https_url_rewrite(url)
        self._check_https(rv)

    def test_python_org_packages(self):
        # https://github.com/python/psf-chef/issues/176
        url = "http://packages.python.org/foo"
        rv = https_url_rewrite(url)
        self._check_https(rv)

    def test_python_org_svn(self):
        url = "http://svn.python.org/"
        rv = https_url_rewrite(url)
        self._check_no_https(rv)

    def test_webhostinggeeks_com(self):
        url = "http://webhostinggeeks.com/foo"
        rv = https_url_rewrite(url)
        self._check_https(rv)

    def test_webhostinggeeks_com_science(self):
        # https://github.com/EFForg/https-everywhere/issues/18867
        url = "http://science.webhostinggeeks.com/foo"
        rv = https_url_rewrite(url)
        self._check_no_https(rv)

    def test_example_com(self):
        url = "http://example.com/"
        rv = https_url_rewrite(url)
        self._check_no_https(rv)

    def test_unknown_com(self):
        url = "http://unknown.com/"
        rv = https_url_rewrite(url)
        self._check_no_https(rv)

    def test_freerangekitten_com(self):
        url = "http://freerangekitten.com/"
        rv = https_url_rewrite(url)
        self._check_https(rv)

    def test_googleapis_com_chart(self):
        url = "http://chart.googleapis.com/"
        rv = https_url_rewrite(url)
        self._check_no_https(rv)

        url = "http://chart.googleapis.com/123"
        rv = https_url_rewrite(url)
        self._check_https(rv)

    def test_prositehosting_co_uk_secure(self):
        url = "http://secure32.prositehosting.co.uk"
        rv = https_url_rewrite(url)
        self._check_https(rv)

    def test_thumbshots_com_three_variables(self):
        url = "http://www.thumbshots.com/portals/0/Images/IncreaseTraffic.png"
        rv = https_url_rewrite(url)
        self._check_https(rv)

    def test_thumbshots_com_second_rule(self):
        url = "http://ranking.thumbshots.com/"
        rv = https_url_rewrite(url)
        self._check_https(rv)

    def test_utwente_nl_overlapping_ruleset(self):
        url = "http://www.iapc.utwente.nl/"
        rv = https_url_rewrite(url)
        self._check_https(rv)

    def test_googlevideo_com_subdomain_real(self):
        url = "http://r2---sn-25ge7nsl.googlevideo.com/videoplayback?keepalive=yes"
        rv = https_url_rewrite(url)
        self._check_https(rv)
        assert rv == url.replace("http://", "https://")

    def test_googlevideo_com_subdomain_test(self):
        url = "http://test.googlevideo.com/"
        rv = https_url_rewrite(url)
        self._check_https(rv)
        assert rv == url.replace("http://", "https://")

    def test_googlevideo_com_subdomain_multiple(self):
        url = "http://test.test.googlevideo.com/"
        rv = https_url_rewrite(url)
        self._check_https(rv)
        assert rv == url.replace("http://", "https://")

    def test_akamaihd_net_imagesmtv(self):
        url = "http://www.akamaihd.net/"
        rv = https_url_rewrite(url)
        self._check_https(rv)

        # exclusion
        url = "http://imagesmtv-a.akamaihd.net/"
        rv = https_url_rewrite(url)
        self._check_no_https(rv)

    @unittest.expectedFailure
    def test_cacert_org_crt_filename_not_secured(self):
        # This ruleset is disabled
        url = "http://www.cacert.org/"
        rv = https_url_rewrite(url)
        self._check_https(rv)

        url = "http://www.cacert.org/certs/root.crt"
        rv = https_url_rewrite(url)
        self._check_no_https(rv)

    def test_cloudfront_net_re_character_class(self):
        url = "http://d1h9a8s8eodvjz.cloudfront.net/crossdomain.xml"
        rv = https_url_rewrite(url)
        self._check_no_https(rv)

    def test_cloudfront_net_amp_query(self):
        url = "http://d1h9a8s8eodvjz.cloudfront.net/"
        rv = https_url_rewrite(url)
        self._check_https(rv)

        url = "http://d1h9a8s8eodvjz.cloudfront.net/test.txt?Signature=1234"
        rv = https_url_rewrite(url)
        self._check_https(rv)

        url = "http://d1h9a8s8eodvjz.cloudfront.net/test.txt?a=b&amp;Signature=1234"
        rv = https_url_rewrite(url)
        self._check_https(rv)

        url = "http://d1h9a8s8eodvjz.cloudfront.net/test.txt?a=b&Signature=1234"
        rv = https_url_rewrite(url)
        self._check_no_https(rv)

    def test_target_wildcard_prefix(self):
        url = "http://www.123-reg.co.uk/"
        rv = https_url_rewrite(url)
        self._check_https(rv)

    def test_target_wildcard_tld(self):
        url = "http://maps.google.com.au/"
        rv = https_url_rewrite(url)
        self._check_https(rv)

    def test_www_add_zuerich(self):
        url = "http://zuerich.ch/"
        rv = https_url_rewrite(url)
        self._check_https(rv)
        assert rv == url.replace("http://", "https://www.")

    def test_www_remove_zarunet(self):
        url = "http://www.zarunet.org/"
        rv = https_url_rewrite(url)
        self._check_https(rv)
        assert rv == url.replace("http://www.", "https://")

    @unittest.expectedFailure
    def test_rewrite_with_credentials(self):
        # A test case from the rust library
        url = "http://eff:techprojects@chart.googleapis.com/123"
        rv = https_url_rewrite(url)
        self._check_https(rv)
        # The auth component conflicts with many rules, and also exclusions
        assert rv == "https://eff:techprojects@chart.googleapis.com/123"
