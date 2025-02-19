from AstroAPI.components import *
import requests



class Genius:
	def __init__(self, token: str):
		self.service = 'genius'
		self.component = 'Genius API'
		self.token = token
		print('[AstroAPI] Genius API has been initialized.')



	async def search_song_knowledge(self, artists: list, title: str, song_type: str = None, collection: str = None, is_explicit: bool = None, country_code: str = 'us') -> object:
		request = {'request': 'search_song', 'artists': artists, 'title': title, 'song_type': song_type, 'collection': collection, 'is_explicit': is_explicit, 'country_code': country_code}
		artists = [optimize_for_search(artist) for artist in artists]
		title = optimize_for_search(title)
		collection = clean_up_collection_title(optimize_for_search(collection)) if collection != None else None
			
		songs = []
		api_url = f'https://api.genius.com/search'
		api_params = {
			'q': f'{artists[0]} {title}'
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
			filtered_song = await filter_song(service = self.service, query_request = request, songs = songs, query_artists = artists, query_title = title, query_song_type = song_type, query_collection = collection, query_is_explicit = is_explicit, query_country_code = country_code)
			song = await self.lookup_song_knowledge(id = filtered_song.id['genius'], country_code = country_code)
			song.meta.processing_time[self.service] = current_unix_time_ms() - start_time
			return song

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



	async def search_query_knowledge(self, query: str, country_code: str = 'us') -> object:
		request = {'request': 'search_query', 'query': query, 'country_code': country_code}

		api_url = f'https://api.genius.com/search'
		api_params = {
			'q': query
		}
		api_headers = {'Authorization': f'Bearer {self.token}'}
		start_time = current_unix_time_ms()
		results = requests.get(api_url, api_params, headers = api_headers)

		if results.status_code == 200:
			results_json = results.json()['response']
			song_id = results_json['hits'][0]['result']['id']
			song = await self.lookup_song_knowledge(id = song_id, country_code = country_code)
			song.meta.processing_time[self.service] = current_unix_time_ms() - start_time
			return song



	async def lookup_song_knowledge(self, id: str, country_code: str = 'us') -> object:
		request = {'request': 'lookup_song', 'id': id, 'country_code': country_code}
		api_url = f'https://api.genius.com/songs/{id}'
		api_headers = {'Authorization': f'Bearer {self.token}'}
		start_time = current_unix_time_ms()
		result = requests.get(api_url, headers = api_headers)
		
		if result.status_code == 200:
			song = result.json()['response']['song']
			#save_json(song)
			song_type = 'track'
			song_url = song['url']
			song_id = song['id']
			song_title = song['title']
			song_artists = [song['primary_artist']['name']]
			song_collection = song['album']['name'] if song['album'] != None else None
			song_description = convert_genius_desc_into_discord_str(song['description'])
			song_release_date = song['release_date_for_display']
			song_cover = song['song_art_image_url']
			song_cover_color_hex = int(song['song_art_primary_color'][1:], base = 16)
			song_is_explicit = None
			return Knowledge(
				service = self.service,
				media_type = song_type,
				url = song_url,
				id = song_id,
				title = song_title,
				artists = song_artists,
				collection = song_collection,
				description = song_description,
				release_date = song_release_date,
				is_explicit = song_is_explicit,
				cover_url = song_cover,
				cover_color_hex = song_cover_color_hex,
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
				error_msg = "HTTP error when looking up song knowledge",
				meta = Meta(
					service = self.service,
					request = request,
					processing_time = {self.service: current_unix_time_ms() - start_time},
					http_code = result.status_code
				)
			)
			await log(error)
			return error
