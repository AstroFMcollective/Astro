from urllib.parse import urlparse
from urllib import request



types = [
	'spotify_song',
	'spotify_collection',
	'apple_music_song',
	'apple_music_collection',
	'apple_music_mv',
	'youtube_music_song',
	'youtube_music_collection',
	'deezer_song',
	'deezer_collection',
	'tidal_song',
	'tidal_collection',
	'tidal_mv'
]

spotify_urls = [
	'https://open.spotify.com'
]

apple_music_urls = [
	'https://music.apple.com',
]

youtube_urls = [
	'https://music.youtube.com/watch',
	'https://music.youtube.com/playlist',
	'https://www.youtube.com/watch',
	'https://youtu.be/',
	'https://www.youtube.com/playlist',
	'https://youtube.com/playlist',
]

deezer_urls = [
	'https://www.deezer.com',
	'https://deezer.page.link'
]

tidal_urls = [
	'https://tidal.com'
]

all_urls = [
	spotify_urls,
	apple_music_urls,
	youtube_urls,
	deezer_urls,
	tidal_urls
]

def find_urls(string: str):
	words = string.split()
	urls = []
	for word in words:
		parsed = urlparse(word)
		if parsed.scheme and parsed.netloc:
			urls.append(word)
	return urls

def get_regular_url(deferred_url: str):
	try:
		data = request.urlopen(deferred_url)
	except:
		return None
	regular_url = data.geturl()
	return regular_url

def get_data_from_urls(urls: list):
	new_urls = []
	for url in urls:
		if url[len(url)-1] == '/':
			new_urls.append(url[:len(url)-1])
		else:
			new_urls.append(url)
	urls = new_urls
	def template(media: str, id: str, country_code: str = None):
		return {
			'media': media,
			'id': id,
			'country_code': country_code
		}
	results = []

	spotify_url_string = ' '.join(spotify_urls)
	apple_music_url_string = ' '.join(apple_music_urls)
	youtube_url_string = ' '.join(youtube_urls)
	deezer_url_string = ' '.join(deezer_urls)
	tidal_url_string = ' '.join(tidal_urls)

	for url in urls:
		for base_url in spotify_urls:
			if base_url in url:
				url = url.replace(base_url, '')
				if '/track/' in url:
					if '?' in url:
						results.append(template(types[0], url[url.index('/track/')+7:url.index('?')]))
					else:
						results.append(template(types[0], url[url.index('/track/')+7:]))
				elif '/album/' in url:
					if '?' in url:
						results.append(template(types[1], url[url.index('/album/')+7:url.index('?')]))
					else:
						results.append(template(types[1], url[url.index('/album/')+7:]))

		for base_url in apple_music_urls:
			if base_url in url:
				country_code = url[24:26]
				url = url.replace(base_url, '')
				if '/song/' in url:
					index = len(url) - 1
					while url[index] != '/':
						index -= 1
					results.append(template(types[2], url[index+1:], country_code))
				elif '/album/' in url:
					if '?i=' in url:
						if '&uo=' in url:
							results.append(template(types[2], url[url.index('?i=')+3:url.index('&uo=')], country_code))
						else:
							results.append(template(types[2], url[url.index('?i=')+3:], country_code))
					else:
						index = len(url) - 1
						while url[index] != '/':
							index -= 1
						if '?uo' in url:
							results.append(template(types[3], url[index+1:url.index('?uo')], country_code))
						else:
							results.append(template(types[3], url[index+1:], country_code))
				elif '/music-video/' in url:
					index = len(url) - 1
					while url[index] != '/':
						index -= 1
					if '?uo' in url:
						results.append(template(types[4], url[index+1:url.index('?uo')], country_code))
					else:
						results.append(template(types[4], url[index+1:], country_code))

		for base_url in youtube_urls:
			if base_url in url:
				url = url.replace(base_url, '')
				if 'v=' in url:
					index = url.index('v=') + 2
					if '&' in url:
						results.append(template(types[5], url[index:url.index('&')]))
					else:
						results.append(template(types[5], url[index:]))
				elif '?si' in url:
					results.append(template(types[5], url[:url.index('?si')]))
				elif 'list=OLAK5' in url:
					index = url.index('?list=') + 6
					if url.find('&si') >= 0:
						results.append(template(types[6], url[index:url.index('&si')]))
					else:
						results.append(template(types[6], url[index:]))	

	return results
