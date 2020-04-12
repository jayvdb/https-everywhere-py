from __future__ import unicode_literals

import unittest

from https_everywhere._chrome_preload_hsts import _preload_including_subdomains
from https_everywhere._mozilla_preload_hsts import _preload_remove_negative

from https_everywhere._util import _check_in


class PreloadBase:
    def test_01(self):
        domains = self.get_preload()
        self.assertTrue(_check_in(domains, "01.org"))

    def test_01_www(self):
        domains = self.get_preload()
        self.assertTrue(_check_in(domains, "www.01.org"))

    def test_doubleclick(self):
        domains = self.get_preload()
        self.assertIn("stats.g.doubleclick.net", domains)

    def test_negative(self):
        domains = self.get_preload()
        self.assertNotIn("0007552.com", domains)
        self.assertFalse(_check_in(domains, "0007552.com"))
        self.assertFalse(_check_in(domains, "cn.search.yahoo.com"))
        self.assertFalse(_check_in(domains, "de.search.yahoo.com"))
        self.assertFalse(_check_in(domains, "www.paypal.com"))

    def test_facebook(self):
        domains = self.get_preload()
        self.assertFalse(_check_in(domains, "facebook.com"))
        self.assertTrue(_check_in(domains, "m.facebook.com"))

    def test_google(self):
        domains = self.get_preload()
        self.assertTrue(_check_in(domains, "google.ax"))
        self.assertTrue(_check_in(domains, "googleandroid.cz"))
        self.assertTrue(_check_in(domains, "googleshortcuts.org"))
        self.assertTrue(_check_in(domains, "g4w.co"))
        self.assertTrue(_check_in(domains, "foo.g4w.co"))
        self.assertTrue(_check_in(domains, "goo.gl"))
        self.assertTrue(_check_in(domains, "foo.goo.gl"))
        self.assertTrue(_check_in(domains, "xn--7xa.google.com"))
        self.assertTrue(_check_in(domains, "foo.xn--7xa.google.com"))

    def test_google_stld(self):
        domains = self.get_preload()
        self.assertTrue(_check_in(domains, "www.google"))
        self.assertTrue(_check_in(domains, "www.gmail"))
        self.assertTrue(_check_in(domains, "corp.goog"))
        self.assertTrue(_check_in(domains, "foo.corp.goog"))

    def test_google_hosts_not_supported(self):
        domains = self.get_preload()
        self.assertFalse(_check_in(domains, "g.co"))
        self.assertFalse(_check_in(domains, "www.g.co"))

    def test_remove_overlap(self):
        domains = self.get_preload(remove_overlap=False)
        self.assertIn("nic.android", domains)
        self.assertIn("nic.chrome", domains)
        self.assertIn("nic.youtube", domains)
        self.assertIn("my.usa.gov", domains)
        self.assertIn("backspace.dev", domains)
        self.assertIn("soundmoney.page", domains)

        domains = self.get_preload(remove_overlap=True)
        self.assertNotIn("nic.android", domains)
        self.assertNotIn("nic.chrome", domains)
        self.assertNotIn("nic.youtube", domains)
        self.assertNotIn("my.usa.gov", domains)
        self.assertNotIn("backspace.dev", domains)
        self.assertNotIn("soundmoney.page", domains)


