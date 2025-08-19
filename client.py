import discord as discord 
from discord import app_commands
from discord import Spotify
from discord.ext import tasks

from random import randint
from asyncio import *
import aiohttp

from AstroDiscord.components.ini import config, tokens, text, presence
from AstroDiscord.components import *
# from AstroDiscord.components.url_tools import types



class Client(discord.AutoShardedClient):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.synced = False
	


api_endpoint = tokens['api_endpoints']['astroapi'] 
version = config['client']['version']
service = 'discord'
component = 'Discord Client'
deployment_channel = config['client']['deployment_channel']
# app_start_time = current_unix_time()
# total_requests = []
# embed_reactions = ['🔥','🗑️']
# knowledge_reactions = ['🤯','😴']
# not_found_reaction = ['🤷']
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
	print('[AstroDiscord] Ready!')



# @client.event
# async def on_message(message):
# 	if message.author != client.user:
# 		urls = find_urls(message.content)
# 		data = await get_data_from_urls(urls)

# 		media_objects = []
# 		embeds = []
# 		log_embeds = []
		
# 		tasks = []

# 		if data != []:
# 			start_time = current_unix_time_ms()
# 			if len(data) == 1:
# 				media_type = data[0]['media']
# 				media_id = data[0]['id']
# 				media_country_code = data[0]['country_code']
# 				media_object = await link_lookup_functions[types.index(media_type)](link_lookup_function_objects[types.index(media_type)], media_id, media_country_code, media_country_code)
# 				media_embed = Embed(
# 					command = 'link',
# 					media_object = media_object,
# 					user = message.author
# 				)
# 				if media_object.type not in invalid_responses:
# 					media_objects.append(media_object)
# 					embeds.append(media_embed.embed)
# 					log_embeds.append(media_embed.log_embed)
# 			else:
# 				for entry in data:
# 					media_type = entry['media']
# 					media_id = entry['id']
# 					media_country_code = entry['country_code']
# 					tasks.append(
# 						create_task(link_lookup_functions[types.index(media_type)](link_lookup_function_objects[types.index(media_type)], media_id, media_country_code, media_country_code))
# 					)

# 				results = await gather(*tasks)
# 				for result in results:
# 					media_embed = Embed(
# 						command = 'link',
# 						media_object = result,
# 						user = message.author
# 					)
# 					if result.type not in invalid_responses:
# 						media_objects.append(result)
# 						embeds.append(media_embed.embed)
# 						log_embeds.append(media_embed.log_embed)

# 		else:
# 			return

# 		while None in embeds:
# 			embeds.remove(None)

# 		api_request_latency = 0
# 		if embeds != []:
# 			for obj in media_objects:
# 				if obj.type not in invalid_responses:
# 					api_request_latency += obj.meta.processing_time['global']
# 			api_request_latency = api_request_latency // len(media_objects)
# 			message_embed = await message.reply(embeds = embeds, mention_author = False)

# 		end_time = current_unix_time_ms()
# 		total_time = end_time - start_time

# 		if embeds != []:
# 			log_request(api_request_latency, total_time - api_request_latency, 'success')
# 			await add_reactions(message_embed, embed_reactions)
			
# 		else:
# 			log_request(api_request_latency, total_time - api_request_latency, 'failure')
# 			await add_reactions(message, not_found_reaction)

# 		await log(
# 			log_embeds = log_embeds,
# 			media = media_objects,
# 			command = 'auto_link_lookup',
# 			parameters = f'music_data:`{data}`',
# 			latency = total_time
# 		)



@tree.command(name = 'searchsong', description = 'Search for a song on all major platforms')
@app_commands.describe(artist = 'The name of the artist of the song you want to search (ex. "Tyler, The Creator")')
@app_commands.describe(title = 'The title of the song you want to search (ex. "NEW MAGIC WAND")')
@app_commands.describe(from_album = 'The album, EP or collection of the song you want to search, helps with precision (ex. "IGOR")')
@app_commands.describe(is_explicit = 'Whether the song you want to search has explicit content (has the little [E] badge next to its name on streaming platforms), helps with precision')
@app_commands.describe(country_code = 'The country code of the country in which you want to search, US by default')
@app_commands.describe(censor = 'Whether you want to censor the title of the song or not, False by default and forced True for User Apps')
@app_commands.guild_install()
@app_commands.user_install()
@app_commands.allowed_contexts(guilds = True, dms = True, private_channels = True)
async def searchsong(interaction: discord.Interaction, artist: str, title: str, from_album: str = None, is_explicit: bool = None, country_code: str = 'us', censor: bool = False):
	if app_commands.AppInstallationType.user:
		censor = True
	await interaction.response.defer()
	embed_composer = EmbedComposer()
	async with aiohttp.ClientSession() as session:
		api_url = f'{api_endpoint}/music/global_io/search_song'
		api_params = {
			'artist': artist,
			'title': title,
		}
		if from_album != None:
			api_params['collection_title'] = from_album
		if is_explicit != None:
			api_params['is_explicit'] = is_explicit
		if country_code != None:
			api_params['country_code'] = country_code
		async with session.get(url = api_url, params = api_params) as response:
			if response.status == 200:
				json_response = await response.json()
				await embed_composer.compose(interaction.user, json_response, 'searchsong', False, censor)
				await interaction.followup.send(embed = embed_composer.embed, view = embed_composer.button_view)
			else:
				await interaction.followup.send("fuck off")

	




