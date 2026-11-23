import discord
from discord import app_commands, Spotify
from discord.ext import commands
from asyncio import create_task, gather

from AstroDiscord.components.api_caller import AstroAPI
from AstroDiscord.components.embed_composer import (
    ASTRO_30L_PERMISSIONS_GUIDE_URL,
    EmbedComposer,
    add_30l_disclaimer_field,
)
from AstroDiscord.components.url_tools import url_tools
from AstroDiscord.components.time import current_unix_time_ms, current_unix_time
from AstroDiscord.components.log import log, log_catastrophe
import AstroDiscord.components.commands.request_counting as request_counting
from AstroDiscord.components.paginator import PaginatorView
from AstroDiscord.components.ini import config, text

TOS_URL = "https://docs.google.com/document/d/1qfNdW0_Gvb3yK52tzd-FGa8TnW9S_cBQnE1-H4i561c/edit?tab=t.0#heading=h.wy2z4bjepw16"
PRIVACY_POLICY_URL = "https://docs.google.com/document/d/1Mm8-Lg1MMYmvYN95XgMjhHoc3J4wbLaTckgIx7s_Igg/edit?tab=t.0#heading=h.t174t5nnt3lg"
SUPPORT_SERVER_URL = "https://discord.gg/F2xaVUv7YX"
REINVITE_URL = "https://discord.com/oauth2/authorize?client_id=1246471351485861967"
LEGAL_LINKS_VALUE = f"[Terms of Service]({TOS_URL}) • [Privacy Policy]({PRIVACY_POLICY_URL})"

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
                await embed_composer.compose(interaction.user, json_resp, 'searchsong', False, censor)
                response = await interaction.followup.send(embed=embed_composer.embed, view=embed_composer.button_view)

                try:
                    ai_report = await self.api.snitch(json_resp)
                except Exception:
                    ai_report = None

                if ai_report:
                    await embed_composer.compose(interaction.user, ai_report, 'searchsong', False, censor)
                    await response.edit(embed=embed_composer.embed, view=embed_composer.button_view)
                
                request_counting.successful_request()
                latency = json_resp.get('meta', {}).get('processing_time_ms', 0)
                if ai_report:
                    latency += ai_report.get('meta', {}).get('processing_time_ms', 0)
                request_counting.api_latency(latency)
                
                # Anonymize before logging
                if ai_report:
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
                await embed_composer.compose(interaction.user, json_resp, 'searchalbum', False, censor)
                response = await interaction.followup.send(embed=embed_composer.embed, view=embed_composer.button_view)

                try:
                    ai_report = await self.api.snitch(json_resp)
                except Exception:
                    ai_report = None

                if ai_report:
                    await embed_composer.compose(interaction.user, ai_report, 'searchalbum', False, censor)
                    await response.edit(embed=embed_composer.embed, view=embed_composer.button_view)

                request_counting.successful_request()
                latency = json_resp.get('meta', {}).get('processing_time_ms', 0)
                if ai_report:
                    latency += ai_report.get('meta', {}).get('processing_time_ms', 0)
                request_counting.api_latency(latency)
                
                # Anonymize before logging
                if ai_report:
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
            if not metadata or (not metadata.get('id') and not metadata.get('type')):
                raw_search = await self.api.search(query, country_code)
                
                # --- NEW REVISED PRIORITIZATION MATRIX ---
                if isinstance(raw_search, dict) and 'meta' in raw_search and 'filter_confidence_percentage' in raw_search['meta']:
                    confidences = raw_search['meta']['filter_confidence_percentage']
                    
                    s_conf = float(confidences.get('songs') or 0)
                    c_conf = float(confidences.get('collections') or 0)
                    m_conf = float(confidences.get('music_videos') or 0)
                    
                    # Sort matrix tuple: (Confidence Score, Priority Weight, Category Name)
                    sorting_matrix = [
                        (s_conf, 3, 'songs'),
                        (m_conf, 2, 'music_videos'),
                        (c_conf, 1, 'collections')
                    ]
                    
                    # Sort descending: Highest confidence score wins. If scores match, highest priority weight wins.
                    sorting_matrix.sort(key=lambda x: (x[0], x[1]), reverse=True)
                    
                    winner_category = sorting_matrix[0][2]
                    max_score = sorting_matrix[0][0]
                    
                    if max_score == 0 and s_conf == 0 and c_conf == 0 and m_conf == 0:
                        json_resp = {} 
                    else:
                        category_data = raw_search.get(winner_category)
                        best_match_item = None
                        
                        if isinstance(category_data, dict):
                            if 'title' in category_data or 'type' in category_data:
                                best_match_item = category_data
                            else:
                                best_match_item = category_data.get('0') or category_data.get(0)
                        elif isinstance(category_data, list) and len(category_data) > 0:
                            best_match_item = category_data[0]
                            
                        if isinstance(best_match_item, dict):
                            if 'type' not in best_match_item:
                                if winner_category == 'songs': best_match_item['type'] = 'track'
                                elif winner_category == 'collections': best_match_item['type'] = 'album'
                                else: best_match_item['type'] = 'music_video'
                                
                            if 'meta' not in best_match_item or not isinstance(best_match_item['meta'], dict):
                                best_match_item['meta'] = {}
                                
                            best_match_item['meta']['processing_time_ms'] = raw_search['meta'].get('processing_time_ms', 0)
                            
                            # Copy the confidence scores to satisfy the search embed lookup
                            if 'filter_confidence_percentage' in raw_search['meta']:
                                best_match_item['filter_confidence_percentage'] = raw_search['meta']['filter_confidence_percentage']
                                best_match_item['meta']['filter_confidence_percentage'] = raw_search['meta']['filter_confidence_percentage']
                                
                            json_resp = best_match_item
                        else:
                            json_resp = {}
                else:
                    json_resp = raw_search if isinstance(raw_search, dict) else {}
            else:
                json_resp = await self.api.lookup(metadata['type'], metadata['id'], metadata['service'], country_code)
                
            # --- STANDARD EMBED CREATION & SNITCH LOGIC ---
            ai_report = None
            if json_resp and 'type' in json_resp:
                await embed_composer.compose(interaction.user, json_resp, 'search', False, censor)
                response = await interaction.followup.send(embed=embed_composer.embed, view=embed_composer.button_view)

                try:
                    # --- payload serialization sanitation ---
                    # create a clean deep copy to remove embedded processing times before posting out
                    sanitized_payload = json_resp.copy()
                    if 'meta' in sanitized_payload:
                        sanitized_payload.pop('meta')
                        
                    ai_report = await self.api.snitch(sanitized_payload)
                except Exception:
                    ai_report = None

                # API COMPLIANT CHECK: Detect by keys or payload presence instead of 'type'
                is_valid_ai_report = ai_report and (any(k in ai_report for k in ('audio_reports', 'image_reports', 'video_reports', 'source_reports')) or 'meta' in ai_report)

                if is_valid_ai_report:
                    await embed_composer.compose(interaction.user, ai_report, 'search', False, censor)
                    await response.edit(embed=embed_composer.embed, view=embed_composer.button_view)
                    
                    request_counting.successful_request()
                    p_time_base = json_resp.get('meta', {}).get('processing_time_ms', 0)
                    p_time_ai = ai_report.get('meta', {}).get('processing_time_ms', 0)
                    request_counting.api_latency(p_time_base + p_time_ai)
                    
                    await embed_composer.compose(interaction.user, ai_report, 'search', anonymous=True, censor=censor)
                    await log([embed_composer.embed], [json_resp], 'search', f'query:`{query}` country_code:`{country_code}` censor:`{censor}`', current_unix_time_ms() - start_time, embed_composer.button_view)
                else:
                    request_counting.successful_request()
                    p_time_base = json_resp.get('meta', {}).get('processing_time_ms', 0)
                    request_counting.api_latency(p_time_base)
                    
                    await embed_composer.compose(interaction.user, json_resp, 'search', anonymous=True, censor=censor)
                    await log([embed_composer.embed], [json_resp], 'search', f'query:`{query}` country_code:`{country_code}` censor:`{censor}`', current_unix_time_ms() - start_time, embed_composer.button_view)
                    
            elif json_resp == {}:
                await embed_composer.error(204)
                await interaction.followup.send(embed=embed_composer.embed)
                request_counting.failed_request()
            else:
                await embed_composer.error(json_resp.get('status', 204))
                await interaction.followup.send(embed=embed_composer.embed)
                request_counting.failed_request()

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
            if user is None:
                user = interaction.user
            identifier = None
            activities = (
                self.bot.get_member_activities(interaction.guild.id, user.id)
                if interaction.guild is not None
                else ()
            )

            for activity in activities:
                if isinstance(activity, Spotify) and activity.track_id:
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
                    await embed_composer.compose(user, json_resp, 'snoop', False, censor)
                    response = await interaction.followup.send(embed=embed_composer.embed, view=embed_composer.button_view)

                    try:
                        ai_report = await self.api.snitch(json_resp)
                    except Exception:
                        ai_report = None

                    if ai_report:
                        await embed_composer.compose(user, ai_report, 'snoop', False, censor)
                        await response.edit(embed=embed_composer.embed, view=embed_composer.button_view)		
                    request_counting.successful_request()
                    latency = json_resp.get('meta', {}).get('processing_time_ms', 0)
                    if ai_report:
                        latency += ai_report.get('meta', {}).get('processing_time_ms', 0)
                    request_counting.api_latency(latency)
                    
                    # Anonymize before logging
                    if ai_report:
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
                    await embed_composer.compose(interaction.user, json_resp, 'coverart', False, censor)
                    response = await interaction.followup.send(embed=embed_composer.embed, view=embed_composer.button_view)

                    try:
                        ai_report = await self.api.snitch(json_resp)
                    except Exception:
                        ai_report = None

                    if ai_report:
                        await embed_composer.compose(interaction.user, ai_report, 'coverart', False, censor)
                        await response.edit(embed=embed_composer.embed, view=embed_composer.button_view)
                    request_counting.successful_request()
                    latency = json_resp.get('meta', {}).get('processing_time_ms', 0)
                    if ai_report:
                        latency += ai_report.get('meta', {}).get('processing_time_ms', 0)
                    request_counting.api_latency(latency)
                    
                    # Anonymize before logging
                    if ai_report:
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
                    if ai_check:
                        # Append the regular (non-anonymous) embed to the message list
                        await embed_composer.compose(message.author, ai_check, 'link', False, False)
                        
                        request_counting.successful_request()
                        request_counting.api_latency(global_object['meta']['processing_time_ms'] + ai_check['meta']['processing_time_ms'])
                        
                        # Use the log composer to create the anonymous log
                        await log_composer.compose(message.author, ai_check, 'link', anonymous=True, censor=False)
                        await log([log_composer.embed], [ai_check], 'Auto Link Lookup', f"type:`{data['type']}` id:`{data['id']}` service:`{data['service']}` country_code:`{data['country_code']}`", current_unix_time_ms() - start_time, embed_composer.button_view)
                    else:
                        raise Exception("Fallback to normal")
                except:
                    # Append the regular (non-anonymous) embed to the message list
                    await embed_composer.compose(message.author, global_object, 'link', False, False)
                    
                    request_counting.successful_request()
                    request_counting.api_latency(global_object['meta']['processing_time_ms'])
                    
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

    async def _run_info_command(self, interaction: discord.Interaction, command_name: str, build_embed):
        """Run an informational slash command with shared defer, footer, stats, and error handling."""
        await interaction.response.defer()
        start_time = current_unix_time_ms()

        try:
            embed = await build_embed()
            embed.set_footer(
                text="Thank you for using Astro!",
                icon_url=text['images']['pfpurl']
            )
            await interaction.followup.send(embed=embed)
            request_counting.successful_request()
        except Exception as error:
            embed_composer = EmbedComposer()
            await embed_composer.error('other')
            await interaction.followup.send(embed=embed_composer.embed)
            request_counting.failed_request()
            await log_catastrophe(command_name, command_name, error)

        request_counting.client_latency(current_unix_time_ms() - start_time)

    @app_commands.command(name='about', description='Get information about Astro and its services')
    @discord.app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def about(self, interaction: discord.Interaction):
        async def build_about_embed():
            bot_version = config['client']['version']
            api_data = await self.api.get_about()

            embed = discord.Embed(
                title="About Astro",
                description="Astro is an open-source, multi-platform music discovery and sharing assistant, designed to connect your music experience seamlessly across services like Spotify, Apple Music, YouTube Music, and Deezer.",
                colour=0xf5c000
            )
            embed.add_field(
                name="Feature suggestions, questions or bug reports?",
                value="Feel free to leave them in our server (link in bio).",
                inline=False
            )
            embed.add_field(
                name="Bot Info",
                value=f"• **Version**: `{bot_version}`\n• **Uptime**: <t:{self.bot.app_start_time}:R> (<t:{self.bot.app_start_time}:f>)",
                inline=True
            )
            if api_data:
                api_version = api_data.get('version', 'Unknown')
                api_uptime = api_data.get('uptime')

                if api_uptime:
                    api_uptime_value = f"<t:{api_uptime}:R> (<t:{api_uptime}:f>)"
                else:
                    api_uptime_value = f"`{api_data.get('uptime_string', 'Unknown')}`"

                embed.add_field(
                    name="API Info",
                    value=f"• **Version**: `{api_version}`\n• **Uptime**: {api_uptime_value}",
                    inline=True
                )
            else:
                embed.add_field(
                    name="API Info",
                    value="• **Status**: `Offline/Error`",
                    inline=True
                )

            embed.add_field(
                name="",
                value=LEGAL_LINKS_VALUE,
                inline=False
            )
            add_30l_disclaimer_field(embed)
            return embed

        await self._run_info_command(interaction, 'about', build_about_embed)

    @app_commands.command(name='3-0l', description='Learn about the upcoming Astro 3.0L update and server permission changes')
    @discord.app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def astro_30l(self, interaction: discord.Interaction):
        async def build_30l_embed():
            embed = discord.Embed(
                title="Astro 3.0L Update",
                description=(
                    "Astro 3.0L is coming soon - the biggest update ever made to Astro. "
                    "The bot has been completely rebuilt from the ground up with cleaner, more streamlined embeds, "
                    "stronger reliability, and the foundation for future features."
                ),
                colour=0xf5c000
            )
            embed.add_field(
                name="What's Changing",
                value=(
                    "- **A new, streamlined design**: Upgraded to Discord's modern Components V2 layout for cleaner, unified, easier-to-read music cards.\n"
                    "- **Persistent pagination**: Auto Link Lookup now uses pagination, and ALL multi-link pagianted results stay interactive forever, and no longer expire after a short timeout.\n"
                    "- **Rebuilt internals**: The whole thing has been redone in JavaScript to take full advantage of all of Discord's features."
                ),
                inline=False
            )
            embed.add_field(
                name="For server moderators",
                value=(
                    "We've revised and expanded Astro's requested server permissions to keep everything working smoothly.\n"
                    f"Please review the **[3.0L Permissions Guide]({ASTRO_30L_PERMISSIONS_GUIDE_URL})** or **[re-add Astro to you server]({REINVITE_URL})**."
                ),
                inline=True
            )
            embed.add_field(
                name="For users & User Apps",
                value=(
                    "All your favorite commands are staying, just faster and cleaner.\n"
                    "No further action is needed."
                ),
                inline=True
            )
            embed.add_field(
                name="Want to try the Astro 3.0L BETA?",
                value=(
                    "Interested in participating in the Astro 3.0L BETA or trying it out before it releases? "
                    f"Join our **[official Discord server]({SUPPORT_SERVER_URL})**!"
                ),
                inline=False
            )
            embed.add_field(
                name="Questions, feedback or privacy?",
                value=(
                    "Astro only retains music links sent to the bot for diagnostics — never message text, server info, or personal data. "
                    f"Have questions? Reach out in our [support server]({SUPPORT_SERVER_URL})."
                ),
                inline=False
            )
            embed.add_field(
                name="",
                value=f"[3.0L Permissions Guide]({ASTRO_30L_PERMISSIONS_GUIDE_URL}) • [Re-add Astro]({REINVITE_URL}) • {LEGAL_LINKS_VALUE}",
                inline=False
            )
            return embed

        await self._run_info_command(interaction, '3-0l', build_30l_embed)

async def setup(bot):
    await bot.add_cog(CoreMusicCog(bot))