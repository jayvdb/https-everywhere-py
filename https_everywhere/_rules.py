from __future__ import unicode_literals

import re
from timeit import default_timer as timer

from cached_property import cached_property
from logging_helper import setup_logging
from urllib3.util.url import parse_url as urlparse

from ._fetch import fetch_update
from ._fixme import (
    # _FIXME_MULTIPLE_RULEST_PREFIXES,
    _FIXME_REJECT_PATTERNS,
    _FIXME_VERY_BAD_EXPANSION,
    _FIXME_ODD_STARS,
    _FIXME_LEADING_STAR_GLOBS,
    _FIXME_BROKEN_REGEX_MATCHES,
    _FIXME_SUBDOMAIN_PREFIXES,
)

try:
    from ._unregex import expand_pattern, ExpansionError
except ImportError:
    expand_pattern, ExpansionError = None, None

logger = setup_logging()

PY2 = str != "".__class__
if PY2:
    str = "".__class__
    expand_pattern = None

# regex sizeof() is broken, and it appears slower;
# real benchmarking needed
# import regex as re

# js_regex should be used instead of `re` however it has some
# critical bugs preventing adoption

_regex_compile = re.compile

_FROM_HTTP = "^http:"
_TO_HTTPS = "https:"
FORCE_HTTPS_RULE_IN = {"from": _FROM_HTTP, "to": _TO_HTTPS}
FORCE_HTTPS_RULE = (_FROM_HTTP, _TO_HTTPS)
FORCE_HTTPS_RULE_COMPILED = (_regex_compile(_FROM_HTTP), _TO_HTTPS)

ONLY_FORCE_HTTPS_RULE_IN = [FORCE_HTTPS_RULE_IN]
ONLY_FORCE_HTTPS_RULE_COMPILED = [FORCE_HTTPS_RULE_COMPILED]
ONLY_FORCE_HTTPS_RULE_COMPILED_NO_EXCEPTIONS = (ONLY_FORCE_HTTPS_RULE_COMPILED, None)

FROM_HTTP_DOMAIN_COMPILED = _regex_compile("^http://([^/]+)/")

REMOVE_WWW_RULE = (_regex_compile("^http://(?:www\\.)?([^/]+)/"), r"https://\g<1>/")
ADD_WWW_RULE = (FROM_HTTP_DOMAIN_COMPILED, r"https://www.\g<1>/")

REMOVE_WWW_and_FORCE_HTTPS_RULES = [REMOVE_WWW_RULE, FORCE_HTTPS_RULE_COMPILED]
ADD_WWW_and_FORCE_HTTPS_RULES = [ADD_WWW_RULE, FORCE_HTTPS_RULE_COMPILED]

_DATA = None

_expected_non_simple_reductions = 4590


def clear_data():
    global _DATA
    _DATA = None


