import asyncio
import sys
import typing
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from os import cpu_count
from pathlib import Path

from binaryornot.check import is_binary
from plumbum import cli

from .core import CombinedReplacerFactory, ReplaceContext
from .core.InBufferReplacer import InBufferReplacer
from .core.InFileReplacer import InFileReplacer
from .replacers.HEReplacer import HEReplacer
from .replacers.HSTSPreloadReplacer import HSTSPreloadReplacer


class OurInBufferReplacer(InBufferReplacer):
    __slots__ = ()
    FACS = CombinedReplacerFactory(
        {
            "preloads": HSTSPreloadReplacer,
            "heRulesets": HEReplacer,
        }
    )

    def __init__(self, preloads=None, heRulesets=None):
        super().__init__(preloads=preloads, heRulesets=heRulesets)


class OurInFileReplacer(InFileReplacer):
    def __init__(self, preloads=None, heRulesets=None):
        super().__init__(OurInBufferReplacer(preloads=preloads, heRulesets=heRulesets))


class CLI(cli.Application):
    """HTTPSEverywhere-like URI rewriter"""


class FileClassifier:
    __slots__ = ("noSkipDot", "noSkipBinary")

    def __init__(self, noSkipDot: bool, noSkipBinary: bool):
        self.noSkipDot = noSkipDot
        self.noSkipBinary = noSkipBinary

    def __call__(self, p: Path) -> str:
        for pa in p.parts:
            if not self.noSkipDot and pa[0] == ".":
                return "dotfile"

        if not p.is_dir():
            if p.is_file():
                if self.noSkipBinary or not is_binary(p):
                    return ""
                else:
                    return "binary"
            else:
                return "not regular file"


class FilesEnumerator:
    __slots__ = ("classifier", "disallowedReportingCallback")

    def __init__(self, classifier, disallowedReportingCallback):
        self.classifier = classifier
        self.disallowedReportingCallback = disallowedReportingCallback

    def __call__(self, fileOrDir: Path):
        reasonOfDisallowal = self.classifier(fileOrDir)
        if not reasonOfDisallowal:
            if fileOrDir.is_dir():
                for f in fileOrDir.iterdir():
                    yield from self(f)
            else:
                yield fileOrDir
        else:
            self.disallowedReportingCallback(fileOrDir, reasonOfDisallowal)


@CLI.subcommand("bulk")
class FileRewriteCLI(cli.Application):
    """Rewrites URIs in files. Use - to consume list of files from stdin. Don't use `find`, it is a piece of shit which is impossible to configure to skip .git dirs."""

    __slots__ = ("_repl",)

    @property
    def repl(self) -> InFileReplacer:
        if self._repl is None:
            self._repl = OurInFileReplacer()
            print(
                len(self._repl.inBufferReplacer.singleURIReplacer.children[0].preloads),
                "HSTS preloads",
            )
            print(len(self._repl.inBufferReplacer.singleURIReplacer.children[1].rulesets), "HE rules")
        return self._repl

    def processEachFileName(self, ctx: ReplaceContext, l: str) -> Path:
        l = l.strip()
        if l:
            l = l.decode("utf-8")
            p = Path(l).resolve().absolute()
            self.processEachFilePath(ctx, p)

    def processEachFilePath(self, ctx: ReplaceContext, p: Path) -> None:
        for pp in self.fe(p):
            if self.trace:
                print("Processing", pp, file=sys.stderr)
            self.repl(ctx, pp)
            if self.trace:
                print("Processed", pp, file=sys.stderr)

    @asyncio.coroutine
    def asyncMainPathsFromStdIn(self):
        conc = []
        asyncStdin = asyncio.StreamReader(loop=self.loop)
        yield from self.loop.connect_read_pipe(
            lambda: asyncio.StreamReaderProtocol(asyncStdin, loop=self.loop), sys.stdin
        )
        with ThreadPoolExecutor(max_workers=cpu_count()) as pool:
            while not asyncStdin.at_eof():
                l = yield from asyncStdin.readline()
                yield from self.loop.run_in_executor(pool, partial(self.processEachFileName, l))

    @asyncio.coroutine
    def asyncMainPathsFromCLI(self, filesOrDirs: typing.Iterable[typing.Union[Path, str]]):
        try:
            from tqdm import tqdm
        except ImportError:

            def tqdm(x):
                return x

        ctx = ReplaceContext(None)
        replaceInEachFileWithContext = partial(self.repl, ctx)

        with tqdm(filesOrDirs) as pb:
            for fileOrDir in pb:
                fileOrDir = Path(fileOrDir).resolve().absolute()

                files = tuple(self.fe(fileOrDir))

                if files:
                    with ThreadPoolExecutor(max_workers=cpu_count()) as pool:
                        for f in files:
                            if self.trace:
                                print("Processing", f, file=pb)
                            yield from self.loop.run_in_executor(pool, partial(replaceInEachFileWithContext, f))
                            if self.trace:
                                print("Processed", f, file=pb)

    noSkipBinary = cli.Flag(
        ["--no-skip-binary", "-n"],
        help="Don't skip binary files. Allows usage without `binaryornot`",
        default=False,
    )
    noSkipDot = cli.Flag(
        ["--no-skip-dotfiles", "-d"],
        help="Don't skip files and dirs which name stem begins from dot.",
        default=False,
    )
    trace = cli.Flag(
        ["--trace", "-t"],
        help="Print info about processing of regular files",
        default=False,
    )
    noReportSkipped = cli.Flag(
        ["--no-report-skipped", "-s"],
        help="Don't report about skipped files",
        default=False,
    )

    def disallowedReportingCallback(self, fileOrDir: Path, reasonOfDisallowal: str) -> None:
        if not self.noReportSkipped:
            print("Skipping ", fileOrDir, ":", reasonOfDisallowal)

    def main(self, *filesOrDirs):
        self._repl = None  # type: OurInFileReplacer
        self.loop = asyncio.get_event_loop()

        self.fc = FileClassifier(self.noSkipDot, self.noSkipBinary)
        self.fe = FilesEnumerator(self.fc, self.disallowedReportingCallback)

        if len(filesOrDirs) == 1 and filesOrDirs[0] == "0":
            t = self.loop.create_task(self.asyncMainPathsFromStdIn())
        else:
            t = self.loop.create_task(self.asyncMainPathsFromCLI(filesOrDirs))
        self.loop.run_until_complete(t)


if __name__ == "__main__":
    CLI.run()
