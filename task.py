import abc
from builder import HttpResponseBuilder


class Task(abc.ABC):
    def __init__(self):
        pass

    @abc.abstractmethod
    def execute(self):
        pass


class WSGITask(Task):
    class ResponseBuilder:
        def __init__(self):
            pass

        def build(self):
            pass

    def __init__(self, env, app, stream):
        super().__init__()
        self._env = env
        self._wsgi_app = app
        self._rsp_builder = HttpResponseBuilder(stream)

    def execute(self):
        self._wsgi_app(self._env, self._start_response)

    def _start_response(self, status, headers, exc_info=None):
        pass
