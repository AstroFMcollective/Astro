from AstroAPI.components.all import *
from ytmusicapi import YTMusic
#from asyncio import run
import aiohttp

class YouTubeMusic:
	def __init__(self):
		self.service = 'youtube_music'
		self.component = 'YouTube Music API'
		self.ytm = YTMusic()



	async def search_song(self, artists: list, title: str, song_type: str = None, collection: str = None, is_explicit: bool = None) -> object:
		try:
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
				song_artists = [artist['name'] for artist in song['artists']]
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
					api_http_code = 200
				))
				return filter_song(service = self.service, songs = songs, query_artists = artists, query_title = title, query_song_type = song_type, query_collection = collection, query_is_explicit = is_explicit)
		except Exception as msg:
			return Error(
				service = self.service,
				component = self.component,
				error_msg = f'Error when searching for song: "{msg}"',
				request = f'Artists: `{', '.join(artists)}`\nTitle: `{title}`\nSong type: `{song_type}`\nCollection title: `{collection}`\nIs explicit? `{is_explicit}`'
			)



	async def search_collection(self, artists: list, title: str, year: int = None) -> object:
		try:
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
					api_http_code = 200
				))
				return filter_collection(service = self.service, collections = collections, query_artists = artists, query_title = title, query_year = year)
		except Exception as msg:
			return Error(
				service = self.service,
				component = self.component,
				error_msg = f'Error when searching for collection: "{msg}"',
				request = f'Artists: `{', '.join(artists)}`\nTitle: `{title}`\nYear: `{year}`'
			)
	


	async def search_query(self, query: str):
		try:
			start_time = current_unix_time_ms()
			results = self.ytm.search(
				query = query,
			)
			result = results[0]
			result_type = result['resultType']
			save_json(result)
			if result_type == 'song':
				return Song(
					service = self.service,
					type = 'track',
					url = f'https://music.youtube.com/watch?v={result['videoId']}',
					id = result['videoId'],
					title = result['title'],
					artists = [artist['name'] for artist in result['artists']],
					collection = result['album']['name'],
					is_explicit = None,
					cover_url = result['thumbnails'][len(result['thumbnails'])-1]['url'],
					api_response_time = current_unix_time_ms() - start_time,
					api_http_code = 200
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
					api_http_code = 200
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
					api_http_code = 200
				)
			else:
				return Empty(
					service = self.service,
					request = f'Query: `{query}`'
				)
		except Exception as msg:
			return Error(
				service = self.service,
				component = self.component,
				error_msg = f'Error when doing general query search: "{msg}"',
				request = f'Query: `{query}`'
			)



	async def lookup_song(self):
		return



	async def lookup_collection(self):
		return
	


	async def lookup_artist(self, id: str):
		try:
			return
		except Exception as msg:
			return Error()