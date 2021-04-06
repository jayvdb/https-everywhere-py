from urllib3.util.url import parse_url

from .._chrome_preload_hsts import \
    _preload_including_subdomains as _get_preload_chrome
from .._mozilla_preload_hsts import \
    _preload_remove_negative as _get_preload_mozilla
from .._util import _check_in
from ..core import SingleURIReplacer


def apply_HSTS_preload(url, domains):
    p = parse_url(url)
    if p.scheme is not None and p.host is not None and _check_in(domains, p.host):
        new_url = "https:" + url[len(p.scheme) + 1:]
        return new_url
    return url


class HSTSPreloadReplacer(SingleURIReplacer):
    __slots__ = ("preloads",)

    def __init__(self, preloads):
        if preloads is None:
            preloads = _get_preload_mozilla() | _get_preload_chrome()
        self.preloads = preloads

    def __call__(self, ctx):
        prevRes = ctx.res
        ctx.res = apply_HSTS_preload(ctx.res, self.preloads)
        if prevRes != ctx.res:
            ctx.count += 1