class _Ruleset(object):
    def __init__(self, rules, exclusions, targets=None):
        self._rules = rules
        self._exclusions = exclusions
        self.targets = targets
        self._max_expand_count = 30
        if targets:
            assert rules[0] == FORCE_HTTPS_RULE_COMPILED or isinstance(rules[0][0], str)
            if (
                len(rules) == 1
                and isinstance(rules[0][0], str)
                and (r"\d\d" in rules[0][0] or r"\d+" in rules[0][0])
            ):  # and
                # Allow 100 expansions and a few extra hosts
                self._max_expand_count = 105
            if len(targets) > 100:
                self._max_expand_count = len(targets)
            elif targets and "accounts.google.*" in targets:
                self._max_expand_count = 70

    def __repr__(self):
        return "_Ruleset(targets={}, exclusions={},\n         rules={})\n".format(
            self.targets, self._exclusions, self._rules
        )

    @property
    def exclusions(self):
        if isinstance(self._exclusions, str):
            self._exclusions = _regex_compile(self._exclusions)
        return self._exclusions

    def exclude_url(self, url):
        exclusions = self.exclusions
        # There are a few exclusions like `&Signature=`, so .match() cant be used
        if exclusions and exclusions.search(url):
            return True

    @property
    def rules(self):
        rules = self._rules
        if isinstance(rules[0][0], str):
            rules[:] = [
                (_regex_compile(from_), re.sub(r"\$(\d)", r"\\g<\1>", to))
                for (from_, to) in rules
            ]
        return rules

    @property
    def is_single_force_https_rule(self):
        return self._rules == ONLY_FORCE_HTTPS_RULE_COMPILED

    @property
    def last_rule_is_simple_https_rule(self):
        return self._rules[-1] == FORCE_HTTPS_RULE_COMPILED

    @property
    def _assert_uncompiled(self):
        rules = self._rules
        assert isinstance(rules[0][0], str), self

    @property
    def _single_simple_target(self):
        return len(self.targets) == 1 and "*" not in self.targets[0]

    @property
    def _single_wildcard_target(self):
        return len(self.targets) == 1 and self.targets[0].startswith("*.")

    @property
    def _single_wildcard_domain(self):
        return len(set(item.lstrip(".*") for item in self.targets)) == 1

    @property
    def _shortest_target(self):
        shortest_target = min((len(i), i) for i in self.targets)[1]
        if shortest_target[0] == "*":
            shortest_target = shortest_target[1:]
        return shortest_target


class _Rule(object):
    def __init__(self, pattern, replacement, ruleset):
        self.pattern = pattern
        self.replacement = replacement
        self.ruleset = ruleset

    @property
    def subdomain_match_any(self):
        for prefix in _FIXME_SUBDOMAIN_PREFIXES:
            if self.pattern.startswith("^http://" + prefix):
                return True

    @property
    def pattern_hostname(self):
        # This will return any path in the rule pattern
        return self.pattern.replace("^http://", "").replace(r"\.", ".").strip("/")

    @cached_property
    def pattern_targets(self):
        return expand_pattern(self.pattern, max_count=self.ruleset._max_expand_count)

    @property
    def replacement_hostname(self):
        # This will return any path in the rule replacement
        return (
            self.replacement.replace("https://", "")
            .replace("$1.", "")
            .replace("$1", "")
            .strip("/")
        )

    @property
    def replacement_target(self):
        unregex = self.replacement.replace("$1.", "").replace("$1", "")
        return urlparse(unregex).host

    @property
    def remove_www(self):
        return (
            self.pattern_hostname.startswith("www.")
            and self.pattern_hostname.replace("www.", "") == self.replacement_hostname
        ) or (
            self.pattern_hostname.startswith(r"(?:www.)?")
            and self.pattern_hostname.replace(r"(?:www.)?", "")
            == self.replacement_hostname
        )

    @property
    def add_www(self):
        return self.replacement_hostname.startswith(
            "www."
        ) and self.pattern_hostname == self.replacement_hostname.replace("www.", "")


def _is_rule_only_force_https(ruleset, rule):
    targets = ruleset.targets
    if ruleset._single_simple_target:
        if len(rule.pattern_targets) == 1:
            various_targets = set(
                [
                    rule.pattern_hostname,
                    rule.pattern_targets[0],
                    rule.replacement_hostname,
                    targets[0],
                ]
            )
            if len(various_targets) == 1:
                logger.debug(
                    "{} == {} == {}".format(rule.pattern, targets, rule.replacement)
                )
                return True

            logger.info("mismatch {}".format(sorted(various_targets)))

            if rule.pattern_targets[0] in targets:
                if (
                    rule.pattern_hostname.startswith(rule.pattern_targets[0])
                    and rule.replacement_hostname == targets[0]
                ):
                    # There are 16 of these, and replacement uses the pattern path, so can easily be reduced
                    # by adding an exclusion as inverse regex of the path in the rule (TODO)
                    return False
                if rule.pattern_hostname != rule.replacement_hostname:
                    # 66 hostname redirects, possibly also with path alterations.
                    # many are '.cloudfront.net', '.amazonaws.com', '.rackcdn.com'
                    logger.debug(
                        "rule redirecting {} to different host {}".format(
                            rule.pattern_hostname, rule.replacement_hostname
                        )
                    )
                    return False
                else:
                    # There are five of these, and the pattern and replacement have the same path, so can easily be
                    # reduced by adding an exclusion as inverse regex of the path in the rule
                    logger.info(
                        "{} matches {} but has a path, and is not reducible yet".format(
                            targets, rule.pattern
                        )
                    )
                    return False
            else:  # pragma: no cover
                logger.debug("{} not matches targets {}".format(rule.pattern, targets))
                assert rule.pattern_targets[0] in targets

        return False
    if ruleset._single_wildcard_target:
        # Some hosts are excluded
        if rule.pattern.startswith("^http://(?!"):
            return False
        # A path element is involved ($1 will be subdomain)
        if "$2" in rule.replacement:
            return False

        if len(rule.pattern_targets) == 1 and rule.pattern_targets[0] in targets:
            logger.debug("{} == {}; reducing".format(rule.pattern, targets))
            # ~50 cases
            return True
        return False


