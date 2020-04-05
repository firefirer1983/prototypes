from dispatcher import Dispatcher
from task import WSGITask


class HttpSink:
    def __init__(self, app):
        self._dispatcher = Dispatcher()
        self._dispatcher.schedule_threads(4)
        self._app = app

    def process(self, header, body, channel):
        env_ = self._create_env(header)
        task = WSGITask(env_, self._app, channel.downstream)
        self._dispatcher.dispatch(task)

    def _create_env(self, data):
        return data
