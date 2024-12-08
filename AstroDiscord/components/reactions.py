import discord as discord
import asyncio

async def add_reactions(message: discord.Message, emojis: list):
	try:
		for emoji in emojis:
			await asyncio.sleep(0.25)
			await message.add_reaction(emoji)
	except:
		pass

async def check_for_reaction(message: discord.Message, reaction_emoji: str):
	if not message.reactions:
		return False
	for reaction in message.reactions:
		if reaction.emoji == reaction_emoji:
			return True
	return False
