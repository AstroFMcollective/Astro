from discord import Embed, User, Member, ButtonStyle
from discord.ui import Button, View
from discord.utils import escape_markdown
from AstroDiscord.components.ini import text

class EmbedComposer:
	def __init__(self):
		pass
	
	async def compose(self, user: User | Member, json_response: dict, command_type: str, anonymous: bool = False, censor: bool = False):
		# Order in which to read the metadata from multiple services
		service_metadata_priority = ['spotify','apple_music','youtube_music','deezer','genius']
		cover_art_priority = ['genius','spotify','deezer','youtube_music','apple_music']
		mv_thumbnail_priority = ['youtube_music', 'apple_music']

		# Object types
		song_obj_types = ['track', 'single']
		collection_obj_types = ['album', 'ep']
		music_video_types = ['music_video']
		knowledge_types = ['knowledge']

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
			'coverart': 'looked up cover art for'
		} 

		# User metadata
		username = user.display_name
		user_pfp = user.display_avatar
		action = actions[command_type]

		# Embed composing
		if json_response['type'] in song_obj_types: # If the media object is a song
			title = escape_markdown(json_response['title']) if censor == False else escape_markdown(json_response['censored_title']) # Get title
			title = f'{title} `E`' if json_response['is_explicit'] == True else title # Add an explicit market if the song is explicit
			artists = ', '.join([f'**{escape_markdown(artist['name'])}**' for artist in json_response['artists']]) # Get artists
			collection = f'*{json_response['collection']['title']}*' if json_response['type'] != 'single' else None # Get collection if found
			genre = json_response['genre'] # Get genre
			desc_elements = [artists, collection, genre]
			while None in desc_elements: # Remove anything without a value
				desc_elements.remove(None)
			color = 0x00b0f4 # Placeholder blue
			cover_url = None
			for service in service_metadata_priority: # Get cover art URL
				if service in json_response['cover']['hq_urls']:
					cover_url = json_response['cover']['hq_urls'][service]
					break
			self.embed = Embed( # Basic embed data
				title = title,
				description = '  •  '.join(desc_elements),
				color = color
			)
			if anonymous == False: # Set author and action of the command (ex. "sushi searched for:")
				self.embed.set_author(
					name = f'{username} {action}:',
					icon_url = user_pfp
				)
			else:
				self.embed.set_author( # Anonymous author and action for logging (ex. "A user searched for:")
					name = f'A user {action}:',
					icon_url = text['images']['default_pfp']
				) 
			if command_type != 'coverart':
				self.embed.set_thumbnail( # Cover art
					url = cover_url
				)
			else:
				self.embed.set_image( # Cover art but small
					url = cover_url
				)
			self.embed.set_footer( # Thanks and API latency report
				text = f'{text['embed']['tymsg']} • Done in {json_response['meta']['processing_time']['global_io']} ms',
				icon_url = text['images']['pfpurl']
			)
			if command_type == 'lookup': # Temporary notice for people using the /lookup command
				self.embed.add_field(
					name = 'Important notice',
                	value = '`/lookup` is getting deprecated starting with Astro 2.3.1, please use `/search` instead. Thank you!',
                	inline = False
				)
			await self.service_buttons(json_response['urls']) # Get service button components
		
		if json_response['type'] in music_video_types:
			title = escape_markdown(json_response['title']) if censor == False else escape_markdown(json_response['censored_title'])
			title = f'{title} `E`' if json_response['is_explicit'] == True else title
			artists = ', '.join([f'**{escape_markdown(artist['name'])}**' for artist in json_response['artists']])
			genre = json_response['genre']
			desc_elements = [artists, 'Music Video', genre]
			while None in desc_elements: # Remove anything without a value
				desc_elements.remove(None)
			color = 0x00b0f4 # Placeholder blue
			cover_url = None
			for service in mv_thumbnail_priority:
				if service in json_response['cover']['hq_urls']:
					cover_url = json_response['cover']['hq_urls'][service]
					break
			self.embed = Embed(
				title = title,
				description = '  •  '.join(desc_elements),
				color = color
			)
			if anonymous == False:
				self.embed.set_author(
					name = f'{username} {action}:',
					icon_url = user_pfp
				)
			else:
				self.embed.set_author(
					name = f'A user {action}:',
					icon_url = text['images']['default_pfp']
				) 
			self.embed.set_image(
				url = cover_url
			)
			self.embed.set_footer(
				text = f'{text['embed']['tymsg']} • Done in {json_response['meta']['processing_time']['global_io']} ms',
				icon_url = text['images']['pfpurl']
			)
			if command_type == 'lookup':
				self.embed.add_field(
					name = 'Important notice',
                	value = '`/lookup` is getting deprecated starting with Astro 2.3.1, please use `/search` instead. Thank you!',
                	inline = False
				)
			await self.service_buttons(json_response['urls'])
		 
		elif json_response['type'] in collection_obj_types:
			title = escape_markdown(json_response['title']) if censor == False else escape_markdown(json_response['censored_title'])
			artists = ', '.join([f'**{escape_markdown(artist['name'])}**' for artist in json_response['artists']])
			year = json_response['release_year']
			genre = json_response['genre']
			desc_elements = [artists, year, genre]
			while None in desc_elements: # Remove anything without a value
				desc_elements.remove(None)
			color = 0x00b0f4 # Placeholder blue
			for service in service_metadata_priority:
				if service in json_response['cover']['hq_urls']:
					cover_url = json_response['cover']['hq_urls'][service]
					break
			self.embed = Embed(
				title = title,
				description = '  •  '.join(desc_elements),
				color = color
			)
			if anonymous == False:
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
				self.embed.set_thumbnail( # Cover art
					url = cover_url
				)
			else:
				self.embed.set_image( # Cover art but small
					url = cover_url
				)
			self.embed.set_footer(
				text = f'{text['embed']['tymsg']} • Done in {json_response['meta']['processing_time']['global_io']} ms',
				icon_url = text['images']['pfpurl']
			)
			await self.service_buttons(json_response['urls'])
		
		elif json_response['type'] in knowledge_types:
			title = escape_markdown(json_response['title']) if censor == False else escape_markdown(json_response['censored_title'])
			artists = ', '.join([f'**{escape_markdown(artist['name'])}**' for artist in json_response['artists']])
			if 'collection' in json_response:
				if json_response['collection'] != None:
					collection = f'*{escape_markdown(json_response['collection']['title'])}*' if censor == False else escape_markdown(json_response['collection']['censored_title'])
			date = json_response['release_date']
			genre = json_response['genre']
			description = json_response['description'] if censor == False else json_response['censored_description']
			desc_elements = [artists, collection, date, genre]
			while None in desc_elements: # Remove anything without a value
				desc_elements.remove(None)
			color = 0x00b0f4 # Placeholder blue
			for service in service_metadata_priority:
				if service in json_response['cover']['hq_urls']:
					cover_url = json_response['cover']['hq_urls'][service]
					break
			self.embed = Embed(
				title = title,
				description = '  •  '.join(desc_elements),
				color = color
			)
			if anonymous == False:
				self.embed.set_author(
					name = f'{username} {action}:',
					icon_url = user_pfp
				)
			else:
				self.embed.set_author(
					name = f'A user {action}:',
					icon_url = text['images']['default_pfp']
				) 
			self.embed.set_image( # Cover art but small
				url = cover_url
			)
			self.embed.add_field(
					name = '',
                	value = description,
                	inline = False
				)
			self.embed.set_footer(
				text = f'{text['embed']['tymsg']} • Done in {'time'} ms',
				icon_url = text['images']['pfpurl']
			)
			await self.service_buttons(json_response['urls'])

	async def service_buttons(self, urls: dict):
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