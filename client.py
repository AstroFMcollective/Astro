import discord as discord 
from discord import app_commands
from discord import Spotify
from discord.ext import tasks

from random import randint
from asyncio import *

from AstroDiscord.components.ini import config, tokens, presence, stats
from AstroDiscord.components import *
from AstroDiscord.components.url_tools import url_tools
from AstroDiscord.components.time import current_unix_time



class Client(discord.AutoShardedClient):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.synced = False
	


api = AstroAPI()
version = config['client']['version']
service = 'discord'
component = 'Discord Client'
deployment_channel = config['client']['deployment_channel']
intents = discord.Intents.all()
intents.message_content = True
intents.presences = True
intents.members = True
app_start_time = current_unix_time()
client = Client(shard_count = int(config['client']['shards']), intents = intents)
tree = app_commands.CommandTree(client)
invalid_responses = [
	'empty_response',
	'error'
]



@client.event
async def on_ready():
	await client.wait_until_ready()
	if not client.synced:
		await tree.sync()
		client.synced = True
	if not discord_presence.is_running():
		discord_presence.start()
	if not dashboard.is_running():
		dashboard.start()
	if not reset_today_stats.is_running():
		reset_today_stats.start()
	print('[AstroDiscord] Ready!')
	


@client.event
async def on_message(message):
	start_time = current_unix_time_ms()

	async def auto_link_lookup(data):
		embed_composer = EmbedComposer()

		response = await message.reply(embed = embed_composer.generic_loading, mention_author = False)

		self_object = await api.get_self(
			data['type'],
			data['id'],
			data['service'],
			data['country_code']
		)

		if 'type' in self_object:
			# First stage - Get baseline data of the music object
			await embed_composer.compose(message.author, self_object, 'link', False, False, True)
			response = await response.edit(embed = embed_composer.embed, view = embed_composer.button_view)

			# Second stage - Get Global Interface data of the music object
			global_object = await api.lookup(
				data['type'],
				data['id'],
				data['service'],
				data['country_code']
			)

			if 'type' in global_object:
				await embed_composer.compose(message.author, global_object, 'link', False, False, True)
				response = await response.edit(embed = embed_composer.embed, view = embed_composer.button_view)

				# Third stage - Check music object for generative AI
				ai_check = await api.snitch(
					global_object
				)

				if 'type' in ai_check:
					await embed_composer.compose(message.author, ai_check, 'link', False, False)
					response = await response.edit(embed = embed_composer.embed, view = embed_composer.button_view)
					successful_request()
					api_latency(self_object['meta']['processing_time'][data['service']] + global_object['meta']['processing_time']['global_io'] + ai_check['meta']['processing_time']['global_io'])
					await embed_composer.compose(message.author, ai_check, 'link', True, False)
					await log(
						[embed_composer.embed],
						[ai_check],
						'Auto Link Lookup',
						f'type:`{data['type']}` id:`{data['id']}` service:`{data['service']}` country_code:`{data['country_code']}`',
						current_unix_time_ms() - start_time, 
						embed_composer.button_view
					)
				else:
					await embed_composer.compose(message.author, global_object, 'link', False, False)
					response = await response.edit(embed = embed_composer.embed, view = embed_composer.button_view)
					successful_request()
					api_latency(self_object['meta']['processing_time'][data['service']] + global_object['meta']['processing_time']['global_io'])
					await embed_composer.compose(message.author, global_object, 'link', True, False)
					await log(
						[embed_composer.embed],
						[global_object],
						'Auto Link Lookup',
						f'type:`{data['type']}` id:`{data['id']}` service:`{data['service']}` country_code:`{data['country_code']}`',
						current_unix_time_ms() - start_time, 
						embed_composer.button_view
					)
			else:
				failed_request()
				await message.delete()
				await log_catastrophe('Auto Link Lookup', f'type:`{data['type']}` id:`{data['id']}` service:`{data['service']}` country_code:`{data['country_code']}`', 'HTTP error when talking to Astro API (Global stage)')

		else:
			failed_request()
			await log_catastrophe('Auto Link Lookup', f'type:`{data['type']}` id:`{data['id']}` service:`{data['service']}` country_code:`{data['country_code']}`', 'HTTP error when talking to Astro API (Baseline stage)')



	if message.author != client.user:
		try:
			media_data = []
			urls = await url_tools.get_urls_from_string(message.content)
			for url in urls:
				metadata = await url_tools.get_metadata_from_url(url)
				if metadata != None:
					media_data.append(metadata)
			if media_data != []:
				tasks = []
				for data in media_data:
					if data['id'] != None and data['type'] != None:
						tasks.append(
							create_task(
								auto_link_lookup(data)
							)
						)
				await gather(*tasks)
			else: 
				return
		except Exception as error:
			failed_request()
			await log_catastrophe('Auto Link Lookup', f'urls:`{await url_tools.get_urls_from_string(message.content)}`', error)
		client_latency(current_unix_time_ms() - start_time)



