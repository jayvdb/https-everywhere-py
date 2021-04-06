import re
import typing

from urllib3.util.url import parse_url

from . import ReplaceContext, SingleURIReplacer

uri_re_source = "(?:http|ftp):\\/\\/?((?:[\\w-]+)(?::[\\w-]+)?@)?[\\w\\.:(-]+(?:\\/[\\w\\.:(/-]*)?"
uri_re_text = re.compile(uri_re_source)
uri_re_binary = re.compile(uri_re_source.encode("ascii"))


class InBufferReplacer(SingleURIReplacer):
    __slots__ = ("singleURIReplacer",)
    FACS = None

    def __init__(self, **kwargs):
        self.singleURIReplacer = self.__class__.FACS(**kwargs)

    def _rePlaceFuncCore(self, uri):
        ctx = ReplaceContext(uri)
        self.singleURIReplacer(ctx)
        return ctx

    def _rePlaceFuncText(self, m):
        uri = m.group(0)
        ctx = self._rePlaceFuncCore(uri)
        if ctx.count > 0:
            return ctx.res
        return uri

    def _rePlaceFuncBinary(self, m):
        uri = m.group(0)
        ctx = self._rePlaceFuncCore(uri.decode("utf-8"))
        if ctx.count > 0:
            return ctx.res.encode("utf-8")
        return uri

    def __call__(self, inputStr: typing.Union[str, bytes]) -> ReplaceContext:
        if isinstance(inputStr, str):
            return ReplaceContext(*uri_re_text.subn(self._rePlaceFuncText, inputStr))
        else:
            return ReplaceContext(*uri_re_binary.subn(self._rePlaceFuncBinary, inputStr))
