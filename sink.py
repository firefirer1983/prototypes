from .parser import HttpParser


class HttpSink:
    def __init__(self):
        self._parser = HttpParser()
        self._upstream = None
        self._downstream = None

    def connect(self, up, down):
        self._upstream = up
        self._downstream = down

    def execute(self):
        pass
