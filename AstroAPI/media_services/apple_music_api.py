from AstroAPI.components import *
import aiohttp



class AppleMusic:
	def __init__(self):
		self.service = 'apple_music'
		self.component = 'Apple Music API'
		print('[AstroAPI] Apple Music API has been initialized.')



	async def search_song(self, artists: list, title: str, song_type: str = None, collection: str = None, is_explicit: bool = None, country_code: str = 'us') -> object:
		async with aiohttp.ClientSession() as session:
			request = {'request': 'search_song', 'artists': artists, 'title': title, 'song_type': song_type, 'collection': collection, 'is_explicit': is_explicit, 'country_code': country_code}
			artists = [optimize_for_search(artist) for artist in artists]
			title = optimize_for_search(replace_with_ascii(title).lower())
			collection = clean_up_collection_title(optimize_for_search(collection)) if collection != None else None
			
			songs = []
			api_url = f'https://itunes.apple.com/search'
			api_params = {
				'term': (f'{artists[0]} "{title}"' if collection == None or song_type == 'single' else f'{artists[0]} "{title}" {collection}'),
				'entity': 'song',
				'limit': 200,
				'country': country_code.lower()
			}
			timeout = aiohttp.ClientTimeout(total = 30)
			start_time = current_unix_time_ms()

			async with session.get(url = api_url, timeout = timeout, params = api_params) as response:
				if response.status == 200:
					json_response = await response.json(content_type = 'text/javascript')

					for song in json_response['results']:
						song_type = ('track' if ' - Single' not in song['collectionName'] else 'single')
						song_url = song['trackViewUrl']
						song_id = song['trackId']
						song_title = song['trackName']
						song_artists = split_artists(song['artistName'])
						song_cover = song['artworkUrl100']
						song_is_explicit = not 'not' in song['trackExplicitness']
						song_collection = remove_feat(clean_up_collection_title(song['collectionName']))
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



	async def search_music_video(self, artists: list, title: str, is_explicit: bool = None, country_code: str = 'us') -> object:
		async with aiohttp.ClientSession() as session:
			request = {'request': 'search_music_video', 'artists': artists, 'title': title, 'is_explicit': is_explicit, 'country_code': country_code}
			artists = [optimize_for_search(artist) for artist in artists]
			title = optimize_for_search(replace_with_ascii(title).lower())
			
			videos = []
			api_url = f'https://itunes.apple.com/search'
			api_params = {
				'term': f'{artists[0]} "{title}"',
				'entity': 'musicVideo',
				'limit': 200,
				'country': country_code.lower()
			}
			timeout = aiohttp.ClientTimeout(total = 30)
			start_time = current_unix_time_ms()

			async with session.get(url = api_url, timeout = timeout, params = api_params) as response:
				if response.status == 200:
					json_response = await response.json(content_type = 'text/javascript')

					for video in json_response['results']:
						mv_url = video['trackViewUrl']
						mv_id = video['trackId']
						mv_title = video['trackName']
						mv_artists = split_artists(video['artistName'])
						mv_cover = video['artworkUrl100']
						mv_is_explicit = not 'not' in video['trackExplicitness']
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
			title = clean_up_collection_title(optimize_for_search(replace_with_ascii(title)))
			
			collections = []
			api_url = f'https://itunes.apple.com/search'
			api_params = {
				'term': f'{artists[0]} "{title}"',
				'entity': 'album',
				'limit': 200,
				'country': country_code.lower()
			}

			timeout = aiohttp.ClientTimeout(total = 30)
			start_time = current_unix_time_ms()

			async with session.get(url = api_url, timeout = timeout, params = api_params) as response:
				if response.status == 200:
					json_response = await response.json(content_type = 'text/javascript')

					for collection in json_response['results']:
						collection_type = ('album' if ' - EP' not in collection['collectionName'] else 'ep')
						collection_url = collection['collectionViewUrl']
						collection_id = collection['collectionId']
						collection_title = clean_up_collection_title(collection['collectionName'])
						collection_artists = split_artists(collection['artistName'])
						collection_year = collection['releaseDate'][:4]
						collection_cover = collection['artworkUrl100']
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
			request = {'request': 'lookup_song', 'id': id, 'country_code': country_code, 'url': f'https://music.apple.com/{country_code}/album/{id}'}
			api_url = f'https://itunes.apple.com/lookup'
			api_params = {
				'id': id,
				'country': country_code.lower()
			}
			timeout = aiohttp.ClientTimeout(total = 30)
			start_time = current_unix_time_ms()

			async with session.get(url = api_url, params = api_params, timeout = timeout) as response:
				if response.status == 200:
					song = await response.json(content_type = 'text/javascript')
					song = song['results'][0]
					
					song_type = 'track' if ' - Single' not in song['collectionName'] else 'single'
					song_url = song['trackViewUrl']
					song_id = song['trackId']
					song_title = song['trackName']
					song_artists = await self.lookup_artist(id = song['artistId'], country_code = country_code)
					song_artists = [song_artists.name] if song_artists.type != 'error' else [song['artistName']]
					song_cover = song['artworkUrl100']
					song_is_explicit = not 'not' in song['trackExplicitness']
					song_collection = remove_feat(clean_up_collection_title(song['collectionName']))
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
				


	async def lookup_music_video(self, id: str, country_code: str = 'us') -> object:
		async with aiohttp.ClientSession() as session:
			request = {'request': 'lookup_music_video', 'id': id, 'country_code': country_code, 'url': f'https://music.apple.com/{country_code}/music-video/{id}'}
			api_url = f'https://itunes.apple.com/lookup'
			api_params = {
				'id': id,
				'country': country_code.lower()
			}
			timeout = aiohttp.ClientTimeout(total = 30)
			start_time = current_unix_time_ms()

			async with session.get(url = api_url, params = api_params, timeout = timeout) as response:
				if response.status == 200:
					video = await response.json(content_type = 'text/javascript')
					video = video['results'][0]

					mv_url = video['trackViewUrl']
					mv_id = video['trackId']
					mv_title = video['trackName']
					mv_artist = await self.lookup_artist(id = video['artistId'], country_code = country_code)
					mv_artist = [mv_artist.name] if mv_artist.type != 'error' else [video['artistName']]
					mv_thumbnail = video['artworkUrl100']
					mv_is_explicit = not 'not' in video['trackExplicitness']
					return MusicVideo(
						service = self.service,
						url = mv_url,
						id = mv_id,
						title = mv_title,
						artists = mv_artist,
						is_explicit = mv_is_explicit,
						thumbnail_url = mv_thumbnail,
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
			request = {'request': 'lookup_collection', 'id': id, 'country_code': country_code, 'url': f'https://music.apple.com/{country_code}/album/{id}'}
			api_url = f'https://itunes.apple.com/lookup'
			api_params = {
				'id': id,
				'country': country_code.lower()
			}
			timeout = aiohttp.ClientTimeout(total = 30)
			start_time = current_unix_time_ms()

			async with session.get(url = api_url, params = api_params, timeout = timeout) as response:
				if response.status == 200:
					collection = await response.json(content_type = 'text/javascript')
					collection = collection['results'][0]

					if ' - Single' not in collection['collectionName']:
						collection_type = ('album' if ' - EP' not in collection['collectionName'] else 'ep')
						collection_url = collection['collectionViewUrl']
						collection_id = collection['collectionId']
						collection_title = clean_up_collection_title(collection['collectionName'])
						collection_artists = await self.lookup_artist(id = collection['artistId'], country_code = country_code)
						collection_artists = [collection_artists.name] if collection_artists.type != 'error' else [collection['artistName']]
						collection_year = collection['releaseDate'][:4]
						collection_cover = collection['artworkUrl100']
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
						song_type = 'single'
						song_url = collection['collectionViewUrl']
						song_id = collection['collectionId']
						song_title = collection['collectionName'].replace(' - Single', '')
						song_artists = await self.lookup_artist(id = collection['artistId'], country_code = country_code)
						song_artists = [song_artists.name] if song_artists.type != 'error' else collection['artistName']
						song_cover = collection['artworkUrl100']
						song_is_explicit = not 'not' in collection['collectionExplicitness']
						song_collection = remove_feat(clean_up_collection_title(collection['collectionName']))
						return Song(
							service = self.service,
							type = song_type,
							url = song_url,
							id = song_id,
							title = song_title,
							artists = [song_artists.name],
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
	


	async def lookup_artist(self, id: str, country_code: str = 'us') -> object:
		async with aiohttp.ClientSession() as session:
			request = {'request': 'lookup_artist', 'id': id, 'country_code': country_code, 'url': f'https://music.apple.com/{country_code}/artist/{id}'}
			api_url = f'https://itunes.apple.com/lookup'
			api_params = {
				'id': id,
				'country': country_code.lower()
			}
			timeout = aiohttp.ClientTimeout(total = 30)
			start_time = current_unix_time_ms()

			async with session.get(url = api_url, params = api_params, timeout = timeout) as response:
				if response.status == 200:
					artist = await response.json(content_type = 'text/javascript')
					artist = artist['results'][0]

					artist_url = artist['artistLinkUrl']
					artist_id = artist['artistId']
					artist_name = artist['artistName']
					artist_genres = [artist['primaryGenreName']]
					return Artist(
						service = self.service,
						url = artist_url,
						id = artist_id,
						name = artist_name,
						genres = artist_genres,
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
						error_msg = "HTTP error when looking up artist ID",
						meta = Meta(
							service = self.service,
							request = request,
							processing_time = current_unix_time_ms() - start_time,
							http_code = response.status
						)
					)
					await log(error)
					return error
