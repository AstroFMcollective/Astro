from discord import Embed, User, Member, ButtonStyle
from discord.ui import Button, View
from discord.utils import escape_markdown
from AstroDiscord.components.ini import text

class EmbedComposer:
	def __init__(self):
		pass
	
	async def compose(self, user: User | Member, json_response: dict, command_type: str, anonymous: bool = False):
		# Order in which to read the metadata from multiple services
		service_metadata_priority = ['spotify','apple_music','youtube_music','deezer','genius']
		song_obj_types = ['track', 'single']
		collection_obj_types = ['album', 'ep']
		music_video_types = ['music_video']
		knowledge_types = ['knowledge']

		refer_to = {
			'track': 'song',
			'single': 'song',
			'album': 'album',
			'ep': 'EP',
			'music_video': 'music video',
		}

		actions = {
			'searchsong': 'searched',
			'searchalbum': 'searched',
			'lookup': 'looked up',
			'snoop': 'is listening to',
			'coverart': 'looked up cover art'
		} 

		username = user.display_name
		user_pfp = user.display_avatar
		action = actions[command_type]

		if json_response['type'] in song_obj_types:
			title = escape_markdown(json_response['title'])
			artists = ', '.join([f'**{escape_markdown(artist['name'])}**' for artist in json_response['artists']])
			collection = f'*{json_response['collection']['title']}*' if json_response['type'] != 'single' else None
			genre = json_response['genre']
			desc_elements = [artists, collection, genre]
			for element in desc_elements:
				if element == None:
					desc_elements.remove(None)
			color = 0x00b0f4 # Placeholder blue
			cover_url = None
			for service in service_metadata_priority:
				if service in json_response['cover']['hq_urls']:
					cover_url = json_response['cover']['hq_urls'][service]
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
			self.embed.set_thumbnail(
				url = cover_url
			)
			self.embed.set_footer(
				text = f'{text['embed']['tymsg']} • Done in TIME ms',
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