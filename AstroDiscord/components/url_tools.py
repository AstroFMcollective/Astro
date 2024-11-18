from urllib.parse import urlparse
from urllib import request

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