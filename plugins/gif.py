import random

from util import hook, http


@hook.api_key('giphy')
@hook.command('gif')
@hook.command
def giphy(inp, api_key="dc6zaTOxFJmzC"):
    '''.gif/.giphy <query> -- returns first giphy search result'''
    url = 'http://api.giphy.com/v1/gifs/search'
    try:
        response = http.get_json(url, q=inp, limit=10, api_key=api_key)
    except http.HTTPError as e:
        return e.msg

    results = response.get('data')
    if results:
        return random.choice(results).get('images').get('original').get('url')
    else:
        return 'no results found'