class TestPreloadChrome(unittest.TestCase, PreloadBase):
    def get_preload(self, **kwargs):
        return _preload_including_subdomains(**kwargs)

    def test_google_base(self):
        domains = self.get_preload()
        self.assertTrue(_check_in(domains, "google.com"))

    def test_longest(self):
        domains = self.get_preload()
        self.assertTrue(_check_in(domains, "business.medbank.com.mt"))
        self.assertTrue(_check_in(domains, "foo.business.medbank.com.mt"))
        self.assertFalse(_check_in(domains, "business2.medbank.com.mt"))
        self.assertFalse(_check_in(domains, "foo.business2.medbank.com.mt"))

    def test_require_force_https(self):
        domains = self.get_preload()
        self.assertTrue(_check_in(domains, "pinning-test.badssl.com"))
        self.assertTrue(_check_in(domains, "foo.pinning-test.badssl.com"))
        self.assertFalse(_check_in(domains, "foo.pinning-test2.badssl.com"))
        self.assertFalse(_check_in(domains, "pinning-test2.badssl.com"))

        domains = self.get_preload(require_force_https=True)
        self.assertFalse(_check_in(domains, "pinning-test.badssl.com"))
        self.assertFalse(_check_in(domains, "foo.pinning-test.badssl.com"))

    def test_no_include_subdomains(self):
        domains = self.get_preload()
        self.assertIn("pinningtest.appspot.com", domains)
        self.assertNotIn("at.search.yahoo.com", domains)

        domains = self.get_preload(require_force_https=True)
        self.assertNotIn("pinningtest.appspot.com", domains)

    def test_remove_overlap_with_order_check(self):
        domains = self.get_preload(remove_overlap=True, overlap_order_check=True)
        self.assertNotIn("www.apollo-auto.com", domains)

    def test_google_unusual(self):
        domains = self.get_preload()
        self.assertTrue(_check_in(domains, "www.googlegroups.com"))
        self.assertTrue(_check_in(domains, "googlecommerce.com"))
        self.assertTrue(_check_in(domains, "google.info"))
        self.assertTrue(_check_in(domains, "www.google.info"))
        self.assertTrue(_check_in(domains, "google.it.ao"))
        self.assertTrue(_check_in(domains, "www.google.it.ao"))
        self.assertTrue(_check_in(domains, "google.jobs"))
        self.assertTrue(_check_in(domains, "www.google.jobs"))
        self.assertTrue(_check_in(domains, "google.ne.jp"))
        self.assertTrue(_check_in(domains, "www.google.ne.jp"))
        self.assertTrue(_check_in(domains, "google.net"))
        self.assertTrue(_check_in(domains, "google.off.ai"))
        self.assertTrue(_check_in(domains, "googlesyndication.com"))
        self.assertTrue(_check_in(domains, "googletagmanager.com"))
        self.assertTrue(_check_in(domains, "googletagservices.com"))
        self.assertTrue(_check_in(domains, "googleusercontent.com"))
        self.assertTrue(_check_in(domains, "googlevideo.com"))
        self.assertTrue(_check_in(domains, "google.vu"))
        self.assertTrue(_check_in(domains, "googleweblight.com"))
        self.assertTrue(_check_in(domains, "google.ws"))
        self.assertTrue(_check_in(domains, "gstatic.com"))
        self.assertTrue(_check_in(domains, "gstatic.cn"))
        self.assertTrue(_check_in(domains, "gvt1.com"))
        self.assertTrue(_check_in(domains, "static.googleadsserving.cn"))

    def test_google_cctld(self):
        domains = self.get_preload()
        self.assertTrue(_check_in(domains, "www.google.com.au"))
        self.assertTrue(_check_in(domains, "www.google.co.uk"))
        self.assertTrue(_check_in(domains, "google.cat"))
        self.assertTrue(_check_in(domains, "www.google.cat"))
        self.assertTrue(_check_in(domains, "accounts.google.com.au"))
        self.assertTrue(_check_in(domains, "accounts.google.co.uk"))


class TestPreloadMozilla(unittest.TestCase, PreloadBase):
    def get_preload(self, **kwargs):
        return _preload_remove_negative(**kwargs)

    def test_negative_override(self):
        domains = self.get_preload()
        self.assertFalse(_check_in(domains, "id.fedoraproject.org"))
        # The current algorithm also removes the base domain
        self.assertFalse(_check_in(domains, "fedoraproject.org"))

        # www.paypal.com is also a negative override, in test_negative

        # Two others not supported by Chrome:

        # schokokeks explicit mentioned in
        # https://bugzilla.mozilla.org/show_bug.cgi?id=1387855
        self.assertFalse(_check_in(domains, "config.schokokeks.org"))
        self.assertFalse(_check_in(domains, "schokokeks.org"))
        self.assertFalse(_check_in(domains, "www.tumblr.com"))
        self.assertFalse(_check_in(domains, "tumblr.com"))

    def test_remove_overlap_mozilla(self):
        domains = self.get_preload(remove_overlap=False)
        self.assertIn("app.recurly.com", domains)
        self.assertIn("cdn.ampproject.org", domains)

        domains = self.get_preload(remove_overlap=True)
        self.assertNotIn("app.recurly.com", domains)
        self.assertNotIn("cdn.ampproject.org", domains)
