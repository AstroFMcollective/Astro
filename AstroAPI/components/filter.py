from AstroAPI.components.media import *
from AstroAPI.components.log import *
from AstroAPI.components.text_manipulation import *



async def filter_song(service: str, query_request: str, songs: list, query_artists: list, query_title: str, query_song_type: str = None, query_collection: str = None, query_is_explicit: bool = None) -> Song:
	max_score = 2000
	if query_collection != None:
		max_score += 1000
	if query_is_explicit != None:
		max_score += 500
	if query_song_type != None:
		max_score += 500

	data_with_similarity = []
	for data in songs:
		song_similarity = 0
		
		#artist_input = ' '.join([bare_bones(artist) for artist in query_artists])
		artist_input = bare_bones(query_artists[0])
		artists_reference = data.artists
		artists_with_similarity = []
		for artist_name in artists_reference:
			artists_with_similarity.append([calculate_similarity(bare_bones(artist_name), artist_input), artist_name])
		artists_with_similarity = sort_similarity_lists(artists_with_similarity)
		if artists_with_similarity != [] and artists_with_similarity[0][0] > 500:
			song_similarity += artists_with_similarity[0][0]
		else:
			continue

		title_input = bare_bones(query_title)
		title_reference = remove_feat(data.title)
		song_similarity += calculate_similarity(bare_bones(title_reference), title_input)

		if query_collection != None:
			collection_input = bare_bones(query_collection)
			collection_reference = data.collection
			song_similarity += calculate_similarity(bare_bones(collection_reference), collection_input)

		if query_is_explicit != None:
			if query_is_explicit == data.is_explicit:
				song_similarity += 500

		if query_song_type != None:
			if query_song_type == data.type:
				song_similarity += 500

		data_with_similarity.append([song_similarity, data])
	
	data_with_similarity = sort_similarity_lists(data_with_similarity)
	if data_with_similarity != []:
		if percentage(max_score, data_with_similarity[0][0]) > 30:
			return data_with_similarity[0][1]
		else:
			response = Empty(
				service = service,
				request = {'request': query_request, 'artists': query_artists, 'title': query_title, 'song_type': query_song_type, 'collection': query_collection, 'is_explicit': query_is_explicit}
			)
			await log(response)
			return response
	else:
		response = Empty(
			service = service,
			request = {'request': query_request, 'artists': query_artists, 'title': query_title, 'song_type': query_song_type, 'collection': query_collection, 'is_explicit': query_is_explicit}
		)
		await log(response)
		return response



async def filter_mv(service: str, query_request: str, videos: list, query_artists: list, query_title: str, query_is_explicit: bool = None) -> Song:
	max_score = 2000
	if query_is_explicit != None:
		max_score += 500

	data_with_similarity = []
	for data in videos:
		song_similarity = 0
		
		artist_input = bare_bones(query_artists[0])
		artists_reference = data.artists
		artists_with_similarity = []
		for artist_name in artists_reference:
			artists_with_similarity.append([calculate_similarity(bare_bones(artist_name), artist_input), artist_name])
		artists_with_similarity = sort_similarity_lists(artists_with_similarity)
		if artists_with_similarity != [] and artists_with_similarity[0][0] > 500:
			song_similarity += artists_with_similarity[0][0]
		else:
			continue

		title_input = bare_bones(query_title)
		title_reference = remove_feat(data.title)
		song_similarity += calculate_similarity(bare_bones(title_reference), title_input)

		if query_is_explicit != None:
			if query_is_explicit == data.is_explicit:
				song_similarity += 500

		data_with_similarity.append([song_similarity, data])
	
	data_with_similarity = sort_similarity_lists(data_with_similarity)
	if data_with_similarity != []:
		if percentage(max_score, data_with_similarity[0][0]) > 30:
			return data_with_similarity[0][1]
		else:
			empty_response = Empty(
				service = service,
				request = {'request': query_request, 'artists': query_artists, 'title': query_title, 'is_explicit': query_is_explicit}
			)
			await log(empty_response)
			return empty_response
	else:
		empty_response = Empty(
			service = service,
			request = {'request': query_request, 'artists': query_artists, 'title': query_title, 'is_explicit': query_is_explicit}
		)
		await log(empty_response)
		return empty_response



async def filter_collection(service: str, query_request: str, collections: list, query_artists: list, query_title: str, query_year: str = None) -> Collection:
	max_score = 2000
	if query_year != None:
		max_score += 1000

	data_with_similarity = []
	for data in collections:
		collection_similarity = 0

		artist_input = bare_bones(query_artists[0])
		artists_reference = data.artists
		artists_with_similarity = []
		for artist_name in artists_reference:
			artists_with_similarity.append([calculate_similarity(bare_bones(artist_name), artist_input), artist_name])
		artists_with_similarity = sort_similarity_lists(artists_with_similarity)
		if artists_with_similarity != [] and artists_with_similarity[0][0] > 500:
			collection_similarity += artists_with_similarity[0][0]
		else:
			continue

		title_input = bare_bones(query_title)
		title_reference = remove_feat(data.title)
		collection_similarity += calculate_similarity(bare_bones(title_reference), title_input)

		if query_year != None:
			if query_year == data.release_year:
				collection_similarity += 1000

		data_with_similarity.append([collection_similarity, data])
	
	data_with_similarity = sort_similarity_lists(data_with_similarity)
	if data_with_similarity != []:
		if percentage(max_score, data_with_similarity[0][0]) > 30:
			return data_with_similarity[0][1]
		else:
			empty_response = Empty(
				service = service,
				request = {'request': query_request, 'artists': query_artists, 'title': query_title, 'year': query_year}
			)
			await log(empty_response)
			return empty_response
	else:
		empty_response = Empty(
			service = service,
			request = {'request': query_request, 'artists': query_artists, 'title': query_title, 'year': query_year}
		)
		await log(empty_response)
		return empty_response
