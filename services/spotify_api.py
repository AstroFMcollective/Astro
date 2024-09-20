from elements import tokens
from elements import etc
from elements.service_elements import Album, Track
import asyncio
import aiohttp

class Spotify:
	def __init__(self, client_id: str, client_secret: str):
		self.client_id = client_id
		self.client_secret = client_secret
		self.token = None
		self.token_type = None
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
						self.token_type = json_response['token_type']
						self.token_expiration_date = etc.current_time() + int(json_response['expires_in'])
		return self.token

	async def search(self, query: str, type: str = 'album,artist,playlist,track,show,episode,audiobook', market: str = None, limit: int = None, offset: int = None):
		async with aiohttp.ClientSession() as session:
			tracks = []
			albums = []
			playlists = []
			podcasts = []
			podcast_episodes = []
			audiobooks = []
			api_url = f'https://api.spotify.com/v1/search'
			api_params = {
				'q': query,
				'type': type
			}
			if market != None:
				api_params |= {'market': market}
			if limit != None:
				api_params |= {'limit': str(limit)}
			if offset != None:
				api_params |= {'offset': str(offset)}
			api_headers = {'Authorization': f'Bearer {await self.get_token()}'}
			timeout = aiohttp.ClientTimeout(total = 30)
			async with session.get(url = api_url, headers = api_headers, timeout = timeout, params = api_params) as response:
				if response.status == 200:
					json_response = await response.json()
					etc.save_json(json_response)
					for album in json_response['albums']['items']:
						url = album['external_urls']['spotify']
						id = album['id']
						title = album['name']
						artists = [artist['name'] for artist in album['artists']]
						cover = album['images'][0]['url']
						year = album['release_date'][:4]
						albums.append(Album('spotify',url,id,title,title,artists,cover,0,response.status,year))
					for track in json_response['tracks']['items']:
						url = track['external_urls']['spotify']
						id = track['id']
						title = track['name']
						artists = [artist['name'] for artist in track['artists']]
						collection_artists = [artist['name'] for artist in track['album']['artists']]
						cover = track['album']['images'][0]['url']
						collection = track['album']['name']
						is_explicit = track['explicit']
						tracks.append(Track('spotify',url,id,title,title,artists,cover,0,response.status,collection,collection_artists,is_explicit))
					return([albums, tracks])
