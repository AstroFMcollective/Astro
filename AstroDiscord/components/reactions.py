import discord as discord
import asyncio

async def add_reactions(message: discord.Message, emojis: list):
	try:
		for emoji in emojis:
			await asyncio.sleep(0.25)
			await message.add_reaction(emoji)
	except:
		pass