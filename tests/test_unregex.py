import sre_compile
import sre_parse
import unittest

from sre_parse import LITERAL

from https_everywhere._unregex import expand_pattern, split_regex


class TestExpandRegex(unittest.TestCase):
    def test_start(self):
        rv = list(expand_pattern(r"(image|l)s\.anyoption\.com"))
        assert rv == ["images.anyoption.com", "ls.anyoption.com"]

    def test_middle_alt(self):
        rv = list(expand_pattern(r"ns(0|1|2)\.bdstatic\.com"))
        assert rv == ["ns0.bdstatic.com", "ns1.bdstatic.com", "ns2.bdstatic.com"]

    def test_end_country_codes(self):
        rv = list(expand_pattern(r"scandinavianphoto\.(fi|no|se)"))
        assert rv == [
            "scandinavianphoto.fi",
            "scandinavianphoto.no",
            "scandinavianphoto.se",
        ]

    def test_middle_star(self):
        rv = list(expand_pattern(r"^http://(?:www\.)?([^.]+)\.yandex\.st/"))
        assert rv == ["*.yandex.st", "www.*.yandex.st"]

    def test_start_nested(self):
        rv = list(expand_pattern(r"^http://(?:(milton\.)|www\.)?vtluug\.org/"))
        assert rv == ["vtluug.org", "milton.vtluug.org", "www.vtluug.org"]

    @unittest.expectedFailure
    # A dot is mandatory
    def test_complex_nothing(self):
        rv = list(expand_pattern(r"^http://(www\.)?([\w.]+)/"))
        assert rv == ["www.*", "*"]

    def test_split_none(self):
        rv = split_regex(r"^ab", "/")
        assert isinstance(rv, tuple), rv
        assert isinstance(rv[0], sre_parse.SubPattern), rv
        assert rv[1] is None

    def test_split_one(self):
        rv = split_regex(r"a/b", "/")
        assert isinstance(rv, tuple), rv
        assert isinstance(rv[0], sre_parse.SubPattern), rv
        assert isinstance(rv[1], sre_parse.SubPattern), rv[1].__class__.__name__
        assert rv[0].data == [(sre_parse.LITERAL, ord("a"))]
        assert rv[1].data == [(sre_parse.LITERAL, ord("b"))]

        assert rv[0].pattern is rv[1].pattern

        c0 = sre_compile.compile(rv[0])
        c1 = sre_compile.compile(rv[1])
        assert c0.match("a")
        assert not c0.match("b")
        assert c1.match("b")
        assert not c1.match("a")
        assert c0.pattern is None
        assert c1.pattern is None

    def test_split_multiple(self):
        rv = split_regex(r"a/b/c", "/")
        assert isinstance(rv, tuple), rv
        assert isinstance(rv[0], sre_parse.SubPattern), rv
        assert isinstance(rv[1], sre_parse.SubPattern), rv[1].__class__.__name__
        assert rv[0].data == [(LITERAL, ord("a"))]
        assert rv[1].data == [(LITERAL, ord("b")), (LITERAL, 47), (LITERAL, 99)]

        assert rv[0].pattern is rv[1].pattern

        c0 = sre_compile.compile(rv[0])
        c1 = sre_compile.compile(rv[1])
        assert c0.match("a")
        assert not c0.match("b")
        assert not c1.match("b")
        assert not c1.match("a")
        assert c1.match("b/c")
        assert c0.pattern is None
        assert c1.pattern is None

    def test_split_at(self):
        rv = split_regex(r"^/b", "/")
        assert isinstance(rv, tuple), rv
        assert isinstance(rv[0], sre_parse.SubPattern), rv
        assert isinstance(rv[1], sre_parse.SubPattern), rv[1].__class__.__name__
        assert rv[0].data == [(sre_parse.AT, sre_parse.AT_BEGINNING)]
        assert rv[1].data == [(sre_parse.LITERAL, ord("b"))]

    def test_split_skip_not(self):
        rv = split_regex(r"[^/]a/b", "/")
        assert isinstance(rv, tuple), rv
        assert isinstance(rv[0], sre_parse.SubPattern), rv
        assert isinstance(rv[1], sre_parse.SubPattern), rv[1].__class__.__name__
        assert rv[0].data == [
            (sre_parse.NOT_LITERAL, ord("/")),
            (sre_parse.LITERAL, ord("a")),
        ]
        assert rv[1].data == [(sre_parse.LITERAL, ord("b"))]

    def test_split_min_max(self):
        rv = split_regex(r"a/{1,3}b", "/")
        assert isinstance(rv, tuple), rv
        assert isinstance(rv[0], sre_parse.SubPattern), rv
        assert rv[0].data == [(sre_parse.LITERAL, ord("a"))]
        assert rv[1].data == [(sre_parse.LITERAL, ord("b"))]

    def test_split_plus(self):
        rv = split_regex(r"a/+b", "/")
        assert isinstance(rv, tuple), rv
        assert isinstance(rv[0], sre_parse.SubPattern), rv
        assert rv[0].data == [(sre_parse.LITERAL, ord("a"))]
        assert rv[1].data == [(sre_parse.LITERAL, ord("b"))]

    def test_split_star(self):
        rv = split_regex(r"a/*b", "/")
        assert isinstance(rv, tuple), rv
        assert isinstance(rv[0], sre_parse.SubPattern), rv
        assert rv[0].data == [(sre_parse.LITERAL, ord("a"))]
        assert rv[1].data == [(sre_parse.LITERAL, ord("b"))]

    def test_split_class(self):
        rv = split_regex(r"a[/]b", "/")
        assert isinstance(rv, tuple), rv
        assert isinstance(rv[0], sre_parse.SubPattern), rv
        assert rv[0].data == [(sre_parse.LITERAL, ord("a"))]
        assert rv[1].data == [(sre_parse.LITERAL, ord("b"))]

    def test_split_class2(self):
        rv = split_regex(r"a[(/]b", "/")
        assert isinstance(rv, tuple), rv
        assert isinstance(rv[0], sre_parse.SubPattern), rv
        assert rv[0].data == [(sre_parse.LITERAL, ord("a"))]
        assert rv[1].data == [(sre_parse.LITERAL, ord("b"))]
