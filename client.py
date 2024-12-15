import discord as discord 
from discord import app_commands
from discord import Spotify
from discord.ext import tasks

from random import randint
from asyncio import *
import AstroAPI as astro
from AstroAPI.components.time import *

from AstroDiscord.components.ini import config, tokens, text, presence
from AstroDiscord.components import *
from AstroDiscord.components.url_tools import types



class Client(discord.AutoShardedClient):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.synced = False
	


version = 'PRE-a2.0'
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



link_lookup_functions = [
	astro.Global.lookup_song,
	astro.Global.lookup_collection,
	astro.Global.lookup_song,
	astro.Global.lookup_collection,
	astro.Global.lookup_music_video,
	astro.Global.lookup_song,
	astro.Global.lookup_collection,
	astro.Global.lookup_song,
	astro.Global.lookup_collection,
	astro.Global.lookup_song,
	astro.Global.lookup_collection,
	astro.Global.lookup_music_video
]

link_lookup_function_objects = [
	astro.Spotify,
	astro.Spotify,
	astro.AppleMusic,
	astro.AppleMusic,
	astro.AppleMusic,
	astro.YouTubeMusic,
	astro.YouTubeMusic,
	astro.Deezer,
	astro.Deezer,
	astro.Tidal,
	astro.Tidal,
	astro.Tidal
]



@client.event
async def on_ready():
	await client.wait_until_ready()
	if not client.synced:
		await tree.sync()
		client.synced = True
	if not discord_presence.is_running():
		discord_presence.start()



@client.event
async def on_message(message):
	if message.author != client.user:
		start_time = current_unix_time_ms()
		urls = find_urls(message.content)
		data = get_data_from_urls(urls)

		media_objects = []
		embeds = []
		log_embeds = []
		
		tasks = []


		if data != []:
			if len(data) == 1:
				media_type = data[0]['media']
				media_id = data[0]['id']
				media_country_code = data[0]['country_code']
				media_object = await link_lookup_functions[types.index(media_type)](link_lookup_function_objects[types.index(media_type)], media_id, media_country_code)
				media_embed = Embed(
					command = 'link',
					media_object = media_object,
					user = message.author
				)
				if media_object.type not in invalid_responses:
					media_objects.append(media_object)
					embeds.append(media_embed.embed)
					log_embeds.append(media_embed.log_embed)
			else:
				for entry in data:
					media_type = entry['media']
					media_id = entry['id']
					media_country_code = entry['country_code']
					tasks.append(
						create_task(link_lookup_functions[types.index(media_type)](link_lookup_function_objects[types.index(media_type)], media_id, media_country_code))
					)

				results = await gather(*tasks)
				for result in results:
					media_embed = Embed(
						command = 'link',
						media_object = result,
						user = message.author
					)
					if result.type not in invalid_responses:
						media_objects.append(result)
						embeds.append(media_embed.embed)
						log_embeds.append(media_embed.log_embed)

		else:
			return

		while None in embeds:
			embeds.remove(None)

		if embeds != []:
			message_embed = await message.reply(embeds = embeds, mention_author = False)

		end_time = current_unix_time_ms()
		total_time = end_time - start_time

		if embeds != []:
			await add_reactions(message_embed, ['👍','👎'])
		else:
			await add_reactions(message, ['🤷'])

		await log(
			log_embeds = log_embeds,
			media = media_objects,
			command = 'auto_link_lookup',
			parameters = f'music_data:`{data}`',
			latency = total_time
		)



@tree.command(name = 'searchsong', description = 'Search for a song on all major platforms')
@app_commands.describe(artist = 'The name of the artist of the song you want to search (ex. "Tyler, The Creator")')
@app_commands.describe(title = 'The title of the song you want to search (ex. "NEW MAGIC WAND")')
@app_commands.describe(from_album = 'The album, EP or collection of the song you want to search, helps with precision (ex. "IGOR")')
@app_commands.describe(is_explicit = 'Whether the song you want to search has explicit content (has the little [E] badge next to its name on streaming platforms), helps with precision')
@app_commands.guild_install()
@app_commands.user_install()
@app_commands.allowed_contexts(guilds = True, dms = True, private_channels = True)
async def searchsong(interaction: discord.Interaction, artist: str, title: str, from_album: str = None, is_explicit: bool = None):
	start_time = current_unix_time_ms()
	await interaction.response.defer()
	song = await astro.Global.search_song(
		artists = [artist],
		title = title,
		collection = from_album,
		is_explicit = is_explicit
	)
	embeds = Embed(
		command = 'search',
		media_object = song,
		user = interaction.user
	)
	embed = await interaction.followup.send(
		embed = embeds.embed
	)
	end_time = current_unix_time_ms()
	total_time = end_time - start_time

	if song.type not in invalid_responses:
		await add_reactions(embed, ['👍','👎'])

	await log(
		log_embeds = [embeds.log_embed],
		media = [song],
		command = 'searchalbum',
		parameters = f'artist:{artist} title:{title} from_album:{from_album} is_explicit:{is_explicit}',
		latency = total_time
	)



