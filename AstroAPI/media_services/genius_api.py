from AstroAPI.components import *
from lyricsgenius import Genius as genius



class Genius:
	def __init__(self):
		self.service = 'genius'
		self.component = 'Genius API'
		self.token = keys['genius']['token']
		self.api = genius(
			access_token = self.token,
			timeout = 30,
			verbose = False,
			skip_non_songs = True,
			sleep_time = 0.1,
			excluded_terms = [
				'(Türkçe Çeviri)',
				'(Tradução em Português)',
				'(Traducción al Español)',
				'(Traduction Française)',
				'(Svensk Översättning)',
				'(Русский перевод)'
			]
		)



	async def search_song(self, artists: list, title: str, song_type: str = None, collection: str = None, is_explicit: bool = None, country_code: str = 'us') -> object:
		try:
			request = 'search_song'
			artists = [optimize_for_search(artist) for artist in artists]
			title = optimize_for_search(title)
			collection = clean_up_collection_title(optimize_for_search(collection)) if collection != None else None

			songs = []
			start_time = current_unix_time_ms()
			results = self.api.search_songs(f'{artists[0]} {title}')
			for result in results['hits']:
				song_url = result['result']['url']
				song_id = result['result']['id']
				song_title = result['result']['title']
				song_artists = [result['result']['primary_artist']['name']]
				song_cover = result['result']['song_art_image_url']
				song_is_explicit = None
				song_collection = None
				end_time = current_unix_time_ms()
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
					api_response_time = end_time - start_time,
					api_http_code = 200,
					request = {'request': request, 'artists': artists, 'title': title, 'song_type': song_type, 'collection': collection, 'is_explicit': is_explicit, 'country_code': country_code}
				))
			return await filter_song(service = self.service, query_request = request, songs = songs, query_artists = artists, query_title = title, query_song_type = song_type, query_collection = None, query_is_explicit = None)
		
		except Exception as msg:
			error = Error(
				service = self.service,
				component = self.component,
				error_msg = f'Error when searching for song: "{msg}"',
				request = {'request': request, 'artists': artists, 'title': title, 'song_type': song_type, 'collection': collection, 'is_explicit': is_explicit, 'country_code': country_code}
			)
			await log(error)
			return error

	async def lookup_song(self, id: str, country_code: str = 'us') -> object:
		try:
			request = 'lookup_song'
			start_time = current_unix_time_ms()
			song = self.api.song(song_id = id)
			song_type = 'track'
			song_url = song['song']['url']
			song_id = song['song']['id']
			song_title = song['song']['title']
			song_artists = [song['song']['primary_artist']['name']]
			song_cover = song['song']['song_art_image_url']
			song_is_explicit = None
			song_collection = song['song']['album']['name']
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
				api_http_code = 200,
				request = {'request': request, 'id': id, 'country_code': country_code}
			)

		except Exception as msg:
			error = Error(
				service = self.service,
				component = self.component,
				error_msg = f'Error when looking up song: "{msg}"',
				request = {'request': request, 'id': id, 'country_code': country_code}
			)
			await log(error)
			return error
