from AstroAPI.components.ini import config

class Error:
	def __init__(self, service: str, component: str, request: dict, http_code: int = None, error_msg: str = None) -> object:
		self.service = service
		self.type = 'error'
		self.component = component
		self.http_code = http_code
		self.error_msg = error_msg
		self.request = request

class Empty:
	def __init__(self, service: str, request: dict) -> object:
		self.service = service
		self.type = 'empty_response'
		self.request = request

class Song:
	def __init__(self, service: str, type: str, url: str | dict, id: any, title: str, artists: list, cover_url: str, api_response_time: int, api_http_code: int, request: dict, collection: str = None, genre: str = None, is_explicit: bool = None) -> object:
		self.service = service
		self.type = type
		self.url = {service: url} if isinstance(url, str) else url
		self.id = {service: str(id)} if not isinstance(id, dict) else id
		self.title = title
		self.censored_title = title
		self.collection = collection
		self.artists = artists
		self.cover_url = cover_url
		self.genre = genre
		self.is_explicit = is_explicit
		self.api_response_time = api_response_time
		self.api_http_code = api_http_code
		self.request = request

class MusicVideo:
	def __init__(self, service: str, url: str | dict, id: any, title: str, artists: list, thumbnail_url: str, api_response_time: int, api_http_code: int, request: dict, is_explicit: bool = None, genre: str = None) -> object:
		self.service = service
		self.type = 'music_video'
		self.url = {service: url} if isinstance(url, str) else url
		self.id = {service: str(id)} if not isinstance(id, dict) else id
		self.title = title
		self.censored_title = title
		self.artists = artists
		self.thumbnail_url = thumbnail_url
		self.is_explicit = is_explicit
		self.api_response_time = api_response_time
		self.api_http_code = api_http_code
		self.request = request

class Collection:
	def __init__(self, service: str, type: str, url: str | dict, id: any, title: str, artists: list, cover_url: str, api_response_time: int, api_http_code: int, request: dict, release_year: int = None, genre: str = None) -> object:
		self.service = service
		self.type = type
		self.url = {service: url} if isinstance(url, str) else url
		self.id = {service: str(id)} if not isinstance(id, dict) else id
		self.title = title
		self.censored_title = title
		self.artists = artists
		self.release_year = None if release_year == None else int(release_year)
		self.cover_url = cover_url
		self.genre = genre
		self.api_response_time = api_response_time
		self.api_http_code = api_http_code
		self.request = request

class Podcast:
	def __init__(self, service: str, url: str | dict, id: any, title: str, publisher: str, cover_url: str, is_explicit: bool, api_response_time: int, api_http_code: int, request: dict) -> object:
		self.service = service
		self.type = 'podcast'
		self.url = {service: url} if isinstance(url, str) else url
		self.id = {service: str(id)} if not isinstance(id, dict) else id
		self.title = title
		self.censored_title = title
		self.publisher = publisher
		self.cover_url = cover_url
		self.is_explicit = is_explicit
		self.api_response_time = api_response_time
		self.api_http_code = api_http_code
		self.request = request

class PodcastEpisode:
	def __init__(self, service: str, url: str | dict, id: any, title: str, release_year: str, cover_url: str, is_explicit: bool, api_response_time: int, api_http_code: int, request: dict) -> object:
		self.service = service
		self.type = 'podcast_episode'
		self.url = {service: url} if isinstance(url, str) else url
		self.id = {service: str(id)} if not isinstance(id, dict) else id
		self.title = title
		self.censored_title = title
		self.release_year = None if release_year == None else int(release_year)
		self.cover_url = cover_url
		self.is_explicit = is_explicit
		self.api_response_time = api_response_time
		self.api_http_code = api_http_code
		self.request = request

class Playlist:
	def __init__(self, service: str, url: str | dict, id: any, title: str, owner: str, songs: list, cover_url: str, api_response_time: int, api_http_code: int, request: dict) -> object:
		self.service = service
		self.type = 'playlist'
		self.url = {service: url} if isinstance(url, str) else url
		self.id = {service: str(id)} if not isinstance(id, dict) else id
		self.title = title
		self.censored_title = title
		self.owner = owner
		self.songs = songs
		self.cover_url = cover_url
		self.api_response_time = api_response_time
		self.api_http_code = api_http_code
		self.request = request

class Audiobook:
	def __init__(self, service: str, url: str | dict, id: any, title: str, authors: list, narrators: list, publisher: str, chapters: int, cover_url: str, is_explicit: bool, api_response_time: int, api_http_code: int, request: dict) -> object:
		self.service = service
		self.type = 'audiobook'
		self.url = {service: url} if isinstance(url, str) else url
		self.id = {service: str(id)} if not isinstance(id, dict) else id
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
		self.request = request

class Artist:
	def __init__(self, service: str, url: str | dict, id: any, name: str, api_response_time: int, api_http_code: int, request: dict, profie_pic_url: str = None, genres: list = None) -> object:
		self.service = service
		self.type = 'artist'
		self.url = {service: url} if isinstance(url, str) else url
		self.id = {service: str(id)} if not isinstance(id, dict) else id
		self.name = name
		self.genres = genres
		self.profile_pic_url = profie_pic_url if profie_pic_url != None else 'https://developer.valvesoftware.com/w/images/thumb/8/8b/Debugempty.png/200px-Debugempty.png'
		self.api_response_time = api_response_time
		self.api_http_code = api_http_code
		self.request = request