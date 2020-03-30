import io
import socket
import selectors

READ_BUF_SIZE = 2048
WRITE_BUF_SIZE = 2048


class SocketIO(io.BufferedIOBase):
    class _SocketIO(io.RawIOBase):
        def __init__(self, stream):
            self._sock = stream
            self._sock.setblocking(False)

        def read(self, size: int = ...):
            recved_ = self._sock.recv(size)
            return recved_

        def write(self, b):
            nsize_ = self._sock.send(b)
            return nsize_

        def close(self):
            super().close()
            self._sock.close()

    def __init__(self, sock):
        super().__init__()
        self.raw = SocketIO._SocketIO(sock)
        self._up_stream = bytearray()
        self._down_stream = bytearray(
            b"HTTP/1.1 200 OK\r\nServer: socketio\r\nDate: Sun, 29 Mar 2020 15:46:43 GMT\r\nConnection: close\r\nContent-Type: text/plain\r\nContent-length: 16\r\n\r\nHello world!\r\n\r\n"
        )

    def handle_read(self):
        self._up_stream.clear()
        done_ = False
        while True:
            try:
                read_ = self.raw.read(16)
            except BlockingIOError as e:
                pass
            except ConnectionResetError as e:
                done_ = True
                self._up_stream.clear()
            else:
                if read_:
                    self._up_stream.extend(read_)
                    if read_.find(b"\r\n\r\n") > -1:
                        done_ = True
                else:
                    done_ = True

            if done_:
                print(self._up_stream)
                return bytes(self._up_stream)

    def handle_write(self):
        written_ = self.raw.write(self._down_stream[:16])
        print("%u bytes written" % written_)
        self._down_stream = self._down_stream[written_:]
        return written_

    def write(self, b):
        self._down_stream.extend(b)

    @property
    def done(self):
        return not bool(self._down_stream)

    @property
    def fileobj(self):
        return self.raw._sock

    def close(self):
        self._down_stream.clear()
        self._up_stream.clear()
        self.raw.close()


if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setblocking(False)
    s.bind(("127.0.0.1", 8004))
    s.listen(5)

    selector = selectors.DefaultSelector()
    selector.register(s, selectors.EVENT_READ)
    request = False
    while True:

        evts = selector.select(10)
        for key, mask in evts:
            if key.fileobj == s:
                c_, addr_ = s.accept()
                print(addr_)
                selector.register(
                    c_,
                    selectors.EVENT_READ | selectors.EVENT_WRITE,
                    data=SocketIO(c_),
                )
            else:
                ch = key.data
                if mask & selectors.EVENT_READ:
                    ch.handle_read()

                if mask & selectors.EVENT_WRITE:
                    ch.handle_write()
                    if ch.done:
                        ch.close()
                        selector.unregister(ch.fileobj)
