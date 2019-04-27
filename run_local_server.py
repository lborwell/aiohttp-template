import asyncio
import logging
import uvloop
from os import environ

from aiohttp import web
from app.bootstrap import bootstrap

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

logger = logging.getLogger(__name__)

DEFAULT_SERVER_PORT = 5000

if __name__ == '__main__':
    port = int(environ.get('SERVER_PORT') or DEFAULT_SERVER_PORT)
    env = environ.get('ENV')

    app = bootstrap(env=env)

    logger.info('--- Starting web service, listening on port {} ---'.format(port))
    web.run_app(app, port=port)
