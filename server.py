import requests
import json
from six.moves.urllib.parse import urlparse, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler
import asyncio
from aiohttp import ClientSession


BASE_GET_URL = "https://postman-echo.com/get?x={}"
INVALID_API_ERROR = {'message': 'invalid API endpoint', 'response': 'error'}
INVALID_ITERATION_ERROR = {'message': 'invalid iterations for /count', 'response': 'error'}


def get_iterations_from_query_string(url, counting_var):
    path = urlparse(url)
    query_string = parse_qs(path.query)
    if not query_string:
        return False

    iterations = int(query_string.get(counting_var)[0])
    if iterations < 1:
        return False

    return iterations


def lookup_route(url, valid_routes):
    path = urlparse(url)
    return path.path in valid_routes

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def write_json(self, content):
        # TODO doc
        self.wfile.write(json.dumps(content, indent=2).encode())

    def write_bytes(self, content):
        # TODO doc
        formated_json = json.dumps(json.loads(content.decode('utf8').replace("'", '"')),indent=2)
        self.wfile.write(formated_json.encode())

    def _set_headers(self):
        # TODO doc
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_HEAD(self):
        # TODO doc
        # TODO remove?
        self._set_headers()

    def do_GET(self):
        # TODO doc
        # send_response and end_headers needed to make this a valid, successful response
        self._set_headers()

        is_valid_route = lookup_route(self.path, valid_routes=['/count'])
        if not is_valid_route:
            self.write_json(INVALID_API_ERROR)
            return

        iterations = get_iterations_from_query_string(self.path, 'x')
        if not iterations:
            self.write_json(INVALID_ITERATION_ERROR)
            return

        loop = asyncio.get_event_loop()
        tasks = []

        async def async_get(url):
            async with ClientSession() as session:
                async with session.get(url) as response:
                    r = await response.read()
                    self.write_bytes(r)

        for i in range(0, iterations):
            get_value = i + 1
            GET_url = BASE_GET_URL.format(get_value)
            task = asyncio.ensure_future(async_get(GET_url))
            tasks.append(task)

        loop.run_until_complete(asyncio.wait(tasks))


def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=8080):
    # TODO doc
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    except Exception:
        pass
    httpd.server_close()

if __name__ == "__main__":
    run()

# TODO should I host this somewhere? Digital Ocean would be easiest?
# TODO set notabs in vim
