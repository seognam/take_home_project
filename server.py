import time
import json
from six.moves.urllib.parse import urlparse, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler
import asyncio
from aiohttp import web
from aiohttp import ClientSession


BASE_GET_URL = "https://postman-echo.com/get?x={}"
INVALID_API_ERROR = {'message': 'invalid API endpoint', 'response': 'error'}
INVALID_ITERATION_ERROR = {'message': 'invalid iterations for /count', 'response': 'error'}


class Server:
    def __init__(self):
        self.loop = asyncio.get_event_loop()

    async def count(self, request):
        iterations = int(request.query['x'])
        # return web.Response(text=json.dumps(res))

        tasks = []

        # TODO add try/except e.g. https://tutorialedge.net/python/create-rest-api-python-aiohttp/#post-requests-and-query-parameters
        async with ClientSession() as session:
            for i in range(0, iterations):
                get_value = i + 1
                GET_url = BASE_GET_URL.format(get_value)
                task = asyncio.ensure_future(self.async_get(session, GET_url))
                tasks.append(task)
                responses = await asyncio.gather(*tasks)

        return web.json_response(responses)

    async def async_get(self, session, url):
        async with session.get(url) as response:
            resp = response.text()
            print(resp)
            return await(resp)
    
    async def create_app(self):
        app = web.Application()
        app.router.add_get('/count', self.count)
        return app


    def run(self):
        loop = self.loop
        app = loop.run_until_complete(self.create_app())
        web.run_app(app)

if __name__ == "__main__":
    server = Server()
    server.run()

# TODO asyncio.run_in_executor(json.dums)

# TODO should I host this somewhere? Digital Ocean would be easiest?
# TODO set notabs in vim
