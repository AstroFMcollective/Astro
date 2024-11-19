from urllib.parse import urlparse
from urllib import request


standard_urls = [ # WIP
	'https://open.spotify.com/track',
	'https://open.spotify.com/album',
	'https://music.apple.com/XX/album',
	'https://music.apple.com/XX/song',
	'https://music.youtube.com/watch',
	'https://music.youtube.com/playlist?list=OLAK5',
	'https://www.youtube.com/watch',
	'https://youtu.be/',
	'https://www.youtube.com/playlist?list=OLAK5',
	'https://youtube.com/playlist?list=OLAK5',
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