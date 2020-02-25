def _check_in(domains, hostname):
    if hostname in domains:
        return True

    parts = hostname.split(".")

    if len(parts) > 2:
        subdomain_rule = "{}.{}".format(parts[-2], parts[-1])
        if subdomain_rule in domains:
            return True

    if len(parts) > 3:
        subdomain_rule = "{}.{}.{}".format(parts[-3], parts[-2], parts[-1])
        if subdomain_rule in domains:
            return True

    if len(parts) > 4:
        subdomain_rule = "{}.{}.{}.{}".format(
            parts[-4], parts[-3], parts[-2], parts[-1]
        )
        if subdomain_rule in domains:
            return True
