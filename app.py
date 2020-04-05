from server import create_server


def wsgi_app(env, start_response):
    print("wsgi app:", env, start_response)


if __name__ == "__main__":
    create_server(wsgi_app, host="127.0.0.1", port=8003).run()
