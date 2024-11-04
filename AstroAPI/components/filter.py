from AstroAPI.components.media import *
from AstroAPI.components.etc import *

def filter_song(service: str, songs: list, query_artists: list, query_title: str, query_song_type: str = None, query_collection: str = None, query_is_explicit: bool = None) -> Song:
	max_score = 3000
	if query_collection != None:
		max_score += 1000
	if query_collection != None:
		max_score += 500

	data_with_similarity = []
	for data in songs:
		track_similarity = 0
		
		artist_input = bare_bones(query_artists[0])
		artists_reference = data.artists
		artists_with_similarity = []
		for artist_name in artists_reference:
			artists_with_similarity.append([calculate_similarity(bare_bones(artist_name), artist_input), artist_name])
		artists_with_similarity = sort_similarity_lists(artists_with_similarity)
		if artists_with_similarity != [] and artists_with_similarity[0][0] > 500:
			track_similarity += artists_with_similarity[0][0]
		else:
			continue

		title_input = bare_bones(query_title)
		title_reference = remove_feat(data.title)
		track_similarity += calculate_similarity(bare_bones(title_reference), title_input)

		if query_collection != None:
			collection_input = bare_bones(query_collection)
			collection_reference = data.collection
			track_similarity += calculate_similarity(bare_bones(collection_reference), collection_input)

		if query_is_explicit != None:
			if query_is_explicit == data.is_explicit:
				track_similarity += 500

		if query_song_type != None:
			if query_song_type == data.type:
				track_similarity += 1000

		data_with_similarity.append([track_similarity, data])
	
	data_with_similarity = sort_similarity_lists(data_with_similarity)
	if data_with_similarity != []:
		if percentage(max_score, data_with_similarity[0][0]) > 30:
			return data_with_similarity[0][1]
		else:
			return Empty(service = service, request = f'Artists: `{', '.join(query_artists)}`\nTitle: `{query_title}`\nSong type: `{query_song_type}`\nCollection title: `{query_collection}`\nIs explicit? `{query_is_explicit}`')
	else:
		return Empty(service = service, request = f'Artists: `{', '.join(query_artists)}`\nTitle: `{query_title}`\nSong type: `{query_song_type}`\nCollection title: `{query_collection}`\nIs explicit? `{query_is_explicit}`')



def filter_collection(service: str, collections: list, query_artists: list, query_title: str, query_year: str = None) -> Collection:
	max_score = 2000
	if query_year != None:
		max_score += 1000

	data_with_similarity = []
	for data in collections:
		track_similarity = 0

		artist_input = bare_bones(query_artists[0])
		artists_reference = data.artists
		artists_with_similarity = []
		for artist_name in artists_reference:
			artists_with_similarity.append([calculate_similarity(bare_bones(artist_name), artist_input), artist_name])
		artists_with_similarity = sort_similarity_lists(artists_with_similarity)
		if artists_with_similarity != [] and artists_with_similarity[0][0] > 500:
			track_similarity += artists_with_similarity[0][0]
		else:
			continue

		title_input = bare_bones(query_title)
		title_reference = remove_feat(data.title)
		track_similarity += calculate_similarity(bare_bones(title_reference), title_input)

		if query_year != None:
			if query_year == data.release_year:
				track_similarity += 1000

		data_with_similarity.append([track_similarity, data])
	
	data_with_similarity = sort_similarity_lists(data_with_similarity)
	if data_with_similarity != []:
		if percentage(max_score, data_with_similarity[0][0]) > 30:
			return data_with_similarity[0][1]
		else:
			return Empty(service = service, request = f'Artists: `{', '.join(query_artists)}`\nTitle: `{query_title}`\nYear: `{query_year}`')
	else:
		return Empty(service = service, request = f'Artists: `{', '.join(query_artists)}`\nTitle: `{query_title}`\nYear: `{query_year}`')
