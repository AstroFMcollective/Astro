from AstroAPI.components import *
from ytmusicapi import YTMusic



class YouTubeMusic:
	def __init__(self):
		self.service = 'youtube_music'
		self.component = 'YouTube Music API'
		self.ytm = YTMusic()
		self.allowed_video_types = [
			'MUSIC_VIDEO_TYPE_ATV',
			'MUSIC_VIDEO_TYPE_OMV',
			'MUSIC_VIDEO_TYPE_OFFICIAL_SOURCE_MUSIC'
		]



	async def search_song(self, artists: list, title: str, song_type: str = None, collection: str = None, is_explicit: bool = None, country_code: str = 'us') -> object:
		try:
			request = 'search_song'
			artists = [optimize_for_search(artist) for artist in artists]
			title = optimize_for_search(replace_with_ascii(title).lower())
			collection = clean_up_collection_title(optimize_for_search(collection)) if collection != None else None
			
			songs = []
			start_time = current_unix_time_ms()
			results = self.ytm.search(
				query = f'{artists[0]} {title}',
				filter = 'songs'
			)

			for song in results:
				song_type = 'track'
				song_url = f'https://music.youtube.com/watch?v={song['videoId']}'
				song_id = song['videoId']
				song_title = song['title']
				song_artists = [artist['name'] for artist in song['artists']] if song['artists'] != [] else await self.lookup_artist(video_id = song['videoId'])
				if not isinstance(song_artists, list): song_artists = split_artists(song_artists.name)
				song_cover = song['thumbnails'][len(song['thumbnails'])-1]['url']
				song_is_explicit = song['isExplicit']
				song_collection = song['album']['name']
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
					api_http_code = 200,
					request = {'request': request, 'artists': artists, 'title': title, 'song_type': song_type, 'collection': collection, 'is_explicit': is_explicit, 'country_code': country_code}
				))
			return await filter_song(service = self.service, query_request = request, songs = songs, query_artists = artists, query_title = title, query_song_type = song_type, query_collection = collection, query_is_explicit = is_explicit, query_country_code = country_code)

		except Exception as msg:
			error = Error(
				service = self.service,
				component = self.component,
				error_msg = f'Error when searching for song: "{msg}"',
				request = {'request': request, 'artists': artists, 'title': title, 'song_type': song_type, 'collection': collection, 'is_explicit': is_explicit, 'country_code': country_code}
			)
			await log(error)
			return error
		

	
	async def search_music_video(self, artists: list, title: str, is_explicit: bool = None, country_code: str = 'us') -> object:
		try:
			request = 'search_music_video'
			artists = [optimize_for_search(artist) for artist in artists]
			title = optimize_for_search(replace_with_ascii(title).lower())
			
			videos = []
			start_time = current_unix_time_ms()
			results = self.ytm.search(
				query = f'{artists[0]} {title}',
				filter = 'videos'
			)

			for video in results:
				mv_url = f'https://music.youtube.com/watch?v={video['videoId']}'
				mv_id = video['videoId']
				mv_title = video['title']
				mv_artists = [artist['name'] for artist in video['artists']] if video['artists'] != [] else await self.lookup_artist(video_id = video['videoId'])
				if not isinstance(mv_artists, list): mv_artists = split_artists(mv_artists.name)
				mv_cover = video['thumbnails'][len(video['thumbnails'])-1]['url']
				end_time = current_unix_time_ms()
				videos.append(MusicVideo(
					service = self.service,
					url = mv_url,
					id = mv_id,
					title = mv_title,
					artists = mv_artists,
					is_explicit = None,
					thumbnail_url = mv_cover,
					api_response_time = end_time - start_time,
					api_http_code = 200,
					request = {'request': request, 'artists': artists, 'title': title, 'is_explicit': is_explicit, 'country_code': country_code}
				))
			return await filter_mv(service = self.service, query_request = request, videos = videos, query_artists = artists, query_title = title, query_is_explicit = is_explicit, query_country_code = country_code)

		except Exception as msg:
			error = Error(
				service = self.service,
				component = self.component,
				error_msg = f'Error when searching for music video: "{msg}"',
				request = {'request': request, 'artists': artists, 'title': title, 'is_explicit': is_explicit, 'country_code': country_code}
			)
			await log(error)
			return error



	async def search_collection(self, artists: list, title: str, year: int = None, country_code: str = 'us') -> object:
		try:
			request = 'search_collection'
			artists = [optimize_for_search(artist) for artist in artists]
			title = optimize_for_search(title)

			collections = []
			start_time = current_unix_time_ms()
			results = self.ytm.search(
				query = f'{artists[0]} {title}',
				filter = 'albums'
			)

			for collection in results:
				collection_type = ('album' if collection['type'] == 'Album' else 'ep')
				collection_url = f'https://music.youtube.com/playlist?list={collection['playlistId']}'
				collection_id = collection['playlistId']
				collection_title = collection['title']
				collection_artists = [artist['name'] for artist in collection['artists']]
				collection_year = collection['year']
				collection_cover = collection['thumbnails'][len(collection['thumbnails'])-1]['url']
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
					api_http_code = 200,
					request = {'request': request, 'artists': artists, 'title': title, 'year': year, 'country_code': country_code}
				))
			return await filter_collection(service = self.service, query_request = request, collections = collections, query_artists = artists, query_title = title, query_year = year, query_country_code = country_code)

		except Exception as msg:
			error = Error(
				service = self.service,
				component = self.component,
				error_msg = f'Error when searching for collection: "{msg}"',
				request = {'request': request, 'artists': artists, 'title': title, 'year': year, 'country_code': country_code}
			)
			await log(error)
			return error
	


	async def search_query(self, query: str, country_code: str = 'us') -> object:
		try:
			request = 'search_query'
			start_time = current_unix_time_ms()
			results = self.ytm.search(
				query = query,
			)
			result = results[0]
			result_type = result['resultType']

			if result_type == 'song':
				return Song(
					service = self.service,
					type = 'track',
					url = f'https://music.youtube.com/watch?v={result['videoId']}',
					id = result['videoId'],
					title = result['title'],
					artists = [artist['name'] for artist in result['artists']],
					collection = None,
					is_explicit = None,
					cover_url = result['thumbnails'][len(result['thumbnails'])-1]['url'],
					api_response_time = current_unix_time_ms() - start_time,
					api_http_code = 200,
					request = {'request': request, 'query': query, 'country_code': country_code}
				)
			elif result_type == 'album':
				return Collection(
					service = self.service,
					type = 'album',
					url = f'https://music.youtube.com/playlist?list={result['playlistId']}',
					id = result['playlistId'],
					title = result['title'],
					artists = [artist['name'] for artist in result['artists']],
					release_year = None,
					cover_url = result['thumbnails'][len(result['thumbnails'])-1]['url'],
					api_response_time = current_unix_time_ms() - start_time,
					api_http_code = 200,
					request = {'request': request, 'query': query, 'country_code': country_code}
				)
			elif result_type == 'video':
				return MusicVideo(
					service = self.service,
					url = f'https://music.youtube.com/watch?v={result['videoId']}',
					id = result['videoId'],
					title = remove_music_video_declaration(result['title']),
					artists = [artist['name'] for artist in result['artists']],
					is_explicit = None,
					thumbnail_url = result['thumbnails'][len(result['thumbnails'])-1]['url'],
					api_response_time = current_unix_time_ms() - start_time,
					api_http_code = 200,
					request = {'request': request, 'query': query, 'country_code': country_code}
				)
			else:
				empty_response = Empty(
					service = self.service,
					request = {'request': request, 'query': query, 'country_code': country_code}
				)
				await log(empty_response)
				return empty_response
		except Exception as msg:
			error = Error(
				service = self.service,
				component = self.component,
				error_msg = f'Error when doing general query search: "{msg}"',
				request = {'request': request, 'query': query, 'country_code': country_code}
			)
			await log(error)
			return error



	async def lookup_song(self, id: str, country_code: str = 'us') -> object:
		try:
			request = 'lookup_song'
			start_time = current_unix_time_ms()
			song = self.ytm.get_song(id)['videoDetails']

			if 'musicVideoType' in song:
				if song['musicVideoType'] in self.allowed_video_types:
					song_url = f'https://music.youtube.com/watch?v={song['videoId']}'
					song_id = song['videoId']
					song_title = song['title']
					song_artists = await self.lookup_artist(video_id = song['videoId'])
					if not isinstance(song_artists, list): song_artists = [song_artists.name]
					song_cover = song['thumbnail']['thumbnails'][len(song['thumbnail']['thumbnails'])-1]['url']
					end_time = current_unix_time_ms()
					if song['musicVideoType'] == 'MUSIC_VIDEO_TYPE_ATV':
						return Song(
							service = self.service,
							type = 'track',
							url = song_url,
							id = song_id,
							title = song_title,
							artists = song_artists,
							collection = None,
							is_explicit = None,
							cover_url = song_cover,
							api_response_time = end_time - start_time,
							api_http_code = 200,
							request = {'request': request, 'id': id, 'country_code': country_code, 'url': f'https://music.youtube.com/watch?v={id}'}
						)

					else:
						song_title = remove_music_video_declaration(song_title)
						return MusicVideo(
							service = self.service,
							url = song_url,
							id = song_id,
							title = song_title,
							artists = song_artists,
							is_explicit = None,
							thumbnail_url = song_cover,
							api_response_time = end_time - start_time,
							api_http_code = 200,
							request = {'request': request, 'id': id, 'country_code': country_code, 'url': f'https://music.youtube.com/watch?v={id}'}
						)
			else:
				return Empty(
					service = self.service,
					request = {'request': request, 'id': id, 'country_code': country_code, 'url': f'https://music.youtube.com/watch?v={id}'}
				)
			
		except Exception as msg:
			error = Error(
				service = self.service,
				component = self.component,
				error_msg = f'Error when looking up song: "{msg}"',
				request = {'request': request, 'id': id, 'country_code': country_code, 'url': f'https://music.youtube.com/watch?v={id}'}
			)
			await log(error)
			return error



	async def lookup_collection(self, id: str, country_code: str = 'us') -> object:
		try:
			request = 'lookup_collection'
			start_time = current_unix_time_ms()
			browse_id = self.ytm.get_album_browse_id(id)
			collection = self.ytm.get_album(browse_id)
			
			collection_type = ('album' if collection['type'] == 'Album' else 'ep')
			collection_url = f'https://music.youtube.com/playlist?list={collection['audioPlaylistId']}'
			collection_id = collection['audioPlaylistId']
			collection_title = collection['title']
			collection_artists = [artist['name'] for artist in collection['artists']]
			collection_year = collection['year']
			collection_cover = collection['thumbnails'][len(collection['thumbnails'])-1]['url']
			end_time = current_unix_time_ms()
			return Collection(
				service = self.service,
				type = collection_type,
				url = collection_url,
				id = collection_id,
				title = collection_title,
				artists = collection_artists,
				release_year = collection_year,
				cover_url = collection_cover,
				api_response_time = end_time - start_time,
				api_http_code = 200,
				request = {'request': request, 'id': id, 'country_code': country_code, 'url': f'https://music.youtube.com/playlist?list={id}'}
			)
			
		except Exception as msg:
			error = Error(
				service = self.service,
				component = self.component,
				error_msg = f'Error when looking up collection: "{msg}"',
				request = {'request': request, 'id': id, 'country_code': country_code, 'url': f'https://music.youtube.com/playlist?list={id}'}
			)
			await log(error)
			return error
	


	async def lookup_artist(self, id: str = None, video_id: str = None, country_code: str = 'us') -> object:
		try:
			request = 'lookup_artist'
			start_time = current_unix_time_ms()
			try:
				if video_id == None and id == None:
					return Empty(
						service = self.service,
						request = {'request': request, 'id': id, 'video_id': video_id, 'country_code': country_code}
					)
				elif video_id != None and id == None:
					id = self.ytm.get_song(video_id)['videoDetails']['channelId']
				artist = self.ytm.get_artist(id)

				artist_url = f'https://www.youtube.com/channel/{artist['channelId']}'
				artist_id = artist['channelId']
				artist_name = artist['name']
				end_time = current_unix_time_ms()
				return Artist(
					service = self.service,
					url = artist_url,
					id = artist_id,
					name = artist_name,
					api_response_time = end_time - start_time,
					api_http_code = 200,
					request = {'request': request, 'id': id, 'video_id': video_id, 'country_code': country_code}
				)
			except:
				artist = self.ytm.get_song(video_id)['videoDetails']

				artist_url = f'https://www.youtube.com/channel/{artist['channelId']}'
				artist_id = artist['channelId']
				artist_name = artist['author']
				end_time = current_unix_time_ms()
				return Artist(
					service = self.service,
					url = artist_url,
					id = artist_id,
					name = artist_name,
					api_response_time = end_time - start_time,
					api_http_code = 200,
					request = {'request': request, 'id': id, 'video_id': video_id, 'country_code': country_code}
				)
		except Exception as msg:
			error = Error(
				service = self.service,
				component = self.component,
				error_msg = f'Error when looking up artist: "{msg}"',
				request = {'request': request, 'id': id, 'video_id': video_id, 'country_code': country_code}
			)
			await log(error)
			return error
		