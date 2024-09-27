from AstroAPI.elements import etc
from AstroAPI.elements.service_elements import Album, Track, Single, Artist, Podcast, PodcastEpisode, Playlist, Audiobook
import asyncio
import aiohttp

class Spotify:
	def __init__(self, client_id: str, client_secret: str):
		self.client_id = client_id
		self.client_secret = client_secret
		self.token = None
		self.token_expiration_date = None
		asyncio.run(self.get_token())

	async def get_token(self):
		if self.token == None or (self.token_expiration_date == None or etc.current_time() > self.token_expiration_date):
			async with aiohttp.ClientSession() as session:
				api_url = 'https://accounts.spotify.com/api/token'
				api_data = f'grant_type=client_credentials&client_id={self.client_id}&client_secret={self.client_secret}'
				api_headers = {'Content-Type': 'application/x-www-form-urlencoded'}
				async with session.post(url = api_url, data = api_data, headers = api_headers) as response:
					if response.status == 200:
						json_response = await response.json()
						self.token = json_response['access_token']
						self.token_expiration_date = etc.current_time() + int(json_response['expires_in'])
		return self.token

	async def search(self, query: str, type: str = 'album,artist,playlist,track,show,episode,audiobook', market: str = 'US', limit: int = 50, offset: int = 0):
		async with aiohttp.ClientSession() as session:
			singles = []
			tracks = []
			albums = []
			playlists = []
			podcasts = []
			podcast_episodes = []
			audiobooks = []
			api_url = f'https://api.spotify.com/v1/search'
			api_params = {
				'q': query,
				'type': type,
				'market': market,
				'limit': limit,
				'offset': offset
			}
			api_headers = {'Authorization': f'Bearer {await self.get_token()}'}
			timeout = aiohttp.ClientTimeout(total = 30)
			start_time = etc.current_time_ms()
			async with session.get(url = api_url, headers = api_headers, timeout = timeout, params = api_params) as response:
				if response.status == 200:
					json_response = await response.json()
					if 'track' in type:
						for track in json_response['tracks']['items']:
							url = track['external_urls']['spotify']
							id = track['id']
							title = track['name']
							artists = [artist['name'] for artist in track['artists']]
							collection_artists = [artist['name'] for artist in track['album']['artists']]
							cover = (track['album']['images'][0]['url'] if track['album']['images'] != [] else '')
							collection = track['album']['name']
							is_explicit = track['explicit']
							if track['album']['album_type'] != 'single':
								end_time = etc.current_time_ms()
								tracks.append(Track(
									service = 'spotify',
									url = url,
									id = id,
									title = title,
									censored_title = title,
									artists = artists,
									album = collection,
									album_artists = collection_artists,
									is_explicit = is_explicit,
									cover_url = cover,
									api_response_time = end_time - start_time,
									api_http_code = response.status
								))
							else:
								end_time = etc.current_time_ms()
								singles.append(Single(
									service = 'spotify',
									url = url,
									id = id,
									title = title,
									censored_title = title,
									artists = artists,
									collection = collection,
									is_explicit = is_explicit,
									cover_url = cover,
									api_response_time = end_time - start_time,
									api_http_code = response.status
								))
					if 'album' in type:
						for album in json_response['albums']['items']:
							url = album['external_urls']['spotify']
							id = album['id']
							title = album['name']
							artists = [artist['name'] for artist in album['artists']]
							cover = (album['images'][0]['url'] if album['images'] != [] else '')
							year = album['release_date'][:4]
							end_time = etc.current_time_ms()
							if album['album_type'] != 'single':
								albums.append(Album(
									service = 'spotify',
									url = url,
									id = id,
									title = title,
									censored_title = title,
									artists = artists,
									release_year = year,
									cover_url = cover,
									api_response_time = end_time - start_time,
									api_http_code = response.status
								))
					if 'artist' in type:
						for artist in json_response['artists']['items']:
							url = artist['external_urls']['spotify']
							id = artist['id']
							name = artist['name'],
							genres = artist['genres'],
							profile_pic = (artist['images'][0]['url'] if artist['images'] != [] else '')
							end_time = etc.current_time_ms()
							artists.append(Artist(
								service = 'spotify',
								url = url,
								id = id,
								name = name,
								genres = genres,
								profie_pic_url = profile_pic,
								api_response_time = end_time - start_time,
								api_http_code = response.status
							))
					if 'show' in type:
						for podcast in json_response['shows']['items']:
							url = podcast['external_urls']['spotify']
							id = podcast['id']
							title = podcast['name']
							publisher = podcast['publisher']
							cover = (podcast['images'][0]['url'] if podcast['images'] != [] else '')
							is_explicit = podcast['explicit']
							end_time = etc.current_time_ms()
							podcasts.append(Podcast(
								service = 'spotify',
								url = url,
								id = id,
								title = title,
								censored_title = title,
								publisher = publisher,
								cover_url = cover,
								is_explicit = is_explicit,
								api_response_time = end_time - start_time,
								api_http_code = response.status
							))
					if 'episode' in type:
						for episode in json_response['episodes']['items']:
							url = episode['external_urls']['spotify']
							id = episode['id']
							title = episode['name']
							year = episode['release_date'][:4]
							cover = (episode['images'][0]['url'] if episode['images'] != [] else '')
							is_explicit = episode['explicit']
							end_time = etc.current_time_ms()
							podcast_episodes.append(PodcastEpisode(
								service = 'spotify',
								url = url,
								id = id,
								title = title,
								censored_title = title,
								release_year = year,
								cover_url = cover,
								is_explicit = is_explicit,
								api_response_time = end_time - start_time,
								api_http_code = response.status
							))
					if 'playlist' in type:
						for playlist in json_response['playlists']['items']:
							url = playlist['external_urls']['spotify']
							id = playlist['id']
							title = playlist['name']
							owner = playlist['owner']['display_name']
							cover = (playlist['images'][0]['url'] if playlist['images'] != [] else '')
							songs = []
							async with session.get(url = playlist['tracks']['href'], headers = {'Authorization': f'Bearer {await self.get_token()}'}, timeout = aiohttp.ClientTimeout(total = 30)) as song_request:
								if song_request.status == 200:
									songs_json = await song_request.json()
									for song in songs_json['items']:
										try:
											song_url = song['track']['external_urls']['spotify']
											song_id = song['track']['id']
											song_title = song['track']['name']
											song_artists = [artist['name'] for artist in song['track']['artists']]
											song_collection_artists = [artist['name'] for artist in song['track']['album']['artists']]
											song_cover = (song['track']['album']['images'][0]['url'] if song['track']['album']['images'] != [] else '')
											song_collection = song['track']['album']['name']
											song_is_explicit = song['track']['explicit']
											if song['track']['album']['album_type'] != 'single':
												end_time = etc.current_time_ms()
												songs.append(Track(
													service = 'spotify',
													url = song_url,
													id = song_id,
													title = song_title,
													censored_title = song_title,
													artists = song_artists,
													album = song_collection,
													album_artists = song_collection_artists,
													is_explicit = song_is_explicit,
													cover_url = song_cover,
													api_response_time = end_time - start_time,
													api_http_code = response.status
												))
											else:
												end_time = etc.current_time_ms()
												songs.append(Single(
													service = 'spotify',
													url = song_url,
													id = song_id,
													title = song_title,
													censored_title = song_title,
													artists = song_artists,
													collection = song_collection,
													is_explicit = song_is_explicit,
													cover_url = song_cover,
													api_response_time = end_time - start_time,
													api_http_code = response.status
												))
										except:
											continue
							end_time = etc.current_time_ms()
							playlists.append(Playlist(
								service = 'spotify',
								url = url,
								id = id,
								title = title,
								owner = owner,
								songs = songs,
								cover_url = cover,
								api_response_time = end_time - start_time,
								api_http_code = response.status
							))
					if 'audiobook' in type:
						for audiobook in json_response['audiobooks']['items']:
							url = audiobook['external_urls']['spotify']
							id = audiobook['id']
							title = audiobook['name']
							authors = [author['name'] for author in audiobook['authors']]
							narrators = [narrator['name'] for narrator in audiobook['narrators']]
							publisher = audiobook['publisher']
							chapters = audiobook['total_chapters']
							cover = (audiobook['images'][0]['url'] if audiobook['images'] != [] else '')
							is_explicit = audiobook['explicit']
							end_time = etc.current_time_ms()
							audiobooks.append(Audiobook(
								service = 'spotify',
								url = url,
								id = id,
								title = title,
								censored_title = title,
								authors = authors,
								narrators = narrators,
								publisher = publisher,
								chapters = chapters,
								cover_url = cover,
								is_explicit = is_explicit,
								api_response_time = end_time - start_time,
								api_http_code = response.status
							))
					return({
						'spotify': {
							'singles': singles,
							'tracks': tracks,
							'albums': albums,
							'podcasts': podcasts,
							'podcast_episodes': podcast_episodes,
							'audiobooks': audiobooks,
							'playlists': playlists
						}
					})
