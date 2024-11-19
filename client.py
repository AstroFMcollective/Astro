import discord as discord 
from discord import app_commands
from discord import Spotify
from discord.ext import tasks
from AstroAPI.components.time import *
from AstroDiscord.components.ini import config
from AstroDiscord.components import *
import asyncio

from random import randint

from AstroAPI.components.time import *
import AstroAPI as astro


class Client(discord.Client):
	def __init__(self):
		discordintents = discord.Intents.all()
		discordintents.message_content = True
		discordintents.presences = True
		discordintents.members = True
		super().__init__(intents = discordintents)
		self.synced = False



version = 'PRE-a2.0'
client = Client()
tree = app_commands.CommandTree(client)
is_internal = True if config['client']['is_internal'] == 'True' else False



@client.event
async def on_ready():
	await client.wait_until_ready()
	if not client.synced:
		await tree.sync()
		client.synced = True





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
		embed = media_embed(
			command = 'search',
			media_object = song,
			user = interaction.user
		)
	)
	end_time = current_unix_time_ms()
	total_time = end_time - start_time
	print(f'Finished in {total_time}ms')
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
		embed = media_embed(
			command = 'search',
			media_object = collection,
			user = interaction.user
		)
	)
	end_time = current_unix_time_ms()
	total_time = end_time - start_time
	print(f'Finished in {total_time}ms')
	await add_reactions(embed, ['👍','👎'])


client.run(config['tokens']['internal_token'])