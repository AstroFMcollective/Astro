import discord
from discord import app_commands
from discord.ext import commands

from AstroDiscord.components.api_caller import AstroAPI
from AstroDiscord.components.embed_composer import EmbedComposer
import AstroDiscord.components.commands.request_counting as request_counting
from AstroDiscord.components.time import current_unix_time_ms
from AstroDiscord.components.log import log, log_catastrophe

class LyricSearchPagination(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, user: discord.User, songs: list, api: AstroAPI, initial_api_time: int, censor: bool, lyrics: str):
        super().__init__(timeout=300) # 5 minutes timeout
        self.interaction = interaction
        self.user = user
        self.songs = songs
        self.api = api
        self.index = 0
        self.composer = EmbedComposer()
        self.initial_api_time = initial_api_time
        self.censor = censor
        self.lyrics = lyrics
        
        # The list of prompts to cycle through
        self.prompts = [
            'Is this the correct song?',
            'How about this one?',
            'What about this?',
            "Are you sure it's not this one?",
            'How about now?',
            'Maybe this one?',
            'Surely it must be this one, right?',
            'No? Is it maybe this one?',
            "This is tough. Is this maybe what you're looking for?"
        ]

    async def update_message(self, interaction: discord.Interaction):
        if self.index >= len(self.songs):
            # Ran out of songs to display
            await self.composer.error('other', {
                'title': 'End of the line!', 
                'description': 'We ran out of songs to show you. Try adjusting your lyric query.', 
                'meaning': 'No more results'
            })
            await interaction.response.edit_message(embed=self.composer.embed, view=None)
            return

        current_song = self.songs[self.index]
        
        # Inject metadata to prevent KeyError in EmbedComposer for partial objects
        current_song['meta'] = {
            'processing_time': {'global_io': self.initial_api_time},
            'filter_confidence_percentage': {}
        }
        
        await self.composer.compose(self.user, current_song, 'searchsong', censor=self.censor)
        
        # --- SELECTION MODE FORMATTING ---
        # 1. Override the author block with the rotating prompt
        prompt = self.prompts[self.index % len(self.prompts)]
        self.composer.embed.set_author(name=prompt, icon_url=self.user.display_avatar)
        
        # 2. Strip the footer so latency and thank you messages don't show yet
        self.composer.embed.remove_footer()
        
        await interaction.response.edit_message(embed=self.composer.embed, view=self)

    @discord.ui.button(label="Yes, that's the one!", style=discord.ButtonStyle.success)
    async def yes_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Only allow the user who initiated the command to interact
        if interaction.user != self.user:
            return await interaction.response.send_message("This isn't your search!", ephemeral=True)
        
        current_song = self.songs[self.index]

        # --- LOADING MODE ---
        # Edit the embed to look like it's loading, push the Spotify button, and acknowledge the interaction immediately
        current_song['meta'] = {'processing_time': {'global_io': 0}, 'filter_confidence_percentage': {}}
        await self.composer.compose(self.user, current_song, 'searchsong', censor=self.censor, loading=True)
        await interaction.response.edit_message(embed=self.composer.embed, view=self.composer.button_view)

        # Call global_io to get the unified track metadata
        start_time = current_unix_time_ms()
        
        spotify_id = current_song['ids']['spotify']
        global_result = await self.api.lookup('song', spotify_id, 'spotify', country_code='us')

        # Handle errors from the global_io search
        if not global_result or ('status' in global_result and global_result['status'] != 200):
            await self.composer.error(global_result.get('status', 204))
            request_counting.failed_request()
            await interaction.followup.edit_message(message_id=interaction.message.id, embed=self.composer.embed, view=None)
            return

        # --- FINAL RESULTS & ASTRO SNITCH ---
        ai_report = None
        if 'type' in global_result:
            # Compose global_result FIRST so the embed composer builds the multi-platform buttons!
            await self.composer.compose(self.user, global_result, 'searchsong', censor=self.censor, loading=True)

            try:
                ai_report = await self.api.snitch(global_result)
                await self.composer.compose(self.user, ai_report, 'searchsong', censor=self.censor, loading=False)
            except:
                await self.composer.compose(self.user, global_result, 'searchsong', censor=self.censor, loading=False)
            
            # Edit the message: Finalized embed and multi-service button view
            await interaction.followup.edit_message(message_id=interaction.message.id, embed=self.composer.embed, view=self.composer.button_view)

            # Log successful requests and latency
            request_counting.successful_request()
            latency = global_result['meta']['processing_time']['global_io']
            if ai_report and 'type' in ai_report: 
                latency += ai_report['meta']['processing_time']['global_io']
            request_counting.api_latency(latency)
            
            # Recompose anonymously to retain user privacy before logging
            if ai_report and 'type' in ai_report:
                await self.composer.compose(self.user, ai_report, 'searchsong', anonymous=True, censor=self.censor, loading=False)
            else:
                await self.composer.compose(self.user, global_result, 'searchsong', anonymous=True, censor=self.censor, loading=False)
            
            # Log the original query parameters
            await log([self.composer.embed], [global_result], 'searchlyric', f'lyrics:`{self.lyrics}` censor:`{self.censor}`', current_unix_time_ms() - start_time, self.composer.button_view)
        else:
            await self.composer.error(204)
            request_counting.failed_request()
            await interaction.followup.edit_message(message_id=interaction.message.id, embed=self.composer.embed, view=None)


    @discord.ui.button(label='No, keep looking', style=discord.ButtonStyle.danger)
    async def no_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Only allow the user who initiated the command to interact
        if interaction.user != self.user:
            return await interaction.response.send_message("This isn't your search!", ephemeral=True)
        
        self.index += 1
        await self.update_message(interaction)


class LyricSearchCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api = AstroAPI()

    @app_commands.command(name='searchlyric', description='Search for a song by its lyrics')
    @app_commands.describe(lyrics='The lyrics of the song you are trying to find')
    @app_commands.describe(censor='Whether you want to censor the title of the song or not')
    @discord.app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def search_lyric(self, interaction: discord.Interaction, lyrics: str, censor: bool = False):
        start_time = current_unix_time_ms()
        if interaction.data.get('integration_owners', {}).get('1') is not None:
            censor = True
        await interaction.response.defer()

        # Call the initial Spotify-based lyric search
        response = await self.api.search_lyric(lyric=lyrics)
        api_latency = current_unix_time_ms() - start_time

        composer = EmbedComposer()

        # Check if the API returned a failure or an empty result
        if not response or ('status' in response and response['status'] != 200) or 'songs' not in response or len(response['songs']) == 0:
            request_counting.failed_request()
            await composer.error(response.get('status', 204))
            await interaction.followup.send(embed=composer.embed)
            return

        songs = response['songs']
        request_counting.api_latency(api_latency)

        # Set up the view to iterate through songs
        view = LyricSearchPagination(interaction, interaction.user, songs, self.api, api_latency, censor, lyrics)
        
        first_song = songs[0]
        # Inject mock metadata to prevent KeyError in EmbedComposer
        first_song['meta'] = {
            'processing_time': {'global_io': api_latency},
            'filter_confidence_percentage': {}
        }

        # Compose the first result
        await composer.compose(interaction.user, first_song, 'searchsong', censor=censor)
        
        # Setup selection mode formatting for the initial response
        composer.embed.set_author(name=view.prompts[0], icon_url=interaction.user.display_avatar)
        composer.embed.remove_footer()
        
        # Send it!
        await interaction.followup.send(embed=composer.embed, view=view)
        request_counting.client_latency(current_unix_time_ms() - start_time)


async def setup(bot):
    await bot.add_cog(LyricSearchCog(bot))