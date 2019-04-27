import asyncio

import aiohttp_jinja2
import aiotask_context

import logging
import logging.config
import psycopg2
from sys import stderr

from aiohttp import web
from jinja2 import FileSystemLoader
from os import path
import app.handlers.bffs.web.books_handler as html_books
import app.handlers.bffs.web.index_handler as html_index
import app.handlers.healthcheck_handler as healthcheck
import app.handlers.rest.v1.book_handler as rest_books
from app.environment.facade import Environment, EnvironmentVars
from config.config import Config


def bootstrap(loop=None, env=None):
    if not loop:
        loop = asyncio.get_event_loop()
    app = web.Application(loop=loop)
    app.loop.set_task_factory(aiotask_context.task_factory)
    aiohttp_jinja2.setup(app, loader=FileSystemLoader(path.join(path.dirname(__file__), './templates')))

    config = load_config(env)
    secrets = load_secrets(config)

    EnvironmentVars.init(config, secrets)

    init_logging(config.get('LOG_CONFIG'))

    load_handlers(app)

    # todo I hate hate hate this
    # it's not necessary for most systems, but was originally devised for a system that had no
    # external access available (either DB or servers)
    # normally you could just run migrations from a jumpbox/laptop
    schema = open(path.join(path.dirname(__file__), '../resources/db/schema.sql')).read()
    try:
        logging.info('migrating')
        database = Environment.database()
        loop.run_until_complete(asyncio.gather(database.migrate(schema)))
    except psycopg2.Error as e:
        print('failed to migrate')
        print(str(e))
        print('error code: ' + str(e.pgcode))
        print('error: ' + str(e.pgerror))

    return app


def load_handlers(app):
    app.router.add_route('GET', '/', html_index.index, name='bff_web_index')
    app.router.add_route('GET', '/bffs/web/books', html_books.index, name='bff_web_book_index')
    app.router.add_route('GET', '/bffs/web/books/{book_id}', html_books.show, name='bff_web_book_show')

    app.router.add_route('GET', '/healthcheck', healthcheck.basic_healthcheck, name='healthcheck')

    app.router.add_route('GET',  '/rest/v1/books', rest_books.index)
    app.router.add_route('POST', '/rest/v1/books', rest_books.create)
    app.router.add_route('GET',  '/rest/v1/books/{book_id}', rest_books.show)


def load_config(env):
    # not in love with loading via modules like this, but it works well enough for now
    default_config = Config.load('config.app.default')
    env_config = {}
    if env is not None:
        env_config = Config.load('config.app.{}'.format(env))
    return {**default_config, **env_config}


def init_logging(logging_config):
    if logging_config:
        logging.config.dictConfig(logging_config)
    else:
        logging.basicConfig(level=logging.INFO)
        print('No logging configured, using default at logging.INFO', file=stderr)


def load_secrets(config):
    if Environment.is_development():
        return config.get('LOCAL_SECRETS', {})
    # todo implement secrets getters/decryptors (e.g. credstash, vault)
    return {}
