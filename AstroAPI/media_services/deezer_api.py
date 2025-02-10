from AstroAPI.components import *
import aiohttp



class Deezer:
	def __init__(self):
		self.service = 'deezer'
		self.component = 'Deezer API'
		print('[AstroAPI] Deezer API has been initialized.')



	async def search_song(self, artists: list, title: str, song_type: str = None, collection: str = None, is_explicit: bool = None, country_code: str = 'us') -> object:
		async with aiohttp.ClientSession() as session:
			request = {'request': 'search_song', 'artists': artists, 'title': title, 'song_type': song_type, 'collection': collection, 'is_explicit': is_explicit, 'country_code': country_code}
			artists = [optimize_for_search(artist) for artist in artists]
			title = optimize_for_search(title)
			collection = clean_up_collection_title(optimize_for_search(collection)) if collection != None else None
			
			songs = []
			api_url = f'https://api.deezer.com/search/track'
			api_params = {
				'q': f'artist:"{artists[0]}" track:"{title}"',
			}
			api_headers = {
				'Content-Type': 'application/json'
			}
			timeout = aiohttp.ClientTimeout(total = 30)
			start_time = current_unix_time_ms()

			async with session.get(url = api_url, headers = api_headers, timeout = timeout, params = api_params) as response:
				if response.status == 200:
					json_response = await response.json()

					for data in json_response['data']:
						async with session.get(url = f'https://api.deezer.com/track/{data['id']}', headers = api_headers) as result:
							song = await result.json()
							song_type = 'track'
							song_url = song['link']
							song_id = song['id']
							song_title = song['title']
							song_artists = [artist['name'] for artist in song['contributors']]
							song_cover = song['album']['cover_xl']
							song_is_explicit = song['explicit_lyrics']
							song_collection = remove_feat(song['album']['title'])
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
								meta = Meta(
									service = self.service,
									request = request,
									processing_time = current_unix_time_ms() - start_time,
									http_code = response.status
								)
							))
					return await filter_song(service = self.service, query_request = request, songs = songs, query_artists = artists, query_title = title, query_song_type = song_type, query_collection = collection, query_is_explicit = is_explicit, query_country_code = country_code)
				
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



	async def search_collection(self, artists: list, title: str, year: int = None, country_code: str = 'us') -> object:
		async with aiohttp.ClientSession() as session:
			request = {'request': 'search_collection', 'artists': artists, 'title': title, 'year': year, 'country_code': country_code}
			artists = [optimize_for_search(artist) for artist in artists]
			title = clean_up_collection_title(optimize_for_search(title))
			
			collections = []
			api_url = f'https://api.deezer.com/search/album'
			api_params = {
				'q': f'artist:"{artists[0]}" album:"{title}"',
			}
			api_headers = {
				'Content-Type': 'application/json'
			}
			timeout = aiohttp.ClientTimeout(total = 30)
			start_time = current_unix_time_ms()

			async with session.get(url = api_url, headers = api_headers, timeout = timeout, params = api_params) as response:
				if response.status == 200:
					json_response = await response.json()

					for data in json_response['data']:
						async with session.get(url = f'https://api.deezer.com/album/{data['id']}', headers = api_headers) as result:
							collection = await result.json()
							collection_type = ('album' if collection['record_type'] != 'ep' else 'ep')
							collection_url = collection['link']
							collection_id = collection['id']
							collection_title = collection['title']
							collection_artists = [artist['name'] for artist in collection['contributors']]
							collection_year = collection['release_date'][:4]
							collection_cover = collection['cover_xl']
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
			request = {'request': 'lookup_song', 'id': id, 'country_code': country_code, 'url': f'https://www.deezer.com/track/{id}'}
			api_url = f'https://api.deezer.com/track/{id}'
			api_headers = {
				'Content-Type': 'application/json'
			}
			timeout = aiohttp.ClientTimeout(total = 30)
			start_time = current_unix_time_ms()

			async with session.get(url = api_url, headers = api_headers, timeout = timeout) as response:
				if response.status == 200:
					song = await response.json()

					song_type = 'track'
					song_url = song['link']
					song_id = song['id']
					song_title = song['title']
					song_artists = [artist['name'] for artist in song['contributors']]
					song_cover = song['album']['cover_xl']
					song_is_explicit = song['explicit_lyrics']
					song_collection = remove_feat(song['album']['title'])
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
							filter_confidence_percentage = {self.service: 100.0},
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
				


	async def lookup_collection(self, id: str, country_code: str = 'us') -> object:
		async with aiohttp.ClientSession() as session:
			request = {'request': 'lookup_collection', 'id': id, 'country_code': country_code, 'url': f'https://www.deezer.com/album/{id}'}
			api_url = f'https://api.deezer.com/album/{id}'
			api_headers = {
				'Content-Type': 'application/json'
			}
			timeout = aiohttp.ClientTimeout(total = 30)
			start_time = current_unix_time_ms()

			async with session.get(url = api_url, headers = api_headers, timeout = timeout) as response:
				if response.status == 200:
					collection = await response.json()

					collection_type = ('album' if collection['record_type'] != 'ep' else 'ep')
					collection_url = collection['link']
					collection_id = collection['id']
					collection_title = collection['title']
					collection_artists = [artist['name'] for artist in collection['contributors']]
					collection_year = collection['release_date'][:4]
					collection_cover = collection['cover_xl']
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
							filter_confidence_percentage = {self.service: 100.0},
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
