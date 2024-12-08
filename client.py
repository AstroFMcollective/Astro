import discord as discord 
from discord import app_commands
from discord import Spotify
from discord.ext import tasks

from random import randint
from asyncio import *
import AstroAPI as astro
from AstroAPI.components.time import *

from AstroDiscord.components.ini import config
from AstroDiscord.components import *
from AstroDiscord.components.url_tools import types 


class Client(discord.AutoShardedClient):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.synced = False



version = 'PRE-a2.0'
intents = discord.Intents.all()
intents.message_content = True
intents.presences = True
intents.members = True
client = Client(shard_count = int(config['client']['shards']), intents = intents)
tree = app_commands.CommandTree(client)
is_internal = True if config['client']['is_internal'] == 'True' else False
invalid_responses = [
	'empty_response',
	'error'
]

link_lookup_functions = [
	astro.Global.lookup_song,
	astro.Global.lookup_collection,
	astro.Global.lookup_song,
	astro.Global.lookup_collection,
	astro.Global.lookup_song,
	astro.Global.lookup_song,
	astro.Global.lookup_collection,
	astro.Global.lookup_song,
	astro.Global.lookup_collection,
	astro.Global.lookup_song,
	astro.Global.lookup_collection,
	astro.Global.lookup_song
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



@client.event
async def on_message(message):
	if message.author != client.user:
		start_time = current_unix_time_ms()
		urls = find_urls(message.content)
		data = get_data_from_urls(urls)

		embeds = []
		
		tasks = []

		if data != []:
			#await add_reactions(message, ['❗'])
			#await message.channel.typing()
			for entry in data:
				media_type = entry['media']
				media_id = entry['id']
				media_country_code = entry['country_code']
				tasks.append(
					create_task(link_lookup_functions[types.index(media_type)](link_lookup_function_objects[types.index(media_type)], media_id, media_country_code))
				)
				
			results = await gather(*tasks)
			for result in results:
				embeds.append(
				create_embed(
					command = 'link',
					media_object = result,
					user = message.author
				)
			)

		else:
			return
		
		while None in embeds:
			embeds.remove(None)
		
		if embeds != []:
			message_embed = await message.reply(embeds = embeds, mention_author = False)
			end_time = current_unix_time_ms()
			total_time = end_time - start_time
			print(f'Finished in {total_time}ms')
			await add_reactions(message_embed, ['👍','👎'])
		else:
			await add_reactions(message, ['🤷'])



@tree.command(name = 'searchsong', description = 'Search for a song on all major platforms')
@app_commands.describe(artist = 'The name of the artist of the song you want to search (ex. "Billie Eilish")')
@app_commands.describe(title = 'The title of the song you want to search (ex. "LUNCH")')
@app_commands.describe(from_album = 'The album, EP or collection of the song you want to search, helps with precision (ex. "HIT ME HARD AND SOFT")')
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
	embed = await interaction.followup.send(
		embed = create_embed(
			command = 'search',
			media_object = song,
			user = interaction.user
		)
	)
	end_time = current_unix_time_ms()
	total_time = end_time - start_time
	print(f'Finished in {total_time}ms')
	if song.type not in invalid_responses:
		await add_reactions(embed, ['👍','👎'])



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
	embed = await interaction.followup.send(
		embed = create_embed(
			command = 'search',
			media_object = collection,
			user = interaction.user
		)
	)
	end_time = current_unix_time_ms()
	total_time = end_time - start_time
	print(f'Finished in {total_time}ms')
	if collection.type not in invalid_responses:
		await add_reactions(embed, ['👍','👎'])



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
	embed = create_embed(
		command = 'search',
		media_object = media_object,
		user = interaction.user
	)
	embed = await interaction.followup.send(
		embed = embed
	)
	end_time = current_unix_time_ms()
	total_time = end_time - start_time
	print(f'Finished in {total_time}ms')
	if media_object.type not in invalid_responses:
		await add_reactions(embed, ['👍','👎'])



@tree.command(name = 'snoop', description = 'Get the track you or another user is listening to on Spotify')
@app_commands.describe(user = 'The user you want to snoop on, defaults to you if left empty')
@app_commands.describe(ephemeral = 'Whether the executed command should be ephemeral (only visible to you), false by default')
@app_commands.guild_install()
@app_commands.allowed_contexts(guilds = True, dms = False, private_channels = True)
async def snoop(interaction: discord.Interaction, user: discord.Member = None, ephemeral: bool = False):
	start_time = current_unix_time_ms()
	await interaction.response.defer(ephemeral = ephemeral)

	if user == None:
		user = interaction.user

	guild = client.get_guild(interaction.guild.id)
	member = guild.get_member(user.id)
	replied = False

	for activity in member.activities:
		if isinstance(activity, Spotify):
			identifier = str(activity.track_id)
	
	song = await astro.Global.lookup_song(
		service = astro.Spotify,
		id = identifier
	)
	embed = await interaction.followup.send(
		embed = create_embed(
			command = 'snoop',
			media_object = song,
			user = user
		)
	)
	end_time = current_unix_time_ms()
	total_time = end_time - start_time
	print(f'Finished in {total_time}ms')
	if song.type not in invalid_responses:
		await add_reactions(embed, ['👍','👎'])

	



client.run(config['tokens']['internal_token'])