@tree.command(name = 'searchsong', description = 'Search for a song on all major platforms')
@app_commands.describe(artist = 'The name of the artist of the song you want to search (ex. "Tyler, The Creator")')
@app_commands.describe(title = 'The title of the song you want to search (ex. "NEW MAGIC WAND")')
@app_commands.describe(from_album = 'The album, EP or collection of the song you want to search, helps with precision (ex. "IGOR")')
@app_commands.describe(is_explicit = 'Whether the song you want to search has explicit content (has the little [E] badge next to its name on streaming platforms), helps with precision')
@app_commands.describe(country_code = 'The country code of the country in which you want to search, US by default')
@app_commands.describe(censor = 'Whether you want to censor the title of the song or not, False by default and forced True for User Apps')
@discord.app_commands.allowed_installs(guilds = True, users = True)
@app_commands.allowed_contexts(guilds = True, dms = True, private_channels = True)
async def searchsong(interaction: discord.Interaction, artist: str, title: str, from_album: str = None, is_explicit: bool = None, country_code: str = 'us', censor: bool = False):
	start_time = current_unix_time_ms()
	if app_commands.AppInstallationType.user == True:
		censor = True
	await interaction.response.defer()
	embed_composer = EmbedComposer()
	try:
		json = await api.search_song(artist, title, from_album, is_explicit, country_code)
		if 'type' in json:
			await embed_composer.compose(interaction.user, json, 'searchsong', False, censor, True)
			response = await interaction.followup.send(embed = embed_composer.embed, view = embed_composer.button_view)

			ai_report = await api.snitch(json)
			await embed_composer.compose(interaction.user, ai_report, 'searchsong', False, censor)
			await response.edit(embed = embed_composer.embed, view = embed_composer.button_view)
			
			successful_request()
			api_latency(json['meta']['processing_time']['global_io'] + ai_report['meta']['processing_time']['global_io'])
		elif json == {}:
			await embed_composer.error(204)
			await interaction.followup.send(embed = embed_composer.embed)
			failed_request()
		else:
			await embed_composer.error(json['status'])
			await interaction.followup.send(embed = embed_composer.embed)
			failed_request()
		await embed_composer.compose(interaction.user, ai_report, 'searchsong', True, censor)
		await log(
			[embed_composer.embed],
			[json],
			'searchsong',
			f'artist:`{artist}` title:`{title}` from_album:`{from_album}` is_explicit:`{is_explicit}` country_code:`{country_code}` censor:`{censor}`',
			current_unix_time_ms() - start_time,
			embed_composer.button_view
		)
	except Exception as error:
		await embed_composer.error('other')
		await interaction.followup.send(embed = embed_composer.embed)
		failed_request()
		await log_catastrophe(
			'searchsong',
			f'artist:`{artist}` title:`{title}` from_album:`{from_album}` is_explicit:`{is_explicit}` country_code:`{country_code}` censor:`{censor}`',
			error
		)
	client_latency(current_unix_time_ms() - start_time)



