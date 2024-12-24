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

deferred_urls = [
	'https://deezer.page.link'
]

all_urls = [
	spotify_urls,
	apple_music_urls,
	youtube_urls,
	deezer_urls,
	tidal_urls
]

def find_urls(string: str) -> list:
	words = string.split()
	urls = []
	for word in words:
		parsed = urlparse(word)
		if parsed.scheme and parsed.netloc:
			urls.append(word)
	return urls

def get_regular_url(deferred_url: str) -> str:
	try:
		data = request.urlopen(deferred_url)
	except:
		return None
	regular_url = data.geturl()
	return regular_url

def get_data_from_urls(urls: str | list) -> list:
	if isinstance(urls, str):
		urls = [urls]
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

	for url in urls:
		for base_url in spotify_urls:
			if base_url in url:
				url = url.replace(base_url, '')
				if '/track/' in url:
					if '?' in url:
						results.append(template(types[0], url[url.index('/track/')+7:url.index('?')]))
						break
					else:
						results.append(template(types[0], url[url.index('/track/')+7:]))
						break
				elif '/album/' in url:
					if '?' in url:
						results.append(template(types[1], url[url.index('/album/')+7:url.index('?')]))
						break
					else:
						results.append(template(types[1], url[url.index('/album/')+7:]))
						break

		for base_url in apple_music_urls:
			if base_url in url:
				country_code = url[24:26]
				url = url.replace(base_url, '')
				if '/song/' in url:
					index = len(url) - 1
					while url[index] != '/':
						index -= 1
					results.append(template(types[2], url[index+1:], country_code))
					break
				elif '/album/' in url:
					if '?i=' in url:
						if '&uo=' in url:
							results.append(template(types[2], url[url.index('?i=')+3:url.index('&uo=')], country_code))
							break
						elif '&l=' in url:
							results.append(template(types[2], url[url.index('?i=')+3:url.index('&l=')], country_code))
							break
						elif '&ls' in url:
							results.append(template(types[2], url[url.index('?i=')+3:url.index('&ls')], country_code))
							break
						else:
							results.append(template(types[2], url[url.index('?i=')+3:], country_code))
							break
					else:
						index = len(url) - 1
						while url[index] != '/':
							index -= 1
						if '?uo' in url:
							results.append(template(types[3], url[index+1:url.index('?uo')], country_code))
							break
						else:
							results.append(template(types[3], url[index+1:], country_code))
							break
				elif '/music-video/' in url:
					index = len(url) - 1
					while url[index] != '/':
						index -= 1
					if '?uo' in url:
						results.append(template(types[4], url[index+1:url.index('?uo')], country_code))
						break
					else:
						results.append(template(types[4], url[index+1:], country_code))
						break

		for base_url in youtube_urls:
			if base_url in url:
				url = url.replace(base_url, '')
				if 'v=' in url:
					index = url.index('v=') + 2
					if '&' in url:
						results.append(template(types[5], url[index:url.index('&')]))
						break
					else:
						results.append(template(types[5], url[index:]))
						break
				elif '?si' in url:
					results.append(template(types[5], url[:url.index('?si')]))
				elif 'list=OLAK5' in url:
					index = url.index('?list=') + 6
					if url.find('&si') >= 0:
						results.append(template(types[6], url[index:url.index('&si')]))
						break
					else:
						results.append(template(types[6], url[index:]))
						break

		for base_url in deezer_urls:
			if base_url in url:
				for deferred_url in deferred_urls:
					if deferred_url in url:
						url = get_regular_url(url)
						break
				url = url.replace(base_url, '')
				if '/track/' in url:
					if url.find('?') >= 0:
						results.append(template(types[7], url[url.index('/track/')+7:url.index('?')]))
						break
					else:
						results.append(template(types[7], url[url.index('/track/')+7:]))
						break
				elif '/album/' in url:
					if url.find('?') >= 0:
						results.append(template(types[8], url[url.index('/album/')+7:url.index('?')]))
						break
					else:
						results.append(template(types[8], url[url.index('/album/')+7:]))
						break
		
		for base_url in tidal_urls:
			if base_url in url:
				url = url.replace(base_url, '')
				if '/track/' in url:
					if '?u' in url:
						results.append(template(types[9], url[url.index('/track/') + 7:url.index('?u')]))
						break
					else:
						results.append(template(types[9], url[url.index('/track/') + 7:]))
						break
				elif '/album/' in url:
					if '?u' in url:
						results.append(template(types[10], url[url.index('/album/') + 7:url.index('?u')]))
					else:
						results.append(template(types[10], url[url.index('/album/') + 7:]))
				elif '/video/' in url:
					if '?u' in url:
						results.append(template(types[11], url[url.index('/video/') + 7:url.index('?u')]))
					else:
						results.append(template(types[11], url[url.index('/video/') + 7:]))

	return results
