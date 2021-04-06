import os.path

import requests

from .logging import setup_logging
from ._fetch import _storage_location
from ._util import _check_in, _reverse_host

logger = setup_logging()

_hg_url = "https://hg.mozilla.org/releases/mozilla-{version}/raw-file/tip/security/manager/ssl/nsSTSPreloadList.inc"
_VERSIONS = ["beta", "release"]


def _fetch_preload(version="release"):
    filename = _storage_location(_hg_url, version)
    if os.path.exists(filename):
        return filename

    r = requests.get(_hg_url.format(version=version))
    r.raise_for_status()

    with open(filename, "w") as f:
        f.write(r.text)

    return filename


def _load_preload_data(filename):
    with open(filename) as f:
        positive = set()
        negative = set()
        lines = [line.strip() for line in f.readlines()]
        start = lines.index("%%")
        lines = lines[start + 1 :]
        end = lines.index("%%")
        lines = lines[:end]
        for line in lines:
            name, flag = line.split(",")
            name = name.strip()
            if flag.strip() == "1":
                positive.add(name)
            else:
                negative.add(name)
        return positive, negative


def _preload_remove_negative(remove_overlap=False):
    filename = _fetch_preload()
    domains, negative = _load_preload_data(filename)

    for name in negative:
        rv = _check_in(domains, name)
        if rv:
            logger.warning("Removing {} because of negative {}".format(rv, name))
            domains.remove(rv)

    if remove_overlap:
        entries = {}
        for name in domains:
            reversed_name = _reverse_host(name)
            assert reversed_name not in entries
            entries[reversed_name] = name

        previous = ""
        for item in sorted(entries.keys()):
            entry = entries[item]
            if not previous or previous not in item:
                previous = item
                continue

            domains.remove(entry)
            logger.warning(
                "Removing {} because of base domain {}".format(entry, entries[previous])
            )

    return domains