@tree.command(name = 'searchalbum', description = 'Search for an album')
@app_commands.describe(artist = 'The artist of the album you want to search (ex. "Kendrick Lamar")')
@app_commands.describe(title = 'The title of the album you want to search (ex. "To Pimp A Butterfly")')
@app_commands.describe(year = 'The release year of the album you want to search, helps with precision (ex. "2015")')
@app_commands.describe(country_code = 'The country code of the country in which you want to search, US by default')
@app_commands.describe(censor = 'Whether you want to censor the title of the song or not, False by default and forced True for User Apps')
@discord.app_commands.allowed_installs(guilds = True, users = True)
@app_commands.allowed_contexts(guilds = True, dms = True, private_channels = True)
async def searchalbum(interaction: discord.Interaction, artist: str, title: str, year: int = None, country_code: str = 'us', censor: bool = False, loading: bool = False):
	start_time = current_unix_time_ms()
	if app_commands.AppInstallationType.user == True:
		censor = True
	await interaction.response.defer()
	embed_composer = EmbedComposer()
	try:
		json = await api.search_album(artist, title, year, country_code)
		if 'type' in json:
			await embed_composer.compose(interaction.user, json, 'searchalbum', False, censor, True)
			response = await interaction.followup.send(embed = embed_composer.embed, view = embed_composer.button_view)

			ai_report = await api.snitch(json)
			await embed_composer.compose(interaction.user, ai_report, 'searchalbum', False, censor)
			await response.edit(embed = embed_composer.embed, view = embed_composer.button_view)

			successful_request()
			api_latency(json['meta']['processing_time']['global_io'] + ai_report['meta']['processing_time']['global_io'])
		elif json == {}:
			await embed_composer.error(204)
			await interaction.followup.send(embed = embed_composer.embed)
			failed_request()
		else:
			await embed_composer.error(json['status'])
			await interaction.followup.send(embed = embed_composer.embed)
			failed_request()
		await embed_composer.compose(interaction.user, ai_report, 'searchalbum', True, censor)
		await log(
			[embed_composer.embed],
			[json],
			'searchalbum',
			f'artist:`{artist}` title:`{title}` year:`{year}` country_code:`{country_code}` censor:`{censor}`',
			current_unix_time_ms() - start_time,
			embed_composer.button_view
		)
	except Exception as error:
		await embed_composer.error('other')
		await interaction.followup.send(embed = embed_composer.embed)
		failed_request()
		await log_catastrophe(
			'searchalbum',
			f'artist:`{artist}` title:`{title}` year:`{year}` country_code:`{country_code}` censor:`{censor}`',
			error
		)
	client_latency(current_unix_time_ms() - start_time)



@tree.command(name = 'search', description = 'Search a song, music video, album or EP from a query or its link')
@app_commands.describe(query = 'Search query or the link of the media you want to search')
@app_commands.describe(country_code = 'The country code of the country in which you want to search, US by default')
@app_commands.describe(censor = 'Whether you want to censor the title of the song or not, False by default and forced True for User Apps')
@discord.app_commands.allowed_installs(guilds = True, users = True)
@app_commands.allowed_contexts(guilds = True, dms = True, private_channels = True)
async def search(interaction: discord.Interaction, query: str, country_code: str = 'us', censor: bool = False):
	start_time = current_unix_time_ms()
	json = {}
	if app_commands.AppInstallationType.user == True:
		censor = True
	await interaction.response.defer()
	embed_composer = EmbedComposer()
	try:
		metadata = await url_tools.get_metadata_from_url(query)
		if metadata == None or metadata['id'] == None and metadata['type'] == None:
			json = await api.search(query, country_code)
		else:
			json = await api.lookup(metadata['type'], metadata['id'], metadata['service'], country_code)
		if 'type' in json:
			await embed_composer.compose(interaction.user, json, 'search', False, censor, True)
			response = await interaction.followup.send(embed = embed_composer.embed, view = embed_composer.button_view)

			ai_report = await api.snitch(json)
			await embed_composer.compose(interaction.user, ai_report, 'search', False, censor)
			await response.edit(embed = embed_composer.embed, view = embed_composer.button_view)

			successful_request()
			api_latency(json['meta']['processing_time']['global_io'] + ai_report['meta']['processing_time']['global_io'])
		elif json == {}:
			await embed_composer.error(204)
			await interaction.followup.send(embed = embed_composer.embed)
			failed_request()
		else:
			await embed_composer.error(json['status'])
			await interaction.followup.send(embed = embed_composer.embed)
			failed_request()
		await embed_composer.compose(interaction.user, ai_report, 'search', True, censor)
		await log(
			[embed_composer.embed],
			[json],
			'search',
			f'query:`{query}` country_code:`{country_code}` censor:`{censor}`',
			current_unix_time_ms() - start_time,
			embed_composer.button_view
		)
	except Exception as error:
		await embed_composer.error('other')
		await interaction.followup.send(embed = embed_composer.embed)
		failed_request()
		print(f'[AstroDiscord] Undocumented error in search has occurred: {error}')
	client_latency(current_unix_time_ms() - start_time)



