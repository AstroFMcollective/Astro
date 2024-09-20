class Error:
	def __init__(self, http_code: int = None, error_msg: str = None):
		self.http_code = http_code
		self.error_msg = error_msg

class Single:
	def __init__(self, service: str, url: str, id: any, title: str, censored_title: str, artists: list, cover_url: str, api_response_time: int, api_http_code: int, collection: str = None, is_explicit: bool = None):
		self.service = service
		self.url = url
		self.id = str(id)
		self.title = title
		self.censored_title = censored_title
		self.collection = collection
		self.artists = artists
		self.cover_url = cover_url
		self.is_explicit = is_explicit
		self.api_response_time = api_response_time
		self.api_http_code = api_http_code

class Track:
	def __init__(self, service: str, url: str, id: any, title: str, censored_title: str, artists: list, cover_url: str, api_response_time: int, api_http_code: int, album: str = None, album_artists: list = None, is_explicit: bool = None):
		self.service = service
		self.url = url
		self.id = str(id)
		self.title = title
		self.censored_title = censored_title
		self.album = album
		self.artists = artists
		self.album_artists = album_artists
		self.cover_url = cover_url
		self.is_explicit = is_explicit
		self.api_response_time = api_response_time
		self.api_http_code = api_http_code

class Album:
	def __init__(self, service: str, url: str, id: any, title: str, censored_title: str, artists: list, cover_url: str, api_response_time: int, api_http_code: int, release_year: int = None):
		self.service = service
		self.url = url
		self.id = str(id)
		self.title = title
		self.censored_title = censored_title
		self.artists = artists
		self.release_year = release_year
		self.cover_url = cover_url
		self.api_response_time = api_response_time
		self.api_http_code = api_http_code

class User:
	def __init__(self, service, url, id, username, premium_account, profile_picture, api_response_time, api_http_code):
		self.service = service
		self.url = url
		self.id = id
		self.username = username
		self.premium_account = premium_account
		self.api_response_time = api_response_time
		self.api_http_code = api_http_code