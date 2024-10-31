from AstroAPI.media_services import spotify_api
from AstroAPI.components.service_keys import service_keys

Spotify = spotify_api.Spotify(client_id = service_keys['spotify']['id'], client_secret = service_keys['spotify']['secret'])