@tree.command(name = 'searchalbum', description = 'Search for an album')
@app_commands.describe(artist = 'The artist of the album you want to search (ex. "Kendrick Lamar")')
@app_commands.describe(title = 'The title of the album you want to search (ex. "To Pimp A Butterfly")')
@app_commands.describe(year = 'The release year of the album you want to search, helps with precision (ex. "2015")')
@app_commands.guild_install()
@app_commands.user_install()
@app_commands.allowed_contexts(guilds = True, dms = True, private_channels = True)
async def searchcollection(interaction: discord.Interaction, artist: str, title: str, year: int = None):
	start_time = current_unix_time_ms()
	await interaction.response.defer()
	collection = await astro.Global.search_collection(
		artists = [artist],
		title = title,
		year = year
	)
	embeds = Embed(
		command = 'search',
		media_object = collection,
		user = interaction.user
	)
	embed = await interaction.followup.send(
		embed = embeds.embed
	)
	end_time = current_unix_time_ms()
	total_time = end_time - start_time

	if collection.type not in invalid_responses:
		await add_reactions(embed, ['👍','👎'])

	await log(
		log_embeds = [embeds.log_embed],
		media = [collection],
		command = 'searchalbum',
		parameters = f'artist:{artist} title:{title} year:{year}',
		latency = total_time
	)



@tree.command(name = 'lookup', description = 'Search a song, music video, album or EP from a query or its link')
@app_commands.describe(query = 'Search query or the link of the media you want to search')
@app_commands.guild_install()
@app_commands.user_install()
@app_commands.allowed_contexts(guilds = True, dms = True, private_channels = True)
async def lookup(interaction: discord.Interaction, query: str):
	start_time = current_unix_time_ms()
	await interaction.response.defer()
	urls = find_urls(query)
	data = get_data_from_urls(urls)
	if data == []:
		media_object = await astro.Global.search_query(query = query)
	else:
		media_type = data[0]['media']
		media_id = data[0]['id']
		media_country_code = data[0]['country_code']
		media_object = await link_lookup_functions[types.index(media_type)](link_lookup_function_objects[types.index(media_type)], media_id, media_country_code)
	embeds = Embed(
		command = 'search',
		media_object = media_object,
		user = interaction.user
	)
	embed = await interaction.followup.send(
		embed = embeds.embed
	)
	end_time = current_unix_time_ms()
	total_time = end_time - start_time

	if media_object.type not in invalid_responses:
		await add_reactions(embed, ['👍','👎'])

	await log(
		log_embeds = [embeds.log_embed],
		media = [media_object],
		command = 'lookup',
		parameters = f'query:{query}',
		latency = total_time
	)



@tree.command(name = 'snoop', description = 'Get the track you or another user is listening to on Spotify')
@app_commands.describe(user = 'The user you want to snoop on, defaults to you if left empty')
@app_commands.describe(ephemeral = 'Whether the executed command should be ephemeral (only visible to you), false by default')
@app_commands.guild_install()
@app_commands.allowed_contexts(guilds = True, dms = False, private_channels = True)
async def snoop(interaction: discord.Interaction, user: discord.Member = None, ephemeral: bool = False):
	request = '/snoop'
	start_time = current_unix_time_ms()
	await interaction.response.defer(ephemeral = ephemeral)

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
		if user == interaction.user:
			error_msg = text['embed']['snoop_you_errormsg']
		else:
			error_msg = text['embed']['snoop_someone_errormsg']
		song = astro.Error(
			service = service,
			component = 'Snoop',
			error_msg = error_msg,
			request = {'request': request, 'self_snoop': (True if user == interaction.user else False)} 
		)
	else:
		song = await astro.Global.lookup_song(
			service = astro.Spotify,
			id = identifier
		)

	embeds = Embed(
		command = 'snoop',
		media_object = song,
		user = user
	)
	embed = await interaction.followup.send(
		embed = embeds.embed
	)
	end_time = current_unix_time_ms()
	total_time = end_time - start_time

	if song.type not in invalid_responses:
		await add_reactions(embed, ['👍','👎'])

	await log(
		log_embeds = [embeds.log_embed],
		media = [song],
		command = 'snoop',
		parameters = f'self_snoop:{(True if user == interaction.user else False)}',
		latency = total_time
	)



