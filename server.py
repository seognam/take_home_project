import functools
from collections import deque
import json
import asyncio
from aiohttp import web, ClientSession

BASE_GET_URL = "https://postman-echo.com/get?x={}"

class Server:
    """
    A python HTTP server using asyncio and aiohttp.

    The only valid route is /count.
    GET requests are processed in the background, prioritizing speed.
    """
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.counter = 0
        self.queue = deque([])
        self.tasks = []
        self.responses = []

    async def reset(self, request):
        """
        An HTTP endpoint that resets the counter incremented by `/count`
        Args:
            request: The HTTP request object
        """
        self.counter = 0
        self.queue = deque([])
        self.tasks = []
        self.responses = []
        return web.json_response({'success': True, 'message': 'Reset counter.'})

    async def count(self, request):
        """
        An HTTP endpoint that makes an API call (to postman-echo.com) each time it is called
        Args:
            request: The HTTP request object
        """
        self.counter += 1
        self.queue.append(self.counter)
        return web.json_response(self.responses, dumps=functools.partial(json.dumps, indent=4))

    async def async_get(self, session, counter):
        """
        Create an asyncronous GET request which will be added to self.tasks

        Args:
            session: The interface for making HTTP requests
            counter: The counter for our next API request
        """
        GET_url = BASE_GET_URL.format(counter)
        try:
            async with session.get(GET_url) as response:
                r = await response.read()
                # Decode bytes into JSON
                r = json.loads(r.decode('utf8').replace("'", '"'))
                self.responses.append(r)
        except Exception as e:
                self.responses.append({'status': 'failed', 'reason': str(e)})

    async def background_start_GET_requests(self):
        """
        A background task to "fire off" GET requests as they come in
        
        Creates tasks from async_get coroutines and adds them to a list of pending tasks.
        Yields control back to the event loop for other background tasks when the queue is empty.
        """
        async with ClientSession() as session:
            while True:
                if self.queue:
                    next_counter = self.queue.popleft()
                    task = asyncio.ensure_future(self.async_get(session, next_counter))
                    self.tasks.append(task)
                else:
                    # We have no more items in the queue to create tasks from, so yield control back to the event loop
                    # Blocking for a half second (to let requests accumulate) shows slight speed gains 
                    # over shorter or longer times for CPU tradeoff.
                    await asyncio.sleep(0.5)

    async def background_finish_GET_requests(self):
        """
        Finishes all pending GET requests
        """
        while True:
            if self.tasks:
                # The queue is empty, so background_start_GET_requests yielded control to complete GET requests
                self.loop.run_until_complete(asyncio.wait(self.tasks))
            else:
                # We have no more tasks to complete, so yield control back to the event loop
                await asyncio.sleep(0.01)

    async def start_background_tasks(self, app):
        """ 
        Start background tasks

        From https://docs.aiohttp.org/en/stable/web_advanced.html#background-tasks
        """
        app['dispatch'] = app.loop.create_task(self.background_start_GET_requests())
        app['dispatch_get'] = app.loop.create_task(self.background_finish_GET_requests())

    async def cleanup_background_tasks(self, app):
        """ 
        Cleanup background tasks

        From https://docs.aiohttp.org/en/stable/web_advanced.html#background-tasks
        """
        app['dispatch'].cancel()
        app['dispatch_get'].cancel()
        await app['dispatch']
        await app['dispatch_get']

    async def create_app(self):
        app = web.Application()
        app.router.add_get('/count', self.count)
        app.router.add_get('/reset', self.reset)
        return app

    def run(self):
        """
        Start and run our application, adding background tasks
        """
        loop = self.loop
        app = loop.run_until_complete(self.create_app())
        app.on_startup.append(self.start_background_tasks)
        app.on_cleanup.append(self.cleanup_background_tasks)
        web.run_app(app)

if __name__ == "__main__":
    server = Server()
    server.run()
