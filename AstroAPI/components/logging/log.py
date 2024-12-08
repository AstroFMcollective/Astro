import discord as discord
from discord import Webhook
from AstroAPI.components.ini import config, keys, text
from AstroDiscord.components.ini import config as discord_config
import aiohttp

async def log(media: object):
	async with aiohttp.ClientSession() as session:
		deployment_channel = discord_config['client']['deployment_channel']
		embed = discord.Embed(
			title = f'Astro API - `{media.type}`',
			colour = 0x0097f5,
		)
		embed.add_field(
			name = 'Service',
			value = f'{text['api_tag'][media.service]}',
			inline = False
		)
		if media.type == 'error':
			report = [
				f'HTTP code: `{media.http_code}`'
				f'Error message: `{media.error_msg}`'
			]
			embed.add_field(
				name = 'Report',
				value = f'{'\n'.join(report)}',
				inline = False
			)
			embed.add_field(
				name = 'Request (parameters)',
				value = f'{media.request}',
				inline = False
			)
			
			webhook = Webhook.from_url(url = keys['webhooks'][f'{deployment_channel}_logs'], session = session)
			await webhook.send(embed = embed, username = 'Astro API', avatar_url = config['images']['astro_trans'])
			return

		elif media.type == 'empty_response':
			embed.add_field(
				name = 'Request (parameters)',
				value = f'{media.request}',
				inline = False
			)

			webhook = Webhook.from_url(url = keys['webhooks'][f'{deployment_channel}_logs'], session = session)
			await webhook.send(embed = embed, username = 'Astro API', avatar_url = config['images']['astro_trans'])
			return