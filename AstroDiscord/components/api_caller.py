from AstroDiscord.components.ini import tokens
import aiohttp

class AstroAPI:
    def __init__(self):
        self.api_endpoint = tokens['api_endpoints']['astroapi']

    async def search_song(self, artist: str, title: str, collection_title: str = None, is_explicit: bool = None, country_code: str = 'us'):
        async with aiohttp.ClientSession() as session:
            if country_code == None:
                country_code = 'us'
            api_url = f'{self.api_endpoint}/music/global_io/search_song'
            api_params = {
                'artist': artist,
                'title': title,
                'country_code': country_code
            }
            if collection_title != None:
                api_params['collection_title'] = collection_title
            if is_explicit != None:
                api_params['is_explicit'] = is_explicit
            async with session.get(url = api_url, params = api_params) as response:
                json_response = dict(await response.json())
                return json_response
            
    async def search_album(self, artist: str, title: str, year: str = None, country_code: str = 'us'):
        async with aiohttp.ClientSession() as session:
            if country_code == None:
                country_code = 'us'
            api_url = f'{self.api_endpoint}/music/global_io/search_collection'
            api_params = {
                'artist': artist,
                'title': title,
                'country_code': country_code
            }
            if year != None:
                api_params['year'] = year
            async with session.get(url = api_url, params = api_params) as response:
                json_response = dict(await response.json())
                return json_response
            
    async def search(self, query: str, country_code: str = 'us'):
        async with aiohttp.ClientSession() as session:
            if country_code == None:
                country_code = 'us'
            api_url = f'{self.api_endpoint}/music/global_io/search_query'
            api_params = {
                'query': query,
                'country_code': country_code
            }
            async with session.get(url = api_url, params = api_params) as response:
                json_response = await response.json()
                return json_response
    
    async def lookup(self, media_type: str, id: str, id_service: str, country_code: str = 'us'):
        async with aiohttp.ClientSession() as session:
            if country_code == None:
                country_code = 'us'
            api_url = f'{self.api_endpoint}/music/global_io/lookup_{media_type}'
            api_params = {
                'id': id,
                'id_service': id_service,
                'country_code': country_code
            }
            async with session.get(url = api_url, params = api_params) as response:
                json_response = dict(await response.json())
                return json_response
            
    async def lookup_knowledge(self, id: str, id_service: str, country_code: str = 'us'):
        async with aiohttp.ClientSession() as session:
            if country_code == None:
                country_code = 'us'
            api_url = f'{self.api_endpoint}/knowledge/global_io/lookup_song'
            api_params = {
                'id': id,
                'id_service': id_service,
                'country_code': country_code
            }
            async with session.get(url = api_url, params = api_params) as response:
                json_response = dict(await response.json())
                return json_response
            
    async def search_knowledge(self, query: str, country_code: str = 'us'):
        async with aiohttp.ClientSession() as session:
            if country_code == None:
                country_code = 'us'
            api_url = f'{self.api_endpoint}/knowledge/global_io/search_query'
            api_params = {
                'query': query,
                'country_code': country_code
            }
            async with session.get(url = api_url, params = api_params) as response:
                json_response = dict(await response.json())
                return json_response