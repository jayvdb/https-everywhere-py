# https-everywhere : Privacy for Pythons

This project primarily provides requests adapters for Chrome [HSTS Preload](http://hstspreload.org/) and [HTTPS Everywhere](https://github.com/EFForg/https-everywhere) rulesets.

At this stage, the focus is on correct efficient loading of the approx 25,000 rulesets of HTTPS Everywhere for use with any requests.
Emphasis is on converting those rulesets to simpler or more common rules to reduce memory requirements.

Current list of data problems can be found in `https_everywhere/_fixme.py`.  Many of these have patches sent upstream to the main HTTPS Everywhere project.

## Testing

To test

```sh
git clone https://github.com/jayvdb/https-everywhere-py
git clone https://github.com/EFForg/https-everywhere
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
