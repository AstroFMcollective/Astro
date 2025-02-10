import aiohttp
from PIL import Image
import numpy as np
from io import BytesIO



async def image_hex(image_url: str, quality: int = 5):
	async with aiohttp.ClientSession() as session:
		async with session.get(url = image_url) as response:
			if response.status == 200:
				image_bytes = await response.read()
				image = Image.open(BytesIO(image_bytes))

				width, height = image.size
				new_width = width // quality
				new_height = height // quality
				image = image.resize((new_width, new_height))

				pixels = image.convert('RGB').getdata()
				average_color = np.mean(pixels, axis = 0).astype(int)

				hex_color = "#{:02x}{:02x}{:02x}".format(*average_color)
				return int(hex_color[1:], base = 16)
			else:
				return 0xf5c000