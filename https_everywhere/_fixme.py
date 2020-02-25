# These cause basic assumptions needed very early in analysis to fail,
# or bad data not yet detected and rejected.
# Entries here may also need an entry in _FIXME_INCORRECT_TEST_URLS below
# to account for the rejection.
_FIXME_REJECT_PATTERNS = [
    r"^http://demo\.neobookings\.com/",
    r"^http://www\.svenskaspel\.se/",
    # https://github.com/EFForg/https-everywhere/issues/18886 :
    r"^http://support\.pickaweb\.co\.uk/(assets/)",
    # PR submitted
    r"^http://((?:a[lt]|s|sca)\d*|www)\.listrakbi\.com/",
    r"^http://(www\.)?partners\.peer1\.ca/",
    r"^http://(?:dashboard(?:-cdn)?|g-pixel|pixel|segment-pixel)\.invitemedia\.com/",
    # merged
    r"^http://ww2\.epeat\.com/",
    r"^http://cdn\.therepublic\.com/",
]

_FIXME_BROKEN_REGEX_MATCHES = [
    "affili.de",
    "www.belgium.indymedia.org",
    "m.aljazeera.com",
    "atms00.alicdn.com",
    "i06.c.aliimg.com",
    "allianz-fuercybersicherheit.de",
    "statics0.beauteprivee.fr",
    "support.bulletproofexec.com",
    "wwwimage0.cbsstatic.com",
    "cdn0.colocationamerica.com",
    "www.login.dtcc.edu",
    "ejunkie.com",
    "e-rewards.com",
    "member.eurexchange.com",
    "4exhale.org",
    "na0.www.gartner.com",
    "blog.girlscouts.org",
    "lh0.google.*",  # fixme
    "nardikt.org",
    ".instellaplatform.com",
    "m.w.kuruc.org",
    "search.microsoft.com",
    "static.millenniumseating.com",
    "watchdog.mycomputer.com",
    "a0.ec-images.myspacecdn.com",
    "a0.mzstatic.com",
    "my.netline.com",
    "img.e-nls.com",
    "x.discover.oceaniacruises.com",
    "www.data.phishtank.com",
    "p00.qhimg.com",
    "webassetsk.scea.com",
    "s00.sinaimg.cn",
    "mosr.sk",
    "sofurryfiles.com",
    "asset-g.soupcdn.com",
    "cdn00.sure-assist.com",
    "www.svenskaspel.se",
    "mail.telecom.sk",
    "s4.thejournal.ie",
    "my.wpi.edu",
    "stec-t*.xhcdn.com",  # fixme
    "www.*.yandex.st",  # fixme
    "s4.jrnl.ie",
    "b2.raptrcdn.com",
    "admin.neobookings.com",
    "webmail.vipserv.org",
    "ak0.polyvoreimg.com",
    "cdn.fora.tv",
    "cdn.vbseo.com",
    "edge.alluremedia.com",
    "secure.trustedreviews.com",
    "icmail.net",
    "www.myftp.utechsoft.com",
    "research-store.com",
    "app.sirportly.com",
    "ec7.images-amazon.com",
    "help.npo.nl",
    "css.palcdn.com",
    "legacy.pgi.com",
    "my.btwifi.co.uk",
    "orders.gigenetcloud.com",
    "owa.space2u.com",
    "payment-solutions.entropay.com",
    "static.vce.com",
    "itpol.dk",
    "orionmagazine.com",
    # fix merged, not distributed
    "citymail.com",
    "mvg-mobile.de",
    "inchinashop.com",
    "www.whispergifts",
    # already merged?
    "css.bzimages.com",
    "cdn0.spiegel.de",
]

_FIXME_LEADING_STAR_GLOBS = [
    "*-d.openxenterprise.com",
    "*sfx.hosted.exlibrisgroup.com",
    "*-async.olark.com",
]

