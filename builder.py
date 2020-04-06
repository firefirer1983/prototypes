from utils import build_http_date
from collections.abc import MutableMapping


class HttpResponseBuilder(MutableMapping):
    def __init__(self, stream, req_header):
        self._stream = stream
        self._rsp_header = dict()
        self._req_header = req_header
        if self._req_header.get("VERSION", "") not in ("1.0", "1.1"):
            self._http_version = "1.0"
        else:
            self._http_version = self._req_header["VERSION"]

    def build(self):
        pass

    def set_content_length(self, length):
        self._rsp_header["Content-Length"] = length

    def set_date(self, date=None):
        if not date:
            self._rsp_header = build_http_date(date)

    def set_server(self, server=None):
        if not server:
            self._rsp_header["Via"] = "petty"
        else:
            self._rsp_header["Server"] = server

    @property
    def content_length(self):
        return self._rsp_header.get("Content-Length", None)

    def set_connection(self, connection):
        if self._http_version == "1.1":
            if connection == "keep-alive":
                # if self.content_length is
                pass

    def __setitem__(self, key, value):
        self._rsp_header.__setitem__(key, value)

    def __getitem__(self, item):
        return self._rsp_header.__getitem__(item)

    def __iter__(self):
        return self._rsp_header.__iter__()

    def __delitem__(self, key):
        return self._rsp_header.__delitem__(key)

    def __len__(self):
        return self._rsp_header.__len__()


if __name__ == "__main__":
    builder = HttpResponseBuilder(None, {})
    builder["Test"] = "Test"
    builder["Hi"] = "Hi"
    print(builder["Test"])
    for k, v in builder.items():
        print(k, v)
