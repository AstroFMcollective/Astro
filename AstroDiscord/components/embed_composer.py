import discord as discord
from AstroDiscord.components.ini import text
from AstroDiscord.components.image_hex import image_hex



class Embed:
    def __init__(self, command: str, media_object: object, user: object, censored: bool = False):
        self.custom_errors = [
            text['embed']['snoop_you_errormsg'],
            text['embed']['snoop_someone_errormsg'],
            text['embed']['cover_errormsg'],
            text['embed']['context_menu_link_lookup_errormsg'],
        ]

        if media_object.type != 'empty_response' and media_object.type != 'error':
            self.cover = media_object.cover_url if media_object.type != 'music_video' else media_object.thumbnail_url
            self.embed_color = image_hex(self.cover)
        
        self.embed = self.create_embed(command = command, media_object = media_object, user = user, censored = censored, anonymous = False)
        self.log_embed = self.create_embed(command = command, media_object = media_object, user = user, censored = False, anonymous = True)

    

    def create_embed(self, command: str, media_object: object, user: object, censored: bool, anonymous: bool):
        if media_object.type == 'empty_response' or media_object.type == 'error':
            embed = discord.Embed(
                title = text['embed']['errortitle'],
                color = 0xf5c000
            )

            if media_object.type == 'error':
                if media_object.error_msg in self.custom_errors:
                    error_msg = media_object.error_msg
                else:
                    error_msg = text['embed']['errormsg'] if media_object.type == 'error' else text['embed']['emptymsg']
            
            if media_object.type == 'empty_response':
                error_msg = text['embed']['emptymsg']

            embed.add_field(
                name = '',
                value = error_msg,
                inline = False
            )
                
            embed.set_footer(
                text = text['embed']['tymsg'],
                icon_url = text['embed']['pfpurl']
            )

            return embed
        
        if len(media_object.url) == 1 and command == 'link':
            return
        
        data = [', '.join(media_object.artists)]
        is_explicit = None

        if media_object.type == 'track':
            if media_object.collection != None:
                data.append(media_object.collection)
            is_explicit = media_object.is_explicit
        elif media_object.type == 'single':
            data.append('Single')
            is_explicit = media_object.is_explicit
        elif media_object.type == 'music_video':
            data.append('Music video')
            is_explicit = media_object.is_explicit
        elif media_object.type == 'album' or media_object.type == 'ep':
            data.append(str(media_object.release_year))
            
        embed = discord.Embed(
            title = f'{discord.utils.escape_markdown(f'{media_object.title}')}  {'`E`' if is_explicit != None and is_explicit != False else ''}',
            description = discord.utils.escape_markdown(f'{' • '.join(data)}'),
            color = self.embed_color
        )

        if anonymous == False:
            embed.set_author(
                name = text['embed'][command].replace('USER',f'@{user.name}'),
                icon_url = user.avatar
            )
        else:
            embed.set_author(
                name = text['embed'][command].replace('USER',f'@USER'),
                icon_url = text['images']['default_pfp']
            )

        if command != 'cover':
            embed.add_field(
                name = text['embed'][media_object.type],
                value = self.create_anchor(media_object),
                inline = False
            )
            
            
        if media_object.type == 'music_video' or command == 'cover':
            embed.set_image(
                url = self.cover
            )
        else:
            embed.set_thumbnail(
                url = self.cover
            )

        embed.set_footer(
            text = text['embed']['tymsg'],
            icon_url = text['embed']['pfpurl']
        )

        return embed
    
    def create_anchor(self, media_object: object):
        anchor = []
        urls = media_object.url
        for url in urls:
            anchor.append(text['anchor'][url].replace('URL', urls[url]))
        return '\n'.join(anchor)
