import logging

from app.environment.db import PostgresProxy, DBFacade


class EnvironmentVars(object):
    _config = {}
    _secrets = {}

    @classmethod
    def init(cls, config, secrets):
        cls._config = config
        cls._secrets = secrets

    @classmethod
    def get(cls, key, default=None):
        return cls._config.get(key, default)

    @classmethod
    def get_secret(cls, key, default=None):
        return cls._secrets.get(key, default)


class Environment(object):
    _database = None

    @classmethod
    def is_development(cls):
        return True

    @classmethod
    def database(cls):
        if not cls._database:
            engine = EnvironmentVars.get('DB_ENGINE')
            if engine == 'pg':
                db = PostgresProxy(
                    database=EnvironmentVars.get('DB_DATABASE'),
                    user=EnvironmentVars.get('DB_USER'),
                    password=EnvironmentVars.get_secret('DB_PASSWORD'),
                    host=EnvironmentVars.get('DB_HOST'),
                    sslmode=EnvironmentVars.get('DB_SSL_MODE', 'prefer'),
                )
                cls._database = DBFacade(db)
        return cls._database
