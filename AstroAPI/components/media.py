class Error:
	def __init__(self, service: str, component: str, http_code: int = None, error_msg: str = None, request: str = None) -> object:
		self.service = service
		self.type = 'error'
		self.component = component
		self.http_code = http_code
		self.error_msg = error_msg
		self.request = request

class Empty:
	def __init__(self, service: str, request: str = None) -> object:
		self.service = service
		self.type = 'empty_response'
		self.request = request

class Song:
	def __init__(self, service: str, type: str, url: str, id: any, title: str, artists: list, cover_url: str, api_response_time: int, api_http_code: int, collection: str = None, is_explicit: bool = None) -> object:
		self.service = service
		self.type = type
		self.url = url
		self.id = str(id)
		self.title = title
		self.censored_title = title
		self.collection = collection
		self.artists = artists
		self.cover_url = cover_url
		self.is_explicit = is_explicit
		self.api_response_time = api_response_time
		self.api_http_code = api_http_code

class MusicVideo:
	def __init__(self, service: str, url: str, id: any, title: str, artists: list, thumbnail_url: str, api_response_time: int, api_http_code: int, is_explicit: bool = None) -> object:
		self.service = service
		self.type = 'music_video'
		self.url = url
		self.id = str(id)
		self.title = title
		self.censored_title = title
		self.artists = artists
		self.thumbnail_url = thumbnail_url
		self.is_explicit = is_explicit
		self.api_response_time = api_response_time
		self.api_http_code = api_http_code

class Collection:
	def __init__(self, service: str, type: str, url: str, id: any, title: str, artists: list, cover_url: str, api_response_time: int, api_http_code: int, release_year: int = None) -> object:
		self.service = service
		self.type = type
		self.url = url
		self.id = str(id)
		self.title = title
		self.censored_title = title
		self.artists = artists
		self.release_year = None if release_year == None else int(release_year)
		self.cover_url = cover_url
		self.api_response_time = api_response_time
		self.api_http_code = api_http_code

class Podcast:
	def __init__(self, service: str, url: str, id: any, title: str, publisher: str, cover_url: str, is_explicit: bool, api_response_time: int, api_http_code: int) -> object:
		self.service = service
		self.type = 'podcast'
		self.url = url
		self.id = str(id)
		self.title = title
		self.censored_title = title
		self.publisher = publisher
		self.cover_url = cover_url
		self.is_explicit = is_explicit
		self.api_response_time = api_response_time
		self.api_http_code = api_http_code

class PodcastEpisode:
	def __init__(self, service: str, url: str, id: any, title: str, release_year: str, cover_url: str, is_explicit: bool, api_response_time: int, api_http_code: int) -> object:
		self.service = service
		self.type = 'podcast_episode'
		self.url = url
		self.id = str(id)
		self.title = title
		self.censored_title = title
		self.release_year = None if release_year == None else int(release_year)
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
		self.censored_title = title
		self.owner = owner
		self.songs = songs
		self.cover_url = cover_url
		self.api_response_time = api_response_time
		self.api_http_code = api_http_code

class Audiobook:
	def __init__(self, service: str, url: str, id: any, title: str, authors: list, narrators: list, publisher: str, chapters: int, cover_url: str, is_explicit: bool, api_response_time: int, api_http_code: int) -> object:
		self.service = service
		self.type = 'audiobook'
		self.url = url
		self.id = str(id)
		self.title = title
		self.censored_title = title
		self.authors = authors
		self.narrators = narrators
		self.publisher = publisher
		self.chapters = chapters
		self.cover_url = cover_url
		self.is_explicit = is_explicit
		self.api_response_time = api_response_time
		self.api_http_code = api_http_code

class Artist:
	def __init__(self, service: str, url: str, id: any, name: str, api_response_time: int, api_http_code: int, profie_pic_url: str = None, genres: list = None) -> object:
		self.service = service
		self.type = 'artist'
		self.url = url
		self.id = str(id)
		self.name = name
		self.genres = genres
		self.profile_pic_url = profie_pic_url if profie_pic_url != None else 'https://developer.valvesoftware.com/w/images/thumb/8/8b/Debugempty.png/200px-Debugempty.png'
		self.api_response_time = api_response_time
		self.api_http_code = api_http_code