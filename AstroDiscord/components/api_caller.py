from AstroDiscord.components.ini import tokens
import aiohttp

class AstroAPI:
    def __init__(self):
        # self.api_endpoint = tokens['api_endpoints']['localhost']
        self.api_endpoint = tokens['api_endpoints']['astroapi']
        self.legacy_endpoint = tokens['api_endpoints']['astroapi_legacy']

    async def search_song(self, artist: str, title: str, collection_title: str = None, is_explicit: bool = None, country_code: str = 'us'):
        async with aiohttp.ClientSession() as session:
            if country_code == None:
                country_code = 'us'
            api_url = f'{self.api_endpoint}/servicecatalog/global_io/search/song'
            api_params = {
                'artists': artist,
                'title': title,
                'market': country_code,
                'hydrate': 'false'
            }
            if collection_title != None:
                api_params['collection_title'] = collection_title
            if is_explicit != None:
                api_params['is_explicit'] = is_explicit
            async with session.get(url = api_url, params = api_params) as response:
                if response.status != 204:
                    json_response = dict(await response.json())
                    json_response['status'] = response.status
                    return json_response
                else:
                    return {}
            
    async def search_album(self, artist: str, title: str, year: str = None, country_code: str = 'us'):
        async with aiohttp.ClientSession() as session:
            if country_code == None:
                country_code = 'us'
            api_url = f'{self.api_endpoint}/servicecatalog/global_io/search/collection'
            api_params = {
                'artists': artist,
                'title': title,
                'market': country_code,
                'hydrate': 'false'
            }
            if year != None:
                api_params['year'] = year
            async with session.get(url = api_url, params = api_params) as response:
                if response.status != 204:
                    json_response = dict(await response.json())
                    json_response['status'] = response.status
                    return json_response
                else:
                    return {}
            
    async def search(self, query: str, country_code: str = 'us'):
        async with aiohttp.ClientSession() as session:
            if country_code == None:
                country_code = 'us'
            api_url = f'{self.api_endpoint}/servicecatalog/global_io/search/query'
            api_params = {
                'q': query,
                'best_match': 'true',
                'market': country_code,
                'hydrate': 'false'
            }
            async with session.get(url = api_url, params = api_params) as response:
                if response.status != 204:
                    json_response = await response.json()
                    json_response['status'] = response.status
                    return json_response
                else:
                    return {}
                
    async def search_lyric(self, lyric: str, country_code: str = 'us'):
        async with aiohttp.ClientSession() as session:
            if country_code == None:
                country_code = 'us'
            api_url = f'{self.api_endpoint}/servicecatalog/spotify/search/query'
            api_params = {
                'q': lyric,
                'best_match': 'false',
                'media_types': 'song',
                'market': country_code,
                'hydrate': 'false'
            }
            async with session.get(url = api_url, params = api_params) as response:
                if response.status != 204:
                    json_response = await response.json()
                    json_response['status'] = response.status
                    return json_response
                else:
                    return {}
    
    async def lookup(self, media_type: str, id: str, id_service: str, country_code: str = 'us'):
        async with aiohttp.ClientSession() as session:
            if country_code == None:
                country_code = 'us'
            api_url = f'{self.api_endpoint}/servicecatalog/global_io/lookup/{media_type}/{id_service}/{id}'
            api_params = {
                'market': country_code,
                'hydrate': 'false'
            }
            async with session.get(url = api_url, params = api_params) as response:
                if response.status != 204:
                    json_response = dict(await response.json())
                    json_response['status'] = response.status
                    return json_response
                else:
                    return {}
    
    async def get_self(self, media_type: str, id: str, id_service: str, country_code: str = 'us'):
        async with aiohttp.ClientSession() as session:
            if country_code == None:
                country_code = 'us'
            api_url = f'{self.api_endpoint}/servicecatalog/{id_service}/lookup/{media_type}/{id}'
            api_params = {
                'market': country_code,
                'hydrate': 'false'
            }
            async with session.get(url = api_url, params = api_params) as response:
                if response.status != 204:
                    json_response = dict(await response.json())
                    json_response['status'] = response.status
                    return json_response
                else:
                    return {}
                
    async def snitch_song(self, media_object: dict):
        async with aiohttp.ClientSession() as session:
            api_url = f'{self.api_endpoint}/snitch/check/song'
            async with session.post(url = api_url, json = media_object) as response:
                if response.status != 204:
                    json_response = dict(await response.json())
                    json_response['status'] = response.status
                    return json_response
                else:
                    return {}

    async def snitch_collection(self, media_object: dict):
        async with aiohttp.ClientSession() as session:
            api_url = f'{self.api_endpoint}/snitch/check/collection'
            async with session.post(url = api_url, json = media_object) as response:
                if response.status != 204:
                    json_response = dict(await response.json())
                    json_response['status'] = response.status
                    return json_response
                else:
                    return {}

    async def snitch_music_video(self, media_object: dict):
        async with aiohttp.ClientSession() as session:
            api_url = f'{self.api_endpoint}/snitch/check/music-video'
            async with session.post(url = api_url, json = media_object) as response:
                if response.status != 204:
                    json_response = dict(await response.json())
                    json_response['status'] = response.status
                    return json_response
                else:
                    return {}

    async def snitch(self, media_object: dict):
        """Routes the generic snitch call to the correct specific endpoint based on media type."""
        obj_type = media_object.get('type')
        
        if obj_type in ['track', 'single', 'knowledge']:
            return await self.snitch_song(media_object)
        elif obj_type in ['album', 'ep', 'eop']:
            return await self.snitch_collection(media_object)
        elif obj_type == 'music_video':
            return await self.snitch_music_video(media_object)
        else:
            # If the type is completely unrecognized, fallback safely
            raise ValueError(f"Unsupported media type for snitch: {obj_type}")

    async def get_about(self):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url=self.api_endpoint) as response:
                    if response.status == 200:
                        return await response.json()
            except Exception:
                pass
            return None