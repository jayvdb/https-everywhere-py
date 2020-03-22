__all__ = ["_reverse_host", "_check_in"]


def _reverse_host(host, trailing_dot=True):
    rv = ".".join(reversed(host.split(".")))
    if trailing_dot:
        return rv + "."
    else:
        return rv


def _check_in(domains, hostname):
    parts = hostname.split(".")
    # Single label names are invalid
    if len(parts) == 1:
        return

    if hostname in domains:
        return hostname

    if parts[-1] in domains:
        return parts[-1]

    if len(parts) > 2:
        subdomain_rule = "{}.{}".format(parts[-2], parts[-1])
        if subdomain_rule in domains:
            return subdomain_rule

    if len(parts) > 3:
        subdomain_rule = "{}.{}.{}".format(parts[-3], parts[-2], parts[-1])
        if subdomain_rule in domains:
            return subdomain_rule

    if len(parts) > 4:
        subdomain_rule = "{}.{}.{}.{}".format(
            parts[-4], parts[-3], parts[-2], parts[-1]
        )
        if subdomain_rule in domains:
            return subdomain_rule
