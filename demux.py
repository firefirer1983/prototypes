import socket
from selectors import DefaultSelector, EVENT_READ, EVENT_WRITE

from channel import StreamingChannel, TriggeringChannel


class ListenEndPoint:
    def __init__(self, host, port, backlog=5):
        self._host = host
        self._port = port
        self._sock_type = socket.SOCK_STREAM
        try:
            self._listen_sock = socket.socket(socket.AF_INET, self._sock_type)
        except socket.error as e:
            print(str(e))
            raise
        self._listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._listen_sock.bind((self._host, self._port))
        self._listen_sock.listen(backlog)
        self._listen_sock.setblocking(False)

    @property
    def fileobj(self):
        return self._listen_sock

    def accept(self):
        return self._listen_sock.accept()


class Demuxer:
    def __init__(self, listener):
        self._selector = DefaultSelector()
        self._listener = listener
        self._trigger = TriggeringChannel()
        self._selector.register(self._listener.fileobj, EVENT_READ)
        self._selector.register(
            self._trigger.fileobj, EVENT_READ, data=self._trigger
        )

    def _create_channel(self) -> StreamingChannel:
        client_, caddr_ = self._listener.accept()
        client_.setblocking(False)
        return StreamingChannel(client_)

    def _attach_channel(self, ch):
        self._selector.register(ch.fileobj, EVENT_READ | EVENT_WRITE, data=ch)

    def demux(self):
        while True:

            for key_, mask_ in self._selector.select(10):
                fileobj_, data_ = key_.fileobj, key_.data

                if fileobj_ == self._listener.fileobj and mask_ & EVENT_READ:
                    ch_ = self._create_channel()
                    self._attach_channel(ch_)
                else:
                    ch_ = data_
                    try:
                        if mask_ & EVENT_READ and ch_.readable():
                            ch_.handle_read()

                        if mask_ & EVENT_WRITE and ch_.writable():
                            ch_.handle_write()
                            
                    except Exception as e:
                        print(str(e))
                        ch_.close()
                        self._selector.unregister(ch_.fileobj)


if __name__ == "__main__":

    demuxer = Demuxer(ListenEndPoint("127.0.0.1", 8003))
    demuxer.demux()
