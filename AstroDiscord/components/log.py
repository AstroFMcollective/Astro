import discord as discord
from discord import Webhook
from AstroDiscord.components.ini import config as discord_config, text as config, tokens as keys
import aiohttp

async def log(log_embeds: list[discord.Embed], media: list[dict], command: str, parameters: str, latency: int, buttons: discord.ui.View):
	async with aiohttp.ClientSession() as session:
		deployment_channel = discord_config['client']['deployment_channel']
		invalid_responses = [
			'empty_response',
			'error'
		]

		embeds = []

		api_latency = 0
		for obj in media:
			if 'type' in obj:
				api_latency += obj['meta']['processing_time']['global_io']

		report_type = 'empty_response'

		for obj in media:
			if 'type' in obj:
				report_type = 'success'
				break
			elif 'details' in obj:
				report_type = 'failure'
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
				embeds.append(objects)
		
		webhook = Webhook.from_url(url = keys['webhooks'][f'{deployment_channel}_logs'], session = session)
		if buttons != None:
			await webhook.send(embeds = embeds, username = 'Astro Client', avatar_url = config['images']['astro_bg'], view = buttons)
		else:
			await webhook.send(embeds = embeds, username = 'Astro Client', avatar_url = config['images']['astro_bg'])
		return



async def log_catastrophe(command: str, parameters: str, error: str):
	async with aiohttp.ClientSession() as session:
		ping = f'<@&1330182469873565749>'
		deployment_channel = discord_config['client']['deployment_channel']
		invalid_responses = [
			'empty_response',
			'error'
		]

		embeds = []

		report_type = 'catastrophe'

		report_card = discord.Embed(
			title = f"Astro Client - `{report_type}`",
			description = f"Client-side command failed irrecoverably",
			colour = 0xeb071e,
		)

		report_card.add_field(
			name = "Error Report",
			value = f"Error: `{error}`",
			inline = False
		)
		
		report_card.add_field(
			name="Command",
			value=f"/{command} {parameters}",
			inline = False
		)

		embeds.append(report_card)
		
		webhook = Webhook.from_url(url = keys['webhooks'][f'{deployment_channel}_logs'], session = session)
		await webhook.send(ping, embeds = embeds, username = 'Astro Client', avatar_url = config['images']['astro_bg'])
		print(f'[AstroDiscord] Undocumented error in on_message has occurred: {error}')
		return