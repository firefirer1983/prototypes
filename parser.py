HTTP_END_SEP = b"\r\n\r\n"
HTTP_END_SEP_LEN = len(HTTP_END_SEP)


class HttpRequestParser:
    def __init__(self):
        pass

    def __iter__(self):
        return self

    def parser(self):
        header_, body_ = yield from self._receive_header()
        try:
            header_ = self._parse_header(header_)
        except Exception as e:
            print(str(e))
        print("start receiving body")
        body_ = yield from self._receive_body(body_)
        try:
            body_ = self._parse_body(body_)
        except Exception as e:
            print(str(e))

        return header_, body_

    __next__ = parser

    @staticmethod
    def _receive_header():
        buf_ = bytearray()
        while True:
            data = yield
            buf_.extend(data)
            index_ = buf_.find(HTTP_END_SEP)
            if index_ >= 0:
                buf_, left_ = (
                    buf_[:index_],
                    buf_[index_ + HTTP_END_SEP_LEN :],
                )
                return buf_, left_

    @staticmethod
    def _receive_body(buf):
        while True:
            data = yield
            buf.extend(data)
            index_ = buf.find(HTTP_END_SEP)
            print(buf)
            if index_ >= 0:
                print("body:", buf[:HTTP_END_SEP_LEN])
                return buf[:HTTP_END_SEP_LEN]

    @staticmethod
    def _parse_header(buf):
        return buf

    @staticmethod
    def _parse_body(buf):
        return buf
