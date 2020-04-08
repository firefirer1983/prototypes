from dispatcher import Dispatcher
from task import WSGITask
from environment import EnvBuilder


class HttpSink:
    def __init__(self, app):
        self._dispatcher = Dispatcher()
        self._dispatcher.schedule_threads(4)
        self._app = app

    def process(self, request, channel):
        env_ = EnvBuilder(request, channel).build()
        task = WSGITask(env_, self._app, channel.downstream)
        self._dispatcher.dispatch(task)