@tree.command(name = 'snoop', description = "Get yours or someone else's currently playing song on Spotify")
@app_commands.describe(user = 'The user you want to snoop on, defaults to you if left empty')
@app_commands.describe(ephemeral = 'Whether the executed command should be ephemeral (only visible to you), false by default')
@app_commands.describe(country_code = 'The country code of the country in which you want to search, US by default')
@app_commands.describe(censor = 'Whether you want to censor the title of the song or not, False by default and forced True for User Apps')
@discord.app_commands.allowed_installs(guilds = True, users = False)
@app_commands.allowed_contexts(guilds = True, dms = False, private_channels = True)
async def snoop(interaction: discord.Interaction, user: discord.Member = None, ephemeral: bool = False, country_code: str = 'us', censor: bool = False):
	start_time = current_unix_time_ms()
	json = {}
	if app_commands.AppInstallationType.user == True:
		censor = True
	await interaction.response.defer(ephemeral = ephemeral)
	try:
		embed_composer = EmbedComposer()
		if user == None:
			user = interaction.user
		identifier = None

		guild = client.get_guild(interaction.guild.id)
		member = guild.get_member(user.id)

		for activity in member.activities:
			if isinstance(activity, Spotify):
				identifier = str(activity.track_id)
				break
		
		if identifier == None:
			person = 'You are' if interaction.user == user else 'This person is'
			grammar = 'have' if interaction.user == user else 'has'
			await embed_composer.error(400, {
				'title': "No Spotify listening activity detected.",
				'description': f'{person} not listening to a Spotify track, or {grammar} Spotify activity disabled in Discord settings. [Learn here](https://support.discord.com/hc/en-us/articles/360000167212-Discord-Spotify-Connection) how to connect Spotify to Discord and enable Spotify activity on your profile.',
				'meaning': 'Bad request'
			})
			await interaction.followup.send(embed = embed_composer.embed)
			failed_request()
		else:
			json = await api.lookup('song', identifier, 'spotify', country_code)	
			if 'type' in json:
				await embed_composer.compose(user, json, 'snoop', False, censor, True)
				response = await interaction.followup.send(embed = embed_composer.embed, view = embed_composer.button_view)

				ai_report = await api.snitch(json)
				await embed_composer.compose(interaction.user, ai_report, 'snoop', False, censor)
				await response.edit(embed = embed_composer.embed, view = embed_composer.button_view)

				successful_request()
				api_latency(json['meta']['processing_time']['global_io'] + ai_report['meta']['processing_time']['global_io'])
			elif json == {}:
				await embed_composer.error(204)
				await interaction.followup.send(embed = embed_composer.embed)
				failed_request()
			else:
				await embed_composer.error(json['status'])
				await interaction.followup.send(embed = embed_composer.embed)
				failed_request()
		await embed_composer.compose(user, json, 'snoop', True, censor)
		await log(
			[embed_composer.embed],
			[json],
			'snoop',
			f'user:`{'self' if user == interaction.user else 'member'}` ephemeral:`{ephemeral}` country_code:`{country_code}` censor:`{censor}`',
			current_unix_time_ms() - start_time,
			embed_composer.button_view
		)
	except Exception as error:
		await embed_composer.error('other')
		await interaction.followup.send(embed = embed_composer.embed)
		failed_request()
		await log_catastrophe(
			'snoop',
			f'user:`{'self' if user == interaction.user else 'member'}` ephemeral:`{ephemeral}` country_code:`{country_code}` censor:`{censor}`',
			error
		)
	client_latency(current_unix_time_ms() - start_time)



