from AstroAPI.media_services import spotify_api, tidal_api, deezer_api
from AstroAPI.components.service_auth import service_keys

Spotify = spotify_api.Spotify(client_id = service_keys['spotify']['id'], client_secret = service_keys['spotify']['secret'])
Tidal = tidal_api.Tidal(client_id = service_keys['tidal']['id'], client_secret = f'{service_keys['tidal']['secret']}=')
Deezer = deezer_api.Deezer()