import discord as discord
from AstroDiscord.components.ini import text
from AstroDiscord.components.image_hex import image_hex



def create_anchor(media_object: object):
        anchor = []
        urls = media_object.url
        for url in urls:
            anchor.append(text['anchor'][url].replace('URL', urls[url]))
        return '\n'.join(anchor)
    
def media_embed(command: str, media_object: object, user: object):
    media_object = media_object
    data = [', '.join(media_object.artists)]
    cover = media_object.cover_url if media_object.type != 'music_video' else media_object.thumbnail_url
    if media_object.type == 'track':
        data.append(media_object.collection)
    elif media_object.type == 'single':
        data.append('Single')
    elif media_object.type == 'music_video':
        data.append('Music Video')
    elif media_object.type == 'album' or media_object.type == 'ep':
        data.append(str(media_object.release_year))
        
    embed = discord.Embed(
        title = discord.utils.escape_markdown(f'{media_object.title}'),
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