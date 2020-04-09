import abc
import sys
import traceback
from builder import HttpResponseBuilder


class Task(abc.ABC):
    def __init__(self):
        pass

    def execute(self):
        try:
            self._execute()
        except Exception as e:
            traceback.print_exc(sys.stdout)

    @abc.abstractmethod
    def _execute(self):
        pass


hop_by_hop = frozenset(
    (
        "connection",
        "keep-alive",
        "proxy-authenticate",
        "proxy-authorization",
        "te",
        "trailers",
        "transfer-encoding",
        "upgrade",
    )
)


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

    def _execute(self):
        self._wsgi_app(self._env, self._start_response)

    def _start_response(self, status, headers, exc_info=None):
        self._status = status

        for k, v in headers:
            if k.__class__ is str and v.__class__ is str:
                if k.lower() in hop_by_hop:
                    raise AssertionError(
                        "hop-by-hop header is not allow in WSGI"
                    )
                self._rsp_builder[k.strip()] = v.strip()
            else:
                raise AssertionError(
                    "Response Header must be string only=> %r: %r" % (k, v)
                )
