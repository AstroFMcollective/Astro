class Error:
	def __init__(self, http_code: int = None, error_msg: str = None):
		self.type = 'error'
		self.http_code = http_code
		self.error_msg = error_msg

class Single:
	def __init__(self, service: str, url: str, id: any, title: str, censored_title: str, artists: list, cover_url: str, api_response_time: int, api_http_code: int, collection: str = None, is_explicit: bool = None):
		self.service = service
		self.type = 'single'
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
		self.type = 'track'
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

class MusicVideo:
	def __init__(self, service: str, url: str, id: any, title: str, censored_title: str, artists: list, release_year: int, thumbnail_url: str, is_explicit: bool, api_response_time: int, api_http_code: int):
		self.service = service
		self.type = 'music_video'
		self.url = url
		self.id = str(id)
		self.title = title
		self.censored_title = censored_title
		self.artists = artists
		self.release_year = release_year
		self.thumbnail_url = thumbnail_url
		self.is_explicit = is_explicit
		self.api_response_time = api_response_time
		self.api_http_code = api_http_code

class Album:
	def __init__(self, service: str, url: str, id: any, title: str, censored_title: str, artists: list, release_year: int, cover_url: str, api_response_time: int, api_http_code: int):
		self.service = service
		self.type = 'album'
		self.url = url
		self.id = str(id)
		self.title = title
		self.censored_title = censored_title
		self.artists = artists
		self.release_year = release_year
		self.cover_url = cover_url
		self.api_response_time = api_response_time
		self.api_http_code = api_http_code

class Podcast:
	def __init__(self, service: str, url: str, id: any, title: str, censored_title: str, publisher: str, release_year: str, cover_url: str, is_explicit: bool, api_response_time: int, api_http_code: int):
		self.service = service
		self.type = 'podcast'
		self.url = url
		self.id = str(id)
		self.title = title
		self.censored_title = censored_title
		self.publisher = publisher
		self.release_year = release_year
		self.cover_url = cover_url
		self.is_explicit = is_explicit
		self.api_response_time = api_response_time
		self.api_http_code = api_http_code

class PodcastEpisode:
	def __init__(self, service: str, url: str, id: any, title: str, censored_title: str, release_year: str, cover_url: str, is_explicit: bool, api_response_time: int, api_http_code: int):
		self.service = service
		self.type = 'podcast_episode'
		self.url = url
		self.id = str(id)
		self.title = title
		self.censored_title = censored_title
		self.release_year = release_year
		self.cover_url = cover_url
		self.is_explicit = is_explicit
		self.api_response_time = api_response_time
		self.api_http_code = api_http_code