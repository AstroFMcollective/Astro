from AstroAPI.components import *
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
		print('[AstroAPI] TIDAL API has been initialized.')



	async def get_token(self) -> str:
		if self.token == None or (self.token_expiration_date == None or current_unix_time() > self.token_expiration_date):
			async with aiohttp.ClientSession() as session:
				request = {'request': 'get_token'}
				credentials = f'{self.client_id}:{self.client_secret}'
				encoded_credentials = b64encode(credentials.encode('utf-8')).decode('utf-8')
				api_url = 'https://auth.tidal.com/v1/oauth2/token'
				api_data = {'grant_type': 'client_credentials'}
				api_headers = {'Authorization': f'Basic {encoded_credentials}'}
				start_time = current_unix_time_ms()

				async with session.post(url = api_url, data = api_data, headers = api_headers) as response:
					if response.status == 200:
						json_response = await response.json()
						self.token = json_response['access_token']
						self.token_expiration_date = current_unix_time() + int(json_response['expires_in'])

					else:
						error = Error(
							service = self.service,
							component = self.component,
							error_msg = "HTTP error when getting token",
							meta = Meta(
								service = self.service,
								request = request,
								processing_time = current_unix_time_ms() - start_time,
								http_code = response.status
							)
						)
						await log(error)
						return error

		return self.token



	async def search_song(self, artists: list, title: str, song_type: str = None, collection: str = None, is_explicit: bool = None, country_code: str = 'us') -> object:
		async with aiohttp.ClientSession() as session:
			request = {'request': 'search_song', 'artists': artists, 'title': title, 'song_type': song_type, 'collection': collection, 'is_explicit': is_explicit, 'country_code': country_code}
			artists = [optimize_for_search(artist) for artist in artists]
			title = optimize_for_search(title)
			collection = clean_up_collection_title(optimize_for_search(collection)) if collection != None else None
			
			songs = []
			query = f'{artists[0]} {title}'
			api_url = f'https://openapi.tidal.com/v2/searchresults/{query}/relationships/tracks'
			api_params = {
				'countryCode': country_code.upper(),
				'include': 'tracks',
			}
			api_headers = {
				'accept': 'application/vnd.api+json',
				'Authorization': f'Bearer {await self.get_token()}',
				'Content-Type': 'application/vnd.api+json'
			}
			timeout = aiohttp.ClientTimeout(total = 30)
			start_time = current_unix_time_ms()

			async with session.get(url = api_url, headers = api_headers, timeout = timeout, params = api_params) as response:
				if response.status == 200:
					json_response = await response.json()
					save_json(json_response)

					# for song in json_response['included']:
					# 	song_type = 'track'
					# 	song_url = song['attributes']['externalLinks'][0]['href']
					# 	song_id = song['id']
					# 	song_title = song['attributes']['title']
					# 	song_artist_objs = await self.lookup_artist(song_id = song_id)
					# 	song_artists = [artist.name for artist in song_artist_objs]
					# 	song_cover = None
					# 	song_is_explicit = song['attributes']['explicit']
					# 	song_collection = None
					
					'''for song in json_response['tracks']:
						song_type = 'track'
						song_url = song['resource']['tidalUrl']
						song_id = song['resource']['id']
						song_title = song['resource']['title']
						song_artists = [artist['name'] for artist in song['resource']['artists']]
						song_cover = (song['resource']['album']['imageCover'][1]['url'] if song['resource']['album']['imageCover'] != [] else '')
						song_is_explicit = ('explicit' in song['resource']['properties']['content'][0] if 'content' in song['resource']['properties'] else False)
						song_collection = remove_feat(song['resource']['album']['title'])'''
					# songs.append(Song(
					# 		service = self.service,
					# 		type = song_type,
					# 		url = song_url,
					# 		id = song_id,
					# 		title = song_title,
					# 		artists = song_artists,
					# 		collection = song_collection,
					# 		is_explicit = song_is_explicit,
					# 		cover_url = song_cover,
					# 		meta = Meta(
					# 			service = self.service,
					# 			request = request,
					# 			processing_time = current_unix_time_ms() - start_time,
					# 			http_code = response.status
					# 		)
					# 	))
					# return await filter_song(service = self.service, query_request = request, songs = songs, query_artists = artists, query_title = title, query_song_type = song_type, query_collection = collection, query_is_explicit = is_explicit, query_country_code = country_code)

				else:
					error = Error(
						service = self.service,
						component = self.component,
						error_msg = "HTTP error when searching for song",
						meta = Meta(
							service = self.service,
							request = request,
							processing_time = current_unix_time_ms() - start_time,
							http_code = response.status
						)
					)
					await log(error)
					return error
	


	async def search_music_video(self, artists: list, title: str, is_explicit: bool = None, country_code: str = 'us') -> object:
		async with aiohttp.ClientSession() as session:
			request = {'request': 'search_music_video', 'artists': artists, 'title': title, 'is_explicit': is_explicit, 'country_code': country_code}
			artists = [optimize_for_search(artist) for artist in artists]
			title = optimize_for_search(title)
			
			videos = []
			api_url = f'https://openapi.tidal.com/search'
			api_params = {
				'query': f'{artists[0]} {title}',
				'type': 'VIDEOS',
				'offset': 0,
				'limit': 100,
				'countryCode': country_code.upper(),
				'popularity': 'WORLDWIDE'
			}
			api_headers = {
				'accept': 'application/vnd.tidal.v1+json',
				'Authorization': f'Bearer {await self.get_token()}',
				'Content-Type': 'application/vnd.tidal.v1+json'
			}
			timeout = aiohttp.ClientTimeout(total = 30)
			start_time = current_unix_time_ms()

			async with session.get(url = api_url, headers = api_headers, timeout = timeout, params = api_params) as response:
				if response.status == 207:
					json_response = await response.json()

					for video in json_response['videos']:
						mv_url = video['resource']['tidalUrl']
						mv_id = video['resource']['id']
						mv_title = video['resource']['title']
						mv_artists = [artist['name'] for artist in video['resource']['artists']]
						mv_cover = (video['resource']['image'][1]['url'] if video['resource']['image'] != [] else '')
						mv_is_explicit = ('explicit' in video['resource']['properties']['content'][0] if 'content' in video['resource']['properties'] else False)
						videos.append(MusicVideo(
							service = self.service,
							url = mv_url,
							id = mv_id,
							title = mv_title,
							artists = mv_artists,
							is_explicit = mv_is_explicit,
							thumbnail_url = mv_cover,
							meta = Meta(
								service = self.service,
								request = request,
								processing_time = current_unix_time_ms() - start_time,
								http_code = response.status
							)
						))
					return await filter_mv(service = self.service, query_request = request, videos = videos, query_artists = artists, query_title = title, query_is_explicit = is_explicit, query_country_code = country_code)

				else:
					error = Error(
						service = self.service,
						component = self.component,
						error_msg = "HTTP error when searching for music video",
						meta = Meta(
							service = self.service,
							request = request,
							processing_time = current_unix_time_ms() - start_time,
							http_code = response.status
						)
					)
					await log(error)
					return error



	async def search_collection(self, artists: list, title: str, year: int = None, country_code: str = 'us') -> object:
		async with aiohttp.ClientSession() as session:
			request = {'request': 'search_collection', 'artists': artists, 'title': title, 'year': year, 'country_code': country_code}
			artists = [optimize_for_search(artist) for artist in artists]
			title = clean_up_collection_title(optimize_for_search(title))
			
			collections = []
			api_url = f'https://openapi.tidal.com/search'
			api_params = {
				'query': f'{artists[0]} {title}',
				'type': 'ALBUMS',
				'offset': 0,
				'limit': 100,
				'countryCode': country_code.upper(),
				'popularity': 'WORLDWIDE'
			}
			api_headers = {
				'accept': 'application/vnd.tidal.v1+json',
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
						collections.append(Collection(
							service = self.service,
							type = collection_type,
							url = collection_url,
							id = collection_id,
							title = collection_title,
							artists = collection_artists,
							release_year = collection_year,
							cover_url = collection_cover,
							meta = Meta(
								service = self.service,
								request = request,
								processing_time = current_unix_time_ms() - start_time,
								http_code = response.status
							)
						))
					return await filter_collection(service = self.service, query_request = request, collections = collections, query_artists = artists, query_title = title, query_year = year, query_country_code = country_code)

				else:
					error = Error(
						service = self.service,
						component = self.component,
						http_code = response.status,
						error_msg = "HTTP error when searching for collection",
						meta = Meta(
							service = self.service,
							request = request,
							processing_time = current_unix_time_ms() - start_time,
							http_code = response.status
						)
					)
					await log(error)
					return error


	
	async def lookup_song(self, id: str, country_code: str = 'us') -> object:
		async with aiohttp.ClientSession() as session:
			request = {'request': 'lookup_song', 'id': id, 'country_code': country_code, 'url': f'https://tidal.com/browse/track/{id}'}
			api_url = f'https://openapi.tidal.com/tracks/{id}?countryCode=US'
			api_headers = {
				'accept': 'application/vnd.tidal.v1+json',
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
						meta = Meta(
							service = self.service,
							request = request,
							processing_time = current_unix_time_ms() - start_time,
							filter_confidence_percentage = 100.0,
							http_code = response.status
						)
					)

				else:
					error = Error(
						service = self.service,
						component = self.component,
						error_msg = "HTTP error when looking up song ID",
						meta = Meta(
							service = self.service,
							request = request,
							processing_time = current_unix_time_ms() - start_time,
							http_code = response.status
						)
					)
					await log(error)
					return error



	async def lookup_music_video(self, id: str) -> object:
		async with aiohttp.ClientSession() as session:
			request = {'request': 'lookup_music_video', 'id': id, 'url': f'https://tidal.com/browse/video/{id}'}
			api_url = f'https://openapi.tidal.com/videos/{id}?countryCode=US'
			api_headers = {
				'accept': 'application/vnd.tidal.v1+json',
				'Authorization': f'Bearer {await self.get_token()}',
				'Content-Type': 'application/vnd.tidal.v1+json'
			}
			timeout = aiohttp.ClientTimeout(total = 30)
			start_time = current_unix_time_ms()

			async with session.get(url = api_url, headers = api_headers, timeout = timeout) as response:
				if response.status == 200:
					video = await response.json()

					mv_url = video['resource']['tidalUrl']
					mv_id = video['resource']['id']
					mv_title = video['resource']['title']
					mv_artists = [artist['name'] for artist in video['resource']['artists']]
					mv_thumbnail = (video['resource']['image'][1]['url'] if video['resource']['image'] != [] else '')
					mv_is_explicit = ('explicit' in video['resource']['properties']['content'][0] if 'content' in video['resource']['properties'] else False)
					
					return MusicVideo(
						service = self.service,
						url = mv_url,
						id = mv_id,
						title = mv_title,
						artists = mv_artists,
						is_explicit = mv_is_explicit,
						thumbnail_url = mv_thumbnail,
						meta = Meta(
							service = self.service,
							request = request,
							processing_time = current_unix_time_ms() - start_time,
							filter_confidence_percentage = 100.0,
							http_code = response.status
						)
					)

				else:
					error = Error(
						service = self.service,
						component = self.component,
						error_msg = "HTTP error when looking up music video ID",
						meta = Meta(
							service = self.service,
							request = request,
							processing_time = current_unix_time_ms() - start_time,
							http_code = response.status
						)
					)
					await log(error)
					return error



	async def lookup_collection(self, id: str, country_code: str = 'us') -> object:
		async with aiohttp.ClientSession() as session:
			request = {'request': 'lookup_collection', 'id': id, 'country_code': country_code, 'url': f'https://tidal.com/browse/album/{id}'}
			api_url = f'https://openapi.tidal.com/albums/{id}?countryCode=US'
			api_headers = {
				'accept': 'application/vnd.tidal.v1+json',
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
					return Collection(
						service = self.service,
						type = collection_type,
						url = collection_url,
						id = collection_id,
						title = collection_title,
						artists = collection_artists,
						release_year = collection_year,
						cover_url = collection_cover,
						meta = Meta(
							service = self.service,
							request = request,
							processing_time = current_unix_time_ms() - start_time,
							filter_confidence_percentage = 100.0,
							http_code = response.status
						)
					)

				else:
					error = Error(
						service = self.service,
						component = self.component,
						error_msg = "HTTP error when looking up collection ID",
						meta = Meta(
							service = self.service,
							request = request,
							processing_time = current_unix_time_ms() - start_time,
							http_code = response.status
						)
					)
					await log(error)
					return error
				


	async def lookup_artist(self, id: str = None, song_id: str = None, country_code: str = 'us') -> list[object]:
		async with aiohttp.ClientSession() as session:
			request = {'request': 'lookup_artist', 'id': id, 'song_id': song_id, 'country_code': country_code}
			api_headers = {
				'accept': 'application/vnd.tidal.v1+json',
				'Authorization': f'Bearer {await self.get_token()}',
				'Content-Type': 'application/vnd.tidal.v1+json'
			}
			timeout = aiohttp.ClientTimeout(total = 30)
			start_time = current_unix_time_ms()
			artists = []

			if id is not None:
				api_url = f'https://openapi.tidal.com/v2/artists/{id}'
				api_params = {
					'countryCode': country_code.upper(),
					'include': 'artists'
				}
				async with session.get(url = api_url, headers = api_headers, timeout = timeout, params = api_params) as response:
					if response.status == 200:
						json_response = await response.json()
						#save_json(json_response)
						artist_url = json_response['data']['attributes']['externalLinks'][0]['href']
						artist_id = json_response['data']['id']
						artist_name = json_response['data']['attributes']['name']
						artist_profile_pic_url = None if json_response['data']['attributes']['imageLinks'] == [] else json_response['data']['attributes']['imageLinks'][0]['href']
						return [
							Artist(
								service = self.service,
								url = artist_url,
								id = artist_id,
								name = artist_name,
								profie_pic_url = artist_profile_pic_url,
								meta = Meta(
									service = self.service,
									request = request,
									processing_time = current_unix_time_ms() - start_time,
									http_code = response.status
								)
							)
						]
					
					else:
						error = Error(
							service = self.service,
							component = self.component,
							error_msg = "HTTP error when looking up artist (via artist ID)",
							meta = Meta(
								service = self.service,
								request = request,
								processing_time = current_unix_time_ms() - start_time,
								http_code = response.status
							)
						)
						await log(error)
						return error
			
			elif song_id is not None:
				api_url = f'https://openapi.tidal.com/v2/tracks/{song_id}/relationships/artists'
				api_params = {
					'countryCode': country_code.upper(),
					'include': 'artists'
				}
				async with session.get(url = api_url, headers = api_headers, timeout = timeout, params = api_params) as response:
					if response.status == 200:
						json_response = await response.json()
						#save_json(json_response)
						for artist in json_response['included']:
							artist_url = artist['attributes']['externalLinks'][0]['href']
							artist_id = artist['id']
							artist_name = artist['attributes']['name']
							artist_profile_pic_url = None if artist['attributes']['imageLinks'] == [] else artist['attributes']['imageLinks'][0]['href']
							artists.append(
								Artist(
									service = self.service,
									url = artist_url,
									id = artist_id,
									name = artist_name,
									profie_pic_url = artist_profile_pic_url,
									meta = Meta(
										service = self.service,
										request = request,
										processing_time = current_unix_time_ms() - start_time,
										http_code = response.status
									)
								)
							)
						return artists

					else:
						error = Error(
							service = self.service,
							component = self.component,
							error_msg = "HTTP error when looking up artist (via song ID)",
							meta = Meta(
								service = self.service,
								request = request,
								processing_time = current_unix_time_ms() - start_time,
								http_code = response.status
							)
						)
						await log(error)
						return error
					