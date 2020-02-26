from __future__ import unicode_literals

import os.path
import unittest
import sys

from https_everywhere._fetch import fetch_channel_ts, fetch_update, _storage_location
from https_everywhere._rules import _reduce_rules, clear_data, _get_rulesets


class TestFetch(unittest.TestCase):
    def setUp(self):
        clear_data()

    def test_storage_location(self):
        rv = _storage_location()
        if sys.platform == "win32":
            self.assertTrue(rv.endswith("https-everywhere-py\\Cache"))
        elif sys.platform == "darwin":
            self.assertTrue(rv.endswith("/Caches/https-everywhere-py"))
        else:
            self.assertEqual(rv, os.path.expanduser("~/.cache/https-everywhere-py"))

    def test_channel_timestamp(self):
        rv = fetch_channel_ts()
        self.assertIsNotNone(rv)

    def test_channel_fetch(self):
        rv = fetch_update(fetch_channel_ts())
        self.assertIsNotNone(rv)
        _reduce_rules(rv)

    def test_get_rulesets(self):
        _get_rulesets()
