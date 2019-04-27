from functools import wraps

from aiohttp import web

from app.utils.complex_json import ComplexEncoder


class ValidationError(Exception):
    pass


class DownstreamError(IOError):
    def __init__(self, message, code):
        super().__init__(message)
        self.code = code


def json_endpoint(f):
    @wraps(f)
    async def wrapper(request):
        try:
            result = await f(request)
            return web.json_response(data=result, dumps=ComplexEncoder.dumps)
        except ValidationError:
            return web.json_response(status=422)
        except DownstreamError as e:
            print(str(e))
            return web.json_response(status=e.code)
        except PermissionError:
            return web.json_response(status=403)
        except FileNotFoundError:
            return web.json_response(status=404)
        except NameError:
            return web.json_response(status=400)
    return wrapper
