from AstroAPI.media_services import spotify_api, apple_music_api, youtube_music_api, tidal_api, deezer_api, genius_api
from AstroAPI.components.ini import keys
from AstroAPI.components import *
from asyncio import *


# Music API-s
Spotify = spotify_api.Spotify(client_id = keys['spotify']['id'], client_secret = keys['spotify']['secret'])
AppleMusic = apple_music_api.AppleMusic()
YouTubeMusic = youtube_music_api.YouTubeMusic()
Deezer = deezer_api.Deezer()
Tidal = tidal_api.Tidal(client_id = keys['tidal']['id'], client_secret = f'{keys['tidal']['secret']}=')

# Knowledge API-s
Genius = genius_api.Genius(token = keys['genius']['token'])



class GlobalIO: 
	def __init__(self):
		self.service = 'global'
		self.component = 'Global Interface'
		self.invalid_responses = [
			'empty_response',
			'error'
		]
		print('[AstroAPI] Global API has been initialized.')



	async def search_song(self, artists: list, title: str, song_type: str = None, collection: str = None, is_explicit: bool = None, country_code: str = 'us', include_premade_media: list = [], exclude_services: list = [Tidal.service]) -> object:
		request = {'request': 'search_song', 'artists': artists, 'title': title, 'song_type': song_type, 'collection': collection, 'is_explicit': is_explicit, 'country_code': country_code, 'exclude_services': exclude_services}
		start_time = current_unix_time_ms()

		try:
			service_objs = [Spotify, AppleMusic, YouTubeMusic, Deezer, Tidal]

			ignore_in_excluded_services = []
			for premade in include_premade_media:
				if premade.service not in exclude_services:
					exclude_services.append(premade.service)
					ignore_in_excluded_services.append(premade.service)

			tasks = []
			for obj in service_objs:
				if obj.service not in exclude_services:
					tasks.append(
						create_task(obj.search_song(artists, title, song_type, collection, is_explicit, country_code), name = obj.service)
					)

			unlabeled_results = await gather(*tasks)

			exclude_services = [service for service in exclude_services if service not in ignore_in_excluded_services]
			for premade in include_premade_media:
				unlabeled_results.append(premade)
			for service in exclude_services:
				unlabeled_results.append(Empty(
					service = service,
					meta = Meta(
						service = self.service,
						request = request,
						processing_time = current_unix_time_ms() - start_time,
						filter_confidence_percentage = {service: 0.0},
					)
				))

			labeled_results = {}
			for result in unlabeled_results:
				labeled_results[result.service] = result

			services = [Spotify.service, AppleMusic.service, YouTubeMusic.service, Deezer.service, Tidal.service]

			type_order = [Spotify.service, AppleMusic.service, YouTubeMusic.service, Deezer.service, Tidal.service]
			title_order = [Spotify.service, AppleMusic.service, YouTubeMusic.service, Deezer.service, Tidal.service]
			artists_order = [Spotify.service, Tidal.service, YouTubeMusic.service, Deezer.service, AppleMusic.service]
			collection_order = [Spotify.service, AppleMusic.service, YouTubeMusic.service, Deezer.service, Tidal.service]
			explicitness_order = [Spotify.service, AppleMusic.service, YouTubeMusic.service, Deezer.service, Tidal.service]
			cover_order = [Spotify.service, Tidal.service, Deezer.service, AppleMusic.service, YouTubeMusic.service]
			cover_single_order = [Spotify.service, Tidal.service, Deezer.service, AppleMusic.service, YouTubeMusic.service]

			for service in services:
				if labeled_results[service].type != 'track' and labeled_results[service].type != 'single':
					type_order.remove(service)
					title_order.remove(service)
					artists_order.remove(service)
					collection_order.remove(service)
					explicitness_order.remove(service)
					cover_order.remove(service)
					cover_single_order.remove(service)
					del unlabeled_results[list(labeled_results.keys()).index(service)]
					del labeled_results[service]

			result_type = None
			result_urls = {}
			result_ids = {}
			result_processing_time = {}
			result_confidence = {}
			result_title = None
			result_artists = None
			result_collection = None
			result_is_explicit = None
			result_cover = None

			for service_index in range(len(type_order)):
				if result_type == None:
					result_type = labeled_results[type_order[service_index]].type
				if result_urls == {}:
					for result in unlabeled_results:
						result_urls[result.service] = result.url[result.service]
				if result_ids == {}:
					for result in unlabeled_results:
						result_ids[result.service] = result.id[result.service]
				if result_processing_time == {}:
					for result in unlabeled_results:
						result_processing_time[result.service] = result.meta.processing_time[result.service]
				if result_confidence == {}:
					for result in unlabeled_results:
						result_confidence[result.service] = result.meta.filter_confidence_percentage[result.service]
				if result_title == None:
					result_title = labeled_results[title_order[service_index]].title
				if result_artists == None:
					result_artists = labeled_results[artists_order[service_index]].artists
				if result_collection == None:
					result_collection = labeled_results[collection_order[service_index]].collection
				if result_is_explicit == None:
					result_is_explicit = labeled_results[explicitness_order[service_index]].is_explicit
				if result_cover == None:
					result_cover = labeled_results[cover_order[service_index]].cover_url

			if result_type == 'single':
				result_cover = None
				for service in range(len(type_order)):
					if result_cover == None:
						result_cover = labeled_results[cover_single_order[service]].cover_url

			sorted_urls = {}
			sorted_ids = {}
			sorted_processing_time = {}
			sorted_confidence = {}
			for service in services:
				try:
					sorted_urls[service] = result_urls[service]
					sorted_ids[service] = result_ids[service]
					sorted_processing_time[service] = result_processing_time[service]
					sorted_confidence[service] = result_confidence[service]
				except:
					pass
			result_urls = sorted_urls
			result_ids = sorted_ids
			result_processing_time = sorted_processing_time
			result_confidence = sorted_confidence

			result_processing_time[self.service] = current_unix_time_ms() - start_time
			color_hex = await image_hex(result_cover)

			if result_type != None:
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
					cover_color_hex = color_hex,
					meta = Meta(
						service = self.service,
						request = request,
						processing_time = result_processing_time,
						filter_confidence_percentage = result_confidence,
						http_code = 200,
					)
				)

			else:
				empty_response = Empty(
					service = self.service,
					meta = Meta(
						service = self.service,
						request = request,
						processing_time = result_processing_time,
						filter_confidence_percentage = result_confidence,
						http_code = 204
					)
				)
				await log(empty_response)
				return empty_response

		except Exception as msg:
			error = Error(
				service = self.service,
				component = self.component,
				error_msg = f'Error when searching for song: "{msg}"',
				meta = Meta(
					service = self.service,
					request = request,
					processing_time = {self.service: current_unix_time_ms() - start_time},
				)
			)
			await log(error)
			return error


	
	async def search_music_video(self, artists: list, title: str, is_explicit: bool = None, country_code: str = 'us', include_premade_media: list = [], exclude_services: list = [Tidal.service]) -> object:
		request = {'request': 'search_music_video', 'artists': artists, 'title': title, 'is_explicit': is_explicit, 'country_code': country_code, 'exclude_services': exclude_services}
		start_time = current_unix_time_ms()

		try:
			service_objs = [AppleMusic, YouTubeMusic, Tidal]

			ignore_in_excluded_services = []
			for premade in include_premade_media:
				if premade.service not in exclude_services:
					exclude_services.append(premade.service)
					ignore_in_excluded_services.append(premade.service)

			tasks = []
			for obj in service_objs:
				if obj.service not in exclude_services:
					tasks.append(
						create_task(obj.search_music_video(artists, title, is_explicit, country_code), name = obj.service)
					)

			unlabeled_results = await gather(*tasks)

			exclude_services = [service for service in exclude_services if service not in ignore_in_excluded_services]
			for premade in include_premade_media:
				unlabeled_results.append(premade)
			for service in exclude_services:
				unlabeled_results.append(Empty(
					service = service,
					meta = Meta(
						service = self.service,
						request = request,
						processing_time = current_unix_time_ms() - start_time,
						filter_confidence_percentage = {service: 0.0},
					)
				))

			labeled_results = {}
			for result in unlabeled_results:
				labeled_results[result.service] = result
			
			services = [AppleMusic.service, YouTubeMusic.service, Tidal.service]

			title_order = [AppleMusic.service, YouTubeMusic.service, Tidal.service]
			artists_order = [Tidal.service, YouTubeMusic.service, AppleMusic.service]
			explicitness_order = [AppleMusic.service, Tidal.service, YouTubeMusic.service]
			cover_order = [Tidal.service, YouTubeMusic.service, AppleMusic.service]

			for service in services:
				if labeled_results[service].type != 'music_video':
					title_order.remove(service)
					artists_order.remove(service)
					explicitness_order.remove(service)
					cover_order.remove(service)
					del unlabeled_results[list(labeled_results.keys()).index(service)]
					del labeled_results[service]

			result_urls = {}
			result_ids = {}
			result_title = None
			result_artists = None
			result_processing_time = {}
			result_confidence = {}
			result_is_explicit = None
			result_cover = None

			for service_index in range(len(title_order)):
				if result_urls == {}:
					for result in unlabeled_results:
						result_urls[result.service] = result.url[result.service]
				if result_ids == {}:
					for result in unlabeled_results:
						result_ids[result.service] = result.id[result.service]
				if result_title == None:
					result_title = labeled_results[title_order[service_index]].title
				if result_artists == None:
					result_artists = labeled_results[artists_order[service_index]].artists
				if result_processing_time == {}:
					for result in unlabeled_results:
						result_processing_time[result.service] = result.meta.processing_time[result.service]
				if result_confidence == {}:
					for result in unlabeled_results:
						result_confidence[result.service] = result.meta.filter_confidence_percentage[result.service]
				if result_is_explicit == None:
					result_is_explicit = labeled_results[explicitness_order[service_index]].is_explicit
				if result_cover == None:
					result_cover = labeled_results[cover_order[service_index]].thumbnail_url

			sorted_urls = {}
			sorted_ids = {}
			sorted_processing_time = {}
			sorted_confidence = {}
			for service in services:
				try:
					sorted_urls[service] = result_urls[service]
					sorted_ids[service] = result_ids[service]
					sorted_processing_time[service] = result_processing_time[service]
					sorted_confidence[service] = result_confidence[service]
				except:
					pass
			result_urls = sorted_urls
			result_ids = sorted_ids
			result_processing_time = sorted_processing_time
			result_confidence = sorted_confidence

			result_processing_time[self.service] = current_unix_time_ms() - start_time
			color_hex = await image_hex(result_cover)

			if result_title != None:
				return MusicVideo(
					service = self.service,
					url = result_urls,
					id = result_ids,
					title = result_title,
					artists = result_artists,
					is_explicit = result_is_explicit,
					thumbnail_url = result_cover,
					thumbnail_color_hex = color_hex,
					meta = Meta(
						service = self.service,
						request = request,
						processing_time = result_processing_time,
						filter_confidence_percentage = result_confidence,
						http_code = 200,
					)

				)

			else:
				return Empty(
					service = self.service,
					meta = Meta(
						service = self.service,
						request = request,
						processing_time = result_processing_time,
						filter_confidence_percentage = result_confidence,
						http_code = 204,
					)
				)

		except Exception as msg:
			error = Error(
				service = self.service,
				component = self.component,
				error_msg = f'Error when searching for music video: "{msg}"',
				meta = Meta(
					service = self.service,
					request = request,
					processing_time = {self.service: current_unix_time_ms() - start_time},
				)
			)
			await log(error)
			return error



	async def search_collection(self, artists: list, title: str, year: int = None, country_code: str = 'us', include_premade_media: list = [], exclude_services: list = [Tidal.service]) -> object:
		request = {'request': 'search_collection', 'artists': artists, 'title': title, 'year': year, 'country_code': country_code}
		start_time = current_unix_time_ms()

		try:
			service_objs = [Spotify, AppleMusic, YouTubeMusic, Deezer, Tidal]

			ignore_in_excluded_services = []
			for premade in include_premade_media:
				if premade.service not in exclude_services:
					exclude_services.append(premade.service)
					ignore_in_excluded_services.append(premade.service)

			tasks = []
			for obj in service_objs:
				if obj.service not in exclude_services:
					tasks.append(
						create_task(obj.search_collection(artists, title, year, country_code), name = obj.service)
					)

			unlabeled_results = await gather(*tasks)

			exclude_services = [service for service in exclude_services if service not in ignore_in_excluded_services]
			for premade in include_premade_media:
				unlabeled_results.append(premade)
			for service in exclude_services:
				unlabeled_results.append(Empty(
					service = service,
					meta = Meta(
						service = self.service,
						request = request,
						processing_time = current_unix_time_ms() - start_time,
						filter_confidence_percentage = {service: 0.0},
					)
				))

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
			result_processing_time = {}
			result_confidence = {}
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
				if result_processing_time == {}:
					for result in unlabeled_results:
						result_processing_time[result.service] = result.meta.processing_time[result.service]
				if result_confidence == {}:
					for result in unlabeled_results:
						result_confidence[result.service] = result.meta.filter_confidence_percentage[result.service]
				if result_title == None:
					result_title = labeled_results[title_order[service]].title
				if result_artists == None:
					result_artists = labeled_results[artists_order[service]].artists
				if result_year == None:
					result_year = labeled_results[release_year_order[service]].release_year
				if result_cover == None:
					result_cover = labeled_results[cover_order[service]].cover_url

			sorted_urls = {}
			sorted_ids = {}
			sorted_processing_time = {}
			sorted_confidence = {}
			for service in services:
				try:
					sorted_urls[service] = result_urls[service]
					sorted_ids[service] = result_ids[service]
					sorted_processing_time[service] = result_processing_time[service]
					sorted_confidence[service] = result_confidence[service]
				except:
					pass
			result_urls = sorted_urls
			result_ids = sorted_ids
			result_processing_time = sorted_processing_time
			result_confidence = sorted_confidence

			result_processing_time[self.service] = current_unix_time_ms() - start_time
			color_hex = await image_hex(result_cover)

			if result_type != None:
				return Collection(
					service = self.service,
					type = result_type,
					url = result_urls,
					id = result_ids,
					title = result_title,
					artists = result_artists,
					release_year = result_year,
					cover_url = result_cover,
					cover_color_hex = color_hex, 
					meta = Meta(
						service = self.service,
						request = request,
						processing_time = result_processing_time,
						filter_confidence_percentage = result_confidence,
						http_code = 200,
					)
				)

			else:
				empty_response = Empty(
					service = service,
					meta = Meta(
						service = self.service,
						request = request,
						processing_time = result_processing_time,
						filter_confidence_percentage = result_confidence,
						http_code = 204,
					)
				)
				await log(empty_response)
				return empty_response

		except Exception as msg:
			error = Error(
				service = self.service,
				component = self.component,
				error_msg = f'Error when searching for collection: "{msg}"',
				meta = Meta(
					service = self.service,
					request = request,
					processing_time = {self.service: current_unix_time_ms() - start_time},
				)
			)
			await log(error)
			return error



	async def search_query(self, query: str, country_code: str = 'us') -> object:
		request = {'request': 'search_query', 'query': query, 'country_code': country_code}
		start_time = current_unix_time_ms()
		
		try:
			result = await YouTubeMusic.search_query(query)

			if result.type == 'track' or result.type == 'single':
				return await self.search_song(result.artists, result.title, result.type, result.collection, result.is_explicit, country_code)
			
			elif result.type == 'album' or result.type == 'ep':
				return await self.search_collection(result.artists, result.title, result.release_year, country_code)
			
			elif result.type == 'music_video':
				return await self.search_music_video(result.artists, result.title, result.is_explicit, country_code)
			
			

			else:
				empty_response = Empty(
					service = self.service,
					meta = Meta(
						service = self.service,
						request = request,
						processing_time = result.meta.processing_time,
						http_code = 204,
					)
				)
				await log(empty_response)
				return empty_response

		except Exception as msg:
			error = Error(
				service = self.service,
				component = self.component,
				error_msg = f'Error when doing general query search: "{msg}"',
				meta = Meta(
					service = self.service,
					request = request,
					processing_time = {self.service: current_unix_time_ms() - start_time},
				)
			)
			await log(error)
			return error



	async def lookup_song(self, service: object, id: str, song_country_code: str = None, lookup_country_code: str = 'us') -> object:
		request = {'request': 'lookup_song', 'service': service.service, 'id': id, 'song_country_code': song_country_code, 'lookup_country_code': lookup_country_code}
		start_time = current_unix_time_ms()

		try:
			song_reference = await service.lookup_song(id = id, country_code = song_country_code)

			if song_reference.type != 'track' and song_reference.type != 'single' and song_reference.type != 'music_video':
				return song_reference

			service_objects = [Spotify, AppleMusic, YouTubeMusic, Deezer, Tidal]
			services = [Spotify.service, AppleMusic.service, YouTubeMusic.service, Deezer.service, Tidal.service]
			if service != YouTubeMusic:
				service_objects.remove(service)
			
			if song_reference.type == 'music_video':
				song = await self.search_song(
					artists = song_reference.artists,
					title = song_reference.title,
					is_explicit = song_reference.is_explicit,
					country_code = lookup_country_code,
					include_premade_media = [song_reference],
					exclude_services = [Tidal.service]
				)
			else:
				song = await self.search_song(
					artists = song_reference.artists,
					title = song_reference.title,
					song_type = song_reference.type,
					collection = song_reference.collection,
					is_explicit = song_reference.is_explicit,
					country_code = lookup_country_code,
					include_premade_media = [song_reference],
					exclude_services = [Tidal.service]
				)

			# if song.type not in self.invalid_responses:
			# 	all_urls = {}
			# 	all_ids = {}
			# 	all_latencies = {}
			# 	all_percentages = {}
			# 	for service in services:
			# 		if service == song_reference.service:
			# 			all_urls[service] = song_reference.url[service]
			# 			all_ids[service] = song_reference.id[service]
			# 			all_latencies[service] = song_reference.meta.processing_time[service]
			# 			all_percentages[service] = song_reference.meta.filter_confidence_percentage[service]
			# 		elif service in list(song.url.keys()):
			# 			all_urls[service] = song.url[service]
			# 			all_ids[service] = song.id[service]
			# 			all_latencies[service] = song.meta.processing_time[service]
			# 			all_percentages[service] = song.meta.filter_confidence_percentage[service]
				
				# song.title = song_reference.title
				# song.artists = song_reference.artists
				# song.type = song_reference.type
				# song.collection = song_reference.collection if song_reference.collection is not None else song.colleciton
				# song.cover_url = song_reference.cover_url
				# song.url = all_urls
				# song.id = all_ids
				# song.meta.processing_time = all_latencies
				# song.meta.processing_time[self.service] = current_unix_time_ms() - start_time
				# song.meta.filter_confidence_percentage = all_percentages

			return song

		except Exception as msg:
			error = Error(
				service = self.service,
				component = self.component,
				error_msg = f'Error when looking up song: "{msg}"',
				meta = Meta(
					service = self.service,
					request = request,
					processing_time = {self.service: current_unix_time_ms() - start_time}
				)
			)
			await log(error)
			return error



	async def lookup_music_video(self, service: object, id: str, mv_country_code: str = None, lookup_country_code: str = 'us') -> object:
		request = {'request': 'lookup_music_video', 'service': service.service, 'id': id, 'mv_country_code': mv_country_code, 'lookup_country_code': lookup_country_code}
		start_time = current_unix_time_ms()

		try:
			if service == YouTubeMusic:
				video_reference = await YouTubeMusic.lookup_song(id = id, country_code = mv_country_code)
			else:
				video_reference = await service.lookup_music_video(id = id, country_code = mv_country_code)

			if video_reference.type != 'music_video':
				return video_reference

			service_objects = [AppleMusic, YouTubeMusic, Tidal]
			services = [AppleMusic.service, YouTubeMusic.service, Tidal.service]
			service_objects.remove(service)

			video = await self.search_music_video(
				video_reference.artists,
				video_reference.title,
				video_reference.is_explicit,
				lookup_country_code,
				[video_reference],
				[Tidal.service]
			)

			# if video.type not in self.invalid_responses:
			# 	all_urls = {}
			# 	all_ids = {}
			# 	all_latencies = {}
			# 	all_percentages = {}
			# 	for service in services:
			# 		if service == video_reference.service:
			# 			all_urls[service] = video_reference.url[service]
			# 			all_ids[service] = video_reference.id[service]
			# 			all_latencies[service] = video_reference.meta.processing_time[service]
			# 			all_percentages[service] = video_reference.meta.filter_confidence_percentage[service]
			# 		elif service in list(video.url.keys()):
			# 			all_urls[service] = video.url[service]
			# 			all_ids[service] = video.id[service]
			# 			all_latencies[service] = video.meta.processing_time[service]
			# 			all_percentages[service] = video.meta.filter_confidence_percentage[service]
				
			# 	video.url = all_urls
			# 	video.id = all_ids
			# 	video.meta.processing_time = all_latencies
			# 	video.meta.processing_time[self.service] = current_unix_time_ms() - start_time
			# 	video.meta.filter_confidence_percentage = all_percentages

			return video

			# else:
			# 	return video

		except Exception as msg:
			error = Error(
				service = self.service,
				component = self.component,
				error_msg = f'Error when looking up music video: "{msg}"',
				meta = Meta(
					service = self.service,
					request = request,
					processing_time = {self.service: current_unix_time_ms() - start_time}
				)
			)
			await log(error)
			return error
		


	async def lookup_collection(self, service: object, id: str, collection_country_code: str = None, lookup_country_code: str = 'us') -> object:
		request = {'request': 'lookup_collection', 'service': service.service, 'id': id, 'collection_country_code': collection_country_code, 'lookup_country_code': lookup_country_code}
		start_time = current_unix_time_ms()

		try:
			collection_reference = await service.lookup_collection(id = id, country_code = collection_country_code)

			if collection_reference.type == 'single':
				song = await self.search_song(collection_reference.artists, collection_reference.title, 'single', collection_reference.collection, collection_reference.is_explicit, lookup_country_code)
				return song

			if collection_reference.type != 'album' and collection_reference.type != 'ep':
				return collection_reference
			
			service_objects = [Spotify, AppleMusic, YouTubeMusic, Deezer, Tidal]
			services = [Spotify.service, AppleMusic.service, YouTubeMusic.service, Deezer.service, Tidal.service]
			service_objects.remove(service)

			collection = await self.search_collection(
				collection_reference.artists,
				collection_reference.title,
				collection_reference.release_year,
				lookup_country_code,
				[collection_reference],
				[Tidal.service]
			)

			# if collection.type not in self.invalid_responses:
			# 	all_urls = {}
			# 	all_ids = {}
			# 	all_latencies = {}
			# 	all_percentages = {}
			# 	for service in services:
			# 		if service == collection_reference.service:
			# 			all_urls[service] = collection_reference.url[service]
			# 			all_ids[service] = collection_reference.id[service]
			# 			all_latencies[service] = collection_reference.meta.processing_time[service]
			# 			all_percentages[service] = collection_reference.meta.filter_confidence_percentage[service]
			# 		elif service in list(collection.url.keys()):
			# 			all_urls[service] = collection.url[service]
			# 			all_ids[service] = collection.id[service]
			# 			all_latencies[service] = collection.meta.processing_time[service]
			# 			all_percentages[service] = collection.meta.filter_confidence_percentage[service]
				
			# 	collection.url = all_urls
			# 	collection.id = all_ids
			# 	collection.meta.processing_time = all_latencies
			# 	collection.meta.processing_time[self.service] = current_unix_time_ms() - start_time
			# 	collection.meta.filter_confidence_percentage = all_percentages

			return collection

			# else:
			# 	return collection

		except Exception as msg:
			error = Error(
				service = self.service,
				component = self.component,
				error_msg = f'Error when looking up collection: "{msg}"',
				meta = Meta(
					service = self.service,
					request = request,
					processing_time = {self.service: current_unix_time_ms() - start_time}
				)
			)
			await log(error)
			return error
	


	async def get_song_knowledge(self, service: object, song_id: str, song_country_code: str = None, knowledge_country_code: str = 'us') -> object:
		request = {'request': 'get_song_knowledge', 'service': service.service, 'song_id': song_id, 'song_country_code': song_country_code, 'knowledge_country_code': knowledge_country_code}
		start_time = current_unix_time_ms()

		try:
			song_reference = await service.lookup_song(id = song_id, country_code = song_country_code)
			#return song_reference
			if song_reference.type != 'track' and song_reference.type != 'single' and song_reference.type != 'music_video':
				empty_response = Empty(
					service = self.service,
					meta = Meta(
						service = self.service,
						request = request,
						processing_time = {self.service: current_unix_time_ms() - start_time},
						http_code = 204,
					)
				)
				await log(empty_response)
				return empty_response

			if song_reference.type == 'music_video':
				song = await Genius.search_song_knowledge(
					artists = song_reference.artists,
					title = song_reference.title,
					is_explicit = song_reference.is_explicit,
					country_code = knowledge_country_code,
				)
			else:
				song = await Genius.search_song_knowledge(
					artists = song_reference.artists,
					title = song_reference.title,
					song_type = song_reference.type,
					collection = song_reference.collection,
					is_explicit = song_reference.is_explicit,
					country_code = knowledge_country_code,
				)

			return song

		except Exception as msg:
			error = Error(
				service = self.service,
				component = self.component,
				error_msg = f'Error when getting song knowledge: "{msg}"',
				meta = Meta(
					service = self.service,
					request = request,
					processing_time = {self.service: current_unix_time_ms() - start_time}
				)
			)
			await log(error)
			return error


Global = GlobalIO()