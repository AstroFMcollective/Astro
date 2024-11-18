import discord as discord 
from discord import app_commands
from discord import Spotify
from discord.ext import tasks
from AstroDiscord.components.ini import config
from AstroDiscord.components.all import *
import asyncio

from random import randint

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



#@tree.command(name = 'Search song', description = 'Search for a song on all major platforms')
#@app_commands.describe(artist = 'The name of the artist of the track you want to look up (ex. "Billie Eilish")')
#@app_commands.describe(track = 'The title of the track you want to look up (ex. "LUNCH")')
#@app_commands.describe(from_album = 'The album or collection of the track you want to look up, helps with precision (ex. "HIT ME HARD AND SOFT")')
#@app_commands.describe(is_explicit = 'Whether the track you want to look up has explicit content (has the little [E] badge next to its name on streaming platforms), helps with precision')
#@app_commands.guild_install()
#@app_commands.user_install()
#@app_commands.allowed_contexts(guilds = True, dms = True, private_channels = True)
#async def searchsong(interaction: discord.Interaction, artist: str, track: str, from_album: str = None, is_explicit: bool = None):



client.run(config['tokens']['internal_token'])