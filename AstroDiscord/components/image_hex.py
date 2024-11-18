import requests
from PIL import Image
import numpy as np
from io import BytesIO

def image_hex(image_url: str, quality: int = 5):
	try:
		response = requests.get(image_url)
		image = Image.open(BytesIO(response.content))
	except:
		return 0xf5c000

	width, height = image.size
	new_width = width // quality
	new_height = height // quality
	image = image.resize((new_width, new_height))

	pixels = image.convert('RGB').getdata()
	average_color = np.mean(pixels, axis = 0).astype(int)

	hex_color = "#{:02x}{:02x}{:02x}".format(*average_color)
	return int(hex_color[1:], base = 16)