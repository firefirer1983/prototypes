from utils import build_http_date
from collections.abc import MutableMapping


class HttpResponseBuilder(MutableMapping):
    def __init__(self, stream, req_header):
        self._stream = stream
        self._rsp_header = dict()
        self._req_header = req_header
        self._status = "200 OK"
        if self._req_header.get("VERSION", "") not in ("1.0", "1.1"):
            self._http_version = "1.0"
        else:
            self._http_version = self._req_header["VERSION"]

    def build(self):
        first_line_ = "HTTP/%s %s" % (self._http_version, self._status)
        left_lines = ["%s: %s" % (k, self[k]) for k in sorted(self)]
        lines = [first_line_] + left_lines
        return ("%s\r\n\r\n" % "\r\n".join(lines)).encode("utf8")

    @property
    def has_body(self):
        return not (
            self._status.startswith("1")
            or self._status.startswith("204")
            or self._status.startswith("304")
        )

    def set_status(self, status):
        self._status = status

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

    @staticmethod
    def _format_header_key(key):
        return "-".join([k.lower().capitalize() for k in key.split("-", 1)])

    def __setitem__(self, key, value):
        self._rsp_header.__setitem__(self._format_header_key(key), value)

    def __getitem__(self, item):
        return self._rsp_header.__getitem__(self._format_header_key(item))

    def __iter__(self):
        return self._rsp_header.__iter__()

    def __delitem__(self, key):
        return self._rsp_header.__delitem__(self._format_header_key(key))

    def __len__(self):
        return self._rsp_header.__len__()


if __name__ == "__main__":
    builder = HttpResponseBuilder(None, {})
    builder["Test"] = "Test"
    builder["Hi"] = "Hi"
    builder["conTent-leNgth"] = "123"
    print(builder["Test"])
    for k, v in builder.items():
        print(k, v)
    print(builder.build())
