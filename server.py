from demux import Demuxer, ListenEndPoint
from parser import HttpRequestParser
from sink import HttpSink
from channel import StreamingChannel


def create_server(application, **kwargs):
    return Server(application, **kwargs)


class Server(Demuxer):
    def __init__(self, app, host, port):
        self._wsgi_app = app
        super().__init__(ListenEndPoint(host, port))

    def create_channel(self, client):
        return StreamingChannel(
            client, HttpRequestParser(), HttpSink(self._wsgi_app)
        )

    def run(self):
        self.demux()
