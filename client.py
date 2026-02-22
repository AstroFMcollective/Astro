import discord
from discord.ext import commands as ext_commands, tasks
from discord import Spotify
from random import randint
from asyncio import create_task, gather

from AstroDiscord.components.ini import config, tokens, presence, stats
from AstroDiscord.components import *
from AstroDiscord.components.url_tools import url_tools
from AstroDiscord.components.time import current_unix_time
from AstroDiscord.components.commands.request_counting import reset, client_latency, failed_request, successful_request, api_latency

# Use ext_commands here instead!
class AstroClient(ext_commands.AutoShardedBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.synced = False
        self.app_start_time = current_unix_time()
        self.api = AstroAPI()

    async def setup_hook(self):
        print("[AstroDiscord] Loading extensions...")
        
        # Load your cogs here
        extensions = [
            "AstroDiscord.components.commands.search_lyric",
            "AstroDiscord.components.commands.core_music"
        ]
        
        for ext in extensions:
            try:
                await self.load_extension(ext)
                print(f"[AstroDiscord] Loaded extension {ext}")
            except Exception as e:
                print(f"[AstroDiscord] Failed to load extension {ext}: {e}")
        
        # Sync the app commands (slash commands) to Discord
        await self.tree.sync()
        self.synced = True
        print("[AstroDiscord] Extensions loaded and commands synced!")

    async def on_ready(self):
        await self.wait_until_ready()
        if not discord_presence.is_running():
            discord_presence.start()
        if not dashboard.is_running():
            dashboard.start()
        if not reset_today_stats.is_running():
            reset_today_stats.start()
        print(f'[AstroDiscord] Logged in as {self.user} (ID: {self.user.id})')
        print('[AstroDiscord] Ready!')

    async def on_message(self, message):
        start_time = current_unix_time_ms()
        
        if message.guild is not None:
            permissions = message.channel.permissions_for(message.guild.me)
            if not permissions.read_message_history:
                return # Abort if we don't have permission to read message history

        async def auto_link_lookup(data):
            embed_composer = EmbedComposer()
            response = await message.reply(embed=embed_composer.generic_loading, mention_author=False)

            self_object = await self.api.get_self(
                data['type'], data['id'], data['service'], data['country_code']
            )

            if 'type' in self_object:
                # First stage - Get baseline data
                await embed_composer.compose(message.author, self_object, 'link', False, False, True)
                response = await response.edit(embed=embed_composer.embed, view=embed_composer.button_view)

                # Second stage - Global Interface data
                global_object = await self.api.lookup(
                    data['type'], data['id'], data['service'], data['country_code']
                )

                if 'type' in global_object:
                    await embed_composer.compose(message.author, global_object, 'link', False, False, True)
                    response = await response.edit(embed=embed_composer.embed, view=embed_composer.button_view)

                    # Third stage - AI check
                    ai_check = await self.api.snitch(global_object)

                    if 'type' in ai_check:
                        await embed_composer.compose(message.author, ai_check, 'link', False, False)
                        response = await response.edit(embed=embed_composer.embed, view=embed_composer.button_view)
                        successful_request()
                        api_latency(self_object['meta']['processing_time'][data['service']] + global_object['meta']['processing_time']['global_io'] + ai_check['meta']['processing_time']['global_io'])
                        await embed_composer.compose(message.author, ai_check, 'link', True, False)
                        await log([embed_composer.embed], [ai_check], 'Auto Link Lookup', f"type:`{data['type']}` id:`{data['id']}` service:`{data['service']}` country_code:`{data['country_code']}`", current_unix_time_ms() - start_time, embed_composer.button_view)
                    else:
                        await embed_composer.compose(message.author, global_object, 'link', False, False)
                        response = await response.edit(embed=embed_composer.embed, view=embed_composer.button_view)
                        successful_request()
                        api_latency(self_object['meta']['processing_time'][data['service']] + global_object['meta']['processing_time']['global_io'])
                        await embed_composer.compose(message.author, global_object, 'link', True, False)
                        await log([embed_composer.embed], [global_object], 'Auto Link Lookup', f"type:`{data['type']}` id:`{data['id']}` service:`{data['service']}` country_code:`{data['country_code']}`", current_unix_time_ms() - start_time, embed_composer.button_view)
                else:
                    failed_request()
                    await message.delete()
                    await log_catastrophe('Auto Link Lookup', f"type:`{data['type']}` id:`{data['id']}` service:`{data['service']}` country_code:`{data['country_code']}`", 'HTTP error when talking to Astro API (Global stage)')
            else:
                failed_request()
                await log_catastrophe('Auto Link Lookup', f"type:`{data['type']}` id:`{data['id']}` service:`{data['service']}` country_code:`{data['country_code']}`", 'HTTP error when talking to Astro API (Baseline stage)')

        if message.author != self.user:
            try:
                media_data = []
                urls = await url_tools.get_urls_from_string(message.content)
                for url in urls:
                    metadata = await url_tools.get_metadata_from_url(url)
                    if metadata != None:
                        media_data.append(metadata)
                if media_data != []:
                    tasks_list = []
                    for data in media_data:
                        if data['id'] != None and data['type'] != None:
                            tasks_list.append(create_task(auto_link_lookup(data)))
                    await gather(*tasks_list)
                else: 
                    return
            except Exception as error:
                failed_request()
                await log_catastrophe('Auto Link Lookup', f'urls:`{await url_tools.get_urls_from_string(message.content)}`', error)
            client_latency(current_unix_time_ms() - start_time)


# --- Global Variables & Initialization ---
version = config['client']['version']
service = 'discord'
component = 'Discord Client'
deployment_channel = config['client']['deployment_channel']

intents = discord.Intents.all()
intents.message_content = True
intents.presences = True
intents.members = True

# Instantiate the bot (prefix is required by commands.Bot but we mainly use tree/slash commands)
client = AstroClient(
    command_prefix="a!",
    shard_count=int(config['client']['shards']),
    intents=intents
)

# --- Tasks ---
@tasks.loop(seconds=60)
async def discord_presence():
    await client.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening,
            name=presence[randint(0, len(presence)-1)],
        )
    )

