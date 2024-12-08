import discord as discord
from AstroDiscord.components.ini import text
from AstroDiscord.components.image_hex import image_hex



def create_anchor(media_object: object):
        anchor = []
        urls = media_object.url
        for url in urls:
            anchor.append(text['anchor'][url].replace('URL', urls[url]))
        return '\n'.join(anchor)
    
def create_embed(command: str, media_object: object, user: object):
    if media_object.type == 'empty_response' or media_object.type == 'error':
        embed = discord.Embed(
            title = text['embed']['errortitle'],
            color = 0xf5c000
        )

        embed.add_field(
            name = '',
            value = text['embed']['errormsg'] if media_object.type == 'error' else text['embed']['emptymsg'],
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
    cover = media_object.cover_url if media_object.type != 'music_video' else media_object.thumbnail_url
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
        color = image_hex(cover)
    )

    embed.set_author(
        name = text['embed'][command].replace('USER',f'@{user.name}'),
        icon_url = user.avatar
    )

    embed.add_field(
        name = text['embed'][media_object.type],
        value = create_anchor(media_object),
        inline = False
    )
        
        
    if media_object.type != 'music_video':
        embed.set_thumbnail(
            url = cover
        )
    else:
        embed.set_image(
            url = cover
        )

    embed.set_footer(
        text = text['embed']['tymsg'],
        icon_url = text['embed']['pfpurl']
    )

    return embed