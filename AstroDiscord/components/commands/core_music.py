import discord
from discord import app_commands, Spotify
from discord.ext import commands
from asyncio import create_task, gather

from AstroDiscord.components.api_caller import AstroAPI
from AstroDiscord.components.embed_composer import EmbedComposer
from AstroDiscord.components.url_tools import url_tools
from AstroDiscord.components.time import current_unix_time_ms
from AstroDiscord.components.log import log, log_catastrophe
import AstroDiscord.components.commands.request_counting as request_counting
from AstroDiscord.components.paginator import PaginatorView

class CoreMusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api = AstroAPI()
        
        # Define the context menu object
        self.ctx_menu = app_commands.ContextMenu(
            name='Search music link(s)',
            callback=self.context_menu_lookup
        )
        self.bot.tree.add_command(self.ctx_menu)

    async def cog_unload(self) -> None:
        self.bot.tree.remove_command(self.ctx_menu.name, type=self.ctx_menu.type)

    @app_commands.command(name='searchsong', description='Search for a song on all major platforms')
    @app_commands.describe(artist='The name of the artist of the song you want to search (ex. "Tyler, The Creator")')
    @app_commands.describe(title='The title of the song you want to search (ex. "NEW MAGIC WAND")')
    @app_commands.describe(from_album='The album, EP or collection of the song you want to search, helps with precision (ex. "IGOR")')
    @app_commands.describe(is_explicit='Whether the song you want to search has explicit content')
    @app_commands.describe(country_code='The country code of the country in which you want to search, US by default')
    @app_commands.describe(censor='Whether you want to censor the title of the song or not')
    @discord.app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def searchsong(self, interaction: discord.Interaction, artist: str, title: str, from_album: str = None, is_explicit: bool = None, country_code: str = 'us', censor: bool = False):
        start_time = current_unix_time_ms()
        if interaction.data.get("integration_owners", {}).get("1") is not None:
            censor = True
        await interaction.response.defer()
        embed_composer = EmbedComposer()
        
        try:
            json_resp = await self.api.search_song(artist, title, from_album, is_explicit, country_code)
            ai_report = None
            if 'type' in json_resp:
                await embed_composer.compose(interaction.user, json_resp, 'searchsong', False, censor, True)
                response = await interaction.followup.send(embed=embed_composer.embed, view=embed_composer.button_view)

                try:
                    ai_report = await self.api.snitch(json_resp)
                    await embed_composer.compose(interaction.user, ai_report, 'searchsong', False, censor)
                except:
                    await embed_composer.compose(interaction.user, json_resp, 'searchsong', False, censor)

                await response.edit(embed=embed_composer.embed, view=embed_composer.button_view)
                
                request_counting.successful_request()
                latency = json_resp['meta']['processing_time']['global_io']
                if ai_report and 'type' in ai_report: 
                    latency += ai_report['meta']['processing_time']['global_io']
                request_counting.api_latency(latency)
                
                # Anonymize before logging
                if ai_report and 'type' in ai_report:
                    await embed_composer.compose(interaction.user, ai_report, 'searchsong', anonymous=True, censor=censor)
                else:
                    await embed_composer.compose(interaction.user, json_resp, 'searchsong', anonymous=True, censor=censor)
                    
            elif json_resp == {}:
                await embed_composer.error(204)
                await interaction.followup.send(embed=embed_composer.embed)
                request_counting.failed_request()
            else:
                await embed_composer.error(json_resp['status'])
                await interaction.followup.send(embed=embed_composer.embed)
                request_counting.failed_request()

            await log([embed_composer.embed], [json_resp], 'searchsong', f'artist:`{artist}` title:`{title}` from_album:`{from_album}` is_explicit:`{is_explicit}` country_code:`{country_code}` censor:`{censor}`', current_unix_time_ms() - start_time, embed_composer.button_view)
        except Exception as error:
            await embed_composer.error('other')
            await interaction.followup.send(embed=embed_composer.embed)
            request_counting.failed_request()
            await log_catastrophe('searchsong', f'artist:`{artist}` title:`{title}` from_album:`{from_album}` is_explicit:`{is_explicit}` country_code:`{country_code}` censor:`{censor}`', error)
        
        request_counting.client_latency(current_unix_time_ms() - start_time)


    @app_commands.command(name='searchalbum', description='Search for an album')
    @app_commands.describe(artist='The artist of the album you want to search (ex. "Kendrick Lamar")')
    @app_commands.describe(title='The title of the album you want to search (ex. "To Pimp A Butterfly")')
    @app_commands.describe(year='The release year of the album you want to search')
    @app_commands.describe(country_code='The country code of the country in which you want to search, US by default')
    @discord.app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def searchalbum(self, interaction: discord.Interaction, artist: str, title: str, year: int = None, country_code: str = 'us', censor: bool = False):
        start_time = current_unix_time_ms()
        if interaction.data.get("integration_owners", {}).get("1") is not None:
            censor = True
        await interaction.response.defer()
        embed_composer = EmbedComposer()

        try:
            json_resp = await self.api.search_album(artist, title, year, country_code)
            ai_report = None
            if 'type' in json_resp:
                await embed_composer.compose(interaction.user, json_resp, 'searchalbum', False, censor, True)
                response = await interaction.followup.send(embed=embed_composer.embed, view=embed_composer.button_view)

                try:
                    ai_report = await self.api.snitch(json_resp)
                    await embed_composer.compose(interaction.user, ai_report, 'searchalbum', False, censor)
                except:
                    await embed_composer.compose(interaction.user, json_resp, 'searchalbum', False, censor)

                await response.edit(embed=embed_composer.embed, view=embed_composer.button_view)

                request_counting.successful_request()
                latency = json_resp['meta']['processing_time']['global_io']
                if ai_report and 'type' in ai_report: 
                    latency += ai_report['meta']['processing_time']['global_io']
                request_counting.api_latency(latency)
                
                # Anonymize before logging
                if ai_report and 'type' in ai_report:
                    await embed_composer.compose(interaction.user, ai_report, 'searchalbum', anonymous=True, censor=censor)
                else:
                    await embed_composer.compose(interaction.user, json_resp, 'searchalbum', anonymous=True, censor=censor)
                    
            elif json_resp == {}:
                await embed_composer.error(204)
                await interaction.followup.send(embed=embed_composer.embed)
                request_counting.failed_request()
            else:
                await embed_composer.error(json_resp['status'])
                await interaction.followup.send(embed=embed_composer.embed)
                request_counting.failed_request()

            await log([embed_composer.embed], [json_resp], 'searchalbum', f'artist:`{artist}` title:`{title}` year:`{year}` country_code:`{country_code}` censor:`{censor}`', current_unix_time_ms() - start_time, embed_composer.button_view)
        except Exception as error:
            await embed_composer.error('other')
            await interaction.followup.send(embed=embed_composer.embed)
            request_counting.failed_request()
            await log_catastrophe('searchalbum', f'artist:`{artist}` title:`{title}` year:`{year}` country_code:`{country_code}` censor:`{censor}`', error)
        
        request_counting.client_latency(current_unix_time_ms() - start_time)


    @app_commands.command(name='search', description='Search a song, music video, album or EP from a query or its link')
    @discord.app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def search(self, interaction: discord.Interaction, query: str, country_code: str = 'us', censor: bool = False):
        start_time = current_unix_time_ms()
        if interaction.data.get("integration_owners", {}).get("1") is not None:
            censor = True
        await interaction.response.defer()
        embed_composer = EmbedComposer()
        json_resp = {}
        
        try:
            metadata = await url_tools.get_metadata_from_url(query)
            if metadata == None or (metadata['id'] == None and metadata['type'] == None):
                json_resp = await self.api.search(query, country_code)
            else:
                json_resp = await self.api.lookup(metadata['type'], metadata['id'], metadata['service'], country_code)
                
            ai_report = None
            if 'type' in json_resp:
                await embed_composer.compose(interaction.user, json_resp, 'search', False, censor, True)
                response = await interaction.followup.send(embed=embed_composer.embed, view=embed_composer.button_view)

                try:
                    ai_report = await self.api.snitch(json_resp)
                    await embed_composer.compose(interaction.user, ai_report, 'search', False, censor)
                except:
                    await embed_composer.compose(interaction.user, json_resp, 'search', False, censor)
                    
                await response.edit(embed=embed_composer.embed, view=embed_composer.button_view)
                request_counting.successful_request()
                latency = json_resp['meta']['processing_time']['global_io']
                if ai_report and 'type' in ai_report: 
                    latency += ai_report['meta']['processing_time']['global_io']
                request_counting.api_latency(latency)
                
                # Anonymize before logging
                if ai_report and 'type' in ai_report:
                    await embed_composer.compose(interaction.user, ai_report, 'search', anonymous=True, censor=censor)
                else:
                    await embed_composer.compose(interaction.user, json_resp, 'search', anonymous=True, censor=censor)
                    
            elif json_resp == {}:
                await embed_composer.error(204)
                await interaction.followup.send(embed=embed_composer.embed)
                request_counting.failed_request()
            else:
                await embed_composer.error(json_resp.get('status', 204))
                await interaction.followup.send(embed=embed_composer.embed)
                request_counting.failed_request()

            await log([embed_composer.embed], [json_resp], 'search', f'query:`{query}` country_code:`{country_code}` censor:`{censor}`', current_unix_time_ms() - start_time, embed_composer.button_view)
        except Exception as error:
            await embed_composer.error('other')
            await interaction.followup.send(embed=embed_composer.embed)
            request_counting.failed_request()
            print(f'[AstroDiscord] Undocumented error in search has occurred: {error}')
            
        request_counting.client_latency(current_unix_time_ms() - start_time)


    @app_commands.command(name='snoop', description="Get yours or someone else's currently playing song on Spotify")
    @discord.app_commands.allowed_installs(guilds=True, users=False)
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
    async def snoop(self, interaction: discord.Interaction, user: discord.Member = None, ephemeral: bool = False, country_code: str = 'us', censor: bool = False):
        start_time = current_unix_time_ms()
        if interaction.data.get("integration_owners", {}).get("1") is not None:
            censor = True
        await interaction.response.defer(ephemeral=ephemeral)
        embed_composer = EmbedComposer()
        
        try:
            if user == None:
                user = interaction.user
            identifier = None
            guild = self.bot.get_guild(interaction.guild.id)
            member = guild.get_member(user.id)

            for activity in member.activities:
                if isinstance(activity, Spotify):
                    identifier = str(activity.track_id)
                    break
            
            if identifier == None:
                person = 'You are' if interaction.user == user else 'This person is'
                grammar = 'have' if interaction.user == user else 'has'
                await embed_composer.error(400, {
                    'title': "No Spotify listening activity detected.",
                    'description': f'{person} not listening to a Spotify track, or {grammar} Spotify activity disabled in Discord settings.',
                    'meaning': 'Bad request'
                })
                await interaction.followup.send(embed=embed_composer.embed)
                request_counting.failed_request()
            else:
                json_resp = await self.api.lookup('song', identifier, 'spotify', country_code)	
                ai_report = None
                if 'type' in json_resp:
                    await embed_composer.compose(user, json_resp, 'snoop', False, censor, True)
                    response = await interaction.followup.send(embed=embed_composer.embed, view=embed_composer.button_view)

                    try:
                        ai_report = await self.api.snitch(json_resp)
                        await embed_composer.compose(interaction.user, ai_report, 'snoop', False, censor)
                    except:
                        await embed_composer.compose(interaction.user, json_resp, 'snoop', False, censor)

                    await response.edit(embed=embed_composer.embed, view=embed_composer.button_view)		
                    request_counting.successful_request()
                    latency = json_resp['meta']['processing_time']['global_io']
                    if ai_report and 'type' in ai_report: 
                        latency += ai_report['meta']['processing_time']['global_io']
                    request_counting.api_latency(latency)
                    
                    # Anonymize before logging
                    if ai_report and 'type' in ai_report:
                        await embed_composer.compose(interaction.user, ai_report, 'snoop', anonymous=True, censor=censor)
                    else:
                        await embed_composer.compose(interaction.user, json_resp, 'snoop', anonymous=True, censor=censor)
                        
                elif json_resp == {}:
                    await embed_composer.error(204)
                    await interaction.followup.send(embed=embed_composer.embed)
                    request_counting.failed_request()
                else:
                    await embed_composer.error(json_resp['status'])
                    await interaction.followup.send(embed=embed_composer.embed)
                    request_counting.failed_request()
                
                await log([embed_composer.embed], [json_resp], 'snoop', f"user:`{'self' if user == interaction.user else 'member'}` ephemeral:`{ephemeral}` country_code:`{country_code}` censor:`{censor}`", current_unix_time_ms() - start_time, embed_composer.button_view)
        except Exception as error:
            await embed_composer.error('other')
            await interaction.followup.send(embed=embed_composer.embed)
            request_counting.failed_request()
            await log_catastrophe('snoop', f"user:`{'self' if user == interaction.user else 'member'}` ephemeral:`{ephemeral}` country_code:`{country_code}` censor:`{censor}`", error)
            
        request_counting.client_latency(current_unix_time_ms() - start_time)


    @app_commands.command(name='coverart', description='Get the cover art of a song or album')
    @discord.app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def coverart(self, interaction: discord.Interaction, link: str, country_code: str = 'us', censor: bool = False):
        start_time = current_unix_time_ms()
        if interaction.data.get("integration_owners", {}).get("1") is not None:
            censor = True
        await interaction.response.defer()
        embed_composer = EmbedComposer()
        
        try:
            metadata = await url_tools.get_metadata_from_url(link)
            if metadata != None and metadata['id'] != None and metadata['type'] != None:
                json_resp = await self.api.lookup(metadata['type'], metadata['id'], metadata['service'], metadata['country_code'] or country_code)
                ai_report = None
                if 'type' in json_resp:
                    await embed_composer.compose(interaction.user, json_resp, 'coverart', False, censor, True)
                    response = await interaction.followup.send(embed=embed_composer.embed, view=embed_composer.button_view)

                    try:
                        ai_report = await self.api.snitch(json_resp)
                        await embed_composer.compose(interaction.user, ai_report, 'coverart', False, censor)
                    except:
                        await embed_composer.compose(interaction.user, json_resp, 'coverart', False, censor)
                    
                    await response.edit(embed=embed_composer.embed, view=embed_composer.button_view)
                    request_counting.successful_request()
                    latency = json_resp['meta']['processing_time']['global_io']
                    if ai_report and 'type' in ai_report: 
                        latency += ai_report['meta']['processing_time']['global_io']
                    request_counting.api_latency(latency)
                    
                    # Anonymize before logging
                    if ai_report and 'type' in ai_report:
                        await embed_composer.compose(interaction.user, ai_report, 'coverart', anonymous=True, censor=censor)
                    else:
                        await embed_composer.compose(interaction.user, json_resp, 'coverart', anonymous=True, censor=censor)
                        
                elif json_resp == {}:
                    await embed_composer.error(204)
                    await interaction.followup.send(embed=embed_composer.embed)
                    request_counting.failed_request()
                else:
                    await embed_composer.error(json_resp['status'])
                    await interaction.followup.send(embed=embed_composer.embed)
                    request_counting.failed_request()
                
                await log([embed_composer.embed], [json_resp], 'coverart', f'link:`{link}` country_code:`{country_code}` censor:`{censor}`', current_unix_time_ms() - start_time, embed_composer.button_view)
            else:
                await embed_composer.error(400, {
                    'title': "Invalid link provided.",
                    'description': 'This command only works with media from supported services.',
                    'meaning': 'Bad request'
                })
                await interaction.followup.send(embed=embed_composer.embed)
                request_counting.failed_request()
        except Exception as error:
            await embed_composer.error('other')
            await interaction.followup.send(embed=embed_composer.embed)
            request_counting.failed_request()
            await log_catastrophe('coverart', f'link:`{link}` country_code:`{country_code}` censor:`{censor}`', error)
            
        request_counting.client_latency(current_unix_time_ms() - start_time)


    @app_commands.command(name='knowledge', description='Get some basic information about a song')
    @discord.app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def knowledge(self, interaction: discord.Interaction, query: str, country_code: str = 'us', censor: bool = False):
        start_time = current_unix_time_ms()
        if interaction.data.get("integration_owners", {}).get("1") is not None:
            censor = True
        await interaction.response.defer()
        embed_composer = EmbedComposer()
        
        try:
            metadata = await url_tools.get_metadata_from_url(query)
            if metadata == None or (metadata['id'] == None and metadata['type'] == None):
                json_resp = await self.api.search_knowledge(query, country_code)
            else:
                json_resp = await self.api.lookup_knowledge(metadata['id'], metadata['service'], country_code)
                
            if 'type' in json_resp:
                await embed_composer.compose(interaction.user, json_resp, 'knowledge', False, censor, True)
                response = await interaction.followup.send(embed=embed_composer.embed, view=embed_composer.button_view)

                try:
                    ai_report = await self.api.snitch(json_resp)
                    await embed_composer.compose(interaction.user, ai_report, 'knowledge', False, censor)
                except:	
                    await embed_composer.compose(interaction.user, json_resp, 'knowledge', False, censor)

                await response.edit(embed=embed_composer.embed, view=embed_composer.button_view)
                request_counting.successful_request()
                request_counting.api_latency(json_resp['meta']['processing_time']['global_io'])
                
                # Anonymize before logging
                try: # Re-try accessing ai_report just in case
                    if ai_report and 'type' in ai_report:
                        await embed_composer.compose(interaction.user, ai_report, 'knowledge', anonymous=True, censor=censor)
                    else:
                        await embed_composer.compose(interaction.user, json_resp, 'knowledge', anonymous=True, censor=censor)
                except NameError:
                    await embed_composer.compose(interaction.user, json_resp, 'knowledge', anonymous=True, censor=censor)

            elif json_resp == {}:
                await embed_composer.error(204)
                await interaction.followup.send(embed=embed_composer.embed)
                request_counting.failed_request()
            else:
                await embed_composer.error(json_resp['status'])
                await interaction.followup.send(embed=embed_composer.embed)
                request_counting.failed_request()
                
            await log([embed_composer.embed], [json_resp], 'knowledge', f'query:`{query}` country_code:`{country_code}` censor:`{censor}`', current_unix_time_ms() - start_time, embed_composer.button_view)
        except Exception as error:
            await embed_composer.error('other')
            await interaction.followup.send(embed=embed_composer.embed)
            request_counting.failed_request()
            await log_catastrophe('knowledge', f'query:`{query}` country_code:`{country_code}` censor:`{censor}`', error)
            
        request_counting.client_latency(current_unix_time_ms() - start_time)

    @discord.app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def context_menu_lookup(self, interaction: discord.Interaction, message: discord.Message):
        start_time = current_unix_time_ms()
        media_data = []
        embeds = []
        buttons = []
        censor = interaction.data.get("integration_owners", {}).get("1") is not None
        
        await interaction.response.defer()

        async def context_menu_link_lookup(data):
            embed_composer = EmbedComposer()
            log_composer = EmbedComposer() # Use a separate composer so logs don't overwrite user output
            
            global_object = await self.api.lookup(data['type'], data['id'], data['service'], data['country_code'])

            if 'type' in global_object:
                try:
                    ai_check = await self.api.snitch(global_object)
                    if 'type' in ai_check:
                        # Append the regular (non-anonymous) embed to the message list
                        await embed_composer.compose(message.author, ai_check, 'link', False, False)
                        
                        request_counting.successful_request()
                        request_counting.api_latency(global_object['meta']['processing_time']['global_io'] + ai_check['meta']['processing_time']['global_io'])
                        
                        # Use the log composer to create the anonymous log
                        await log_composer.compose(message.author, ai_check, 'link', anonymous=True, censor=False)
                        await log([log_composer.embed], [ai_check], 'Auto Link Lookup', f"type:`{data['type']}` id:`{data['id']}` service:`{data['service']}` country_code:`{data['country_code']}`", current_unix_time_ms() - start_time, embed_composer.button_view)
                    else:
                        raise Exception("Fallback to normal")
                except:
                    # Append the regular (non-anonymous) embed to the message list
                    await embed_composer.compose(message.author, global_object, 'link', False, False)
                    
                    request_counting.successful_request()
                    request_counting.api_latency(global_object['meta']['processing_time']['global_io'])
                    
                    # Use the log composer to create the anonymous log
                    await log_composer.compose(message.author, global_object, 'link', anonymous=True, censor=False)
                    await log([log_composer.embed], [global_object], 'Search music link(s)', f"type:`{data['type']}` id:`{data['id']}` service:`{data['service']}` country_code:`{data['country_code']}`", current_unix_time_ms() - start_time, embed_composer.button_view)
                
                embeds.append(embed_composer.embed)
                buttons.append(embed_composer.button_view)
            else:
                request_counting.failed_request()

        try:
            urls = await url_tools.get_urls_from_string(message.content)
            if not urls:
                embed_composer = EmbedComposer()
                await embed_composer.error(400, {'title': "No links provided.", 'description': 'No supported links detected.', 'meaning': 'Bad request'})
                await interaction.followup.send(embed=embed_composer.embed)
                request_counting.failed_request()
                request_counting.client_latency(current_unix_time_ms() - start_time)
                return
                
            for url in urls:
                metadata = await url_tools.get_metadata_from_url(url)
                if metadata: media_data.append(metadata)
                
            if media_data:
                tasks_list = [create_task(context_menu_link_lookup(data)) for data in media_data if data['id'] and data['type']]
                if tasks_list:
                    await gather(*tasks_list)
                    if embeds:
                        if len(embeds) == 1:
                            await interaction.followup.send(embed=embeds[0], view=buttons[0])
                        else:
                            pagination = PaginatorView(embeds=embeds, button_views=buttons)
                            pagination.message = await interaction.followup.send(embed=pagination.initial_embed, view=pagination)
                    else:
                        embed_composer = EmbedComposer()
                        await embed_composer.error(204)
                        await interaction.followup.send(embed=embed_composer.embed)
                        request_counting.failed_request()
                else:
                    embed_composer = EmbedComposer()
                    await embed_composer.error(400, {'title': "Invalid link(s) provided.", 'description': 'Supported: Spotify, Apple Music, YouTube (Music), Deezer.', 'meaning': 'Bad request'})
                    await interaction.followup.send(embed=embed_composer.embed)
                    request_counting.failed_request()
        except Exception as error:
            embed_composer = EmbedComposer()
            await embed_composer.error('other')
            await interaction.followup.send(embed=embed_composer.embed)
            request_counting.failed_request()
            await log_catastrophe('Search music link(s)', f"urls:`{await url_tools.get_urls_from_string(message.content)}`", error)
            
        request_counting.client_latency(current_unix_time_ms() - start_time)

async def setup(bot):
    await bot.add_cog(CoreMusicCog(bot))