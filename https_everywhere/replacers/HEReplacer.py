from .. import _rules
from .._rules import _get_rulesets, https_url_rewrite
from ..core import SingleURIReplacer


class HEReplacer(SingleURIReplacer):
    __slots__ = ("rulesets",)

    def __init__(self, rulesets):
        if rulesets is None:
            _get_rulesets()
            rulesets = _rules._DATA
        self.rulesets = rulesets

    def __call__(self, ctx):
        prevRes = ctx.res
        ctx.res = https_url_rewrite(ctx.res, self.rulesets)
        if prevRes != ctx.res:
            ctx.count += 1
