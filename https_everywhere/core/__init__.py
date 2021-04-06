from functools import partial


class ReplaceContext:
    __slots__ = ("res", "shouldStop", "count")

    def __init__(self, res, count=0, shouldStop=False):
        self.res = res
        self.shouldStop = shouldStop
        self.count = count


class SingleURIReplacer:
    def __init__(self, arg):
        raise NotImplementedError

    def __call__(self, ctx):
        raise NotImplementedError


class CombinedReplacer(SingleURIReplacer):
    __slots__ = ("children",)

    def __init__(self, children):
        self.children = children

    def __call__(self, ctx):
        for r in self.children:
            r(ctx)
            if ctx.shouldStop:
                break
        return ctx


class CombinedReplacerFactory:
    __slots__ = ("args2Ctors", "ctor")

    def __init__(self, args2Ctors):
        self.args2Ctors = args2Ctors

    def _gen_replacers(self, kwargs):
        for k, v in kwargs.items():
            c = self.args2Ctors.get(k, None)
            if c:
                yield c(v)

    def __call__(self, **kwargs):
        return CombinedReplacer(tuple(self._gen_replacers(kwargs)))