@tree.command(name = 'coverart', description = 'Get the cover art of a track or album')
@app_commands.describe(link = 'The link of the track or album you want to retrieve the cover art from')
@app_commands.guild_install()
@app_commands.user_install()
@app_commands.allowed_contexts(guilds = True, dms = True, private_channels = True)
async def coverart(interaction: discord.Interaction, link: str):
	request = '/coverart'
	start_time = current_unix_time_ms()
	await interaction.response.defer()
	data = get_data_from_urls(link)

	if data == []:
		media_object = astro.Error(
			service = service,
			component = '`/coverart`',
			error_msg = text['embed']['cover_errormsg'],
			request = {'request': request, 'url': link}
		)
	else:
		media_type = data[0]['media']
		media_id = data[0]['id']
		media_country_code = data[0]['country_code']
		media_object = await link_lookup_functions[types.index(media_type)](link_lookup_function_objects[types.index(media_type)], media_id, media_country_code)

	embeds = Embed(
		command = 'cover',
		media_object = media_object,
		user = interaction.user
	)
	embed = await interaction.followup.send(
		embed = embeds.embed
	)
	end_time = current_unix_time_ms()
	total_time = end_time - start_time

	if media_object.type not in invalid_responses:
		await add_reactions(embed, ['🔥','🗑️'])

	await log(
		log_embeds = [embeds.log_embed],
		media = [media_object],
		command = 'coverart',
		parameters = f'link:`{link}`',
		latency = total_time
	)
	


@tree.context_menu(name = 'Search music link(s)')
@app_commands.guild_install()
@app_commands.user_install()
@app_commands.allowed_contexts(guilds = True, dms = True, private_channels = True)
async def context_menu_lookup(interaction: discord.Interaction, message: discord.Message):
	request = 'context_menu_lookup'
	start_time = current_unix_time_ms()
	await interaction.response.defer()
	urls = find_urls(message.content)
	data = get_data_from_urls(urls)

	media_objects = []
	embeds = []
	log_embeds = []

	tasks = []

	if data != []:
		if len(data) == 1:
			media_type = data[0]['media']
			media_id = data[0]['id']
			media_country_code = data[0]['country_code']
			media_object = await link_lookup_functions[types.index(media_type)](link_lookup_function_objects[types.index(media_type)], media_id, media_country_code)
			media_embed = Embed(
				command = 'link',
				media_object = media_object,
				user = message.author
			)
			media_objects.append(media_object)
			embeds.append(media_embed.embed)
			log_embeds.append(media_embed.log_embed)
		else:
			for entry in data:
				media_type = entry['media']
				media_id = entry['id']
				media_country_code = entry['country_code']
				tasks.append(
					create_task(link_lookup_functions[types.index(media_type)](link_lookup_function_objects[types.index(media_type)], media_id, media_country_code))
				)

			results = await gather(*tasks)
			for result in results:
				media_embed = Embed(
					command = 'link',
					media_object = result,
					user = message.author
				)
				media_objects.append(result)
				embeds.append(media_embed.embed)
				log_embeds.append(media_embed.log_embed)

	else:
		media_object = astro.Error(
			service = service,
			component = 'Context Menu Link Lookup',
			error_msg = text['embed']['context_menu_link_lookup_errormsg'],
			request = {'request': request, 'urls': urls}
		)
		media_embed = Embed(
			command = 'link',
			media_object = media_object,
			user = message.author
		)
		media_objects.append(media_object)
		embeds.append(media_embed.embed)

	while None in embeds:
		embeds.remove(None)

	message_embed = await interaction.followup.send(embeds = embeds)
	if media_object.type not in invalid_responses:
		await add_reactions(message_embed, ['👍','👎'])

	end_time = current_unix_time_ms()
	total_time = end_time - start_time

	await log(
		log_embeds = log_embeds,
		media = media_objects,
		command = 'context_menu_link_lookup',
		parameters = f'urls:`{urls}`',
		latency = total_time
	)



@tasks.loop(seconds = 60)
async def discord_presence():
	await client.change_presence(activity = discord.Activity(
		type = discord.ActivityType.listening,
		name = presence[randint(0, len(presence)-1)],
	))
	

	
client.run(tokens['tokens'][deployment_channel])