from AstroAPI.components.all import *
import aiohttp

class AppleMusic:
	def __init__(self):
		self.service = 'apple_music'
		self.component = 'Apple Music API'

	async def search_song(self, artists: list, title: str, song_type: str = None, collection: str = None, is_explicit: bool = None) -> object:
		async with aiohttp.ClientSession() as session:
			artists = [optimize_for_search(artist) for artist in artists]
			title = optimize_for_search(replace_with_ascii(title).lower())
			collection = clean_up_collection_title(optimize_for_search(collection)) if collection != None else None
			
			songs = []
			api_url = f'https://itunes.apple.com/search'
			api_params = {
				'term': (f'{artists[0]} "{title}"' if collection == None else f'{artists[0]} "{title}" {collection}'),
				'entity': 'song',
				'limit': 200,
				'country': 'us'
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
			title = clean_up_collection_title(optimize_for_search(replace_with_ascii(title)))
			
			collections = []
			api_url = f'https://itunes.apple.com/search'
			api_params = {
				'term': f'{artists[0]} "{title}"',
				'entity': 'album',
				'limit': 200,
				'country': 'us'
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


	
	async def lookup_song(self, id: str, country_code: str) -> object:
		async with aiohttp.ClientSession() as session:
			api_url = f'https://itunes.apple.com/lookup'
			api_params = {
				'id': id,
				'country': country_code
			}
			timeout = aiohttp.ClientTimeout(total = 30)
			start_time = current_unix_time_ms()

			async with session.get(url = api_url, params = api_params, timeout = timeout) as response:
				if response.status == 200:
					song = await response.json(content_type = 'text/javascript')
					song = song['results'][0]
					
					song_type = ('track' if ' - Single' not in song['collectionName'] else 'single')
					song_url = song['trackViewUrl']
					song_id = song['trackId']
					song_title = song['trackName']
					song_artists = await self.lookup_artist(id = song['artistId'], country_code = country_code)
					song_cover = song['artworkUrl100']
					song_is_explicit = not 'not' in song['trackExplicitness']
					song_collection = remove_feat(clean_up_collection_title(song['collectionName']))
					end_time = current_unix_time_ms()
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
						api_response_time = end_time - start_time,
						api_http_code = response.status
					)
				else:
					return Error(
						service = self.service,
						component = self.component,
						http_code = response.status,
						error_msg = "HTTP error when looking up song ID",
						request = f'ID: `{id}`\n[Open Song URL](https://music.apple.com/{country_code}/album/{id})'
					)
				


	async def lookup_collection(self, id: str, country_code: str) -> object:
		async with aiohttp.ClientSession() as session:
			api_url = f'https://itunes.apple.com/lookup'
			api_params = {
				'id': id,
				'country': country_code
			}
			timeout = aiohttp.ClientTimeout(total = 30)
			start_time = current_unix_time_ms()

			async with session.get(url = api_url, params = api_params, timeout = timeout) as response:
				if response.status == 200:
					collection = await response.json(content_type = 'text/javascript')
					collection = collection['results'][0]

					collection_type = ('album' if ' - EP' not in collection['collectionName'] else 'ep')
					collection_url = collection['collectionViewUrl']
					collection_id = collection['collectionId']
					collection_title = clean_up_collection_title(collection['collectionName'])
					collection_artists = await self.lookup_artist(id = collection['artistId'], country_code = country_code)
					collection_year = collection['releaseDate'][:4]
					collection_cover = collection['artworkUrl100']
					end_time = current_unix_time_ms()
					return Collection(
						service = self.service,
						type = collection_type,
						url = collection_url,
						id = collection_id,
						title = collection_title,
						artists = [collection_artists.name],
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
						request = f'ID: `{id}`\n[Open Collection URL](https://music.apple.com/{country_code}/album/{id})'
					)
	
	async def lookup_music_video(self, id: str, country_code: str) -> object:
		async with aiohttp.ClientSession() as session:
			api_url = f'https://itunes.apple.com/lookup'
			api_params = {
				'id': id,
				'country': country_code
			}
			timeout = aiohttp.ClientTimeout(total = 30)
			start_time = current_unix_time_ms()

			async with session.get(url = api_url, params = api_params, timeout = timeout) as response:
				if response.status == 200:
					song = await response.json(content_type = 'text/javascript')
					song = song['results'][0]

					mv_url = song['trackViewUrl']
					mv_id = song['trackId']
					mv_title = song['trackName']
					mv_artists = await self.lookup_artist(id = song['artistId'], country_code = country_code)
					mv_thumbnail = song['artworkUrl100']
					mv_is_explicit = not 'not' in song['trackExplicitness']
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
						request = f'ID: `{id}`\n[Open MV URL](https://music.apple.com/{country_code}/music-video/{id})'
					)
	


	async def lookup_artist(self, id: str, country_code: str) -> object:
		async with aiohttp.ClientSession() as session:
			api_url = f'https://itunes.apple.com/lookup'
			api_params = {
				'id': id,
				'country': country_code
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
					end_time = current_unix_time_ms()
					return Artist(
						service = self.service,
						url = artist_url,
						id = artist_id,
						name = artist_name,
						genres = artist_genres,
						profie_pic_url = 'https://developer.valvesoftware.com/w/images/thumb/8/8b/Debugempty.png/200px-Debugempty.png',
						api_response_time = end_time - start_time,
						api_http_code = response.status
					)
				else:
					return Error(
						service = self.service,
						component = self.component,
						http_code = response.status,
						error_msg = "HTTP error when looking up artist ID",
						request = f'ID: `{id}`\n[Open Artist URL](https://music.apple.com/{country_code}/artist/{id})'
					)