@tree.command(name = 'searchalbum', description = 'Search for an album')
@app_commands.describe(artist = 'The artist of the album you want to search (ex. "Kendrick Lamar")')
@app_commands.describe(title = 'The title of the album you want to search (ex. "To Pimp A Butterfly")')
@app_commands.describe(year = 'The release year of the album you want to search, helps with precision (ex. "2015")')
@app_commands.describe(country_code = 'The country code of the country in which you want to search, US by default')
@app_commands.describe(censor = 'Whether you want to censor the title of the song or not, False by default and forced True for User Apps')
@app_commands.guild_install()
@app_commands.user_install()
@app_commands.allowed_contexts(guilds = True, dms = True, private_channels = True)
async def searchcollection(interaction: discord.Interaction, artist: str, title: str, year: int = None, country_code: str = 'us', censor: bool = False):
	if app_commands.AppInstallationType.user:
		censor = True
	await interaction.response.defer()
	embed_composer = EmbedComposer()
	async with aiohttp.ClientSession() as session:
		api_url = f'{api_endpoint}/music/global_io/search_collection'
		api_params = {
			'artist': artist,
			'title': title,
		}
		if year != None:
			api_params['year'] = year
		if country_code != None:
			api_params['country_code'] = country_code
		async with session.get(url = api_url, params = api_params) as response:
			if response.status == 200:
				json_response = await response.json()
				await embed_composer.compose(interaction.user, json_response, 'searchalbum', False, censor)
				await interaction.followup.send(embed = embed_composer.embed, view = embed_composer.button_view)
			else:
				await interaction.followup.send("fuck off")



@tree.command(name = 'lookup', description = 'Search a song, music video, album or EP from a query or its link')
@app_commands.describe(query = 'Search query or the link of the media you want to search')
@app_commands.describe(country_code = 'The country code of the country in which you want to search, US by default')
@app_commands.describe(censor = 'Whether you want to censor the title of the song or not, False by default and forced True for User Apps')
@app_commands.guild_install()
@app_commands.user_install()
@app_commands.allowed_contexts(guilds = True, dms = True, private_channels = True)
async def lookup(interaction: discord.Interaction, query: str, country_code: str = 'us', censor: bool = False):
	if app_commands.AppInstallationType.user:
		censor = True
	await interaction.response.defer()
	embed_composer = EmbedComposer()
	async with aiohttp.ClientSession() as session:
		api_url = f'{api_endpoint}/music/global_io/search_query'
		api_params = {
			'query': query,
		}
		if country_code != None:
			api_params['country_code'] = country_code
		async with session.get(url = api_url, params = api_params) as response:
			if response.status == 200:
				json_response = await response.json()
				await embed_composer.compose(interaction.user, json_response, 'lookup', False, censor)
				await interaction.followup.send(embed = embed_composer.embed, view = embed_composer.button_view)
			else:
				await interaction.followup.send("fuck off")




@tree.command(name = 'search', description = 'Search a song, music video, album or EP from a query or its link')
@app_commands.describe(query = 'Search query or the link of the media you want to search')
@app_commands.describe(country_code = 'The country code of the country in which you want to search, US by default')
@app_commands.describe(censor = 'Whether you want to censor the title of the song or not, False by default and forced True for User Apps')
@app_commands.guild_install()
@app_commands.user_install()
@app_commands.allowed_contexts(guilds = True, dms = True, private_channels = True)
async def lookup(interaction: discord.Interaction, query: str, country_code: str = 'us', censor: bool = False):
	if app_commands.AppInstallationType.user:
		censor = True
	await interaction.response.defer()
	embed_composer = EmbedComposer()
	async with aiohttp.ClientSession() as session:
		api_url = f'{api_endpoint}/music/global_io/search_query'
		api_params = {
			'query': query,
		}
		if country_code != None:
			api_params['country_code'] = country_code
		async with session.get(url = api_url, params = api_params) as response:
			if response.status == 200:
				json_response = await response.json()
				await embed_composer.compose(interaction.user, json_response, 'search', False, censor)
				await interaction.followup.send(embed = embed_composer.embed, view = embed_composer.button_view)
			else:
				await interaction.followup.send("fuck off")