@tree.command(name = 'coverart', description = 'Get the cover art of a song or album')
@app_commands.describe(link = 'The link of the track or album you want to retrieve the cover art from')
@app_commands.describe(country_code = 'The country code of the country in which you want to search, US by default')
@app_commands.describe(censor = 'Whether you want to censor the title of the song or not, False by default and forced True for User Apps')
@discord.app_commands.allowed_installs(guilds = True, users = True)
@app_commands.allowed_contexts(guilds = True, dms = True, private_channels = True)
async def coverart(interaction: discord.Interaction, link: str, country_code: str = 'us', censor: bool = False):
	start_time = current_unix_time_ms()
	json = {}
	if app_commands.AppInstallationType.user == True:
		censor = True
	await interaction.response.defer()
	embed_composer = EmbedComposer()
	try:
		metadata = await url_tools.get_metadata_from_url(link)
		if metadata != None:
			if metadata == None or metadata['id'] != None and metadata['type'] != None:
				json = await api.lookup(metadata['type'], metadata['id'], metadata['service'], metadata['country_code'])
				if 'type' in json:
					await embed_composer.compose(interaction.user, json, 'coverart', False, censor, True)
					response = await interaction.followup.send(embed = embed_composer.embed, view = embed_composer.button_view)

					ai_report = await api.snitch(json)
					await embed_composer.compose(interaction.user, ai_report, 'coverart', False, censor)
					await response.edit(embed = embed_composer.embed, view = embed_composer.button_view)

					successful_request()
					api_latency(json['meta']['processing_time']['global_io'] + ai_report['meta']['processing_time']['global_io'])
				elif json == {}:
					await embed_composer.error(204)
					await interaction.followup.send(embed = embed_composer.embed)
					failed_request()
				else:
					await embed_composer.error(json['status'])
					await interaction.followup.send(embed = embed_composer.embed)
					failed_request()
			else:
				await embed_composer.error(400, {
					'title': "Invalid link provided.",
					'description': f'This command only works with songs, albums, EP-s and music videos from Spotify, Apple Music, YouTube (Music), and Deezer.',
					'meaning': 'Bad request'
				})
				await interaction.followup.send(embed = embed_composer.embed)
				failed_request()
			await embed_composer.compose(interaction.user, json, 'coverart', True, censor)
			await log(
				[embed_composer.embed],
				[json],
				'coverart',
				f'link:`{link}` country_code:`{country_code}` censor:`{censor}`',
				current_unix_time_ms() - start_time,
				embed_composer.button_view
			)
		else:
			await embed_composer.error(400, {
				'title': "Invalid link provided.",
				'description': f'This command only works with songs, albums, EP-s and music videos from Spotify, Apple Music, YouTube (Music), and Deezer.',
				'meaning': 'Bad request'
			})
			await interaction.followup.send(embed = embed_composer.embed)
			failed_request()
	except Exception as error:
		await embed_composer.error('other')
		await interaction.followup.send(embed = embed_composer.embed)
		failed_request()
		await log_catastrophe(
			'coverart',
			f'link:`{link}` country_code:`{country_code}` censor:`{censor}`',
			error
		)
	client_latency(current_unix_time_ms() - start_time)



@tree.command(name = 'knowledge', description = 'Get some basic information about a song')
@app_commands.describe(query = 'Search query or the link of the media you want to search')
@app_commands.describe(country_code = 'The country code of the country in which you want to search, US by default')
@app_commands.describe(censor = 'Whether you want to censor the title of the song or not, False by default and forced True for User Apps')
@discord.app_commands.allowed_installs(guilds = True, users = True)
@app_commands.allowed_contexts(guilds = True, dms = True, private_channels = True)
async def knowledge(interaction: discord.Interaction, query: str, country_code: str = 'us', censor: bool = False):
	start_time = current_unix_time_ms()
	json = {}
	if app_commands.AppInstallationType.user == True:
		censor = True
	await interaction.response.defer()
	embed_composer = EmbedComposer()
	try:
		metadata = await url_tools.get_metadata_from_url(query)
		if metadata == None or metadata['id'] == None and metadata['type'] == None:
			json = await api.search_knowledge(query, country_code)
		else:
			json = await api.lookup_knowledge(metadata['id'], metadata['service'], country_code)
		if 'type' in json:
			await embed_composer.compose(interaction.user, json, 'knowledge', False, censor, True)
			response = await interaction.followup.send(embed = embed_composer.embed, view = embed_composer.button_view)

			ai_report = await api.snitch(json)
			await embed_composer.compose(interaction.user, ai_report, 'knowledge', False, censor)
			await response.edit(embed = embed_composer.embed, view = embed_composer.button_view)

			successful_request()
			api_latency(json['meta']['processing_time']['global_io'])
		elif json == {}:
			await embed_composer.error(204)
			await interaction.followup.send(embed = embed_composer.embed)
			failed_request()
		else:
			await embed_composer.error(json['status'])
			await interaction.followup.send(embed = embed_composer.embed)
			failed_request()
		await embed_composer.compose(interaction.user, json, 'knowledge', True, censor)
		await log(
			[embed_composer.embed],
			[json],
			'knowledge',
			f'query:`{query}` country_code:`{country_code}` censor:`{censor}`',
			current_unix_time_ms() - start_time,
			embed_composer.button_view
		)
	except Exception as error:
		await embed_composer.error('other')
		await interaction.followup.send(embed = embed_composer.embed)
		failed_request()
		await log_catastrophe(
			'knowledge',
			f'query:`{query}` country_code:`{country_code}` censor:`{censor}`',
			error
		)
	client_latency(current_unix_time_ms() - start_time)