def _reduce_ruleset(ruleset):
    if ruleset.is_single_force_https_rule:
        return False

    ruleset._assert_uncompiled
    rules = ruleset._rules
    targets = ruleset.targets

    assert len(rules) >= 1 or not ruleset.last_rule_is_simple_https_rule

    if not ruleset.last_rule_is_simple_https_rule:
        # Just a precaution to simplify cohort
        if len(rules) > 2:
            return False

        last_rule = _Rule(*rules[-1], ruleset=ruleset)
        if _is_rule_only_force_https(ruleset, last_rule):
            logger.warning(
                "{} last rule of {} rules reduced to simple force https".format(
                    ruleset, len(rules)
                )
            )
            ruleset._rules[-1] = FORCE_HTTPS_RULE_COMPILED

    if ruleset.is_single_force_https_rule:
        return True

    if ruleset.last_rule_is_simple_https_rule:
        non_simple_rules = rules[:-1]
    else:
        non_simple_rules = rules

    for item in non_simple_rules:
        from_, to = item
        assert isinstance(from_, str)
        rule = _Rule(from_, to, ruleset)

        try:
            pattern_targets = rule.pattern_targets
        except ExpansionError as e:
            # TypeError occurs if sre_yield 0.2.0 was installed
            logger.info(
                "expansion failure in rule {} {}: {}".format(
                    ruleset.targets, ruleset.rules, e
                )
            )
            return
        except Exception as e:  # pragma: no cover
            logger.warning(
                "unknown failure in rule {} {}: {}".format(
                    ruleset.targets, ruleset.rules, e
                )
            )
            raise
        assert rule.pattern_targets
        assert "" not in rule.pattern_targets

        middle_star_exists = False

        for pat in pattern_targets:
            if pat.startswith(".") or pat.endswith("."):
                logger.info(
                    '{} expands to invalid hostname "{}"'.format(rule.pattern, pat)
                )
                continue

            assert set(pat) - set("(|)") == set(pat)
            assert ".." not in pat
            assert isinstance(pat, str)
            if "*" in pat:
                stripped_pat = pat.strip("*.")
                # dpfile.com has too many patterns
                if set(targets) & _FIXME_VERY_BAD_EXPANSION:
                    middle_star_exists = True
                    logger.info(
                        "* in the middle of {} in {} for {}; some analysis not feasible".format(
                            pat, stripped_pat, rule.pattern
                        )
                    )
                    continue
                if (
                    ".*." in stripped_pat
                    or "-*." in stripped_pat
                    or pat in _FIXME_ODD_STARS
                ):
                    logger.info(
                        "* in the middle of {} in {} for {}; some analysis not feasible".format(
                            pat, stripped_pat, rule.pattern
                        )
                    )
                    middle_star_exists = True
                    continue
                assert (
                    "*" not in stripped_pat
                ), "* incorrectly placed in {} for {}".format(pat, rule.pattern)

            if (
                "*" in pat
                and "*." not in pat
                and ".*" not in pat
                and pat not in _FIXME_LEADING_STAR_GLOBS
            ):  # pragma: no cover
                assert False

        if len(pattern_targets) > ruleset._max_expand_count:  # pragma: no cover
            assert False

        assert rule.pattern_targets is not None and rule.pattern_targets != []

        if "dbs.com" in targets:
            continue  # pattern is `dbs.*` nothing to match with

        pattern_targets = list(rule.pattern_targets)
        for pattern_target in pattern_targets:
            pattern_target = pattern_target.split(":")[0]
            if pattern_target not in targets:
                for target in targets:
                    if target.startswith("*."):
                        target = target.strip("*.")
                        if pattern_target.endswith(target):
                            break
                else:
                    if pattern_target.startswith("*."):
                        logger.warning(
                            "glob {} is used in regex and doesnt appear in targets {}".format(
                                pattern_target, targets
                            )
                        )
                        continue

                    if pattern_target in _FIXME_BROKEN_REGEX_MATCHES:
                        logger.warning(
                            "host {} is used in regex and doesnt appear in targets {}; discarding invalid rule".format(
                                pattern_target, targets
                            )
                        )
                        # TODO: really discard it
                        return

                    if middle_star_exists:
                        continue
                    else:  # pragma: no cover
                        logger.error(
                            "{} expands to {} which is not in {}".format(
                                rule.pattern, pattern_target, targets
                            )
                        )
                        assert pattern_target in targets, "{} not in targets {}".format(
                            pattern_target, targets
                        )

        if len(non_simple_rules) == 1:

            if ruleset._single_simple_target:
                # 163 single simple target rulesets
                target = targets[0]

                # None with pattern and replacement that are the same as target
                assert (
                    target != rule.pattern_hostname
                    or target != rule.replacement_hostname
                )

                if target == rule.pattern_hostname:
                    # ~120 cases
                    ruleset._rules = [(FROM_HTTP_DOMAIN_COMPILED, to)]
                    return True

                # They all have a path, so cant be a simple add/remove www rule
                assert not rule.remove_www
                assert not rule.add_www

            if ruleset.last_rule_is_simple_https_rule:
                if rule.remove_www:
                    # ~500 cases
                    ruleset._rules = REMOVE_WWW_and_FORCE_HTTPS_RULES
                    return True
                elif rule.add_www:
                    # ~1100 cases
                    ruleset._rules = ADD_WWW_and_FORCE_HTTPS_RULES
                    return True

        if (
            rule.subdomain_match_any
            and "*." + rule.replacement_hostname in targets
            and "$1" in rule.replacement
            and "*." + rule.replacement_target in rule.pattern_targets
        ):
            if len(rules) == 2:
                if FORCE_HTTPS_RULE_COMPILED in rules:
                    # Is this rule redundant with existing blanket http->https rule?
                    # 1 case; *.svn.sourceforge.net
                    ruleset._rules = ONLY_FORCE_HTTPS_RULE_COMPILED
                    return True
            elif len(rules) == 1:
                if ruleset._single_wildcard_domain:
                    # ~65 cases
                    ruleset._rules = ONLY_FORCE_HTTPS_RULE_COMPILED
                    return True

    ruleset._rules = rules
    return True


