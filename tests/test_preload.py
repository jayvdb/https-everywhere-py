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

    def test_require_force_https(self):
        domains = _preload_including_subdomains()
        self.assertTrue(_check_in(domains, "pinning-test.badssl.com"))
        self.assertTrue(_check_in(domains, "foo.pinning-test.badssl.com"))
        self.assertFalse(_check_in(domains, "foo.pinning-test2.badssl.com"))
        self.assertFalse(_check_in(domains, "pinning-test2.badssl.com"))

        domains = _preload_including_subdomains(require_force_https=True)
        self.assertFalse(_check_in(domains, "pinning-test.badssl.com"))
        self.assertFalse(_check_in(domains, "foo.pinning-test.badssl.com"))

    def test_doubleclick(self):
        domains = _preload_including_subdomains()
        self.assertIn("stats.g.doubleclick.net", domains)

    def test_no_include_subdomains(self):
        domains = _preload_including_subdomains()
        self.assertIn("pinningtest.appspot.com", domains)
        self.assertNotIn("at.search.yahoo.com", domains)

        domains = _preload_including_subdomains(require_force_https=True)
        self.assertNotIn("pinningtest.appspot.com", domains)

    def test_remove_overlap(self):
        domains = _preload_including_subdomains(
            remove_overlap=True, overlap_order_check=True
        )
        self.assertNotIn("www.apollo-auto.com", domains)

    def test_google_unusual(self):
        domains = _preload_including_subdomains()
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
        self.assertTrue(_check_in(domains, "google.ax"))
        self.assertTrue(_check_in(domains, "googleandroid.cz"))
        self.assertTrue(_check_in(domains, "googleshortcuts.org"))
        self.assertTrue(_check_in(domains, "g4w.co"))
        self.assertTrue(_check_in(domains, "foo.g4w.co"))
        self.assertTrue(_check_in(domains, "goo.gl"))
        self.assertTrue(_check_in(domains, "foo.goo.gl"))
        self.assertTrue(_check_in(domains, "xn--7xa.google.com"))
        self.assertTrue(_check_in(domains, "foo.xn--7xa.google.com"))

    def test_google_cctld(self):
        domains = _preload_including_subdomains()
        self.assertTrue(_check_in(domains, "www.google.com.au"))
        self.assertTrue(_check_in(domains, "www.google.co.uk"))
        self.assertTrue(_check_in(domains, "google.cat"))
        self.assertTrue(_check_in(domains, "www.google.cat"))
        self.assertTrue(_check_in(domains, "www.google.com.au"))
        self.assertTrue(_check_in(domains, "accounts.google.co.uk"))

    def test_google_stld(self):
        domains = _preload_including_subdomains()
        self.assertTrue(_check_in(domains, "www.google"))
        self.assertTrue(_check_in(domains, "www.gmail"))
        self.assertTrue(_check_in(domains, "corp.goog"))
        self.assertTrue(_check_in(domains, "foo.corp.goog"))

    def test_google_hosts_not_supported(self):
        domains = _preload_including_subdomains()
        self.assertFalse(_check_in(domains, "g.co"))
        self.assertFalse(_check_in(domains, "www.g.co"))