@tree.context_menu(name = 'Search music link(s)')
@discord.app_commands.allowed_installs(guilds = True, users = True)
@app_commands.allowed_contexts(guilds = True, dms = True, private_channels = True)
async def context_menu_lookup(interaction: discord.Interaction, message: discord.Message):
	start_time = current_unix_time_ms()
	media_data = []
	embeds = []
	buttons = []

	async def context_menu_link_lookup(data):
		embed_composer = EmbedComposer()
		global_object = await api.lookup(
			data['type'],
			data['id'],
			data['service'],
			data['country_code']
		)

		if 'type' in global_object:
			ai_check = await api.snitch(
				global_object
			)

			if 'type' in ai_check:
				await embed_composer.compose(message.author, ai_check, 'link', False, False)
				embeds.append(embed_composer.embed)
				buttons.append(embed_composer.button_view)

				successful_request()
				api_latency(global_object['meta']['processing_time']['global_io'] + ai_check['meta']['processing_time']['global_io'])
				await log(
					[embed_composer.embed],
					[ai_check],
					'Auto Link Lookup',
					f'type:`{data['type']}` id:`{data['id']}` service:`{data['service']}` country_code:`{data['country_code']}`',
					current_unix_time_ms() - start_time, 
					embed_composer.button_view
				)
			else:
				await embed_composer.compose(message.author, ai_check, 'link', False, False)
				embeds.append(embed_composer.embed)
				buttons.append(embed_composer.button_view)

				successful_request()
				api_latency(global_object['meta']['processing_time']['global_io'])
				await log(
					[embed_composer.embed],
					[global_object],
					'Search music link(s)',
					f'type:`{data['type']}` id:`{data['id']}` service:`{data['service']}` country_code:`{data['country_code']}`',
					current_unix_time_ms() - start_time, 
					embed_composer.button_view
				)
		else:
			failed_request()

	if app_commands.AppInstallationType.user == True:
		censor = True
	else:
		censor = False
	await interaction.response.defer()
	try:
		urls = await url_tools.get_urls_from_string(message.content)

		if urls == []:
			embed_composer = EmbedComposer()
			await embed_composer.error(400, {
				'title': "No links provided.",
				'description': f'This command only works with links of songs, albums, EP-s and music videos from Spotify, Apple Music, YouTube/YouTube Music, and Deezer.',
				'meaning': 'Bad request'
			})
			await interaction.followup.send(embed = embed_composer.embed)
			failed_request()
			client_latency(current_unix_time_ms() - start_time)
			return
			
		for url in urls:
			metadata = await url_tools.get_metadata_from_url(url)
			if metadata != None:
				media_data.append(metadata)
			
		if media_data != []:
			tasks = []
			for data in media_data:
				if data['id'] != None and data['type'] != None:
					tasks.append(
						create_task(
							context_menu_link_lookup(data)
						)
					)
			if len(tasks) != 0:
				results = await gather(*tasks)

				if embeds != []:
					if len(results) == 1:
						await interaction.followup.send(embed = embeds[0], view = buttons[0])
					else:
						pagination = PaginatorView(embeds = embeds, button_views = buttons)
						pagination.message = await interaction.followup.send(embed = pagination.initial_embed, view = pagination)
				else:
					await embed_composer.error(204)
					await interaction.followup.send(embed = embed_composer.embed)
					failed_request()

			else:
				embed_composer = EmbedComposer()
				await embed_composer.error(400, {
					'title': "Invalid link(s) provided.",
					'description': f'This command only works with songs, albums, EP-s and music videos from Spotify, Apple Music, YouTube/YouTube Music, and Deezer.',
					'meaning': 'Bad request'
				})
				await interaction.followup.send(embed = embed_composer.embed)
				failed_request()
			
		else:
			embed_composer = EmbedComposer()
			await embed_composer.error(400, {
				'title': "Invalid link(s) provided.",
				'description': f'This command only works with songs, albums, EP-s and music videos from Spotify, Apple Music, YouTube/YouTube Music, and Deezer.',
				'meaning': 'Bad request'
			})
			await interaction.followup.send(embed = embed_composer.embed)
			failed_request()
	except Exception as error:
		embed_composer = EmbedComposer()
		await embed_composer.error('other')
		await interaction.followup.send(embed = embed_composer.embed)
		failed_request()
		await log_catastrophe(
			'Search music link(s)',
			f'urls:`{await url_tools.get_urls_from_string(message.content)}`',
			error
		)
	client_latency(current_unix_time_ms() - start_time)



