from AstroAPI.components.all import *
from base64 import b64encode
from asyncio import run
import aiohttp

class Tidal:
	def __init__(self, client_id: str, client_secret: str):
		self.service = 'tidal'
		self.component = 'TIDAL API'
		self.client_id = client_id
		self.client_secret = client_secret
		self.token = None
		self.token_expiration_date = None
		run(self.get_token())



	async def get_token(self) -> str:
		if self.token == None or (self.token_expiration_date == None or current_unix_time() > self.token_expiration_date):
			credentials = f'{self.client_id}:{self.client_secret}'
			encoded_credentials = b64encode(credentials.encode('utf-8')).decode('utf-8')
			async with aiohttp.ClientSession() as session:
				api_url = 'https://auth.tidal.com/v1/oauth2/token'
				api_data = {'grant_type': 'client_credentials'}
				api_headers = {'Authorization': f'Basic {encoded_credentials}'}

				async with session.post(url = api_url, data = api_data, headers = api_headers) as response:
					if response.status == 200:
						json_response = await response.json()
						self.token = json_response['access_token']
						self.token_expiration_date = current_unix_time() + int(json_response['expires_in'])
					else:
						return Error(
							service = self.service,
							component = self.component,
							http_code = response.status,
							error_msg = "HTTP error when getting token"
						)

		return self.token
	


	async def search_song(self, artists: list, title: str, song_type: str = None, collection: str = None, is_explicit: bool = None) -> object:
		async with aiohttp.ClientSession() as session:
			artists = [optimize_for_search(artist) for artist in artists]
			title = optimize_for_search(title)
			collection = clean_up_collection_title(optimize_for_search(collection)) if collection != None else None
			
			songs = []
			api_url = f'https://openapi.tidal.com/search'
			api_params = {
				'query': f'{artists[0]} {title}',
				'type': 'TRACKS',
				'offset': 0,
				'limit': 100,
				'countryCode': 'US',
				'popularity': 'WORLDWIDE'
			}
			api_headers = {
				'accept': 'application/vnd.api+json',
				'Authorization': f'Bearer {await self.get_token()}',
				'Content-Type': 'application/vnd.tidal.v1+json'
			}
			timeout = aiohttp.ClientTimeout(total = 30)
			start_time = current_unix_time_ms()

			async with session.get(url = api_url, headers = api_headers, timeout = timeout, params = api_params) as response:
				if response.status == 207:
					json_response = await response.json()

					for song in json_response['tracks']:
						song_type = 'track'
						song_url = song['resource']['tidalUrl']
						song_id = song['resource']['id']
						song_title = song['resource']['title']
						song_artists = [artist['name'] for artist in song['resource']['artists']]
						song_cover = (song['resource']['album']['imageCover'][1]['url'] if song['resource']['album']['imageCover'] != [] else '')
						song_is_explicit = ('explicit' in song['resource']['properties']['content'][0] if 'content' in song['resource']['properties'] else False)
						song_collection = remove_feat(song['resource']['album']['title'])
						end_time = current_unix_time_ms()
						songs.append(Song(
							service = self.service,
							type = song_type,
							url = song_url,
							id = song_id,
							title = song_title,
							artists = song_artists,
							collection = song_collection,
							is_explicit = song_is_explicit,
							cover_url = song_cover,
							api_response_time = end_time - start_time,
							api_http_code = response.status
						))
					return filter_song(service = self.service, songs = songs, query_artists = artists, query_title = title, query_song_type = song_type, query_collection = collection, query_is_explicit = is_explicit)
				else:
					return Error(
						service = self.service,
						component = self.component,
						http_code = response.status,
						error_msg = "HTTP error when searching for song",
						request = f'Artists: `{', '.join(artists)}`\nTitle: `{title}`\nSong type: `{song_type}`\nCollection title: `{collection}`\nIs explicit? `{is_explicit}`'
					)



	async def search_collection(self, artists: list, title: str, year: int = None) -> object:
		async with aiohttp.ClientSession() as session:
			artists = [optimize_for_search(artist) for artist in artists]
			title = clean_up_collection_title(optimize_for_search(title))
			
			collections = []
			api_url = f'https://openapi.tidal.com/search'
			api_params = {
				'query': f'{artists[0]} {title}',
				'type': 'ALBUMS',
				'offset': 0,
				'limit': 100,
				'countryCode': 'US',
				'popularity': 'WORLDWIDE'
			}
			api_headers = {
				'accept': 'application/vnd.api+json',
				'Authorization': f'Bearer {await self.get_token()}',
				'Content-Type': 'application/vnd.tidal.v1+json'
			}
			timeout = aiohttp.ClientTimeout(total = 30)
			start_time = current_unix_time_ms()

			async with session.get(url = api_url, headers = api_headers, timeout = timeout, params = api_params) as response:
				if response.status == 207:
					json_response = await response.json()

					for collection in json_response['albums']:
						collection_type = ('album' if collection['resource']['type'] != 'EP' else 'ep')
						collection_url = collection['resource']['tidalUrl']
						collection_id = collection['resource']['id']
						collection_title = collection['resource']['title']
						collection_artists = [artist['name'] for artist in collection['resource']['artists']]
						collection_year = collection['resource']['releaseDate'][:4]
						collection_cover = (collection['resource']['imageCover'][1]['url'] if collection['resource']['imageCover'] != [] else '')
						end_time = current_unix_time_ms()
						collections.append(Collection(
							service = self.service,
							type = collection_type,
							url = collection_url,
							id = collection_id,
							title = collection_title,
							artists = collection_artists,
							release_year = collection_year,
							cover_url = collection_cover,
							api_response_time = end_time - start_time,
							api_http_code = response.status
						))
					return filter_collection(service = self.service, collections = collections, query_artists = artists, query_title = title, query_year = year)
				else:
					return Error(
						service = self.service,
						component = self.component,
						http_code = response.status,
						error_msg = "HTTP error when searching for collection",
						request = f'Artists: `{', '.join(artists)}`\nTitle: `{title}`\nYear: `{year}`'
					)


	
	async def lookup_song(self, id: str) -> object:
		async with aiohttp.ClientSession() as session:
			api_url = f'https://openapi.tidal.com/tracks/{id}?countryCode=US'
			api_headers = {
				'accept': 'application/vnd.api+json',
				'Authorization': f'Bearer {await self.get_token()}',
				'Content-Type': 'application/vnd.tidal.v1+json'
			}
			timeout = aiohttp.ClientTimeout(total = 30)
			start_time = current_unix_time_ms()

			async with session.get(url = api_url, headers = api_headers, timeout = timeout) as response:
				if response.status == 200:
					song = await response.json()

					song_type = 'track'
					song_url = song['resource']['tidalUrl']
					song_id = song['resource']['id']
					song_title = song['resource']['title']
					song_artists = [artist['name'] for artist in song['resource']['artists']]
					song_cover = (song['resource']['album']['imageCover'][1]['url'] if song['resource']['album']['imageCover'] != [] else '')
					song_is_explicit = ('explicit' in song['resource']['properties']['content'][0] if 'content' in song['resource']['properties'] else False)
					song_collection = remove_feat(song['resource']['album']['title'])
					end_time = current_unix_time_ms()
					return Song(
						service = self.service,
						type = song_type,
						url = song_url,
						id = song_id,
						title = song_title,
						artists = song_artists,
						collection = song_collection,
						is_explicit = song_is_explicit,
						cover_url = song_cover,
						api_response_time = end_time - start_time,
						api_http_code = response.status
					)
				else:
					return Error(
						service = self.service,
						component = self.component,
						http_code = response.status,
						error_msg = "HTTP error when looking up song ID",
						request = f'ID: `{id}`\n[Open Song URL](https://tidal.com/browse/track/{id})'
					)
				


	async def lookup_collection(self, id: str) -> object:
		async with aiohttp.ClientSession() as session:
			api_url = f'https://openapi.tidal.com/albums/{id}?countryCode=US'
			api_headers = {
				'accept': 'application/vnd.api+json',
				'Authorization': f'Bearer {await self.get_token()}',
				'Content-Type': 'application/vnd.tidal.v1+json'
			}
			timeout = aiohttp.ClientTimeout(total = 30)
			start_time = current_unix_time_ms()

			async with session.get(url = api_url, headers = api_headers, timeout = timeout) as response:
				if response.status == 200:
					collection = await response.json()

					collection_type = ('album' if collection['resource']['type'] != 'EP' else 'ep')
					collection_url = collection['resource']['tidalUrl']
					collection_id = collection['resource']['id']
					collection_title = collection['resource']['title']
					collection_artists = [artist['name'] for artist in collection['resource']['artists']]
					collection_year = collection['resource']['releaseDate'][:4]
					collection_cover = (collection['resource']['imageCover'][1]['url'] if collection['resource']['imageCover'] != [] else '')
					end_time = current_unix_time_ms()
					return Collection(
						service = self.service,
						type = collection_type,
						url = collection_url,
						id = collection_id,
						title = collection_title,
						artists = collection_artists,
						release_year = collection_year,
						cover_url = collection_cover,
						api_response_time = end_time - start_time,
						api_http_code = response.status
					)
				else:
					return Error(
						service = self.service,
						component = self.component,
						http_code = response.status,
						error_msg = "HTTP error when looking up collection ID",
						request = f'ID: `{id}`\n[Open Collection URL](https://tidal.com/browse/album/{id})'
					)



	async def lookup_music_video(self, id: str) -> object:
		async with aiohttp.ClientSession() as session:
			api_url = f'https://openapi.tidal.com/videos/{id}?countryCode=US'
			api_headers = {
				'accept': 'application/vnd.api+json',
				'Authorization': f'Bearer {await self.get_token()}',
				'Content-Type': 'application/vnd.tidal.v1+json'
			}
			timeout = aiohttp.ClientTimeout(total = 30)
			start_time = current_unix_time_ms()

			async with session.get(url = api_url, headers = api_headers, timeout = timeout) as response:
				if response.status == 200:
					mv = await response.json()

					mv_url = mv['resource']['tidalUrl']
					mv_id = mv['resource']['id']
					mv_title = mv['resource']['title']
					mv_artists = [artist['name'] for artist in mv['resource']['artists']]
					mv_thumbnail = (mv['resource']['image'][1]['url'] if mv['resource']['image'] != [] else '')
					mv_is_explicit = ('explicit' in mv['resource']['properties']['content'][0] if 'content' in mv['resource']['properties'] else False)
					end_time = current_unix_time_ms()
					return MusicVideo(
						service = self.service,
						url = mv_url,
						id = mv_id,
						title = mv_title,
						artists = mv_artists,
						is_explicit = mv_is_explicit,
						thumbnail_url = mv_thumbnail,
						api_response_time = end_time - start_time,
						api_http_code = response.status
					)
				else:
					return Error(
						service = self.service,
						component = self.component,
						http_code = response.status,
						error_msg = "HTTP error when looking up music video ID",
						request = f'ID: `{id}`\n[Open MV URL](https://tidal.com/browse/video/{id})'
					)
