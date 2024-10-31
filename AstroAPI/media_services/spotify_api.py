from AstroAPI.components.all import *
import asyncio
import aiohttp

class Spotify:
	def __init__(self, client_id: str, client_secret: str):
		self.service = 'spotify'
		self.client_id = client_id
		self.client_secret = client_secret
		self.token = None
		self.token_expiration_date = None
		asyncio.run(self.get_token())


	
	async def get_token(self) -> str:
		if self.token == None or (self.token_expiration_date == None or current_time() > self.token_expiration_date):
			async with aiohttp.ClientSession() as session:
				api_url = 'https://accounts.spotify.com/api/token'
				api_data = f'grant_type=client_credentials&client_id={self.client_id}&client_secret={self.client_secret}'
				api_headers = {'Content-Type': 'application/x-www-form-urlencoded'}

				async with session.post(url = api_url, data = api_data, headers = api_headers) as response:
					if response.status == 200:
						json_response = await response.json()
						self.token = json_response['access_token']
						self.token_expiration_date = current_time() + int(json_response['expires_in'])

		return self.token



	async def search_song(self, artists: list, title: str, song_type: str = None, collection: str = None, is_explicit: bool = None) -> object:
		async with aiohttp.ClientSession() as session:
			songs = []
			api_url = f'https://api.spotify.com/v1/search'
			api_params = {
				'q': f'artist:{artists[0]} track:{title}',
				'type': 'track',
				'market': 'US',
				'limit': 50,
				'offset': 0
			}
			api_headers = {'Authorization': f'Bearer {await self.get_token()}'}
			timeout = aiohttp.ClientTimeout(total = 30)
			start_time = current_time_ms()

			async with session.get(url = api_url, headers = api_headers, timeout = timeout, params = api_params) as response:
				if response.status == 200:
					json_response = await response.json()
					save_json(json_response)

					for song in json_response['tracks']['items']:
						song_type = ('track' if song['album']['album_type'] != 'single' else 'single')
						song_url = song['external_urls']['spotify']
						song_id = song['id']
						song_title = song['name']
						song_artists = [artist['name'] for artist in song['artists']]
						song_cover = (song['album']['images'][0]['url'] if song['album']['images'] != [] else '')
						song_is_explicit = song['explicit']
						song_collection = song['album']['name']
						end_time = current_time_ms()
						songs.append(Song(
							service = self.service,
							type = song_type,
							url = song_url,
							id = song_id,
							title = song_title,
							censored_title = song_title,
							artists = song_artists,
							collection = song_collection,
							is_explicit = song_is_explicit,
							cover_url = song_cover,
							api_response_time = end_time - start_time,
							api_http_code = response.status
						))
						return filter_song(songs = songs, query_artist = artists[0], query_title = title, query_song_type = song_type, query_collection = collection, query_is_explicit = is_explicit)



	async def search_collection(self, artists: list, title: str, year: int = None) -> object:
		async with aiohttp.ClientSession() as session:
			collections = []
			api_url = f'https://api.spotify.com/v1/search'
			api_params = {
				'q': f'artist:{artists[0]} album:{title}',
				'type': 'album',
				'market': 'US',
				'limit': 50,
				'offset': 0
			}
			api_headers = {'Authorization': f'Bearer {await self.get_token()}'}
			timeout = aiohttp.ClientTimeout(total = 30)
			start_time = current_time_ms()

			async with session.get(url = api_url, headers = api_headers, timeout = timeout, params = api_params) as response:
				if response.status == 200:
					json_response = await response.json()
					save_json(json_response)

					for collection in json_response['albums']['items']:
						collection_type = ('album' if collection['album_type'] != 'single' else 'ep')
						collection_url = collection['external_urls']['spotify']
						collection_id = collection['id']
						collection_title = collection['name']
						collection_artists = [artist['name'] for artist in collection['artists']]
						collection_year = collection['release_date'][:4]
						collection_cover = (collection['images'][0]['url'] if collection['images'] != [] else '')
						end_time = current_time_ms()
						collections.append(Collection(
							service = self.service,
							type = collection_type,
							url = collection_url,
							id = collection_id,
							title = collection_title,
							censored_title = collection_title,
							artists = collection_artists,
							release_year = collection_year,
							cover_url = collection_cover,
							api_response_time = end_time - start_time,
							api_http_code = response.status
						))
						return filter_collection(collections = collections, query_artist = artists[0], query_title = title, query_year = year)


	
	async def lookup_song(self, song_id: str):
		async with aiohttp.ClientSession() as session:
			api_url = f'https://api.spotify.com/v1/tracks/{song_id}'
			api_headers = {'Authorization': f'Bearer {await self.get_token()}'}
			timeout = aiohttp.ClientTimeout(total = 30)
			start_time = current_time_ms()

			async with session.get(url = api_url, headers = api_headers, timeout = timeout) as response:
				if response.status == 200:
					song = await response.json()

					song_type = ('track' if song['album']['album_type'] != 'single' else 'single')
					song_url = song['external_urls']['spotify']
					song_id = song['id']
					song_title = song['name']
					song_artists = [artist['name'] for artist in song['artists']]
					song_cover = (song['album']['images'][0]['url'] if song['album']['images'] != [] else '')
					song_is_explicit = song['explicit']
					song_collection = song['album']['name']
					end_time = current_time_ms()
					return Song(
						service = self.service,
						type = song_type,
						url = song_url,
						id = song_id,
						title = song_title,
						censored_title = song_title,
						artists = song_artists,
						collection = song_collection,
						is_explicit = song_is_explicit,
						cover_url = song_cover,
						api_response_time = end_time - start_time,
						api_http_code = response.status
					)


	
	async def lookup_collection(self, collection_id: str):
		async with aiohttp.ClientSession() as session:
			api_url = f'https://api.spotify.com/v1/albums/{collection_id}'
			api_headers = {'Authorization': f'Bearer {await self.get_token()}'}
			timeout = aiohttp.ClientTimeout(total = 30)
			start_time = current_time_ms()

			async with session.get(url = api_url, headers = api_headers, timeout = timeout) as response:
				if response.status == 200:
					collection = await response.json()

					collection_type = ('album' if collection['album_type'] != 'single' else 'ep')
					collection_url = collection['external_urls']['spotify']
					collection_id = collection['id']
					collection_title = collection['name']
					collection_artists = [artist['name'] for artist in collection['artists']]
					collection_year = collection['release_date'][:4]
					collection_cover = (collection['images'][0]['url'] if collection['images'] != [] else '')
					end_time = current_time_ms()
					return Collection(
						service = self.service,
						type = collection_type,
						url = collection_url,
						id = collection_id,
						title = collection_title,
						censored_title = collection_title,
						artists = collection_artists,
						release_year = collection_year,
						cover_url = collection_cover,
						api_response_time = end_time - start_time,
						api_http_code = response.status
					)
