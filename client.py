import discord as discord 
from discord import app_commands
from discord import Spotify
from discord.ext import tasks

from random import randint
from asyncio import *

from AstroDiscord.components.ini import config, tokens, text, presence
from AstroDiscord.components import *
from AstroDiscord.components.url_tools import url_tools



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
	print('[AstroDiscord] Ready!')



@client.event
async def on_message(message):
	if message.author != client.user:
		media_data = []
		embeds = []
		urls = await url_tools.get_urls_from_string(message.content)
		
		for url in urls:
			metadata = await url_tools.get_metadata_from_url(url)
			media_data.append(metadata)
		
		if media_data != []:
			tasks = []
			for data in media_data:
				if data['id'] != None and data['type'] != None:
					tasks.append(
						create_task(
							api.lookup(
								data['type'],
								data['id'],
								data['service'],
								data['country_code']
							)
						)
					)

			results = await gather(*tasks)
			
			for result in results:
				embed_composer = EmbedComposer()
				if 'type' in result:
					await embed_composer.compose(message.author, result, 'link', False)
					await message.reply(embed = embed_composer.embed, view = embed_composer.button_view, mention_author = False)



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
	if app_commands.AppInstallationType.user == True:
		censor = True
	await interaction.response.defer()
	embed_composer = EmbedComposer()
	json = await api.search_song(artist, title, from_album, is_explicit, country_code)
	if 'type' in json:
		await embed_composer.compose(interaction.user, json, 'searchsong', False, censor)
		await interaction.followup.send(embed = embed_composer.embed, view = embed_composer.button_view)
	elif json == {}:
		await embed_composer.error(204)
		await interaction.followup.send(embed = embed_composer.embed)
	else:
		await embed_composer.error(json['status'])
		await interaction.followup.send(embed = embed_composer.embed)





@tree.command(name = 'searchalbum', description = 'Search for an album')
@app_commands.describe(artist = 'The artist of the album you want to search (ex. "Kendrick Lamar")')
@app_commands.describe(title = 'The title of the album you want to search (ex. "To Pimp A Butterfly")')
@app_commands.describe(year = 'The release year of the album you want to search, helps with precision (ex. "2015")')
@app_commands.describe(country_code = 'The country code of the country in which you want to search, US by default')
@app_commands.describe(censor = 'Whether you want to censor the title of the song or not, False by default and forced True for User Apps')
@discord.app_commands.allowed_installs(guilds = True, users = True)
@app_commands.allowed_contexts(guilds = True, dms = True, private_channels = True)
async def searchalbum(interaction: discord.Interaction, artist: str, title: str, year: int = None, country_code: str = 'us', censor: bool = False):
	if app_commands.AppInstallationType.user == True:
		censor = True
	await interaction.response.defer()
	embed_composer = EmbedComposer()
	json = await api.search_album(artist, title, year, country_code)
	if 'type' in json:
		await embed_composer.compose(interaction.user, json, 'searchalbum', False, censor)
		await interaction.followup.send(embed = embed_composer.embed, view = embed_composer.button_view)
	elif json == {}:
		await embed_composer.error(204)
		await interaction.followup.send(embed = embed_composer.embed)
	else:
		await embed_composer.error(json['status'])
		await interaction.followup.send(embed = embed_composer.embed)



@tree.command(name = 'lookup', description = 'Search a song, music video, album or EP from a query or its link')
@app_commands.describe(query = 'Search query or the link of the media you want to search')
@app_commands.describe(country_code = 'The country code of the country in which you want to search, US by default')
@app_commands.describe(censor = 'Whether you want to censor the title of the song or not, False by default and forced True for User Apps')
@discord.app_commands.allowed_installs(guilds = True, users = True)
@app_commands.allowed_contexts(guilds = True, dms = True, private_channels = True)
async def lookup(interaction: discord.Interaction, query: str, country_code: str = 'us', censor: bool = False):
	if app_commands.AppInstallationType.user == True:
		censor = True
	await interaction.response.defer()
	embed_composer = EmbedComposer()
	metadata = await url_tools.get_metadata_from_url(query)
	if metadata['id'] == None and metadata['type'] == None:
		json = await api.search(query, country_code)
	else:
		json = await api.lookup(metadata['type'], metadata['id'], metadata['service'], country_code)
	if 'type' in json:
		await embed_composer.compose(interaction.user, json, 'lookup', False, censor)
		await interaction.followup.send(embed = embed_composer.embed, view = embed_composer.button_view)
	elif json == {}:
		await embed_composer.error(204)
		await interaction.followup.send(embed = embed_composer.embed)
	else:
		await embed_composer.error(json['status'])
		await interaction.followup.send(embed = embed_composer.embed)