@tree.command(name = 'snoop', description = "Get yours or someone else's currently playing song on Spotify")
@app_commands.describe(user = 'The user you want to snoop on, defaults to you if left empty')
@app_commands.describe(ephemeral = 'Whether the executed command should be ephemeral (only visible to you), false by default')
@app_commands.describe(country_code = 'The country code of the country in which you want to search, US by default')
@app_commands.describe(censor = 'Whether you want to censor the title of the song or not, False by default and forced True for User Apps')
@app_commands.guild_install()
@app_commands.allowed_contexts(guilds = True, dms = False, private_channels = True)
async def snoop(interaction: discord.Interaction, user: discord.Member = None, ephemeral: bool = False, country_code: str = 'us', censor: bool = False):
	if app_commands.AppInstallationType.user:
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
		await interaction.followup.send("no spotify activity detected")
	else:
		async with aiohttp.ClientSession() as session:
			api_url = f'{api_endpoint}/music/global_io/lookup_song'
			api_params = {
				'id': identifier,
				'id_service': 'spotify'
			}
			if country_code != None:
				api_params['country_code'] = country_code
			async with session.get(url = api_url, params = api_params) as response:
				if response.status == 200:
					json_response = await response.json()
					await embed_composer.compose(interaction.user, json_response, 'snoop', False, censor)
					await interaction.followup.send(embed = embed_composer.embed, view = embed_composer.button_view)
				else:
					await interaction.followup.send("fuck off")




# @tree.command(name = 'coverart', description = 'Get the cover art of a song or album')
# @app_commands.describe(link = 'The link of the track or album you want to retrieve the cover art from')
# @app_commands.guild_install()
# @app_commands.user_install()
# @app_commands.allowed_contexts(guilds = True, dms = True, private_channels = True)
# async def coverart(interaction: discord.Interaction, link: str):
# 	request = {'request': '/coverart', 'url': link}
# 	start_time = current_unix_time_ms()
# 	await interaction.response.defer()
# 	data = await get_data_from_urls(link)

# 	if data == []:
# 		media_object = astro.Error(
# 			service = service,
# 			component = '`/coverart`',
# 			error_msg = text['error']['invalid_link'],
# 			meta = astro.Meta(
# 				service = service,
# 				request = request,
# 				processing_time = current_unix_time_ms() - start_time
# 			)
# 		)
# 	else:
# 		media_type = data[0]['media']
# 		media_id = data[0]['id']
# 		media_country_code = data[0]['country_code']
# 		media_object = await link_lookup_functions[types.index(media_type)](link_lookup_function_objects[types.index(media_type)], media_id, media_country_code)

# 	embeds = Embed(
# 		command = 'cover',
# 		media_object = media_object,
# 		user = interaction.user
# 	)
# 	embed = await interaction.followup.send(
# 		embed = embeds.embed
# 	)
# 	end_time = current_unix_time_ms()
# 	total_time = end_time - start_time

# 	if media_object.type not in invalid_responses:
# 		log_request(media_object.meta.processing_time['global'], total_time - media_object.meta.processing_time['global'], 'success')
# 		await add_reactions(embed, embed_reactions)
# 	else:
# 		log_request(0, total_time, 'failure')

# 	await log(
# 		log_embeds = [embeds.log_embed],
# 		media = [media_object],
# 		command = 'coverart',
# 		parameters = f'link:`{link}`',
# 		latency = total_time
# 	)



# @tree.command(name = 'knowledge', description = 'Get some basic information about a song')
# @app_commands.describe(query = 'The link of the song you want yo retrieve information about')
# @app_commands.describe(country_code = 'The country code of the country in which you want to search, US by default')
# @app_commands.guild_install()
# @app_commands.user_install()
# @app_commands.allowed_contexts(guilds = True, dms = True, private_channels = True)
# async def knowledge(interaction: discord.Interaction, query: str, country_code: str = 'us'):
# 	request = {'request': '/knowledge', 'query': query, 'country_code': country_code}
# 	start_time = current_unix_time_ms()
# 	await interaction.response.defer()
# 	urls = find_urls(query)
# 	data = await get_data_from_urls(urls)
# 	if data == [] and len(urls) == 0:
# 		knowledge = await astro.Global.search_query_knowledge(query = query)
# 	elif data == [] and len(urls) >= 1:
# 		knowledge = astro.Error(
# 			service = service,
# 			component = '`/lookup`',
# 			error_msg = text['error']['invalid_link'],
# 			meta = astro.Meta(
# 				service = service,
# 				request = request,
# 				processing_time = current_unix_time_ms() - start_time
# 			)
# 		)
# 	else:
# 		media_type = data[0]['media']
# 		media_id = data[0]['id']
# 		media_country_code = data[0]['country_code']
# 		knowledge = await astro.Global.lookup_song_knowledge(link_lookup_function_objects[types.index(media_type)], media_id, media_country_code)