def _reduce_rules(rulesets, check=False, simplify=False):
    if isinstance(rulesets, dict):
        rulesets = rulesets["rulesets"]

    if (check or simplify) and not expand_pattern:
        logger.warning("Rule analysis and simplification only supported on Python 3")
        check = simplify = False

    mapping = {}
    domains = set()
    prefix_targets = set()
    suffix_targets = set()
    simplifications_performed = 0

    logger.info("Importing HTTPSEverywhere rules")
    start = timer()

    for ruleset in rulesets:
        orig_ruleset = ruleset.copy()
        name = ruleset.pop("name")
        exclusions = ruleset.pop("exclusion", [])
        targets = ruleset.pop("target")
        rules = ruleset.pop("rule")
        default_off = ruleset.pop("default_off", False)
        platform = ruleset.pop("platform", None)

        if check:
            securecookie = ruleset.pop("securecookie", [])
            assert not ruleset.keys(), orig_ruleset

            assert isinstance(name, str), orig_ruleset
            if default_off:
                assert isinstance(default_off, str), orig_ruleset

            assert isinstance(targets, list), orig_ruleset
            assert isinstance(rules, list), orig_ruleset
            assert isinstance(securecookie, list)

            assert name, orig_ruleset
            assert targets, orig_ruleset
            assert rules, orig_ruleset
            assert platform in ["mixedcontent", None], orig_ruleset

            assert len(targets) == len(set(targets))
            # Exclusions in the XML are already merged in the JSON
            assert len(exclusions) < 2, exclusions
            if exclusions:
                assert "[^$]" not in exclusions, orig_ruleset

        if platform in ["mixedcontent"]:
            continue

        if default_off:
            continue

        if name in ["1.0.0.1", "1.1.1.1"]:
            continue

        # There is a non-trivial overlap with the Chrome preload list, as
        # HTTPS Everything only purges rulesets when they are also covered
        # by Firefox, so there is some memory saving possible by skipping
        # these HTTPS Everything rulesets.
        # TODO: quantify the overlap and reduce if significant/efficient.
        # Probably determine the overlap once either is updated and store it
        # for quicker processing during reload.

        # https://github.com/EFForg/https-everywhere/issues/18892
        if "accounts.google.com.*" in targets or "www.google.com.*" in targets:
            for item in list(targets):
                if item.endswith("google.com.*") and item.rstrip(".*") not in targets:
                    targets.append(item.rstrip(".*"))

        if not exclusions:
            exclusions = None
        else:
            exclusions = exclusions[0]
            # https://github.com/EFForg/https-everywhere/issues/18873
            # '...|http..' can also occur and is not assisted here
            if exclusions.startswith("http"):
                exclusions = "^" + exclusions

        if check:
            # TODO: compute shortest_target in loop below and move asserts after
            # TODO: use existing rulset.shortest_target
            shortest_target = min((len(i), i) for i in targets)[1]
            if shortest_target.startswith("*"):
                # Remove '*'
                star_target = shortest_target[1:]
            elif "*." + shortest_target in targets:
                star_target = "." + shortest_target
            else:
                star_target = [i for i in targets if i.startswith("*.")]
                if star_target:
                    star_target = min((len(i), i) for i in star_target)[1]
                    # Remove '*'
                    star_target = star_target[1:]
                else:
                    star_target = None

            if star_target:
                # No redundant explicit subdomains should appear
                # Only asserting wrt the shortest base domain
                # TODO: split all targets into groups of base domains for complete check
                redundant_explicit_subdomains = [
                    item
                    for item in targets
                    if item not in [shortest_target, "*" + star_target]
                    and item.endswith(star_target)
                ]
                assert not redundant_explicit_subdomains

            for item in targets:
                assert item[0] != "^", orig_ruleset
                assert "." in item, orig_ruleset
                # '*' should only appear and beginning or end, not both
                assert (item[0], item[-1]) != ("*", "*"), orig_ruleset
                # '*' should not appear elsewhere
                assert "*" not in item[1:-1], orig_ruleset

                if name in ["1.0.0.1", "1.1.1.1"]:
                    continue

                parts = item.split(".")
                assert not all(
                    part.isdigit() or part == "*" for part in parts
                ), orig_ruleset

                # https://github.com/EFForg/https-everywhere/issues/18897
                if "voxmedia.com" not in item:
                    assert item not in domains, (orig_ruleset, mapping[item])

                domains.add(item)

                if item[0] == "*":
                    prefix_targets.add(item[1:])
                elif item[-1] == "*":
                    suffix_targets.add(item[:-1])

            if exclusions:
                _check_regex(exclusions)

            hashable_rules = []
            for item in rules:
                assert set(item.keys()) == set(["from", "to"])

                from_ = item["from"]
                to = item["to"]
                _check_regex(from_)

                # TODO: check why this is being skipped
                if "no-ip.com" in targets:  # pragma: no cover
                    # https://github.com/Zac-HD/js-regex/issues/8
                    # https://github.com/EFForg/https-everywhere/issues/18877
                    assert "[^$]" in rules[1]["from"], orig_ruleset
                    hashable_rules.append((from_, to))
                    continue

                assert "[^$]" not in from_, orig_ruleset

                _check_regex(to, is_to=True)
                assert from_[0] == "^", orig_ruleset
                assert "$10" not in to, orig_ruleset
                assert not to.startswith("http://"), orig_ruleset
                rule = (from_, to)
                assert rule not in hashable_rules
                hashable_rules.append((from_, to))

        # Discard common data
        if rules == ONLY_FORCE_HTTPS_RULE_IN:
            rules = ONLY_FORCE_HTTPS_RULE_COMPILED
            ruleset = rules, exclusions

        elif simplify:
            reduced_rules = []
            original_rule_count = len(rules)
            for item in rules:
                from_ = item["from"]
                if from_ in _FIXME_REJECT_PATTERNS:
                    logger.warning('Rejecting rule with pattern "{}"'.format(from_))
                    continue
                to = item["to"]
                rule = (from_, to)
                reduced_rules.append(rule)

            if not reduced_rules:
                logger.warning(
                    "Rejecting ruleset {} as it has no usable rules".format(name)
                )
                continue

            rules = reduced_rules

            if rules[-1] == FORCE_HTTPS_RULE:
                rules[-1] = FORCE_HTTPS_RULE_COMPILED

            reduced_ruleset = _Ruleset(rules, exclusions, targets)

            _reduce_ruleset(reduced_ruleset)
            final_rule_count = len(reduced_ruleset._rules)
            simplifications_performed += final_rule_count

            ruleset = (reduced_ruleset._rules, reduced_ruleset._exclusions)

        else:
            rules = [(item["from"], item["to"]) for item in rules]
            ruleset = rules, exclusions

        if ruleset == ONLY_FORCE_HTTPS_RULE_COMPILED_NO_EXCEPTIONS:
            ruleset = ONLY_FORCE_HTTPS_RULE_COMPILED_NO_EXCEPTIONS

        for target in targets:
            # https://github.com/EFForg/https-everywhere/issues/18897
            if (
                check
                and name == "Vox Media.com (resources)"
                and target
                in [
                    "voxmedia.com",
                    "marketing.voxmedia.com",
                    "product.voxmedia.com",
                    "www.voxmedia.com",
                ]
                and target in mapping
                and reduced_ruleset.is_single_force_https_rule
            ):
                prior_ruleset = mapping[target]
                assert isinstance(prior_ruleset, tuple)
                if FORCE_HTTPS_RULE_COMPILED in prior_ruleset[0]:
                    continue
                assert False, "vox"  # pragma: no cover
            assert target not in mapping
            mapping[target] = ruleset

    if check:
        for target in sorted(suffix_targets):
            if ".google." not in target and target not in ["google."]:
                assert not any(
                    item != target + "*" and item.startswith(target) for item in domains
                )

        overlapping_prefixes = set()
        for target in sorted(prefix_targets):
            star_target = "*" + target
            for item in domains:
                if item == star_target:
                    continue
                if item.endswith(target):
                    overlapping_prefixes.add(target)
                    break

        # published ruleset also has amazon in it
        # TODO: re-enable or remove when new published ruleset is fixed
        # assert sorted(overlapping_prefixes) == _FIXME_MULTIPLE_RULEST_PREFIXES, sorted(overlapping_prefixes)

    end = timer()
    elapsed = end - start
    simplifications_message = "; {} non-trivial simplifications".format(
        simplifications_performed
    )
    logger.info(
        "Finished importing HTTPSEverywhere rules after {:.2f}s{}".format(
            elapsed, simplifications_message if simplifications_performed else ""
        )
    )

    return mapping


