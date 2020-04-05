from server import create_server


def serve(application, **kwargs):
    s = create_server(application, **kwargs)
    s.run()