@tree.command(name = 'search', description = 'Search a song, music video, album or EP from a query or its link')
@app_commands.describe(query = 'Search query or the link of the media you want to search')
@app_commands.describe(country_code = 'The country code of the country in which you want to search, US by default')
@app_commands.describe(censor = 'Whether you want to censor the title of the song or not, False by default and forced True for User Apps')
@discord.app_commands.allowed_installs(guilds = True, users = True)
@app_commands.allowed_contexts(guilds = True, dms = True, private_channels = True)
async def search(interaction: discord.Interaction, query: str, country_code: str = 'us', censor: bool = False):
	if app_commands.AppInstallationType.user == True:
		censor = True
	await interaction.response.defer()
	embed_composer = EmbedComposer()
	metadata = await url_tools.get_metadata_from_url(query)
	if metadata['id'] == None and metadata['type'] == None:
		json = await api.search(query, country_code)
	else:
		json = await api.lookup(metadata['type'], metadata['id'], metadata['service'], country_code)
	if 'type' in json:
		await embed_composer.compose(interaction.user, json, 'search', False, censor)
		await interaction.followup.send(embed = embed_composer.embed, view = embed_composer.button_view)
	elif json == {}:
		await embed_composer.error(204)
		await interaction.followup.send(embed = embed_composer.embed)
	else:
		await embed_composer.error(json['status'])
		await interaction.followup.send(embed = embed_composer.embed)



@tree.command(name = 'snoop', description = "Get yours or someone else's currently playing song on Spotify")
@app_commands.describe(user = 'The user you want to snoop on, defaults to you if left empty')
@app_commands.describe(ephemeral = 'Whether the executed command should be ephemeral (only visible to you), false by default')
@app_commands.describe(country_code = 'The country code of the country in which you want to search, US by default')
@app_commands.describe(censor = 'Whether you want to censor the title of the song or not, False by default and forced True for User Apps')
@discord.app_commands.allowed_installs(guilds = True, users = False)
@app_commands.allowed_contexts(guilds = True, dms = False, private_channels = True)
async def snoop(interaction: discord.Interaction, user: discord.Member = None, ephemeral: bool = False, country_code: str = 'us', censor: bool = False):
	if app_commands.AppInstallationType.user == True:
		censor = True
	await interaction.response.defer(ephemeral = ephemeral)
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
	else:
		json = await api.lookup('song', identifier, 'spotify', country_code)	
		if 'type' in json:
			await embed_composer.compose(interaction.user, json, 'snoop', False, censor)
			await interaction.followup.send(embed = embed_composer.embed, view = embed_composer.button_view)
		elif json == {}:
			await embed_composer.error(204)
			await interaction.followup.send(embed = embed_composer.embed)
		else:
			await embed_composer.error(json['status'])
			await interaction.followup.send(embed = embed_composer.embed)




@tree.command(name = 'coverart', description = 'Get the cover art of a song or album')
@app_commands.describe(link = 'The link of the track or album you want to retrieve the cover art from')
@app_commands.describe(country_code = 'The country code of the country in which you want to search, US by default')
@app_commands.describe(censor = 'Whether you want to censor the title of the song or not, False by default and forced True for User Apps')
@discord.app_commands.allowed_installs(guilds = True, users = True)
@app_commands.allowed_contexts(guilds = True, dms = True, private_channels = True)
async def coverart(interaction: discord.Interaction, link: str, country_code: str = 'us', censor: bool = False):
	if app_commands.AppInstallationType.user == True:
		censor = True
	await interaction.response.defer()
	embed_composer = EmbedComposer()
	metadata = await url_tools.get_metadata_from_url(link)
	if metadata['id'] != None and metadata['type'] != None:
		json = await api.lookup(metadata['type'], metadata['id'], metadata['service'], metadata['country_code'])
		if 'type' in json:
			await embed_composer.compose(interaction.user, json, 'coverart', False, censor)
			await interaction.followup.send(embed = embed_composer.embed, view = embed_composer.button_view)
		elif json == {}:
			await embed_composer.error(204)
			await interaction.followup.send(embed = embed_composer.embed)
		else:
			await embed_composer.error(json['status'])
			await interaction.followup.send(embed = embed_composer.embed)
	else:
		await embed_composer.error(400, {
			'title': "Invalid link provided.",
			'description': f'This command only works with songs, albums, EP-s and music videos from Spotify, Apple Music, YouTube (Music), and Deezer.',
			'meaning': 'Bad request'
		})
		await interaction.followup.send(embed = embed_composer.embed)



@tree.command(name = 'knowledge', description = 'Get some basic information about a song')
@app_commands.describe(query = 'Search query or the link of the media you want to search')
@app_commands.describe(country_code = 'The country code of the country in which you want to search, US by default')
@app_commands.describe(censor = 'Whether you want to censor the title of the song or not, False by default and forced True for User Apps')
@discord.app_commands.allowed_installs(guilds = True, users = True)
@app_commands.allowed_contexts(guilds = True, dms = True, private_channels = True)
async def knowledge(interaction: discord.Interaction, query: str, country_code: str = 'us', censor: bool = False):
	if app_commands.AppInstallationType.user == True:
		censor = True
	await interaction.response.defer()
	embed_composer = EmbedComposer()
	metadata = await url_tools.get_metadata_from_url(query)
	if metadata['id'] == None and metadata['type'] == None:
		json = await api.search_knowledge(query, country_code)
	else:
		json = await api.lookup_knowledge(metadata['id'], metadata['service'], country_code)
	if 'type' in json:
		await embed_composer.compose(interaction.user, json, 'search', False, censor)
		await interaction.followup.send(embed = embed_composer.embed, view = embed_composer.button_view)
	elif json == {}:
		await embed_composer.error(204)
		await interaction.followup.send(embed = embed_composer.embed)
	else:
		await embed_composer.error(json['status'])
		await interaction.followup.send(embed = embed_composer.embed)



