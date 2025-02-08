from AstroAPI.components import *
import requests



class Genius:
	def __init__(self, token: str):
		self.service = 'genius'
		self.component = 'Genius API'
		self.token = token
		print('[AstroAPI] Genius API has been initialized.')




	async def search_song(self, artists: list, title: str, song_type: str = None, collection: str = None, is_explicit: bool = None, country_code: str = 'us') -> object:
		request = {'request': 'search_song', 'artists': artists, 'title': title, 'song_type': song_type, 'collection': collection, 'is_explicit': is_explicit, 'country_code': country_code}
		artists = [optimize_for_search(artist) for artist in artists]
		title = optimize_for_search(title)
		collection = clean_up_collection_title(optimize_for_search(collection)) if collection != None else None
			
		songs = []
		api_url = f'https://api.genius.com/search'
		api_params = {
			'q': f'{artists[0]} {title}',
		}
		api_headers = {'Authorization': f'Bearer {self.token}'}
		start_time = current_unix_time_ms()
		results = requests.get(api_url, api_params, headers = api_headers)

		if results.status_code == 200:
			results_json = results.json()['response']
			for result in results_json['hits']:
				song_url = result['result']['url']
				song_id = result['result']['id']
				song_title = result['result']['title']
				song_artists = [result['result']['primary_artist']['name']]
				song_cover = result['result']['song_art_image_url']
				song_is_explicit = None
				song_collection = None
				songs.append(Song(
					service = self.service,
					type = 'track',
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
						processing_time = {self.service: current_unix_time_ms() - start_time},
						http_code = results.status_code
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
					processing_time = {self.service: current_unix_time_ms() - start_time},
					http_code = result.status_code
				)			
			)
			await log(error)
			return error



	async def search_music_video(self, artists: list, title: str, is_explicit: bool = None, country_code: str = 'us') -> object:
		request = {'request': 'search_music_video', 'artists': artists, 'title': title, 'is_explicit': is_explicit, 'country_code': country_code}
		artists = [optimize_for_search(artist) for artist in artists]
		title = optimize_for_search(replace_with_ascii(title).lower())
			
		videos = []
		api_url = f'https://api.genius.com/search'
		api_params = {
			'q': f'{artists[0]} {title}',
		}
		api_headers = {'Authorization': f'Bearer {self.token}'}
		start_time = current_unix_time_ms()
		results = requests.get(api_url, api_params, headers = api_headers)
		
		if results.status_code == 200:
			results_json = results.json()['response']
			for result in results_json['hits']:
				mv_url = result['result']['url']
				mv_id = result['result']['id']
				mv_title = result['result']['title']
				mv_artists = [result['result']['primary_artist']['name']]
				mv_cover = result['result']['song_art_image_url']
				mv_is_explicit = None
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
						processing_time = {self.service: current_unix_time_ms() - start_time},
						http_code = results.status_code
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
					processing_time = {self.service: current_unix_time_ms() - start_time},
					http_code = result.status_code
				)
			)
			await log(error)
			return error


	async def lookup_song(self, id: str, country_code: str = 'us') -> object:
		request = {'request': 'lookup_song', 'id': id, 'country_code': country_code}
		api_url = f'https://api.genius.com/songs/{id}'
		api_headers = {'Authorization': f'Bearer {self.token}'}
		start_time = current_unix_time_ms()
		result = requests.get(api_url, headers = api_headers)
		
		if result.status_code == 200:
			song = result['response']
			song_type = 'track'
			song_url = song['song']['url']
			song_id = song['song']['id']
			song_title = song['song']['title']
			song_artists = [song['song']['primary_artist']['name']]
			song_cover = song['song']['song_art_image_url']
			song_is_explicit = None
			song_collection = song['song']['album']['name']
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
					processing_time = {self.service: current_unix_time_ms() - start_time},
					filter_confidence_percentage = {self.service: 100.0},
					http_code = result.status_code
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
					processing_time = {self.service: current_unix_time_ms() - start_time},
					http_code = result.status_code
				)
			)
			await log(error)
			return error
