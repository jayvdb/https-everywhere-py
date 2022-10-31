import typing
from os import close
from pathlib import Path
from shutil import copystat
from tempfile import NamedTemporaryFile
from warnings import warn

from . import ReplaceContext
from .InBufferReplacer import InBufferReplacer

chardet = None  # lazily initialized
fallbackDefaultEncoding = "utf-8"


class InFileReplacer:
    __slots__ = ("inBufferReplacer", "encoding")

    def __init__(self, inBufferReplacer: InBufferReplacer, encoding: typing.Optional[str] = None) -> None:
        global chardet
        self.inBufferReplacer = inBufferReplacer
        self.encoding = encoding
        if encoding is None:
            try:
                import chardet
            except ImportError:
                warn("`chardet` is not installed. Assumming utf-8. There will be errors if another encoding is used.")
                encoding = fallbackDefaultEncoding

    def __call__(self, ctx: ReplaceContext, inputFilePath: Path, safe: bool = True) -> None:
        if safe:
            return self.safe(ctx, inputFilePath)
        return self.unsafe(ctx, inputFilePath)

    def safe(self, ctx: ReplaceContext, inputFilePath: Path) -> None:
        fo = None
        tmpFilePath = None

        encodingsAccum = []

        if not self.encoding:
            encDetector = chardet.UniversalDetector()
            encodingPrevConfidence = -1.0
            encoding = fallbackDefaultEncoding

        try:
            with open(inputFilePath, "rb") as fi:
                while True:
                    origLineStart = fi.tell()
                    l = fi.readline()
                    origLineEnd = fi.tell()
                    origLineLength = origLineEnd - origLineStart

                    if not l:
                        break

                    if not self.encoding:
                        # black magic here. UniversalDetector doesn't return correct encoding unless closed in some cases. So we close it. Then modify its internal state to make it look like if it is open and accept strings.
                        encDetector.feed(l)
                        encDetector.close()
                        encDetector.done = False
                        res = encDetector.result
                        #ic(res)
                        detectedConfidence = res["confidence"]
                        detectedEncoding = res["encoding"]
                        encodings2try = [(detectedConfidence, detectedEncoding)]
                        if detectedEncoding != encoding:
                            encodings2try.append((encodingPrevConfidence, encoding))

                        if detectedConfidence < encodingPrevConfidence:
                            encodings2try.reverse()

                        encodings2try.append((0, fallbackDefaultEncoding))

                        encoding = None
                        decodedLine = None
                        for curConfidence, curEnc in encodings2try:
                            if not curEnc:
                                continue
                            try:
                                #print("Trying", curEnc, ", confidence=", curConfidence)
                                decodedLine = l.decode(curEnc)
                            except ValueError:
                                #print("Fail")
                                pass
                            except LookupError:
                                warn("Unsupported encoding: " + curEnc)
                            else:
                                #print("Success")
                                encoding = curEnc
                                encodingPrevConfidence = curConfidence
                                break
                        if decodedLine is None:
                            warn("No supported encoding has been detected for the line " + repr(l) + "; Processing as binary.")
                            encoding = None
                            decodedLine = l
                    else:
                        encoding = self.encoding
                        decodedLine = l.decode(encoding)

                    cctx = self.inBufferReplacer(decodedLine)
                    if cctx.count:
                        if not fo:
                            fo = NamedTemporaryFile(
                                mode="ab",
                                encoding=None,
                                suffix="new",
                                prefix=inputFilePath.stem,
                                dir=inputFilePath.parent,
                                delete=False,
                            ).__enter__()
                            tmpFilePath = Path(fo.name)
                            fi.seek(0)
                            beginning = fi.read(origLineStart)
                            fo.flush()
                            fo.write(beginning)
                            fo.flush()
                            fi.seek(origLineEnd)
                            fi.flush()
                        if encoding:
                            fo.write(cctx.res.encode(encoding))
                        else:
                            fo.write(cctx.res)
                        ctx.count += ctx.count
                    else:
                        if fo:
                            fo.write(l)

        except BaseException as ex:
            if fo:
                fo.__exit__(type(ex), ex, None)
                if tmpFilePath.exists():
                    tmpFilePath.unlink()
            raise
        else:
            if fo:
                fo.__exit__(None, None, None)
                copystat(inputFilePath, tmpFilePath)
                tmpFilePath.rename(inputFilePath)

    def unsafe(self, ctx: ReplaceContext, inputFilePath: Path) -> None:
        from warnings import warn

        warn("Unsafe in-place editing is not yet implamented")
        return self.safe(ctx, inputFilePath)
