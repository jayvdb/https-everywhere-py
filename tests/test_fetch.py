import os.path
import unittest

from https_everywhere._fetch import fetch_channel_ts, fetch_update, _storage_location
from https_everywhere._rules import _reduce_rules, clear_data, _get_rulesets


class TestFetch(unittest.TestCase):
    def setUp(self):
        clear_data()

    def test_storage_location(self):
        rv = _storage_location()
        assert rv == os.path.expanduser("~/.cache/https-everywhere-py")

    def test_channel_timestamp(self):
        rv = fetch_channel_ts()
        assert rv is not None

    def test_channel_fetch(self):
        rv = fetch_update(fetch_channel_ts())
        assert rv is not None
        _reduce_rules(rv)

    def test_get_rulesets(self):
        _get_rulesets()
