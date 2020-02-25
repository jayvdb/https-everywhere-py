import json
import logging
import os.path

import requests

from logzero import setup_logger

from ._fetch import _storage_location

logger = setup_logger(name="httpseverwhere.preload", level=logging.INFO)

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


def _preload_including_subdomains():
    filename = _fetch_preload()
    data = _load_preload_data(filename)
    data = data["entries"]
    domains = set()

    for entry in data:
        name = entry["name"]
        if "." not in name:
            continue
        includeSubdomains = entry.get("include_subdomains")
        if not includeSubdomains:
            continue

        pos = name.rfind(".", 1)
        pos = name.rfind(".", 1, pos)
        if pos != -1:
            check_domain = name[pos + 1 :]
            if check_domain in domains:
                logger.debug(
                    "{} base {} already in the list".format(name, check_domain)
                )
                continue

        parts = name.split(".")
        if name in ["stats.g.doubleclick.net"]:
            continue
        if parts[-2:] == ["google", "com"]:
            continue
        assert len(parts) < 5, "{} ({}) is very long and {} not found".format(
            name, parts[-2:], check_domain
        )

        domains.add(name)

    return domains
