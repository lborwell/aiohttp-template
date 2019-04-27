import aiohttp_jinja2


@aiohttp_jinja2.template('index.html.jinja2')
async def index(request):
    return {}
