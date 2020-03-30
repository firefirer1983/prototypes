import io


READ_BUF_SIZE = 16
WRITE_BUF_SIZE = 16


class StreamingChannel:
    def __init__(self, sock):
        self._sock = sock
        self._rd_buf = io.BytesIO()
        self._wr_buf = io.BytesIO()
        self._active = True
        self._sock.setblocking(False)
        self._parser = None

    def register_parser(self, p):
        self._parser = p
        self._rd_buf = self._parser.get_read_buffer()
        self._wr_buf = self._parser.get_write_buffer()

    @property
    def fileobj(self):
        return self._sock

    def handle_read(self):
        length_ = 0
        while True:
            try:
                recved_ = self._sock.recv(READ_BUF_SIZE)
            except BlockingIOError as e:
                pass
            except ConnectionResetError as e:
                self._active = False
            else:
                if recved_:
                    if recved_.find(b"\r\n\r\n") > 0:
                        self._active = False
                    self._rd_buf.write(recved_)
                    length_ += len(recved_)
                else:
                    self._active = False

            if not self._active:
                print(self._rd_buf.getvalue())
                return -1

    def handle_write(self):
        if self._wr_buf.readable():
            dat_ = self._wr_buf.getvalue()

    def is_active(self):
        return self._active

    def close(self):
        self._sock.close()
        self._rd_buf.close()
