class Error:
	def __init__(self, http_code: int = None, error_msg: str = None) -> object:
		self.type = 'error'
		self.http_code = http_code
		self.error_msg = error_msg

class Song:
	def __init__(self, service: str, type: str, url: str, id: any, title: str, censored_title: str, artists: list, cover_url: str, api_response_time: int, api_http_code: int, collection: str = None, is_explicit: bool = None) -> object:
		self.service = service
		self.type = type
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

class MusicVideo:
	def __init__(self, service: str, url: str, id: any, title: str, censored_title: str, artists: list, release_year: int, thumbnail_url: str, is_explicit: bool, api_response_time: int, api_http_code: int) -> object:
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

class Collection:
	def __init__(self, service: str, type: str, url: str, id: any, title: str, censored_title: str, artists: list, release_year: int, cover_url: str, api_response_time: int, api_http_code: int) -> object:
		self.service = service
		self.type = type
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
	def __init__(self, service: str, url: str, id: any, title: str, censored_title: str, publisher: str, cover_url: str, is_explicit: bool, api_response_time: int, api_http_code: int) -> object:
		self.service = service
		self.type = 'podcast'
		self.url = url
		self.id = str(id)
		self.title = title
		self.censored_title = censored_title
		self.publisher = publisher
		self.cover_url = cover_url
		self.is_explicit = is_explicit
		self.api_response_time = api_response_time
		self.api_http_code = api_http_code

class PodcastEpisode:
	def __init__(self, service: str, url: str, id: any, title: str, censored_title: str, release_year: str, cover_url: str, is_explicit: bool, api_response_time: int, api_http_code: int) -> object:
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

class Playlist:
	def __init__(self, service: str, url: str, id: any, title: str, owner: str, songs: list, cover_url: str, api_response_time: int, api_http_code: int) -> object:
		self.service = service
		self.type = 'playlist'
		self.url = url
		self.id = str(id)
		self.title = title
		self.owner = owner
		self.songs = songs
		self.cover_url = cover_url
		self.api_response_time = api_response_time
		self.api_http_code = api_http_code

class Audiobook:
	def __init__(self, service: str, url: str, id: any, title: str, censored_title: str, authors: list, narrators: list, publisher: str, chapters: int, cover_url: str, is_explicit: bool, api_response_time: int, api_http_code: int) -> object:
		self.service = service
		self.type = 'audiobook'
		self.url = url
		self.id = str(id)
		self.title = title
		self.censored_title = censored_title
		self.authors = authors
		self.narrators = narrators
		self.publisher = publisher
		self.chapters = chapters
		self.cover_url = cover_url
		self.is_explicit = is_explicit
		self.api_response_time = api_response_time
		self.api_http_code = api_http_code

class Artist:
	def __init__(self, service: str, url: str, id: any, name: str, genres: list, profie_pic_url: str, api_response_time: int, api_http_code: int) -> object:
		self.service = service
		self.type = 'artist'
		self.url = url
		self.id = str(id)
		self.name = name
		self.genres = genres
		self.profile_pic_url = profie_pic_url
		self.api_response_time = api_response_time
		self.api_http_code = api_http_code