# 	embeds = Embed(
# 		command = 'search',
# 		media_object = knowledge,
# 		user = interaction.user
# 	)

# 	embed = await interaction.followup.send(
# 		embed = embeds.embed
# 	)
# 	end_time = current_unix_time_ms()
# 	total_time = end_time - start_time

# 	if knowledge.type not in invalid_responses:
# 		log_request(knowledge.meta.processing_time['global'], total_time - knowledge.meta.processing_time['global'], 'success')
# 		await add_reactions(embed, knowledge_reactions)
# 	else:
# 		log_request(0, total_time, 'failure')

# 	await log(
# 		log_embeds = [embeds.log_embed],
# 		media = [knowledge],
# 		command = 'knowledge',
# 		parameters = f'query:`{query}`',
# 		latency = total_time
# 	)



# @tree.context_menu(name = 'Search music link(s)')
# @app_commands.guild_install()
# @app_commands.user_install()
# @app_commands.allowed_contexts(guilds = True, dms = True, private_channels = True)
# async def context_menu_lookup(interaction: discord.Interaction, message: discord.Message):
# 	start_time = current_unix_time_ms()
# 	await interaction.response.defer()
# 	urls = find_urls(message.content)
# 	data = await get_data_from_urls(urls)
# 	request = {'request': 'context_menu_lookup', 'urls': urls}

# 	media_objects = []
# 	embeds = []
# 	log_embeds = []

# 	tasks = []

# 	if data != []:
# 		if len(data) == 1:
# 			media_type = data[0]['media']
# 			media_id = data[0]['id']
# 			media_country_code = data[0]['country_code']
# 			media_object = await link_lookup_functions[types.index(media_type)](link_lookup_function_objects[types.index(media_type)], media_id, media_country_code)
# 			media_embed = Embed(
# 				command = 'link',
# 				media_object = media_object,
# 				user = message.author
# 			)
# 			media_objects.append(media_object)
# 			embeds.append(media_embed.embed)
# 			log_embeds.append(media_embed.log_embed)
# 		else:
# 			for entry in data:
# 				media_type = entry['media']
# 				media_id = entry['id']
# 				media_country_code = entry['country_code']
# 				tasks.append(
# 					create_task(link_lookup_functions[types.index(media_type)](link_lookup_function_objects[types.index(media_type)], media_id, media_country_code))
# 				)

# 			results = await gather(*tasks)
# 			for result in results:
# 				media_embed = Embed(
# 					command = 'link',
# 					media_object = result,
# 					user = message.author
# 				)
# 				media_objects.append(result)
# 				embeds.append(media_embed.embed)
# 				log_embeds.append(media_embed.log_embed)

# 	else:
# 		media_object = astro.Error(
# 			service = service,
# 			component = 'Context Menu Link Lookup',
# 			error_msg = text['error']['no_links_detected'],
# 			meta = astro.Meta(
# 				service = service,
# 				request = request,
# 				processing_time = current_unix_time_ms() - start_time
# 			)
# 		)
# 		media_embed = Embed(
# 			command = 'link',
# 			media_object = media_object,
# 			user = message.author
# 		)
# 		media_objects.append(media_object)
# 		embeds.append(media_embed.embed)

# 	while None in embeds:
# 		embeds.remove(None)

# 	message_embed = await interaction.followup.send(embeds = embeds)

# 	end_time = current_unix_time_ms()
# 	total_time = end_time - start_time

# 	api_request_latency = 0
# 	for obj in media_objects:
# 		if obj.type not in invalid_responses:
# 			api_request_latency += obj.meta.processing_time['global']
# 	api_request_latency = api_request_latency // len(media_objects)

# 	if media_object.type not in invalid_responses:
# 		log_request(api_request_latency, total_time - api_request_latency, 'success')
# 		await add_reactions(message_embed, embed_reactions)
# 	else:
# 		log_request(api_request_latency, total_time - api_request_latency, 'failure')

# 	await log(
# 		log_embeds = log_embeds,
# 		media = media_objects,
# 		command = 'context_menu_link_lookup',
# 		parameters = f'urls:`{urls}`',
# 		latency = total_time
# 	)



# @tasks.loop(seconds = 300)
# async def discord_presence():
# 	await client.change_presence(activity = discord.Activity(
# 		type = discord.ActivityType.listening,
# 		name = presence[randint(0, len(presence)-1)],
# 	))



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