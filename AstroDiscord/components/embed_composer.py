from discord import Embed, User, Member, ButtonStyle
from discord.ui import Button, View
from discord.utils import escape_markdown
from AstroDiscord.components.ini import text
import aiohttp
from PIL import Image
import numpy as np
from io import BytesIO


class EmbedComposer:
    def __init__(self):
        self.button_view = None
        self.embed = None
        self.last_json = None
        self.generic_loading = Embed(
            description="Loading...",
            colour=0xf5c000
        )

    async def error(self, error: int, custom: dict = None):
        error_titles = {
            500: 'An error has occurred!',
            204: "I couldn't find what you're looking for.",
            'other': 'An undocumented error has occured!'
        }
        error_descriptions = {
            500: 'Something has gone wrong on our end. Please try again! If this keeps happening, feel free to report it in our Discord server!',
            204: 'Please check your request for typos and if everything is in its right order.',
            'other': 'Something has gone horribly wrong. Please report this in our Discord server.'
        }
        error_meanings = {
            500: 'Internal server error',
            204: 'Empty response',
            'other': 'Unforeseen consequences'
        }

        if custom is not None:
            title = custom['title']
            description = custom['description']
            meaning = custom['meaning']
        elif error not in error_titles:
            title = error_titles['other']
            description = error_descriptions['other']
            meaning = error_meanings['other']
        else:
            title = error_titles[error]
            description = error_descriptions[error]
            meaning = error_meanings[error]

        self.embed = Embed(
            title=title,
            description=description,
            colour=0xf5c000
        )
        self.embed.set_author(name='Oh no!')
        self.embed.set_footer(
            text=f"Thanks for using Astro!  •  Error code {error} - {meaning}",
            icon_url=text['images']['pfpurl']
        )

    async def compose(self, user: User | Member, json_response: dict, command_type: str, anonymous: bool = False, censor: bool = False, loading: bool = False):
        service_metadata_priority = ['spotify', 'apple_music', 'youtube_music', 'deezer', 'genius']
        mv_thumbnail_priority = ['youtube_music', 'apple_music']

        song_obj_types = ['track', 'single']
        collection_obj_types = ['album', 'ep']
        music_video_types = ['music_video']
        knowledge_types = ['knowledge']

        actions = {
            'searchsong': 'searched for',
            'searchalbum': 'searched for',
            'search': 'searched for',
            'lookup': 'searched for',
            'snoop': 'is listening to',
            'coverart': 'looked up cover art for',
            'link': 'sent a link to',
            'knowledge': 'searched for knowledge about'
        }

        username = user.display_name
        user_pfp = user.display_avatar
        action = actions.get(command_type, 'searched for')

        def get_confidence(meta):
            if meta and 'filter_confidence_percentage' in meta and meta['filter_confidence_percentage'] is not None:
                raw_val = meta['filter_confidence_percentage']
                
                # If it's a dict (New Schema), extract the 'songs' confidence value or default to 0
                if isinstance(raw_val, dict):
                    # Try to get 'songs', fallback to extracting the maximum value present if 'songs' isn't there
                    confidence_num = raw_val.get('songs') or max(list(raw_val.values()) or [0])
                else:
                    confidence_num = raw_val

                # If the score is an integer greater than 1, it's already pre-multiplied (e.g., 72.78 instead of 0.7278)
                if confidence_num > 1.0:
                    return f"`[{round(float(confidence_num), 3)}%]`"
                elif confidence_num > 0.0:
                    return f"`[{round(float(confidence_num) * 100, 3)}%]`"
            return ''

        async def apply_common_formatting(title, desc_elements, cover_url, processing_time_ms):
            color = await self.image_hex(cover_url)
            
            # Remove empty/None description elements
            desc_elements = [d for d in desc_elements if d]
            self.embed = Embed(
                title=title,
                description='  •  '.join(desc_elements),
                color=color
            )

            if not anonymous:
                self.embed.set_author(name=f'{username} {action}:', icon_url=user_pfp)
            else:
                self.embed.set_author(name=f'A user {action}:', icon_url=text['images']['default_pfp'])

            if command_type != 'coverart':
                self.embed.set_thumbnail(url=cover_url)
            else:
                self.embed.set_image(url=cover_url)

            if not loading:
                for field in self.embed.fields.copy():
                    if field.value == 'Loading...':
                        self.embed.remove_field(self.embed.fields.index(field))
                self.embed.set_footer(
                    text=f"{text['embed']['tymsg']} • Done in {processing_time_ms} ms",
                    icon_url=text['images']['pfpurl']
                )
            else:
                self.embed.add_field(name='', value='Loading...', inline=False)
                
            await self.service_buttons(json_response.get('urls', {}))

        async def build_media_embed(data, media_category):
            confidence = get_confidence(data.get('meta'))
            title = escape_markdown(data.get('title', 'Unknown'))
            if data.get('is_explicit'):
                title = f"{title}   `EXPLICIT` {confidence}".strip()
            else:
                title = f"{title}   {confidence}".strip()

            artists = ', '.join([f"**{escape_markdown(a['name'])}**" for a in data.get('artists', [])])
            genre = data.get('genre')
            desc_elements = [artists]

            if media_category == 'song':
                collection_data = data.get('collection')
                if collection_data and data.get('type') != 'single':
                    col_title = collection_data.get('censored_title') if censor and collection_data.get('censored_title') else collection_data.get('title')
                    if col_title:
                        desc_elements.append(f"*{escape_markdown(col_title)}*")
                desc_elements.append(genre)
                
                cover_url = None
                for service in service_metadata_priority:
                    if 'cover' in data and 'hq_urls' in data['cover'] and data['cover']['hq_urls'].get(service):
                        cover_url = data['cover']['hq_urls'][service]
                        break
                    elif collection_data and 'cover' in collection_data and 'hq_urls' in collection_data['cover'] and collection_data['cover']['hq_urls'].get(service):
                        cover_url = collection_data['cover']['hq_urls'][service]
                        break

            elif media_category == 'music_video':
                desc_elements.extend(['Music Video', genre])
                cover_url = None
                for service in mv_thumbnail_priority:
                    if 'cover' in data and 'hq_urls' in data['cover'] and data['cover']['hq_urls'].get(service):
                        cover_url = data['cover']['hq_urls'][service]
                        break

            elif media_category == 'collection':
                release_year = str(data.get('release_year', ''))
                desc_elements.extend([release_year, genre])
                cover_url = None
                for service in service_metadata_priority:
                    if 'cover' in data and 'hq_urls' in data['cover'] and data['cover']['hq_urls'].get(service):
                        cover_url = data['cover']['hq_urls'][service]
                        break

            # Now rounded to a clean integer
            proc_time = int(round(float(data.get('meta', {}).get('processing_time_ms', 0))))
            await apply_common_formatting(title, desc_elements, cover_url, proc_time)

        async def analysis(json_data):
            am = self.last_json or {}
            am_type = am.get('type', 'media')
            
            media_label = 'media'
            if am_type in song_obj_types or am_type in knowledge_types:
                media_label = 'song'
            elif am_type in music_video_types:
                media_label = 'music video'
            elif am_type in collection_obj_types:
                media_label = 'EP' if am_type in ['ep', 'eop'] else 'album'

            analysis_string = ''

            for report in json_data.get('audio_reports') or []:
                ai_analysis = report.get('ai_analysis', {})
                confidence = ai_analysis.get('ai_confidence_score', 0) * 100
                if ai_analysis.get('is_ai_generated', False) or confidence >= 50.0:
                    analysis_string += f"- There is a probability this {media_label}'s audio has been AI-generated `[{round(confidence, 3)}%]`\n"

            for report in json_data.get('image_reports') or []:
                ai_analysis = report.get('ai_analysis', {})
                confidence = ai_analysis.get('ai_confidence_score', 0) * 100
                if ai_analysis.get('is_ai_generated', False) or confidence >= 50.0:
                    analysis_string += f"- There is a probability this {media_label}'s cover has been AI-generated `[{round(confidence, 3)}%]`\n"

            for report in json_data.get('video_reports') or []:
                ai_analysis = report.get('ai_analysis', {})
                confidence = ai_analysis.get('ai_confidence_score', 0) * 100
                if ai_analysis.get('is_ai_generated', False) or confidence >= 50.0:
                    analysis_string += f"- There is a probability this {media_label}'s video has been AI-generated `[{round(confidence, 3)}%]`\n"

            if analysis_string:
                if not any(field.name == 'Generative AI report' for field in self.embed.fields):
                    self.embed.add_field(
                        name='Generative AI report',
                        value=f"{analysis_string}-# Powered by Astro Snitch. Analysis may not be 100% accurate. Rely on your own judgment and verify with additional context.",
                        inline=False
                    )

            for field in self.embed.fields.copy():
                if field.value == 'Loading...':
                    self.embed.remove_field(self.embed.fields.index(field))

            # Ensure the author block is correctly updated (anonymized or standard)
            if self.embed:
                if anonymous:
                    self.embed.set_author(name=f'A user {action}:', icon_url=text['images']['default_pfp'])
                else:
                    self.embed.set_author(name=f'{username} {action}:', icon_url=user_pfp)

            # Combine processing times as clean integers
            analysed_time = int(round(float(am.get('meta', {}).get('processing_time_ms', 0))))
            snitch_time = int(round(float(json_data.get('meta', {}).get('processing_time_ms', 0))))

            self.embed.set_footer(
                text=f"{text['embed']['tymsg']} • Done in {analysed_time} + {snitch_time} ms",
                icon_url=text['images']['pfpurl']
            )

        # Logic selector
        is_ai_report = any(k in json_response for k in ('audio_reports', 'image_reports', 'video_reports')) or json_response.get('type') == 'analysis'

        if is_ai_report:
            await analysis(json_response)
            
        elif 'type' in json_response:
            obj_type = json_response['type']
            if obj_type in song_obj_types:
                await build_media_embed(json_response, 'song')
            elif obj_type in music_video_types:
                await build_media_embed(json_response, 'music_video')
            elif obj_type in collection_obj_types:
                await build_media_embed(json_response, 'collection')
            
            self.last_json = json_response
            
        elif self.embed is not None and self.last_json:
            for field in self.embed.fields.copy():
                if field.value == 'Loading...':
                    self.embed.remove_field(self.embed.fields.index(field))
            proc_time = int(round(float(self.last_json.get('meta', {}).get('processing_time_ms', 0))))
            self.embed.set_footer(
                text=f"{text['embed']['tymsg']} • Done in {proc_time} ms",
                icon_url=text['images']['pfpurl']
            )
            
    async def service_buttons(self, urls: dict):
        self.button_view = View()
        for service, url in urls.items():
            if url:
                self.button_view.add_item(
                    Button(
                        style=ButtonStyle.link,
                        url=url,
                        emoji=text['emoji'].get(service) 
                    )
                )

    async def image_hex(self, image_url: str, quality: int = 5):
        if not image_url:
            return 0xf5c000
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url=image_url) as response:
                    if response.status == 200:
                        image_bytes = await response.read()
                        image = Image.open(BytesIO(image_bytes))
                        width, height = image.size
                        new_width = max(1, width // quality)
                        new_height = max(1, height // quality)
                        image = image.resize((new_width, new_height))
                        pixels = image.convert('RGB').getdata()
                        average_color = np.mean(pixels, axis=0).astype(int)
                        hex_color = '#{:02x}{:02x}{:02x}'.format(*average_color)
                        return int(hex_color[1:], base=16)
        except Exception:
            pass
        return 0xf5c000