import re
import traceback
import sys

HTTP_HDR_SEP = "\r\n"
HTTP_HDR_END = b"\r\n\r\n"
HTTP_HDR_END_LEN = len(HTTP_HDR_END)


METHOD_RE = re.compile("[A-Z0-9$-_.]{3,20}")
VERSION_RE = re.compile("HTTP/(\d+).(\d+)")
HEADER_RE = re.compile('[\x00-\x1F\x7F()<>@,;:\[\]={} \t\\\\"]')

STATUS_RE = re.compile("(\d{3})\s*(\w*)")


class InvalidRequestLine(Exception):
    """ error raised when first line is invalid """


class InvalidHeader(Exception):
    """ error raised on invalid header """


class InvalidChunkSize(Exception):
    """ error raised when we parse an invalid chunk size """


class HttpRequestParser:
    def __init__(self):
        self._http_version = None
        self._http_method = None

    def parser(self):
        header_, body_ = yield from self._receive_header()
        print("recved:", header_, body_)
        try:
            header_ = self._parse_header(header_)
        except Exception as e:
            print(str(e))
            traceback.print_exc(sys.stdout)
        content_length_ = int(header_.get("Content-Length"))
        body_ = yield from self._receive_body(body_, content_length_)
        try:
            body_ = self._parse_body(body_)
        except Exception as e:
            print(str(e))
            traceback.print_exc(sys.stdout)

        return header_, body_

    @staticmethod
    def _receive_header():
        buf_ = bytearray()
        while True:
            data = yield
            buf_.extend(data)
            index_ = buf_.find(HTTP_HDR_END)
            if index_ >= 0:
                buf_, left_ = (
                    buf_[:index_],
                    buf_[index_ + HTTP_HDR_END_LEN :],
                )
                return buf_, left_

    @staticmethod
    def _receive_body(buf, content_length=0):
        while True:
            data = yield
            buf.extend(data)
            if len(buf) >= content_length > 0:
                return buf[:content_length]

    def _parse_header(self, buf):
        header_dict_ = {}
        buf = buf.decode("utf8")
        first_line, left = buf.split(HTTP_HDR_SEP, 1)
        bits = first_line.split(None, 2)

        if len(bits) != 3:
            raise InvalidRequestLine(first_line)

        if not METHOD_RE.match(bits[0]):
            raise InvalidRequestLine("invalid method:%s" % bits[0])

        self._http_method = bits[0].upper()
        self._url = bits[1]

        for line in left.split(HTTP_HDR_SEP):
            k, v = [p.strip() for p in line.split(":", 1)]
            header_dict_[k] = v
        for k, v in header_dict_.items():
            print("%s:%s" % (k, v))
        return header_dict_

    @staticmethod
    def _parse_body(buf):
        return buf.decode("utf8")
