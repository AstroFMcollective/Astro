from discord import Embed, User, Member, ButtonStyle
from discord.ui import Button, View
from discord.utils import escape_markdown
from AstroDiscord.components.ini import text
import aiohttp
from PIL import Image
import numpy as np
from io import BytesIO



class EmbedComposer:
	def __init__(self):
		self.button_view = None
		self.embed = None
	
	async def error(self, error: int, custom: dict = None):
		error_titles = {
			500: 'An error has occurred!',
			204: "I couldn't find what you're looking for.",
			'other': 'An undocumented error has occured!'
		}
		error_descriptions = {
			500: 'Something has gone wrong on our end. Please try again! If this keeps happening, feel free to report it in our Discord server!',
			204: 'Please check your request for typos and if everything is in its right order.',
			'other': 'Something has gone horribly wrong. Please report this in our Discord server.'
		}
		error_meanings = {
			500: 'Internal server error',
			204: 'Empty response',
			'other': 'Unforeseen consequences'
		}

		if custom != None:
			title = custom['title']
			description = custom['description']
			meaning = custom['meaning']
		elif error not in error_titles:
			title = error_titles['other']
			description = error_descriptions['other']
			meaning = error_meanings['other']
		else:
			title = error_titles[error]
			description = error_descriptions[error]
			meaning = error_meanings[error]
		self.embed = Embed(
			title = title,
            description = description,
            colour = 0xf5c000
		)

		self.embed.set_author(name='Oh no!')

		self.embed.set_footer(
			text = f'Thanks for using Astro!  •  Error code {error} - {meaning}',
            icon_url = text['images']['pfpurl']
		)

	
	async def compose(self, user: User | Member, json_response: dict, command_type: str, anonymous: bool = False, censor: bool = False, loading: bool = False):
		"""
			Compose a Discord embed from a given JSON file.
		"""
		# Order in which to read the metadata from multiple services
		service_metadata_priority = ['spotify','apple_music','youtube_music','deezer','genius']
		cover_art_priority = ['genius','spotify','deezer','youtube_music','apple_music']
		mv_thumbnail_priority = ['youtube_music', 'apple_music']

		loading_emojis = {
			'loading1': '<a:loading1:1438606345153806468>',
			'loading2': '<a:loading2:1438606347942756423>',
			'loading3': '<a:loading3:1438606349431865515>',
			'loading4': '<a:loading4:1438606352174940170>',
			'loading5': '<a:loading5:1438606355681509396>',
			'loading6': '<a:loading6:1438606359192141885>',
			'loading7': '<a:loading7:1438606361448546324>',
			'loading8': '<a:loading8:1438606364535689376>',
			'loading9': '<a:loading9:1438606365798043708>',
			'loading10': '<a:loading10:1438606367584686212>',
			'loading11': '<a:loading11:1438606378120777808>',

		}

		# Object types
		song_obj_types = ['track', 'single']
		collection_obj_types = ['album', 'ep']
		music_video_types = ['music_video']
		knowledge_types = ['knowledge']
		snitch_types = ['analysis']

		# How to refer to a give piece of media
		refer_to = {
			'track': 'song',
			'single': 'song',
			'album': 'album',
			'ep': 'EP',
			'music_video': 'music video',
		}

		# Embed actions
		actions = {
			'searchsong': 'searched for',
			'searchalbum': 'searched for',
			'search': 'searched for',
			'lookup': 'searched for',
			'snoop': 'is listening to',
			'coverart': 'looked up cover art for',
			'link': 'sent a link to',
			'knowledge': 'searched for knowledge about'
		}

		# User metadata
		username = user.display_name
		user_pfp = user.display_avatar
		action = actions[command_type]

		async def song(json_response: dict, loading: bool = False):
			title = escape_markdown(json_response['title']) if censor == False else escape_markdown(json_response['censored_title']) # Get title
			title = f'{title}   `EXPLICIT`' if json_response['is_explicit'] == True else title # Add an explicit marker if the song is explicit
			artists = ', '.join([f'**{escape_markdown(artist['name'])}**' for artist in json_response['artists']]) # Get artists
			if 'collection' in json_response: # Get collection
				if json_response['collection'] != None:
					if json_response['type'] != 'single':
						collection = f'*{escape_markdown(json_response['collection']['title'])}*' if censor == False else f'*{escape_markdown(json_response['collection']['censored_title'])}*'
					else:
						collection = None
				else:
					collection = None
			else:
				collection = None
			genre = json_response['genre'] # Get genre
			confidence = f'`[{round(json_response['meta']['filter_confidence_percentage']['global_io'], 3)}%]`' if 'global_io' in json_response['meta']['filter_confidence_percentage'] else None
			desc_elements = [artists, collection, genre, confidence]
			while None in desc_elements: # Remove anything without a value
				desc_elements.remove(None)
			cover_url = None
			for service in service_metadata_priority: # Get cover art URL
				if service in json_response['cover']['hq_urls']:
					cover_url = json_response['cover']['hq_urls'][service]
					break
			color = await self.image_hex(cover_url) # Get color from average color in cover
			self.embed = Embed( # Basic embed data
				title = title,
				description = '  •  '.join(desc_elements),
				color = color
			)
			if anonymous == False: # Set author and action of the command (ex. 'sushi searched for:')
				self.embed.set_author(
					name = f'{username} {action}:',
					icon_url = user_pfp
				)
			else:
				self.embed.set_author( # Anonymous author and action for logging (ex. 'A user searched for:')
					name = f'A user {action}:',
					icon_url = text['images']['default_pfp']
				) 
			if command_type != 'coverart':
				self.embed.set_thumbnail( # Cover art but small
					url = cover_url
				)
			else:
				self.embed.set_image( # Cover art
					url = cover_url
				)
			if loading == False:
				for field in self.embed.fields:
					if field.value == 'Loading...':
						self.embed.remove_field(self.embed.fields.index(field))
				self.embed.set_footer( # Thanks and API latency report
					text = f'{text['embed']['tymsg']} • Done in {json_response['meta']['processing_time']['global_io']} ms',
					icon_url = text['images']['pfpurl']
				)
			else:
				self.embed.add_field(
					name = '',
					value = 'Loading...',
					inline = False
				)
			await self.service_buttons(json_response['urls']) # Get service button components

		async def music_video(json_response: dict, loading: bool = False):
			title = escape_markdown(json_response['title']) if censor == False else escape_markdown(json_response['censored_title']) # Get title
			title = f'{title}   `EXPLICIT`' if json_response['is_explicit'] == True else title # Add an explicit marker if the song is explicit
			artists = ', '.join([f'**{escape_markdown(artist['name'])}**' for artist in json_response['artists']]) # Get artists
			genre = json_response['genre'] # Get genre
			confidence = f'`[{round(json_response['meta']['filter_confidence_percentage']['global_io'], 3)}%]`' if 'global_io' in json_response['meta']['filter_confidence_percentage'] else None
			desc_elements = [artists, 'Music Video', genre, confidence]
			while None in desc_elements: # Remove anything without a value
				desc_elements.remove(None)
			cover_url = None
			for service in mv_thumbnail_priority: # Get cover art URL
				if service in json_response['cover']['hq_urls']:
					cover_url = json_response['cover']['hq_urls'][service]
					break
			color = await self.image_hex(cover_url) # Get color from average color in cover
			self.embed = Embed( # Basic embed data
				title = title,
				description = '  •  '.join(desc_elements),
				color = color
			)
			if anonymous == False: # Set author and action of the command (ex. 'sushi searched for:')
				self.embed.set_author(
					name = f'{username} {action}:',
					icon_url = user_pfp
				)
			else:
				self.embed.set_author( # Anonymous author and action for logging (ex. 'A user searched for:')
					name = f'A user {action}:',
					icon_url = text['images']['default_pfp']
				) 
			if command_type != 'coverart':
				self.embed.set_thumbnail( # Cover art but small
					url = cover_url
				)
			else:
				self.embed.set_image( # Cover art
					url = cover_url
				)
			if loading == False:
				for field in self.embed.fields:
					if field.value == 'Loading...':
						self.embed.remove_field(self.embed.fields.index(field))
				self.embed.set_footer( # Thanks and API latency report
					text = f'{text['embed']['tymsg']} • Done in {json_response['meta']['processing_time']['global_io']} ms',
					icon_url = text['images']['pfpurl']
				)
			else:
				self.embed.add_field(
					name = '',
					value = 'Loading...',
					inline = False
				)
			await self.service_buttons(json_response['urls'])
		
		async def collection(json_response: dict, loading: bool = False):
			title = escape_markdown(json_response['title']) if censor == False else escape_markdown(json_response['censored_title']) # Get title
			artists = ', '.join([f'**{escape_markdown(artist['name'])}**' for artist in json_response['artists']]) # Get artists
			year = json_response['release_year'] # Get release year
			genre = json_response['genre'] # Get genre
			confidence = f'`[{round(json_response['meta']['filter_confidence_percentage']['global_io'], 3)}%]`' if 'global_io' in json_response['meta']['filter_confidence_percentage'] else None
			desc_elements = [artists, year, genre, confidence] 
			while None in desc_elements: # Remove anything without a value
				desc_elements.remove(None)
			cover_url = None
			for service in service_metadata_priority: # Get cover art URL
				if service in json_response['cover']['hq_urls']:
					cover_url = json_response['cover']['hq_urls'][service]
					break
			color = await self.image_hex(cover_url) # Get color from average color in cover
			self.embed = Embed( # Basic embed data
				title = title,
				description = '  •  '.join(desc_elements),
				color = color
			)
			if anonymous == False: # Set author and action of the command (ex. 'sushi searched for:')
				self.embed.set_author(
					name = f'{username} {action}:',
					icon_url = user_pfp
				)
			else:
				self.embed.set_author( 
					name = f'A user {action}:',
					icon_url = text['images']['default_pfp']
				) 
			if command_type != 'coverart':
				self.embed.set_thumbnail( # Cover art but small
					url = cover_url
				)
			else:
				self.embed.set_image( # Cover art
					url = cover_url
				)
			if loading == False:
				for field in self.embed.fields:
					if field.value == 'Loading...':
						self.embed.remove_field(self.embed.fields.index(field))
				self.embed.set_footer( # Thanks and API latency report
					text = f'{text['embed']['tymsg']} • Done in {json_response['meta']['processing_time']['global_io']} ms',
					icon_url = text['images']['pfpurl']
				)
			else:
				self.embed.add_field(
					name = '',
					value = 'Loading...',
					inline = False
				)
			await self.service_buttons(json_response['urls'])

		async def knowledge(json_response: dict, loading: bool = False):
			title = escape_markdown(json_response['title']) if censor == False else escape_markdown(json_response['censored_title']) # Get title
			artists = ', '.join([f'**{escape_markdown(artist['name'])}**' for artist in json_response['artists']]) # Get artists
			if 'collection' in json_response: # Get collection
				if json_response['collection'] != None:
					if json_response['media_type'] != 'single':
						collection = f'*{escape_markdown(json_response['collection']['title'])}*' if censor == False else f'*{escape_markdown(json_response['collection']['censored_title'])}*'
					else:
						collection = None
				else:
					collection = None
			else:
				collection = None
			date = json_response['release_date'] # Get release date
			genre = json_response['genre'] # Get genre
			description = json_response['description'] if censor == False else json_response['censored_description'] # Get description
			description = description[:description.index('\n\n\n\n')] if description.find('\n\n\n\n') >= 0 else description # Cut out anything that is not the first paragraph of the description
			confidence = f'`[{round(json_response['meta']['filter_confidence_percentage']['global_io'], 3)}%]`' if 'global_io' in json_response['meta']['filter_confidence_percentage'] else None
			desc_elements = [artists, collection, date, genre, confidence]
			while None in desc_elements: # Remove anything without a value
				desc_elements.remove(None)
			for service in service_metadata_priority: # Get cover art
				if service in json_response['cover']['hq_urls']:
					cover_url = json_response['cover']['hq_urls'][service]
					break
			color = await self.image_hex(cover_url) # Get color from average color in cover
			self.embed = Embed( # Basic embed data
				title = title,
				description = '  •  '.join(desc_elements),
				color = color
			)
			if anonymous == False: # Set author and action of the command (ex. 'sushi searched for:')
				self.embed.set_author(
					name = f'{username} {action}:',
					icon_url = user_pfp
				)
			else:
				self.embed.set_author( # Anonymous author and action for logging (ex. 'A user searched for:')
					name = f'A user {action}:',
					icon_url = text['images']['default_pfp']
				) 
			if command_type != 'coverart':
				self.embed.set_thumbnail( # Cover art but small
					url = cover_url
				)
			else:
				self.embed.set_image( # Cover art
					url = cover_url
				)
			self.embed.add_field( # Add description
					name = '',
					value = description,
					inline = False
				)
			if loading == False:
				for field in self.embed.fields:
					if field.value == 'Loading...':
						self.embed.remove_field(self.embed.fields.index(field))
				self.embed.set_footer( # Thanks and API latency report
					text = f'{text['embed']['tymsg']} • Done in {json_response['meta']['processing_time']['global_io']} ms',
					icon_url = text['images']['pfpurl']
				)
			else:
				self.embed.add_field(
					name = '',
					value = 'Loading...',
					inline = False
				)
			await self.service_buttons(json_response['urls'])

		async def analysis(json_response: dict):
			if json_response['analysed_media']['type'] in song_obj_types:
				await song(json_response['analysed_media'], False)
			
			elif json_response['analysed_media']['type'] in music_video_types:
				await music_video(json_response['analysed_media'], False)
			
			elif json_response['analysed_media']['type'] in collection_obj_types:
				await collection(json_response['analysed_media'], False)
			
			elif json_response['analysed_media']['type'] in knowledge_types:
				await knowledge(json_response['analysed_media'], False)


			analysis_string = ''

			for analysis in json_response['analysis']:
				media_type = ''
				analysed_media_type = ''
				if analysis['ai_generated_confidence'] >= 50.0:
					if analysis['media_type'] == 'audio':
						media_type = 'audio'
					elif analysis['media_type'] == 'image':
						media_type = 'cover art'

					if json_response['analysed_media']['type'] in song_obj_types:
						analysed_media_type = 'song'
					elif json_response['analysed_media']['type'] in collection_obj_types:
						if json_response['analysed_media']['type'] == 'eop':
							analysed_media_type = 'EP'
						else:
							analysed_media_type = 'album'
					elif json_response['analysed_media']['type'] in music_video_types:
						analysed_media_type = 'music video'
					elif json_response['analysed_media']['type'] in knowledge_types:
						if json_response['analysed_media']['media_type'] in song_obj_types:
							analysed_media_type = 'song'
						elif json_response['analysed_media']['media_type'] in collection_obj_types:
							if json_response['analysed_media']['media_type'] == 'eop':
								analysed_media_type = 'EP'
							else:
								analysed_media_type = 'album'
						elif json_response['analysed_media']['media_type'] in music_video_types:
							analysed_media_type = 'music video'
					analysis_string += f"- There is a large probability this {analysed_media_type}'s {media_type} has been AI-generated • `[{round(analysis['ai_generated_confidence'], 3)}%]`\n"
			if analysis_string != '':
				# Only add the field if one with the same name doesn't already exist
				if not any(field.name == 'Generative AI report' for field in self.embed.fields):
					self.embed.add_field(
						name = 'Generative AI report',
						value = f'{analysis_string}-# Powered by Astro Snitch. Analysis may not be 100% accurate.',
						inline = False
					)
			for field in self.embed.fields:
				if field.value == 'Loading...':
					self.embed.remove_field(self.embed.fields.index(field))
			self.embed.set_footer( # Thanks and API latency report
				text = f'{text['embed']['tymsg']} • Done in {json_response['analysed_media']['meta']['processing_time']['global_io']} ms',
				icon_url = text['images']['pfpurl']
			)
		
		# Embed composing
		if 'type' in json_response:
			if json_response['type'] in song_obj_types: # If the media object is a song
				await song(json_response, loading = loading)
			
			elif json_response['type'] in music_video_types: # If the media object is a music video
				await music_video(json_response, loading = loading)
			
			elif json_response['type'] in collection_obj_types: # If the media object is a collection
				await collection(json_response, loading = loading)
			
			elif json_response['type'] in knowledge_types: # If the media object is a knowledge object
				await knowledge(json_response, loading = loading)

			elif json_response['type'] in snitch_types: # If the media object is an Astro Snitch analysis object
				await analysis(json_response)
		
		

	async def service_buttons(self, urls: dict):
		"""
			Create Discord component buttons for each service URL.
		"""
		url_services =  list(urls.keys())
		self.button_view = View()

		for service in url_services:
			self.button_view.add_item(
				Button(
					style = ButtonStyle.link,
					url = urls[service],
					emoji = text['emoji'][service]
				)
			)
	
	async def image_hex(self, image_url: str, quality: int = 5):
		"""
			Get the average color of cover art and return its hex value.
		"""
		async with aiohttp.ClientSession() as session:
			async with session.get(url = image_url) as response: # Open the image URL and check if it's legitimate
				if response.status == 200:
					image_bytes = await response.read() # Read the image file
					image = Image.open(BytesIO(image_bytes)) # Open the image file

					# Get image specs
					width, height = image.size
					# Resize the image
					new_width = width // quality
					new_height = height // quality
					image = image.resize((new_width, new_height))

					# Convert to RGB values
					pixels = image.convert('RGB').getdata()
					# Get average color
					average_color = np.mean(pixels, axis = 0).astype(int)

					# Create a hex string
					hex_color = '#{:02x}{:02x}{:02x}'.format(*average_color)
					# Return as base 16 integer
					return int(hex_color[1:], base = 16)
				else:
					# If the image link is invalid, return Astro's signature yellow
					return 0xf5c000