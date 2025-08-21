from urllib.parse import urlparse
from urllib import request
from asyncio import run



class URLTools:
	def __init__(self):
		self.spotify_domains = [
			'open.spotify.com'
		]
		self.apple_music_domains = [
			'music.apple.com',
		]
		self.youtube_domains = [
			'music.youtube.com',
			'www.youtube.com',
			'youtu.be',
		]
		self.deezer_domains = [
			'www.deezer.com',
			'deezer.page.link',
			'link.deezer.com'
		]
		self.deferred_domains = [
			'deezer.page.link',
			'link.deezer.com'
		]

	async def get_urls_from_string(self, string: str):
		words = string.split()
		urls = []
		for word in words:
			parsed = urlparse(word)
			if parsed.scheme and parsed.netloc:
				urls.append(word)
		return urls
	
	async def get_undeferred_url(self, url: str):
		try:
			data = request.urlopen(url)
		except:
			return None
		regular_url = data.geturl()
		return regular_url
	
	async def get_metadata_from_url(self, url: str):
		is_url = await self.get_urls_from_string(url)
		if is_url == []:
			return {
				'id': None,
				'service': None,
				'type': None,
				'country_code': None
			}
		url_data = self.deconstruct_url(url)
		if url_data['domain'] in self.deferred_domains:
			url = await self.get_undeferred_url(url)
			url_data = self.deconstruct_url(url)

		url_domain = url_data['domain']
		url_path = url_data['path']
		url_parameters = url_data['parameters']

		if url_domain in self.spotify_domains: # Spotify
			media_service = 'spotify'
			media_country_code = None
			if url_path.find('track') >= 0: # Spotify songs
				identifier = url_path.replace('/track/','') 
				media_type = 'song'
			elif url_path.find('album') >= 0: # Spotify collections
				identifier = url_path.replace('/album/','')
				media_type = 'collection'
			else:
				identifier = None
				media_type = None

		elif url_domain in self.apple_music_domains: # Apple Music
			media_service = 'apple_music'
			media_country_code = url_path[1:3]
			url_path = url_path.replace(f'/{media_country_code}/','')
			if url_path.find('album') >= 0: # Apple Music songs and collections
				url_path = url_path.replace('album/', '')
				if 'i' in url_parameters: # Apple Music songs
					identifier = url_parameters['i']
					media_type = 'song'
				else: # Apple Music collections
					identifier = url_path[url_path.find('/')+1:]
					media_type = 'collection'
			elif url_path.find('music-video') >= 0: # Apple Music music videos
				url_path = url_path.replace('music_video/', '')
				identifier = url_path[url_path.find('/')+1:]
				media_type = 'music_video'
			else:
				identifier = None
				media_type = None

		elif url_domain in self.youtube_domains: # YouTube (Music)
			media_service = 'youtube_music'
			media_country_code = None
			if url_domain.find('youtube.com') >= 0: # Non-shortened URL
				if url_path.find('watch') >= 0: # YouTube (Music) song
					identifier = url_parameters['v']
					media_type = 'song'
				elif url_path.find('playlist') >= 0: # YouTube (Music) collection
					if url_parameters['list'][:4] == 'OLAK5': # Checks if the playlist is an album, because all albums/EPs have OLAK5 at the start of the ID
						identifier = url_parameters['list']
						media_type = 'collection'
					else: # If not, just return None and deal with it later
						identifier = None
						media_type = None
				else:
					identifier = None
					media_type = None
			elif url_domain.find('youtu.be') >= 0: # Shortened URL, immediately assume it's a song
				identifier = url_path[1:]
				media_type = 'song'
			else:
				identifier = None
				media_type = None

		elif url_domain in self.deezer_domains: # Deezer
			media_service = 'deezer'
			if url_path[:7] != '/track/' and url_path[:7] != '/album/': # Check if the URL contains a country code
				media_country_code = url_path[1:3]
				url_path = url_path.replace(f'/{media_country_code}','') # DON'T remove the other slash like in Apple Music
			else:
				media_country_code = None
			if url_path.find('track') >= 0: # Deezer song
				identifier = url_path.replace('/track/', '')
				media_type = 'song'
			elif url_path.find('album') >= 0: # Deezer collection
				identifier = url_path.replace('/album/', '')
				media_type = 'collection'
			else:
				identifier = None
				media_type = None

		return {
			'id': identifier,
			'service': media_service,
			'type': media_type,
			'country_code': media_country_code
		}
	
	def deconstruct_url(self, url: str):
		url_data = urlparse(url)
		url_scheme = url_data.scheme
		url_domain = url_data.netloc
		url_path = url_data.path
		url_fragment = url_data.fragment
		url_parameters = {}
		if '?' in url:
			url_unfiltered_parameters = url[url.find('?')+1:]
			for param in url_unfiltered_parameters.split('&'):
				if '=' in param:
					key, value = param.split('=', 1)
					url_parameters[key] = value
				else:
					url_parameters[param] = None
		
		return {
			'scheme': url_scheme,
			'domain': url_domain,
			'path': url_path,
			'parameters': url_parameters,
			'fragment': url_fragment
		}
	
url_tools = URLTools()