_FIXME_ODD_STARS = [
    "go*.imgsmail.ru",
    "img*.imgsmail.ru",
    "my*.imgsmail.ru",
    "secure*.inmotionhosting.com",
    "www.secure*.inmotionhosting.com",
    "whm*.louhi.net",
    "*.r*.cf*.rackcdn.com",
    "*.ssl.cf*.rackcdn.com",
    "*.la*.salesforceliveagent.com",
    "di*.shoppingshadow.com",
    "img*.www.spoki.lv",
    "mysql*.tal.de",
    "clk*.tradedoubler.com",
    "imp*.tradedoubler.com",
    "star*.tradedoubler.com",
    "web.facilities!*.nss.udel.edu",  # fixme
    "vg*.met.vgwort.de",
    "ssl-vg*.met.vgwort.de",
    # PR sent
    "stec-t*.xhcdn.com",
    "p*.qhimg.com",
    "webassets*.scea.com",
    "s*.sinaimg.cn",
    "cdn*.sure-assist.com",
    # '(i|j|m|si|t)*.dpfile.com',  # see below
]

_FIXME_VERY_BAD_EXPANSION = set(["*.dpfile.com"])

_FIXME_MULTIPLE_RULEST_PREFIXES = [
    ".actionkit.com",
    ".bbb.org",
    ".blogspot.com",
    ".bloxcms.com",
    ".cachefly.net",
    ".force.com",
    ".google.com",
    ".icann.org",
    ".lumension.com",
    ".maine.edu",
    ".my.com",
    ".ou.edu",
    ".pbworks.com",
    ".photobucket.com",
    ".sec.s-msft.com",
    ".topcoder.com",
    ".utwente.nl",
    ".uva.nl",
    ".vo.msecnd.net",
    ".which.co.uk",
    ".wpengine.com",
]

# These should all end with .
_FIXME_SUBDOMAIN_PREFIXES = (
    r"([^.]+)\.",
    r"([A-Za-z]+\.)?",
    r"([.]+)\.",
    r"([\w]+)\.",
    r"(?:\w+\.)?",
    r"([\w-]+)\.",
    r"([\w-]+\.)?",
    r"([\w-]+\.)",
    r"([\w\-])\.",  # rsys.net, matches single char, probably broken
    r"([\w\-]+)\.",
    r"([\w.-]+)\.",  # Allows a.b.
    r"([^@:/]*)\.",  # adverticum.net
    r"([^/:@]+\.)?",  # atlantic.net
    r"([^/:@]+)\.",  # 16personalities; single char
    r"([^/:@\.]+)\.",  # cibc.com, stevens.edu
    r"([^/:@\.]+\.)?",  # dkb.de
    r"([^/:@]*)\.",  # pszaf.hu
    r"([^/:@]+)?\.",  # axa-winterthur
    r"([^/@:\.]+)\.",  # alliedmods
    r"(?:\d\.)?([^@:/\.]+)\.",  # cachefly
    r"([^@:/]+)?",  # domaintank
    r"([^\.]+)\.",  # iapplicants
    r"(?:\w\w\.){0,4}",  # List.ru
    r"(?:\w\w\.){4}",  # Mail.ru
    r"(?:[\w-]+\.)?",  # ace.advertising.com
    r"(?:[\\w-]+\.)?",  # uberspace.de
    r"\S+\.",  # baidu, bdimg.com
    r"(?:[\w-]+\.)",  # kintera.com
    r"([\w\.-]+\.)?",
    r"\w{3}\.",  # sitemeter.com
    r"\w\d+\.",  # adspeed.biz
    r"(\w+)\.",
    r"(\w+\.)?",
    # r'(-\w\w\d)?\.',  # givex
    r"([\w-])\.",  # hitbox
    # very broad patterns
    r"(\d{3}-\w{3}-\d{3})\.",  # Mktoresp
)
assert len(set(_FIXME_SUBDOMAIN_PREFIXES)) == len(_FIXME_SUBDOMAIN_PREFIXES)

# These should all begin with .
_FIXME_SUBDOMAIN_SUFFIXES = (r"\.([^/:@]+)",)  # dbs

