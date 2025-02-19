from unidecode import *
import difflib
import re
from AstroAPI.components.time import save_json

def remove_punctuation(string: str, remove_all: bool):
	all_punc = f'''!()[];:'",<>./?@#$%^&*`_~'''
	some_punc = f'''!()[];:'",<>./?^*_~`'''
	for element in string:
		if remove_all == True:
			if element in all_punc:
				string = string.replace(element, '')
		elif remove_all == False:
			if element in some_punc:
				string = string.replace(element, '')
	return string

def replace_punctuation_with_spaces(string: str):
	punc = f'''!()[];:'",<>./?^*_`-~'''
	for element in string:
		if element in punc:
			string = string.replace(element, ' ')
	return string

def replace_with_ascii(string: str):
	return unidecode(string)

def bare_bones(string: str, remove_all_punctuation: bool = True):
	return replace_with_ascii(remove_punctuation(string, remove_all_punctuation)).lower().replace('  ',' ')

def split_artists(string: str):
	strings = re.split(r",|\&", string)
	fixed_strings = []
	for element in strings:
		if element == ' ':
			continue
		if element[0] == ' ':
			element = element[1:]
		if element[-1] == ' ':
			element = element[:-1]
		fixed_strings.append(element)
	return fixed_strings

def get_common_data(data: list):
	element_counts = {}
	for element in data:
		if element in element_counts:
			element_counts[element] += 1
		else:
			element_counts[element] = 1
 
	max_count = max(element_counts.values(), default=0)

	most_common = [key for key, value in element_counts.items() if value == max_count]

	return most_common[0] if most_common else None

def remove_feat(string: str):
	if string.lower().find('feat. ') >= 0:
		if string[string.lower().index('feat. ')-1] == '[':
			first_bracket = string.lower().index('feat. ')-1
			second_bracket = string.lower().index('feat. ')-1
			while string[second_bracket-1] != ']':
				second_bracket += 1
			string = string.replace(string[first_bracket:second_bracket],'')
		elif string[string.lower().index('feat. ')-1] == '(':
			first_bracket = string.lower().index('feat. ')-1
			second_bracket = string.lower().index('feat. ')-1
			while string[second_bracket-1] != ')':
				second_bracket += 1
			string = string.replace(string[first_bracket:second_bracket],'')
		elif string[string.lower().index('feat. ')-1] == ' ':
			string = string[:string.lower().index('feat. ')-1]
	if string.lower().find('(with ') >= 0 or string.lower().find('[with ') >= 0:
		if string[string.lower().index('with ')-1] == '[':
			first_bracket = string.lower().index('with ')-1
			second_bracket = string.lower().index('with ')-1
			while string[second_bracket-1] != ']':
				second_bracket += 1
			string = string.replace(string[first_bracket:second_bracket],'')
		elif string[string.lower().index('with ')-1] == '(':
			first_bracket = string.lower().index('with ')-1
			second_bracket = string.lower().index('with ')-1
			while string[second_bracket-1] != ')':
				second_bracket += 1
			string = string.replace(string[first_bracket:second_bracket],'')
	if string[len(string)-1] == ' ':
		string = string[:len(string)-1]
	return string

def optimize_string(string: str):
	string = remove_feat(string)
	string = replace_punctuation_with_spaces(string)
	string = bare_bones(string, False)
	string_list = string.split(sep = ' ')
	for counter in range(string_list.count('')):
		string_list.remove('')
	return string_list

def calculate_similarity(reference_string: str, input_string: str):
	return difflib.SequenceMatcher(None, reference_string, input_string).ratio() * 1000

def sort_similarity_lists(data_list: list, similarity_index: int = 0):
	return sorted(data_list, key = lambda x: x[similarity_index], reverse = True)

def percentage(hundred_percent: int, number: int):
	thing = 100 / hundred_percent
	return number * thing

def optimize_for_search(string: str):
	optimized_string = string
	optimized_string = optimized_string.replace('#','')
	optimized_string = remove_feat(optimized_string)
	if optimized_string[0] == '&':
		optimized_string = optimized_string[1:]
	if ' l ' in optimized_string:
		for instances in range(optimized_string.count(' l ')):
			optimized_string = optimized_string.replace(' l ', ' | ')
	return optimized_string

def has_music_video_declaration(string: str):
	declarations = [
		'(official video)',
		'(official music video)',
		'[official video]',
		'[official music video]'
	]
	for declaration in declarations:
		if declaration in string.lower():
			return True
	return False

def remove_music_video_declaration(string: str):
	og_string = string
	optimized_string = string.lower()
	declarations = [
		'(official video)',
		'(official music video)',
		'[official video]',
		'[official music video]'
	]
	for declaration in declarations:
		if declaration in optimized_string:
			optimized_string = optimized_string.replace(declaration, '')
			optimized_string = optimized_string[:len(optimized_string)-1]
	og_string = og_string[:len(optimized_string)]
	return og_string

def track_is_explicit(is_explicit: bool | None):
	if is_explicit != None:
		if is_explicit:
			return '  <:explicit:1282046436598480907>'
		else:
			return ''
	else:
		return ''

def clean_up_collection_title(string: str):
	if ' - Single' in string:
		return string.replace(' - Single','')
	elif ' - EP' in string:
		return string.replace(' - EP','')
	else:
		return string

def remove_duplicates(items: list):
	return list(dict.fromkeys(items))

def convert_genius_desc_into_discord_str(description: dict):
	converted_description = ''

	description = description['dom']['children'][0]['children']
	#save_json(description)

	for element in description:
		if isinstance(element, str):
			converted_description += element
		elif isinstance(element, dict):
			if element['tag'] == 'a':
				if isinstance(element['children'][0], dict):
					if element['children'][0]['tag'] == 'em' or element['children'][0]['tag'] == 'i':
						converted_description += f'*[{element['children'][0]['children'][0]}]({element['attributes']['href']})*'
				else:
					converted_description += f'[{element['children'][0]}]({element['attributes']['href']})'
			if element['tag'] == 'em':
				converted_description += f'*{element['children'][0]}*'



	return converted_description