@tasks.loop(seconds=86400)
async def reset_today_stats():
    reset()

@tasks.loop(seconds=60)
async def dashboard():
    embed = discord.Embed(
        title='ASTRO DASHBOARD',
        colour=0x6ae70e
    )
    embed.add_field(name='About', value=f"Version: `{version}`\nDeployment channel: `{deployment_channel}`\nShards: `{config['client']['shards']}`", inline=False)
    embed.add_field(name='Stats', value=f"Servers: `{len(client.guilds)}`\nAccessible users: `{len(client.users)}`", inline=False)
    embed.add_field(name='Start time', value=f"<t:{client.app_start_time}:F>", inline=True)
    embed.add_field(name='Last refreshed', value=f"<t:{current_unix_time()}:F>", inline=True)
    embed.add_field(name='Average latency today', value=f"API latency: `{stats['runtime']['avg_api_latency']}` ms\nClient latency: `{stats['runtime']['avg_client_latency']}` ms", inline=False)
    embed.add_field(name='Requests today', value=f"Total requests: `{int(stats['runtime']['successful_requests']) + int(stats['runtime']['failed_requests'])}`\nSuccessful requests: `{stats['runtime']['successful_requests']}`\nFailed requests: `{stats['runtime']['failed_requests']}`", inline=True)
    embed.add_field(name='Lifetime requests', value=f"Total requests: `{int(stats['lifetime']['total_successful_requests']) + int(stats['lifetime']['total_failed_requests'])}`\nSuccessful requests: `{stats['lifetime']['total_successful_requests']}`\nFailed requests: `{stats['lifetime']['total_failed_requests']}`", inline=True)
    
    try:
        server = await client.fetch_guild(tokens['dashboard']['astro_server_id'])
        channel = await server.fetch_channel(tokens['dashboard']['dashboard_channel_id'])
        dash = await channel.fetch_message(str(tokens['dashboard']['dashboard_message_id']))
        await dash.edit(embed=embed)
        print('[AstroDiscord] Dashboard refreshed')
    except:
        print('[AstroDiscord] Dashboard refresh failed, creating new one as fallback')
        server = await client.fetch_guild(tokens['dashboard']['astro_server_id'])
        channel = await server.fetch_channel(tokens['dashboard']['dashboard_channel_id'])
        message = await channel.send(embed=embed)
        tokens.set('dashboard', 'dashboard_message_id', str(message.id))
        with open('AstroDiscord/tokens.ini', 'w') as token_file:
            tokens.write(token_file)
        print('[AstroDiscord] New dashboard created')


if __name__ == '__main__':
    reset()
    client.run(tokens['tokens'][deployment_channel])