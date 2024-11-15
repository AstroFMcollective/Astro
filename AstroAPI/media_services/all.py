from AstroAPI.media_services import spotify_api, apple_music_api, youtube_music_api, tidal_api, deezer_api
from AstroAPI.components.ini import service_keys
from AstroAPI.components.all import *
from asyncio import *



Spotify = spotify_api.Spotify(client_id = service_keys['spotify']['id'], client_secret = service_keys['spotify']['secret'])
AppleMusic = apple_music_api.AppleMusic()
YouTubeMusic = youtube_music_api.YouTubeMusic()
Tidal = tidal_api.Tidal(client_id = service_keys['tidal']['id'], client_secret = f'{service_keys['tidal']['secret']}=')
Deezer = deezer_api.Deezer()



class GlobalIO: 
	def __init__(self):
		self.service = 'global'
		self.component = 'Global API Interface'



	async def search_song(self, artists: list, title: str, song_type: str = None, collection: str = None, is_explicit: bool = None) -> object:
		start_time = current_unix_time_ms()
		tasks = [
			asyncio.create_task(Spotify.search_song(artists, title, song_type, collection, is_explicit), name = Spotify.service),
			asyncio.create_task(AppleMusic.search_song(artists, title, song_type, collection, is_explicit), name = AppleMusic.service),
			asyncio.create_task(YouTubeMusic.search_song(artists, title, song_type, collection, is_explicit), name = YouTubeMusic.service),
			asyncio.create_task(Tidal.search_song(artists, title, song_type, collection, is_explicit), name = Tidal.service),
			asyncio.create_task(Deezer.search_song(artists, title, song_type, collection, is_explicit), name = Deezer.service)
		]

		unlabeled_results = await asyncio.gather(*tasks)
		labeled_results = {}
		for result in unlabeled_results:
			labeled_results[result.service] = result
		
		services = [Spotify.service, AppleMusic.service, YouTubeMusic.service, Deezer.service, Tidal.service]

		type_order = [Spotify.service, AppleMusic.service, YouTubeMusic.service, Deezer.service, Tidal.service]
		title_order = [Spotify.service, AppleMusic.service, YouTubeMusic.service, Deezer.service, Tidal.service]
		artists_order = [Spotify.service, Tidal.service, YouTubeMusic.service, Deezer.service, AppleMusic.service]
		collection_order = [Spotify.service, AppleMusic.service, YouTubeMusic.service, Deezer.service, Tidal.service]
		explicitness_order = [Spotify.service, AppleMusic.service, YouTubeMusic.service, Deezer.service, Tidal.service]
		cover_order = [Tidal.service, Deezer.service, Spotify.service, AppleMusic.service, YouTubeMusic.service]

		for service in services:
			if labeled_results[service].type != 'track' and labeled_results[service].type != 'single':
				type_order.remove(service)
				title_order.remove(service)
				artists_order.remove(service)
				collection_order.remove(service)
				explicitness_order.remove(service)
				cover_order.remove(service)
				del unlabeled_results[list(labeled_results.keys()).index(service)]
				del labeled_results[service]

		result_type = None
		result_urls = {}
		result_ids = {}
		result_title = None
		result_artists = None
		result_collection = None
		result_is_explicit = None
		result_cover = None

		for service in range(len(type_order)):
			if result_type == None:
				result_type = labeled_results[type_order[service]].type
			if result_urls == {}:
				for result in unlabeled_results:
					result_urls[result.service] = result.url[result.service]
			if result_ids == {}:
				for result in unlabeled_results:
					result_ids[result.service] = result.id[result.service]
			if result_title == None:
				result_title = labeled_results[title_order[service]].title
			if result_artists == None:
				result_artists = labeled_results[artists_order[service]].artists
			if result_collection == None:
				result_collection = labeled_results[collection_order[service]].collection
			if result_is_explicit == None:
				result_is_explicit = labeled_results[explicitness_order[service]].is_explicit
			if result_cover == None:
				result_cover = labeled_results[cover_order[service]].cover_url

		end_time = current_unix_time_ms()

		if result_title != None:
			return Song(
				service = self.service,
				type = result_type,
				url = result_urls,
				id = result_ids,
				title = result_title,
				artists = result_artists,
				collection = result_collection,
				is_explicit = result_is_explicit,
				cover_url = result_cover,
				api_response_time = end_time - start_time,
				api_http_code = 200
			)
		else:
			return Empty(
				service = service,
				request = f'Artists: `{', '.join(artists)}`\nTitle: `{title}`\nSong type: `{song_type}`\nCollection title: `{collection}`\nIs explicit? `{is_explicit}`'
			)
	


	async def search_collection(self, artists: list, title: str, year: int = None) -> object:
		start_time = current_unix_time_ms()
		tasks = [
			asyncio.create_task(Spotify.search_collection(artists, title, year), name = Spotify.service),
			asyncio.create_task(AppleMusic.search_collection(artists, title, year), name = AppleMusic.service),
			asyncio.create_task(YouTubeMusic.search_collection(artists, title, year), name = YouTubeMusic.service),
			asyncio.create_task(Tidal.search_collection(artists, title, year), name = Tidal.service),
			asyncio.create_task(Deezer.search_collection(artists, title, year), name = Deezer.service)
		]

		unlabeled_results = await asyncio.gather(*tasks)
		labeled_results = {}
		for result in unlabeled_results:
			labeled_results[result.service] = result

		services = [Spotify.service, AppleMusic.service, YouTubeMusic.service, Deezer.service, Tidal.service]
		
		type_order = [Spotify.service, AppleMusic.service, YouTubeMusic.service, Deezer.service, Tidal.service]
		title_order = [Spotify.service, AppleMusic.service, YouTubeMusic.service, Deezer.service, Tidal.service]
		artists_order = [Spotify.service, Tidal.service, YouTubeMusic.service, Deezer.service, AppleMusic.service]
		release_year_order = [Spotify.service, AppleMusic.service, YouTubeMusic.service, Deezer.service, Tidal.service]
		cover_order = [Tidal.service, Deezer.service, Spotify.service, AppleMusic.service, YouTubeMusic.service]

		for service in services:
			if labeled_results[service].type != 'album' and labeled_results[service].type != 'ep':
				type_order.remove(service)
				title_order.remove(service)
				artists_order.remove(service)
				release_year_order.remove(service)
				cover_order.remove(service)
				del unlabeled_results[list(labeled_results.keys()).index(service)]
				del labeled_results[service]

		result_type = None
		result_urls = {}
		result_ids = {}
		result_title = None
		result_artists = None
		result_year = None
		result_cover = None

		for service in range(len(type_order)):
			if result_type == None:
				result_type = labeled_results[type_order[service]].type
			if result_urls == {}:
				for result in unlabeled_results:
					result_urls[result.service] = result.url[result.service]
			if result_ids == {}:
				for result in unlabeled_results:
					result_ids[result.service] = result.id[result.service]
			if result_title == None:
				result_title = labeled_results[title_order[service]].title
			if result_artists == None:
				result_artists = labeled_results[artists_order[service]].artists
			if result_year == None:
				result_year = labeled_results[release_year_order[service]].release_year
			if result_cover == None:
				result_cover = labeled_results[cover_order[service]].cover_url

		end_time = current_unix_time_ms()

		return Collection(
			service = self.service,
			type = result_type,
			url = result_urls,
			id = result_ids,
			title = result_title,
			artists = result_artists,
			release_year = result_year,
			cover_url = result_cover,
			api_response_time = end_time - start_time,
			api_http_code = 200
		)



Global = GlobalIO()