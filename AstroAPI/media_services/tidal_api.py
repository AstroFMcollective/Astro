from AstroAPI.components.all import *
import asyncio
import aiohttp

class TIDAL:
	def __init__(self, client_id: str, client_secret: str):
		self.service = 'tidal'
		self.client_id = client_id
		self.client_secret = client_secret
		self.token = None
		self.token_expiration_date = None
		asyncio.run(self.get_token())



	async def get_token(self) -> str:
		if self.token == None or (self.token_expiration_date == None or current_time() > self.token_expiration_date):
			async with aiohttp.ClientSession() as session:
				api_url = 'https://accounts.spotify.com/api/token'
				api_data = f'grant_type=client_credentials&client_id={self.client_id}&client_secret={self.client_secret}'
				api_headers = {'Content-Type': 'application/x-www-form-urlencoded'}

				async with session.post(url = api_url, data = api_data, headers = api_headers) as response:
					if response.status == 200:
						json_response = await response.json()
						self.token = json_response['access_token']
						self.token_expiration_date = current_time() + int(json_response['expires_in'])

		return self.token