@tasks.loop(seconds = 60)
async def discord_presence():
	await client.change_presence(
		activity = discord.Activity(
			type = discord.ActivityType.listening,
			name = presence[randint(0, len(presence)-1)],
		)
	)

@tasks.loop(seconds = 86400)
async def reset_today_stats():
	reset()



@tasks.loop(seconds = 60)
async def dashboard():
	embed = discord.Embed(
		title = 'ASTRO DASHBOARD',
        colour = 0x6ae70e
	)
	embed.add_field(
		name = 'About',
		value = f'Version: `{version}`\nDeployment channel: `{deployment_channel}`\nShards: `{config['client']['shards']}`',
		inline = False
	)
	embed.add_field(
		name = 'Stats',
		value = f'Servers: `{len(client.guilds)}`\nAccessible users: `{len(client.users)}`',
		inline = False
	)
	embed.add_field(
		name = 'Start time',
		value = f'<t:{app_start_time}:F>',
		inline = True
	)
	embed.add_field(
		name = 'Last refreshed',
		value = f'<t:{current_unix_time()}:F>',
		inline = True
	)
	embed.add_field(
		name = 'Average latency today',
		value = f'API latency: `{stats['runtime']['avg_api_latency']}` ms\nClient latency: `{stats['runtime']['avg_client_latency']}` ms',
		inline = False
	)
	embed.add_field(
		name = 'Requests today',
		value = f'Total requests: `{int(stats['runtime']['successful_requests']) + int(stats['runtime']['failed_requests'])}`\nSuccessful requests: `{stats['runtime']['successful_requests']}`\nFailed requests: `{stats['runtime']['failed_requests']}`',
		inline = True
	)
	embed.add_field(
		name = 'Lifetime requests',
		value = f'Total requests: `{int(stats['lifetime']['total_successful_requests']) + int(stats['lifetime']['total_failed_requests'])}`\nSuccessful requests: `{stats['lifetime']['total_successful_requests']}`\nFailed requests: `{stats['lifetime']['total_failed_requests']}`',
		inline = True
	)
	try:
		server = await client.fetch_guild(tokens['dashboard']['astro_server_id'])
		channel = await server.fetch_channel(tokens['dashboard']['dashboard_channel_id'])
		dash = await channel.fetch_message(str(tokens['dashboard']['dashboard_message_id']))
		await dash.edit(embed = embed)
		print('[AstroDiscord] Dashboard refreshed')
	except:
		print('[AstroDiscord] Dashboard refresh failed, creating new one as fallback')
		server = await client.fetch_guild(tokens['dashboard']['astro_server_id'])
		channel = await server.fetch_channel(tokens['dashboard']['dashboard_channel_id'])
		message = await channel.send(embed = embed)
		tokens.set('dashboard', 'dashboard_message_id', str(message.id))
		with open('AstroDiscord/tokens.ini', 'w') as token_file:
			tokens.write(token_file)
		print('[AstroDiscord] New dashboard created')



reset()
client.run(tokens['tokens'][deployment_channel])