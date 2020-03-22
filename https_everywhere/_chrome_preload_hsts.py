import json
import logging
import os.path

import requests

from logging_helper import setup_logging

from ._fetch import _storage_location
from ._util import _check_in, _reverse_host

logger = setup_logging()

_github_url = "https://raw.githubusercontent.com/chromium/chromium/master/net/http/transport_security_state_static.json"


def _fetch_preload():
    filename = _storage_location("transport_security_state_static.json")
    if os.path.exists(filename):
        return filename

    r = requests.get(_github_url)

    with open(filename, "w") as f:
        f.write(r.text)

    return filename


def _load_preload_data(filename):
    with open(filename) as f:
        lines = [line for line in f.readlines() if not line.lstrip().startswith("/")]
        raw = "\n".join(lines)
        data = json.loads(raw)
        return data


def _preload_including_subdomains(
    remove_overlap=False, require_force_https=False, overlap_order_check=False
):
    filename = _fetch_preload()
    data = _load_preload_data(filename)
    data = data["entries"]
    domains = set()
    entries = {}
    overlap_entries = {"googlegroups.com", "dropbox.com", "appspot.com"}

    for entry in data:
        name = entry["name"]
        if remove_overlap:
            reversed_name = _reverse_host(name)
            assert reversed_name not in entries
            entries[reversed_name] = entry

        mode = entry.get("mode")
        force_https = mode == "force-https"
        if force_https:
            pass
        elif not mode:
            assert entry.get("expect_ct") or entry.get("pins")
            if require_force_https:
                continue
        else:
            raise AssertionError("Unknown mode {}".format(mode))

        includeSubdomains = entry.get("include_subdomains")

        if not includeSubdomains:
            logger.info(
                "{}: Ignoring !include_subdomains entry: {!r}".format(name, entry)
            )
            continue

        if remove_overlap and overlap_order_check:
            base = _check_in(domains, name)
            if base:
                if base in overlap_entries:
                    func = logger.info if base == "appspot.com" else logger.warning
                    func(
                        "{}: covered by prior rule {}\n{!r}\n{!r}".format(
                            name, base, entry, entries[_reverse_host(base)]
                        )
                    )
                else:
                    logger.error(
                        "Unexpected {} base {} already seen; please raise an issue: {!r}".format(
                            name, base, entry
                        )
                    )
                continue

        parts = name.split(".")
        assert (
            len(parts) < 5
        ), "{} ({}) has too many parts for _check_in to work".format(name, parts[-2:])

        domains.add(name)

    if remove_overlap:
        previous = ""
        previous_data = None
        for item in sorted(entries.keys()):
            entry = entries[item]
            if not previous or previous not in item:
                previous = item
                previous_entry = entry
                continue

            name = entry["name"]
            if previous.startswith("com.appspot."):
                # https://bugs.chromium.org/p/chromium/issues/detail?id=568378
                if name in domains:
                    domains.remove(name)
                continue

            if not previous_entry.get("include_subdomains"):
                continue
            if not entry.get("include_subdomains"):
                continue
            if (
                entry.get("mode") != "force-https"
                or previous_entry.get("mode") != "force-https"
            ):
                continue
            if entry.get("pins") and entry["pins"] != previous_entry.get("pins"):
                continue

            func = logger.info if previous in overlap_entries else logger.warning
            func(
                "{}: covered by latter rule {}: (first only; log level info may show more)\n{!r}\n{!r}".format(
                    name, previous_entry["name"], entry, previous_entry
                )
            )
            overlap_entries.add(item)
            overlap_entries.add(previous)
            if name in domains:
                domains.remove(name)

    return domains
