from __future__ import unicode_literals

import glob
import json
import os.path
import sys
import unittest

from unittest_expander import foreach, expand

from https_everywhere._rules import https_url_rewrite, _reduce_rules
from https_everywhere._fixme import _FIXME_INCORRECT_TEST_URLS

PY2 = str != "".__class__
if PY2:
    str = "".__class__

project_root = os.path.join(os.path.dirname(__file__), "..")
https_everything_project = os.path.join(project_root, "..", "https-everywhere")

if not os.path.exists(https_everything_project):
    raise unittest.SkipTest(
        "Clone https-everywhere beside https-everywhere-py to run rule tests"
    )

https_everywhere_checker_root = os.path.join(
    https_everything_project, "test", "rules", "src"
)
https_everywhere_checker_root_init = os.path.join(
    https_everywhere_checker_root, "https_everywhere_checker", "__init__.py"
)

if not os.path.exists(https_everywhere_checker_root_init):
    with open(https_everywhere_checker_root_init, "w") as f:
        f.write("")

sys.path.append(https_everywhere_checker_root)

try:
    from lxml import etree
    from https_everywhere_checker.rules import Ruleset, Rule
except ImportError as e:
    raise unittest.SkipTest("https_everywhere_checker not importable: {}".format(e))

rules_path = os.path.join(
    https_everything_project, *("src/chrome/content/rules".split("/"))
)
ruleset_file = os.path.join(rules_path, "default.rulesets")

if not os.path.exists(ruleset_file):
    os.chdir(https_everything_project)
    os.system("{} utils/merge-rulesets.py".format(sys.executable))
    os.chdir(project_root)

_upstream_reduced = None
_run_check = True

xmlFnames = sorted(glob.glob(os.path.join(rules_path, "*.xml")))

assert xmlFnames

rulesets = {}

for xmlFname in xmlFnames:
    ruleset = Ruleset(etree.parse(open(xmlFname, "rb")).getroot(), xmlFname)
    rulesets[ruleset.name] = ruleset


def _get_enabled_rulesets():
    return [
        ruleset.name
        for ruleset in rulesets.values()
        if not ruleset.defaultOff
        and ruleset.platform == "default"
        and ruleset.name not in ["1.0.0.1", "1.1.1.1"]
    ]


def _load_upstream_reduced_rulesets():
    global _upstream_reduced

    if _upstream_reduced:
        return _upstream_reduced

    with open(ruleset_file) as f:
        _upstream_data = json.load(f)
        _upstream_reduced = _reduce_rules(
            _upstream_data, check=_run_check, simplify=True
        )
        return _upstream_reduced


@expand
class TestRules(unittest.TestCase):
    def _check_https(self, url):
        self.assertIsNotNone(url)
        self.assertIsInstance(url, str)
        self.assertTrue(url.startswith("https://"))

    def _check_no_https(self, url):
        self.assertIsNotNone(url)
        self.assertIsInstance(url, str)
        self.assertTrue(url.startswith("http://"))

    def _check_ruleset(self, ruleset, url=None):
        reduced_rulesets = _load_upstream_reduced_rulesets()
        for test in ruleset.tests:
            if url and test.url != url:
                continue

            applier = ruleset.whatApplies(test.url)
            rv = https_url_rewrite(test.url, rulesets=reduced_rulesets)
            expect_https = isinstance(applier, Rule)
            if test.url in _FIXME_INCORRECT_TEST_URLS:
                expect_https = not expect_https

            if expect_https:
                self._check_https(rv)
            else:
                self._check_no_https(rv)

    @foreach(_get_enabled_rulesets())
    def test_package(self, name):
        ruleset = rulesets[name]
        self._check_ruleset(ruleset)

    def _test_rules(self):
        for ruleset in rulesets.values():
            if ruleset.defaultOff or ruleset.platform != "default":
                continue
            try:
                self._check_ruleset(ruleset)
            except Exception as e:
                print(
                    'failure in "{}" ({}): {}'.format(ruleset.name, ruleset.filename, e)
                )
                raise

    def _test_rule_aws(self):
        ruleset = rulesets["AmazonWebServices"]
        self._check_ruleset(
            ruleset, "http://s3.lbrcdn.net.s3-external-3.amazonaws.com/"
        )

    def test_rule_google_deep(self):
        ruleset = rulesets["Google.com Subdomains"]
        self._check_ruleset(ruleset, "http://next.dasher-qa.corp.google.com/")

    def test_rule_google_tld(self):
        ruleset = rulesets["Google.tld Subdomains"]
        self._check_ruleset(ruleset)

    def test_rule_google_main(self):
        ruleset = rulesets["Google"]
        self._check_ruleset(ruleset)

    def test_rule_greek_travel(self):
        ruleset = rulesets["Greek-travel"]
        self._check_ruleset(ruleset)

    def test_rule_indymedia(self):
        ruleset = rulesets["Indymedia.org (partial)"]
        self._check_ruleset(ruleset)

    def test_rule_vox(self):
        ruleset = rulesets["Vox Media.com (partial)"]
        self._check_ruleset(ruleset, "http://marketing.voxmedia.com/")
        self._check_ruleset(ruleset, "http://www.voxmedia.com/")
        self._check_ruleset(ruleset, "http://voxmedia.com/")
        self._check_ruleset(ruleset, "http://product.voxmedia.com/")

    def test_rule_vox_overlap(self):
        ruleset = rulesets["Vox Media.com (resources)"]
        self._check_ruleset(ruleset, "http://marketing.voxmedia.com/")

    # https://github.com/EFForg/https-everywhere/issues/18891
    def test_rule_rother(self):
        ruleset = rulesets["Rother.gov.uk (partial)"]
        self._check_ruleset(
            ruleset,
            "http://hub.rother.gov.uk/RotherPortal/ServiceForms/BrownBinForGardenWasteFrm.aspx",
        )

    def test_ports(self):
        ruleset = rulesets["W3C-test.org"]
        self._check_ruleset(ruleset)

        ruleset = rulesets["LBP.me"]
        self._check_ruleset(ruleset)

        ruleset = rulesets["hostalite.com"]
        self._check_ruleset(ruleset)

        ruleset = rulesets["MIT.edu (partial)"]
        self._check_ruleset(ruleset)

        ruleset = rulesets["Unwanted Witness.or.ug"]
        self._check_ruleset(ruleset)

        ruleset = rulesets["Verizon.com (partial)"]
        self._check_ruleset(ruleset)

        ruleset = rulesets["adtomafusion.com"]
        self._check_ruleset(ruleset)
