import discord as discord
from AstroDiscord.components.ini import text



class Embed:
	def __init__(self, command: str, media_object: object, user: object, censored: bool = False):
		self.custom_errors = [
			text['error']['no_spotify_you'],
			text['error']['no_spotify_someone'],
			text['error']['invalid_link'],
			text['error']['no_links_detected'],
		]

		if media_object.type != 'empty_response' and media_object.type != 'error':
			self.cover = media_object.cover_url if media_object.type != 'music_video' else media_object.thumbnail_url
			self.embed_color = media_object.cover_color_hex if media_object.type != 'music_video' else media_object.thumbnail_color_hex

		self.embed = self.create_embed(command = command, media_object = media_object, user = user, censored = censored, anonymous = False)
		self.log_embed = self.create_embed(command = command, media_object = media_object, user = user, censored = False, anonymous = True)

	

	def create_embed(self, command: str, media_object: object, user: object, censored: bool, anonymous: bool):
		if media_object.type == 'empty_response' or media_object.type == 'error':
			embed = discord.Embed(
				title = text['error']['title'],
				color = 0xf5c000
			)

			if media_object.type == 'error':
				if media_object.error_msg in self.custom_errors:
					error_msg = media_object.error_msg
				else:
					error_msg = text['error']['generic'] if media_object.type == 'error' else text['error']['empty_response']
			
			if media_object.type == 'empty_response':
				error_msg = text['error']['empty_response']

			embed.add_field(
				name = '',
				value = error_msg,
				inline = False
			)
				
			embed.set_footer(
				text = text['embed']['tymsg'],
				icon_url = text['images']['pfpurl']
			)

			return embed
		
		if len(media_object.url) == 1 and command == 'link':
			return
		
		data = [f'**{discord.utils.escape_markdown(', '.join(media_object.artists))}**']
		is_explicit = None

		if media_object.type == 'track':
			if media_object.collection != None:
				data.append(f'{discord.utils.escape_markdown(media_object.collection)}')
			is_explicit = media_object.is_explicit
		elif media_object.type == 'single':
			data.append('Single')
			is_explicit = media_object.is_explicit
		elif media_object.type == 'music_video':
			data.append('Music video')
			is_explicit = media_object.is_explicit
		elif media_object.type == 'album' or media_object.type == 'ep':
			data.append(str(media_object.release_year))
		elif media_object.type == 'knowledge':
			if media_object.media_type == 'single':
				data.append('Single')
			else:
				if media_object.collection != None:
					data.append(f'{discord.utils.escape_markdown(media_object.collection)}')
			is_explicit = media_object.is_explicit
			data.append(str(media_object.release_date))
			
		embed = discord.Embed(
			title = f'{f'{discord.utils.escape_markdown(media_object.title)}'}  {'`E`' if is_explicit != None and is_explicit != False else ''}',
			description = f'{' • '.join(data)}',
			color = self.embed_color
		)

		

		if anonymous == False:
			embed.set_author(
				name = text['embed'][command].replace('USER',f'@{user.name}'),
				icon_url = user.avatar
			)
		else:
			embed.set_author(
				name = text['embed'][command].replace('USER',f'@USER'),
				icon_url = text['images']['default_pfp']
			)
		
		if media_object.type == 'knowledge':
			if media_object.description != None:
				embed.add_field(
					name = '',
					value = media_object.description,
					inline = False
				)

		if command != 'cover':
			embed.add_field(
				name = text['embed'][media_object.type],
				value = self.create_anchor(media_object),
				inline = False
			)
			
			
		if media_object.type == 'music_video' or media_object.type == 'knowledge' or command == 'cover':
			embed.set_image(
				url = self.cover
			)
		else:
			embed.set_thumbnail(
				url = self.cover
			)

		embed.set_footer(
			text = text['embed']['tymsg'],
			icon_url = text['images']['pfpurl']
		)

		return embed
	
	def create_anchor(self, media_object: object):
		anchor = []
		urls = media_object.url
		for url in urls:
			anchor.append(text['anchor'][url].replace('URL', urls[url]).replace('NOTEXT',''))
		return '\n'.join(anchor)