@tree.context_menu(name = 'Search music link(s)')
@discord.app_commands.allowed_installs(guilds = True, users = True)
@app_commands.allowed_contexts(guilds = True, dms = True, private_channels = True)
async def context_menu_lookup(interaction: discord.Interaction, message: discord.Message):
	if app_commands.AppInstallationType.user == True:
		censor = True
	else:
		censor = False
	await interaction.response.defer(ephemeral = True)
	media_data = []
	embeds = []
	urls = await url_tools.get_urls_from_string(message.content)
		
	for url in urls:
		metadata = await url_tools.get_metadata_from_url(url)
		media_data.append(metadata)
		
	if media_data != []:
		tasks = []
		for data in media_data:
			if data['id'] != None and data['type'] != None:
				tasks.append(
					create_task(
						api.lookup(
							data['type'],
							data['id'],
							data['service'],
							data['country_code']
						)
					)
				)
		await interaction.followup.send(f"Looking up {len(tasks)} link(s), please wait...")
		results = await gather(*tasks)
		
		for result in results:
			embed_composer = EmbedComposer()
			if 'type' in result:
				await embed_composer.compose(message.author, result, 'link', False, censor)
				embeds.append(embed_composer.embed)
				await message.reply(embed = embed_composer.embed, view = embed_composer.button_view, mention_author = False)
	else:
		await embed_composer.error(400, {
			'title': "Invalid link(s) provided.",
			'description': f'This command only works with songs, albums, EP-s and music videos from Spotify, Apple Music, YouTube (Music), and Deezer.',
			'meaning': 'Bad request'
		})
		await interaction.followup.send(embed = embed_composer.embed)




@tasks.loop(seconds = 60)
async def discord_presence():
	await client.change_presence(
		activity = discord.Activity(
			type = discord.ActivityType.listening,
			name = presence[randint(0, len(presence)-1)],
		)
	)



# @tasks.loop(seconds = 60)
# async def dashboard():
# 	api_latency = 0
# 	client_latency = 0
# 	successful_requests = 0
# 	failed_requests = 0

# 	for request in total_requests:
# 		api_latency += request['api_latency']
# 		client_latency += request['client_latency']
# 		successful_requests += 1 if request['request_result_type'] == 'success' else 0
# 		failed_requests += 1 if request['request_result_type'] == 'failure' else 0

# 	if api_latency != 0:
# 		api_latency = api_latency // len(total_requests)
	
# 	if client_latency != 0:
# 		client_latency = client_latency // len(total_requests)

# 	embed = discord.Embed(
# 		title = 'ASTRO DASHBOARD',
#         colour = 0x6ae70e
# 	)
# 	embed.add_field(
# 		name = 'About',
# 		value = f'Version: `{version}`\nDeployment channel: `{deployment_channel}`\nShards: `{config['client']['shards']}`',
# 		inline = False
# 	)
# 	embed.add_field(
# 		name = 'Stats',
# 		value = f'Servers: `{len(client.guilds)}`\nAccessible users: `{len(client.users)}`',
# 		inline = False
# 	)
# 	embed.add_field(
# 		name = 'Start time',
# 		value = f'<t:{app_start_time}:F>',
# 		inline = True
# 	)
# 	embed.add_field(
# 		name = 'Last refreshed',
# 		value = f'<t:{current_unix_time()}:F>',
# 		inline = True
# 	)
# 	embed.add_field(
# 		name = 'Average latency today',
# 		value = f'API latency: `{api_latency}` ms\nClient latency: `{client_latency}` ms',
# 		inline = False
# 	)
# 	embed.add_field(
# 		name = 'Requests today',
# 		value = f'Total requests: `{len(total_requests)}`\nSuccessful requests: `{successful_requests}`\nFailed requests: `{failed_requests}`',
# 		inline = True
# 	)
# 	try:
# 		server = await client.fetch_guild(tokens['dashboard']['astro_server_id'])
# 		channel = await server.fetch_channel(tokens['dashboard']['dashboard_channel_id'])
# 		dash = await channel.fetch_message(str(tokens['dashboard']['dashboard_message_id']))
# 		await dash.edit(embed = embed)
# 	except:
# 		server = await client.fetch_guild(tokens['dashboard']['astro_server_id'])
# 		channel = await server.fetch_channel(tokens['dashboard']['dashboard_channel_id'])
# 		message = await channel.send(embed = embed)
# 		tokens.set('dashboard', 'dashboard_message_id', str(message.id))
# 		with open('AstroDiscord/tokens.ini', 'w') as token_file:
# 			tokens.write(token_file)



# @tasks.loop(seconds = 86400)
# async def reset_requests():
# 	total_requests.clear()
	


client.run(tokens['tokens'][deployment_channel])