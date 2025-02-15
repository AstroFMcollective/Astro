from AstroAPI.components.ini import config

class Error:
	def __init__(self, service: str, component: str, meta: object, error_msg: str = None) -> object:
		self.service = service
		self.type = 'error'
		self.component = component
		self.error_msg = error_msg
		self.meta = meta

class Empty:
	def __init__(self, service: str, meta: object) -> object:
		self.service = service
		self.type = 'empty_response'
		self.meta = meta

class Meta:
	def __init__(self, service: str, request: dict, processing_time: int | dict, filter_confidence_percentage: dict = None, http_code: int = None):
		self.service = service
		self.request = request
		self.http_code = http_code
		self.processing_time = {service: processing_time} if isinstance(processing_time, int) else processing_time
		self.filter_confidence_percentage = filter_confidence_percentage

class Song:
	def __init__(self, service: str, type: str, url: str | dict, id: any, title: str, artists: list, cover_url: str, meta: object, cover_color_hex: int = None, collection: str = None, genre: str = None, is_explicit: bool = None) -> object:
		self.service = service
		self.type = type
		self.url = {service: url} if isinstance(url, str) else url
		self.id = {service: str(id)} if not isinstance(id, dict) else id
		self.title = title
		self.censored_title = title
		self.collection = collection
		self.artists = artists
		self.cover_url = cover_url
		self.cover_color_hex = cover_color_hex
		self.genre = genre
		self.is_explicit = is_explicit
		self.meta = meta

class MusicVideo:
	def __init__(self, service: str, url: str | dict, id: any, title: str, artists: list, thumbnail_url: str, meta = object, thumbnail_color_hex: int = None, is_explicit: bool = None, genre: str = None) -> object:
		self.service = service
		self.type = 'music_video'
		self.url = {service: url} if isinstance(url, str) else url
		self.id = {service: str(id)} if not isinstance(id, dict) else id
		self.title = title
		self.censored_title = title
		self.artists = artists
		self.thumbnail_url = thumbnail_url
		self.thumbnail_color_hex = thumbnail_color_hex
		self.is_explicit = is_explicit
		self.meta = meta

class Collection:
	def __init__(self, service: str, type: str, url: str | dict, id: any, title: str, artists: list, cover_url: str, meta = object, cover_color_hex: int = None, release_year: int = None, genre: str = None) -> object:
		self.service = service
		self.type = type
		self.url = {service: url} if isinstance(url, str) else url
		self.id = {service: str(id)} if not isinstance(id, dict) else id
		self.title = title
		self.censored_title = title
		self.artists = artists
		self.release_year = None if release_year == None else int(release_year)
		self.cover_url = cover_url
		self.cover_color_hex = cover_color_hex
		self.genre = genre
		self.meta = meta

class Podcast:
	def __init__(self, service: str, url: str | dict, id: any, title: str, publisher: str, cover_url: str, is_explicit: bool, meta = object, cover_color_hex: int = None) -> object:
		self.service = service
		self.type = 'podcast'
		self.url = {service: url} if isinstance(url, str) else url
		self.id = {service: str(id)} if not isinstance(id, dict) else id
		self.title = title
		self.censored_title = title
		self.publisher = publisher
		self.cover_url = cover_url
		self.cover_color_hex = cover_color_hex
		self.is_explicit = is_explicit
		self.meta = meta

class PodcastEpisode:
	def __init__(self, service: str, url: str | dict, id: any, title: str, release_year: str, cover_url: str, is_explicit: bool, meta = object, cover_color_hex: int = None) -> object:
		self.service = service
		self.type = 'podcast_episode'
		self.url = {service: url} if isinstance(url, str) else url
		self.id = {service: str(id)} if not isinstance(id, dict) else id
		self.title = title
		self.censored_title = title
		self.release_year = None if release_year == None else int(release_year)
		self.cover_url = cover_url
		self.cover_color_hex = cover_color_hex
		self.is_explicit = is_explicit
		self.meta = meta

class Playlist:
	def __init__(self, service: str, url: str | dict, id: any, title: str, owner: str, songs: list, cover_url: int, meta = object, cover_color_hex: int = None) -> object:
		self.service = service
		self.type = 'playlist'
		self.url = {service: url} if isinstance(url, str) else url
		self.id = {service: str(id)} if not isinstance(id, dict) else id
		self.title = title
		self.censored_title = title
		self.owner = owner
		self.songs = songs
		self.cover_url = cover_url
		self.cover_color_hex = cover_color_hex
		self.meta = meta

class Audiobook:
	def __init__(self, service: str, url: str | dict, id: any, title: str, authors: list, narrators: list, publisher: str, chapters: int, cover_url: str, is_explicit: bool, meta = object, cover_color_hex: int = None) -> object:
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
		self.cover_color_hex = cover_color_hex
		self.is_explicit = is_explicit
		self.meta = meta

class Artist:
	def __init__(self, service: str, url: str | dict, id: any, name: str, meta = object, profie_pic_url: str = None, profile_pic_color_hex: int = None, genres: list = None) -> object:
		self.service = service
		self.type = 'artist'
		self.url = {service: url} if isinstance(url, str) else url
		self.id = {service: str(id)} if not isinstance(id, dict) else id
		self.name = name
		self.genres = genres
		self.profile_pic_url = profie_pic_url if profie_pic_url != None else 'https://developer.valvesoftware.com/w/images/thumb/8/8b/Debugempty.png/200px-Debugempty.png'
		self.profile_pic_color_hex = profile_pic_color_hex
		self.meta = meta

class Cover:
	def __init__(self, service: str, type: str, hq_url: str | dict, lq_url: str | dict, title: str, artists: list, meta = object, color_hex: int = None) -> object:
		self.service = service
		self.type = 'cover'
		self.media_type = type
		self.title = title
		self.censored_title = title
		self.artists = artists
		self.hq_url = {service: hq_url} if isinstance(hq_url, str) else hq_url
		self.lq_url = {service: lq_url} if isinstance(lq_url, str) else lq_url
		self.color_hex = color_hex
		self.meta = meta

class Knowledge:
	def __init__(self, service: str, media_type: str, url: str | dict, id: any, title: str, artists: list, description: str, cover_url: str, meta: object, cover_color_hex: int = None, collection: str = None, release_date: str = None, is_explicit: bool = None, genre: str = None) -> object:
		self.service = service
		self.type = 'knowledge'
		self.media_type = media_type
		self.url = {service: url} if isinstance(url, str) else url
		self.id = {service: str(id)} if not isinstance(id, dict) else id
		self.title = title
		self.censored_title = title
		self.collection = collection
		self.artists = artists
		self.description = description
		self.release_date = release_date
		self.cover_url = cover_url
		self.cover_color_hex = cover_color_hex
		self.genre = genre
		self.is_explicit = is_explicit
		self.meta = meta
