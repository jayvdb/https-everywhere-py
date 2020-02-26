import gzip
import io
import json
import os
import os.path

import appdirs
import requests

base_url = "https://www.https-rulesets.org/v1/"
_ts = None


def _storage_location(filename=None, timestamp=None):
    cache_dir = appdirs.user_cache_dir("https-everywhere-py")
    try:
        os.makedirs(cache_dir, exist_ok=True)
    except TypeError:
        try:
            os.makedirs(cache_dir)
        except (IOError, OSError):
            pass

    if timestamp:
        filename = "default.rulesets.{}".format(timestamp)

    if filename:
        return os.path.join(cache_dir, filename)

    return cache_dir


def fetch_channel_ts():
    ruleset_ts_url = base_url + "latest-rulesets-timestamp"
    r = requests.get(ruleset_ts_url)
    r.raise_for_status()
    ts_string = r.text
    return int(ts_string)


def _get_local_ts():
    global _ts
    if not _ts:  # pragma: no cover
        _ts = fetch_channel_ts()
    return _ts


def _get_local(timestamp=None):
    if not timestamp:
        timestamp = _get_local_ts()  # pragma: no cover
    location = _storage_location(timestamp=timestamp)
    if os.path.exists(location):
        with open(location) as f:
            return json.load(f)


def fetch_update(timestamp=None):
    if not timestamp:  # pragma: no cover
        timestamp = _get_local_ts()
    data = _get_local(timestamp)
    if data:
        return data
    ruleset_url = "{}rulesets-signature.{}.sha256".format(base_url, timestamp)
    r = requests.get(ruleset_url)
    r.raise_for_status()
    ruleset_url = "{}default.rulesets.{}.gz".format(base_url, timestamp)
    r = requests.get(
        ruleset_url, headers={"Accept-Encoding": "gzip, deflate, br"}, stream=True
    )
    r.raise_for_status()
    location = _storage_location(timestamp=timestamp)
    try:
        data = gzip.GzipFile(fileobj=r.raw).read()
    except Exception:
        # r.raw (urllib3.Response) doesnt implement buffer interface
        data = gzip.GzipFile(fileobj=io.BytesIO(r.raw.read())).read()
    with open(location, "wb") as f:
        f.write(data)
    try:
        return json.loads(data)
    except TypeError:
        return json.loads(data.decode("utf-8"))