_FIXME_EXTRA_REPLACEMENTS = [
    # foo.*.bar
    (r"\.\w\w\.", r"\.~~"),  # kernel.org
    (r"\.\w+\.", r"\.~~"),  # emailsrvr.com
    # Other
    (r"(eu|[\da-f]{12})", "~"),  # Yottaa.net
    (r"(\d\d)\.", "~~"),  # xg4ken.com
    (r"([a-z][a-z]\.)?", "~~"),  # wikifur
    (
        r"(?:\w+\.cdn-ec|cdn-static(?:-\d\d)?|",
        r"(?:~~cdn-ec|cdn-static(?:-~)?|",
    ),  # viddler.com
    (r"vg\d\d\.met", "vg~~met"),  # vgwort.de
    (r"|imp\w\w|", r"|imp~|"),  # tradedoubler.com
    (r"|clk\w\w|", r"|clk~|"),  # tradedoubler.com
    (r"|star\w\w|", r"|star~|"),  # tradedoubler.com
    (r"|\w\w)\.thesims3", r"|~)\.thesims3"),  # thesims3.com country
    (r"|mysql\d\d|", r"|mysql~|"),  # tal.de
    (r"(\w+)-d\.", r"~-d\."),  # openxenterprise.com
    (r"(?:img\d\w\.)?www", r"(?:img~~)?www"),  # spoki.lv
    (r"di(\d-?\d?)\.", r"di~~"),  # shoppingshadow.com
    (r"asp-(\w\w)\.", r"asp-~~"),  # secure-zone.net
    (r"(\w\w|", r"(~|"),  # OpenSUSE
    (r"\w\w\.khronos", r"~~khronos"),  # khronos
    (r"|hal-\w+|", r"|hal-~|"),  # archives-ouvertes.fr
    (r"((?:[\w-]+|", r"((?:~|"),  # bbb
    (r"(\w+\.(", r"(~~("),  # byteark
    (r"(?:\w+sfx\.|sfx)", r"(?:~sfx\.|sfx)"),  # exlibrisgroup.com
    (r"([\w-]+)(?:\.secure)?\.", r"~(?:\.secure)?\."),  # ipcdigital
    (
        r"|go\d*|hi-tech|img\d*|limg|minigames|my\d+|proxy|\w+\.radar)",
        r"|go~|hi-tech|img~|limg|minigames|my~|proxy|~~radar)",
    ),  # mailimg
    (r"secure\d{1,3}|", r"secure~|"),  # inmotionhosting
    (r"|\w+\.i|", r"|~~i|"),  #
    (r"|whm\d\d)\.", r"|whm~)\."),
    (r"|\w+-async|", r"|~-async|"),
    (r"(?:r\d+|ssl)\.cf(\d)\.", r"(?:r~|ssl)\.cf~~"),  # rackcdn
    (r"wwws(-\w\w\d)?\.", r"wwws(-*)?\."),  # givex
    (r"(?:\.\w+)?|xs|xs2010)", r"(?:\.~)?|xs|xs2010)"),
    (r"|[\w-]+\.", "|~~"),  # uberspace
    (r"|\w+\.", "!~~"),  # udel.edu
    (r"|\w\.", "|~~"),  # wso2.com
    (r"la(\w{3})\.", "la~~"),  # salesforceliveagent.com
    (r"(\w+\.api|ssl-[\w\-]+)\.", r"(~~api\.|ssl-~~)"),
    (r"\.((com?\.)?\w{2,3})", r"\.((com?\.)?~)"),  # google
    # PR sent
    (r"p\d+\.qhimg", "p~~qhimg"),  # qhimg
    (r"webassets\w\.scea", "webassets~~scea"),  # scea
    (r"s(\d+)\.sinaimg", "s~~sinaimg"),  # sinaimg
    (r"(\w)\.asset\.soup\.io", r"~~asset\.soup\.io"),
    (r"asset-(\w)\.soupcdn", "asset-~~soupcdn"),
    (r"cdn\d+\.sure-assist", "cdn~~sure-assist"),
    (r"(i|j|m|si|t)(\d+)\.", "(i|j|m|si|t)~~"),
    (r"(\w\w\.|www\.)?bitstamp", r"(~~|www\.)?bitstamp"),
]

_FIXME_INCORRECT_TEST_URLS = [
    "http://canadapost.ca/",
    "http://cibc.com/",
    # https://github.com/EFForg/https-everywhere/issues/18891 :
    "http://hub.rother.gov.uk/RotherPortal/ServiceForms/BrownBinForGardenWasteFrm.aspx",
    # https://github.com/EFForg/https-everywhere/issues/18893 :
    "http://es.about.aegeanair.com/Css/fonts/Roboto-Bold/Roboto-Bold.ttf",
    "http://ru.about.aegeanair.com/Css/fonts/Roboto-Bold/Roboto-Bold.ttf",
    "http://www.belgium.indymedia.org/",
]
