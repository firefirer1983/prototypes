from collections.abc import MutableMapping
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


class HttpRequest(MutableMapping):
    def __init__(self):
        self._headers = {}
        self._version = "1.0"
        self._method = None
        self._request_url = None
        self._body = None

    @property
    def version(self):
        return self._version

    def set_version(self, v):
        self._version = v.strip()

    @property
    def method(self):
        return self._method

    def set_method(self, v):
        self._method = v.strip()

    @property
    def request_url(self):
        return self._request_url

    @property
    def content_length(self):
        return int(self._headers.get("Content-Length"))

    def set_request_url(self, v):
        self._request_url = v.strip()

    def __setitem__(self, key, value):
        return self._headers.__setitem__(key, value)

    def __getitem__(self, item):
        return self._headers.__getitem__(item)

    def __iter__(self):
        return self._headers.__iter__()

    def __delitem__(self, key):
        return self._headers.__delitem__(key)
    
    def __len__(self):
        return self._headers.__len__()
    
    def set_body(self, body):
        self._body = body

    @property
    def body(self):
        return self._body


class HttpRequestParser:
    def __init__(self):
        pass

    def parser(self):
        request_ = HttpRequest()
        headers_, partial_body_ = yield from self._receive_header()
        print("recved:", headers_, partial_body_)
        try:
            method_, request_url_, headers_ = self._parse_header(headers_)
        except Exception as e:
            print(str(e))
            traceback.print_exc(sys.stdout)
            raise

        request_.set_method(method_)
        request_.set_request_url(request_url_)
        request_.update(headers_)
        
        body_ = yield from self._receive_body(
            partial_body_, request_.content_length
        )
        try:
            body_ = self._parse_body(body_)
        except Exception as e:
            print(str(e))
            traceback.print_exc(sys.stdout)
            raise
        request_.set_body(body_)
        return request_

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

    @staticmethod
    def _parse_header(buf):
        buf = buf.decode("utf8")
        first_line, left = buf.split(HTTP_HDR_SEP, 1)
        bits = first_line.split(None, 2)

        if len(bits) != 3:
            raise InvalidRequestLine(first_line)

        if not METHOD_RE.match(bits[0]):
            raise InvalidRequestLine("invalid method:%s" % bits[0])

        method_ = bits[0].upper()
        request_url_ = bits[1]

        headers_ = dict()
        for line in left.split(HTTP_HDR_SEP):
            k, v = [p.strip() for p in line.split(":", 1)]
            headers_[k] = v
        return method_, request_url_, headers_

    @staticmethod
    def _parse_body(buf):
        return buf.decode("utf8")
