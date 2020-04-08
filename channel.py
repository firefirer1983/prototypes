import os
import abc
import threading
import socket
from parser import HttpRequestParser

READ_BUF_SIZE = 16
WRITE_BUF_SIZE = 16


class UpStreamer:
    def __init__(self, sock, parser_factory):
        self._sock = sock
        self._buf = bytearray()
        self._get = 0
        self._parser_factory = parser_factory
        self._parser = None

    def read(self, size):
        if len(self._buf) > size:
            read_, self._buf = self._buf[:size], self._buf[size:]
            return read_

    def write(self):
        terminated_ = False
        while True:
            try:
                read_ = self._sock.recv(16)
            except BlockingIOError as e:
                pass
            except ConnectionResetError as e:
                terminated_ = True
            else:
                if read_:
                    done_ = self._parse(read_)
                    if done_:
                        return done_
                else:
                    terminated_ = True

            if terminated_:
                break

    def readable(self):
        return bool(self._buf)

    def writable(self):
        return True

    def _parse(self, data):
        if not self._parser:
            self._parser = self._parser_factory.parser()
            next(self._parser)

        try:
            self._parser.send(data)
        except StopIteration as e:
            return e.value
        else:
            return None


class DownStreamer:
    def __init__(self, sock):
        self._sock = sock
        self._buf = bytearray(
            b"HTTP/1.1 200 OK\r\nServer: socketio\r\nDate: Sun, 29 Mar 2020 15:46:43 GMT\r\nConnection: close\r\nContent-Type: text/plain\r\nContent-length: 16\r\n\r\nHello World!\r\n\r\n"
        )

    def read(self):
        read_ = self._sock.send(self._buf[:16])
        self._buf = self._buf[read_:]
        return read_

    def write(self, b):
        self._buf.extend(b)

    def readable(self):
        return bool(self._buf)

    def writable(self):
        return True


class Channel:
    @abc.abstractmethod
    def handle_read(self):
        pass

    @abc.abstractmethod
    def handle_write(self):
        pass

    @abc.abstractproperty
    def fileobj(self):
        pass

    @abc.abstractmethod
    def readable(self):
        pass

    @abc.abstractmethod
    def writable(self):
        pass


class StreamingChannel(Channel):
    def __init__(self, sock, parser_factory, sink):
        self._sock = sock
        self._sock.setblocking(False)
        self._parser_factory = parser_factory
        self._upstream = UpStreamer(self._sock, self._parser_factory)
        self._downstream = DownStreamer(self._sock)
        self._sink = sink
        self._active = True

    @property
    def fileobj(self):
        return self._sock

    def handle_read(self):
        req_ = self._upstream.write()
        if req_:
            self._sink.process(req_, self)

    def handle_write(self):
        self._downstream.read()

    def is_active(self):
        return self._active

    def close(self):
        self._sock.close()

    def readable(self):
        return self._upstream.writable()

    def writable(self):
        return self._downstream.readable()

    @property
    def downstream(self):
        return self._downstream


class AsyncFileWrapper:
    def __init__(self, fd):
        self._fd = os.dup(fd)

    def recv(self, *args):
        return os.read(self._fd, *args)

    def send(self, *args):
        return os.write(self._fd, *args)

    def getsockopt(self):
        raise NotImplementedError("Not Implemented Yet")

    read = recv
    write = send

    def close(self):

        if self._fd < 0:
            return
        closing, self._fd = self._fd, -1
        os.close(closing)

    def fileno(self):
        return self._fd


class TriggeringChannel(Channel):
    def __init__(self):
        self._lock = threading.RLock()
        r_, self._w = self._fds = os.pipe()
        os.set_blocking(r_, False)
        self._sock = AsyncFileWrapper(r_)

    def handle_read(self):
        try:
            print("trigger read:%r" % self._sock.recv(8192))
        except (OSError, socket.error):
            return

    def handle_write(self):
        raise NotImplementedError("Not Implement Yet!")

    @property
    def fileobj(self):
        return self._sock

    def trigger_pull(self):
        return os.write(self._w, b"x")

    def close(self):
        self._sock.close()
        os.close(self._w)

    def readable(self):
        return True

    def writable(self):
        return False