def _check_regex(pattern, is_to=False):
    if pattern in [_FROM_HTTP, _TO_HTTPS]:
        return
    try:
        rv = _regex_compile(pattern)
        assert rv, pattern
    except Exception as e:  # pragma: no cover
        raise RuntimeError("{} failed: {}".format(pattern, e))
    if is_to:
        return
    if re.__name__ == "regex":  # pragma: no cover
        # '^http://www\\.0p\\.no/' is size 352, and so is the largest regex from JS.org.xml
        # Only a few become larger, up to size ~380.  ergo __sizeof__() is broken
        assert (
            len(pattern) < 22 and rv.__sizeof__() < pattern.__sizeof__() * 6
        ) or rv.__sizeof__() < pattern.__sizeof__() * 5, (
            pattern,
            rv.__sizeof__() / pattern.__sizeof__(),
        )
        assert rv.__sizeof__() < 380, (pattern, rv.__sizeof__())
    else:
        # Technische_Universitat_Berlin.xml from is ~8.2 greater than string size
        assert rv.__sizeof__() < pattern.__sizeof__() * 9, (
            pattern,
            rv.__sizeof__() / pattern.__sizeof__(),
        )
        # JS.org.xml has re.compile sizeof 59,000 for len 11441
        # The same regex.compile is size 352
        assert rv.__sizeof__() < 61000, (pattern, rv.__sizeof__())


