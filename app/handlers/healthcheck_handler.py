from aiohttp import web

async def basic_healthcheck(request):
    return web.json_response({'healthy': 'yes'})
