from elements import etc
from elements.service_elements import Album, Track, Single
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
				end_time = etc.current_time_ms()
				if response.status == 200:
					json_response = await response.json()
					etc.save_json(json_response)
					if 'track' in type:
						for track in json_response['tracks']['items']:
							url = track['external_urls']['spotify']
							id = track['id']
							title = track['name']
							artists = [artist['name'] for artist in track['artists']]
							collection_artists = [artist['name'] for artist in track['album']['artists']]
							cover = track['album']['images'][0]['url']
							collection = track['album']['name']
							is_explicit = track['explicit']
							if track['album']['album_type'] != 'single':
								tracks.append(Track(service = 'spotify', url = url, id = id, title = title, censored_title = title, artists = artists, album = collection, album_artists = collection_artists, is_explicit = is_explicit, cover_url = cover, api_response_time = end_time - start_time, api_http_code = response.status))
							else:
								singles.append(Single(service = 'spotify', url = url, id = id, title = title, censored_title = title, artists = artists, collection = collection, is_explicit = is_explicit, cover_url = cover, api_response_time = end_time - start_time, api_http_code = response.status))
					if 'album' in type:
						for album in json_response['albums']['items']:
							url = album['external_urls']['spotify']
							id = album['id']
							title = album['name']
							artists = [artist['name'] for artist in album['artists']]
							cover = album['images'][0]['url']
							year = album['release_date'][:4]
							if album['album_type'] != 'single':
								albums.append(Album(service = 'spotify', url = url, id = id, title = title, censored_title = title, artists = artists, release_year = year, cover_url = cover, api_response_time = end_time - start_time, api_http_code = response.status))
					return({
						'spotify': {
							'tracks': tracks,
							'singles': singles,
							'albums': albums,
							'podcasts': podcasts,
							'podcast_episodes': podcast_episodes,
							'audiobooks': audiobooks,
							'playlists': playlists
						}
					})