def _get_rulesets():
    global _DATA
    if not _DATA:
        data = fetch_update()
        _DATA = _reduce_rules(data, simplify=True)
    return _DATA


def _get_ruleset(hostname, rulesets=None):
    if not rulesets:
        rulesets = _get_rulesets()
    exact_match = rulesets.get(hostname)
    if exact_match:
        return exact_match
    dot_pos = hostname.find(".")
    prefix_hostname = "*" + hostname[dot_pos:]
    ruleset = rulesets.get(prefix_hostname)
    if ruleset:
        return ruleset

    # Try tld
    dot_pos = hostname.rfind(".")
    suffix_hostname = hostname[: dot_pos + 1] + "*"
    ruleset = rulesets.get(suffix_hostname)
    if ruleset:
        return ruleset

    parts = hostname.split(".")

    if len(parts) > 5:
        subdomain_rule = "*.{}.{}.{}.{}".format(
            parts[-4], parts[-3], parts[-2], parts[-1]
        )
        ruleset = rulesets.get(subdomain_rule)
        if ruleset:
            return ruleset

    if len(parts) > 4:
        subdomain_rule = "*.{}.{}.{}".format(parts[-3], parts[-2], parts[-1])
        ruleset = rulesets.get(subdomain_rule)
        if ruleset:
            return ruleset

    if len(parts) > 3:
        subdomain_rule = "*.{}.{}".format(parts[-2], parts[-1])
        ruleset = rulesets.get(subdomain_rule)
        if ruleset:
            return ruleset

    logger.debug("no ruleset matches {}".format(hostname))


def https_url_rewrite(url, rulesets=None):
    if isinstance(url, str):
        # In HTTPSEverywhere, URLs must contain a '/'.
        if url.replace("http://", "").find("/") == -1:
            url += "/"
        parsed_url = urlparse(url)
    else:
        parsed_url = url
        if hasattr(parsed_url, "geturl"):
            url = parsed_url.geturl()
        else:
            url = str(parsed_url)

    try:
        ruleset = _get_ruleset(parsed_url.host, rulesets)
    except AttributeError:
        ruleset = _get_ruleset(parsed_url.netloc, rulesets)

    if not ruleset:
        return url

    if not isinstance(ruleset, _Ruleset):
        ruleset = _Ruleset(ruleset[0], ruleset[1])

    if ruleset.exclude_url(url):
        return url

    # process rules
    for rule in ruleset.rules:
        logger.debug("checking rule {} -> {}".format(rule[0], rule[1]))
        try:
            new_url = rule[0].sub(rule[1], url)
        except Exception as e:  # pragma: no cover
            logger.warning(
                "failed during rule {} -> {} , input {}: {}".format(
                    rule[0], rule[1], url, e
                )
            )
            raise

        # stop if this rule was a hit
        if new_url != url:
            return new_url

    return url
