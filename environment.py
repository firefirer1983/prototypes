import sys
from collections.abc import MappingView


class EnvBuilder(MappingView):
    def __init__(self, request, channel):
        self._env = {
            "REMOTE_ADDR": channel.addr[0],
            # Nah, we aren't actually going to look up the reverse DNS for
            # REMOTE_ADDR, but we will happily set this environment variable
            # for the WSGI application. Spec says we can just set this to
            # REMOTE_ADDR, so we do.
            "REMOTE_HOST": channel.addr[0],
            # try and set the REMOTE_PORT to something useful, but maybe None
            "REMOTE_PORT": str(channel.addr[1]),
            "REQUEST_METHOD": request.method,
            "SERVER_PORT": str(server.effective_port),
            "SERVER_NAME": server.server_name,
            "SERVER_SOFTWARE": server.adj.ident,
            "SERVER_PROTOCOL": "HTTP/%s" % self.version,
            "SCRIPT_NAME": url_prefix,
            "PATH_INFO": path,
            "QUERY_STRING": request.query,
            "wsgi.url_scheme": request.url_scheme,
            # the following environment variables are required by the WSGI spec
            "wsgi.version": (1, 0),
            # apps should use the logging module
            "wsgi.errors": sys.stderr,
            "wsgi.multithread": True,
            "wsgi.multiprocess": False,
            "wsgi.run_once": False,
            "wsgi.input": request.get_body_stream(),
            "wsgi.file_wrapper": ReadOnlyFileBasedBuffer,
            "wsgi.input_terminated": True,  # wsgi.input is EOF terminated
        }

        for k, v in headers.items():
            pass
        
    def build(self):
        return self

    def __getitem__(self, item):
        return self._env[item.upper()]
