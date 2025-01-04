from AstroAPI.components import *
from lyricsgenius import Genius as genius

import aiohttp



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



	async def search_song(self, artists: list, title: str, song_type: str = None, collection: str = None, is_explicit: bool = None) -> object:
		request = 'search_song'
		artists = [optimize_for_search(artist) for artist in artists]
		title = optimize_for_search(title)
		collection = clean_up_collection_title(optimize_for_search(collection)) if collection != None else None
			
		songs = []
		start_time = current_unix_time_ms()
		results = self.api.search_song(title = title, artist = artists[0])
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
				request = {'request': request, 'artists': artists, 'title': title, 'song_type': song_type, 'collection': collection, 'is_explicit': is_explicit}
			))
		return await filter_song(service = self.service, query_request = request, songs = songs, query_artists = artists, query_title = title, query_song_type = song_type, query_collection = None, query_is_explicit = None)
		

	# TODO: make not slow af
	async def search_collection(self, artists: list, title: str, year: int = None) -> object:
		request = 'search_collection'
		artists = [optimize_for_search(artist) for artist in artists]
		title = clean_up_collection_title(optimize_for_search(title))

		collections = []
		start_time = current_unix_time_ms()
		results = self.api.search_albums(f'{artists[0]} {title}')
		# print(current_unix_time_ms() - start_time)
		# save_json(results)
		for result in results['sections'][0]['hits']:
			collection_url = result['result']['url']
			collection_id = result['result']['id']
			collection_title = result['result']['name']
			collection_artists = [result['result']['artist']['name']]
			collection_year = result['result']['release_date_components']['year']
			collection_cover = result['result']['cover_art_url']
			end_time = current_unix_time_ms()
			collections.append(Collection(
				service = self.service,
				type = 'album',
				url = collection_url,
				id = collection_id,
				title = collection_title,
				artists = collection_artists,
				release_year = collection_year,
				cover_url = collection_cover,
				api_response_time = end_time - start_time,
				api_http_code = 200,
				request = {'request': request, 'artists': artists, 'title': title, 'year': year}
			))
		return await filter_collection(service = self.service, query_request = request, collections = collections, query_artists = artists, query_title = title, query_year = year)


