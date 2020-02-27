# https-everywhere : Privacy for Pythons

![Codecov](https://img.shields.io/codecov/c/gh/jayvdb/https-everywhere-py)
![AppVeyor CI](https://img.shields.io/appveyor/build/jayvdb/https-everywhere-py)
![Cirrus CI](https://img.shields.io/cirrus/github/jayvdb/https-everywhere-py)

This project primarily provides [requests](https://github.com/psf/requests/) adapters for Chrome [HSTS Preload](http://hstspreload.org/) and [HTTPS Everywhere](https://github.com/EFForg/https-everywhere) rulesets.

At this stage, the focus is on correct efficient loading of the approx 25,000 rulesets of HTTPS Everywhere for use with any requests.
Emphasis is on converting those rulesets to simpler or more common rules to reduce memory requirements.

Current list of data problems can be found in `https_everywhere/_fixme.py`.  Many of these have patches sent upstream to the main HTTPS Everywhere project.

## Usage

```py
from https_everywhere.session import HTTPSEverywhereSession

s = HTTPSEverywhereSession()
r = s.get("http://freerangekitten.com/")
r.raise_for_status()

assert r.url == "https://freerangekitten.com/"
assert len(r.history) == 1
assert r.history[0].status_code == 302
assert r.history[0].reason == "HTTPS Everywhere"
```

The log will emit
```console
[W 200226 09:40:55 _rules:632] Rejecting rule with pattern "^http://ww2\.epeat\.com/"
[W 200226 09:40:55 _rules:640] Rejecting ruleset EPEAT (partial) as it has no usable rules
[W 200226 09:40:55 _rules:632] Rejecting rule with pattern "^http://(?:dashboard(?:-cdn)?|g-pixel|pixel|segment-pixel)\.invitemedia\.com/"
[W 200226 09:40:55 _rules:632] Rejecting rule with pattern "^http://((?:a[lt]|s|sca)\d*|www)\.listrakbi\.com/"
[W 200226 09:40:55 _rules:640] Rejecting ruleset ListrakBI.com as it has no usable rules
[W 200226 09:40:55 _rules:632] Rejecting rule with pattern "^http://demo\.neobookings\.com/"
[W 200226 09:40:55 _rules:632] Rejecting rule with pattern "^http://(www\.)?partners\.peer1\.ca/"
[W 200226 09:40:55 _rules:640] Rejecting ruleset Peer1.ca (partial) as it has no usable rules
[W 200226 09:40:55 _rules:632] Rejecting rule with pattern "^http://support\.pickaweb\.co\.uk/(assets/)"
[W 200226 09:40:55 _rules:632] Rejecting rule with pattern "^http://www\.svenskaspel\.se/"
[W 200226 09:40:55 _rules:632] Rejecting rule with pattern "^http://cdn\.therepublic\.com/"
[W 200226 09:40:55 _rules:640] Rejecting ruleset The Republic (partial) as it has no usable rules
```

### Adapters

There are many adapters in https_everywhere.adapter which can be used depending on use cases.

Adapters can be mounted on 'http://', or a narrower mount point.

* HTTPBlockAdapter - Mount on 'http://' to block HTTP traffic
* HTTPRedirectBlockAdapter - Mount on 'https://' to block HTTPS responses redirecting to HTTP
* HTTPSEverywhereOnlyAdapter - Apply HTTPS Everywhere rules
* ChromePreloadHSTSAdapter - Upgrade to HTTPS for sites on Chrome preload list
* HTTPSEverywhereAdapter - Chrome preload hsts and https everywhere rules combined
* ForceHTTPSAdapter - Just use HTTPS, always, everywhere
* PreferHTTPSAdapter - Check HTTP if there are any redirects, before switching to HTTPS.
* UpgradeHTTPSAdapter - Force HTTPS, but fall back to HTTP when HTTPS problems occur.
* SafeUpgradeHTTPSAdapter - First check HTTP if there are any redirects, force HTTPS, and fallback to HTTP.

## Testing

To test

```sh
git clone https://github.com/jayvdb/https-everywhere-py
git clone https://github.com/EFForg/https-everywhere  # possibly use --depth 1
cd https-everywhere-py
tox
```
(Note: `test_rules` takes a long time to begin.)

## Not implemented

- custom local ruleset channels
- cookie support
- credentials in urls, such as `http://eff:techprojects@chart.googleapis.com/`,
  which interfers with many rules, and also prevents exclusions from being applied
- efficient memory structure for target mapping
- rules with `@platform='mixedcontent'`; approx 800 rulesets ignored
- rules with `@default_off`; approx 300 rulesets ignored, but all are mixedcontent
- ruleset targets containing wildcards in the middle of the domain names (`foo.*.com`), which doesnt exist in the default channel
- ruleset targets containing a wildcard at beginning and end (`*.foo.*`), which doesnt exist in the default channel
- overlapping rules, which only applies to voxmedia.com in the default channel when filtered to exclude rules with `@default_off` and `@platform`.
- rules for IPs; there are two 1.0.0.1 and 1.1.1.1 in the default channel. See https://en.wikipedia.org/wiki/1.1.1.1
