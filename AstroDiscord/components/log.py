import discord as discord
from discord import Webhook
from AstroAPI.components.ini import config, keys, text
from AstroDiscord.components.ini import config as discord_config
import aiohttp

async def log(log_embeds: list[discord.Embed], media: list[object], command: str, parameters: str, latency: int):
	async with aiohttp.ClientSession() as session:
		deployment_channel = discord_config['client']['deployment_channel']
		invalid_responses = [
			'empty_response',
			'error'
		]

		embeds = []

		api_latency = 0
		for obj in media:
			if obj.type not in invalid_responses:
				api_latency += obj.meta.processing_time['global']
		
		if api_latency != 0:
			api_latency = api_latency // len(media)

		report_type = 'failure'

		for obj in media:
			if obj.type not in invalid_responses and len(obj.url) > 1:
				report_type = 'success'
				break

		report_card = discord.Embed(
			title = f"Astro Client - `{report_type}`",
			description = f"Command executed in `{latency}` ms",
			colour = 0x791a3c,
		)

		report_card.add_field(
			name = "Latency Report",
			value = f"API latency: `{api_latency}` ms\nClient latency: `{latency - api_latency}` ms",
			inline = False
		)
		
		report_card.add_field(
			name="Command",
			value=f"/{command} {parameters}",
			inline = False
		)

		embeds.append(report_card)

		if report_type == 'success':
			for objects in log_embeds:
				if len(media[log_embeds.index(objects)].url) > 1:
					embeds.append(objects)
			
		webhook = Webhook.from_url(url = keys['webhooks'][f'{deployment_channel}_logs'], session = session)
		await webhook.send(embeds = embeds, username = 'Astro Client', avatar_url = config['images']['astro_bg'])
		return