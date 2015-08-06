from lib import re_math
import numpy as np

def get_inner(math, start_symbol='(', end_symbol=')'):
	if len(math) == 0: 
		return '', 0 

	if math[0] != start_symbol:
		return math[0], 1
			
	count = 0	
	for i in range(0, len(math)):
		if math[i] == start_symbol:
			count += 1
		elif math[i] == end_symbol:
			count -= 1

		if count == 0:
			return math[1:i], i + 1
			
	raise ValueError('Unclosed ' + start_symbol)

def parse_tex(math):
	index = { '_': None, '^': None }
	m = re_math.tex.match(math)
	pos = m.span()[1]

	while math[pos:] is not '':
		if math[pos] == '{':
			break

		inner, length = get_inner(math[pos + 1:], '{', '}')
		index[math[pos]] = inner
		pos += length + 1

	inner, length = get_inner(math[pos:], '{', '}')
	
	return {
		'command': m.group('command'),
		'lower_index': index['_'],
		'upper_index': index['^'],
		'content': inner,
		'string': math[m.span()[0] : pos + length]
	}

def validate(tex, check_lower=True, check_upper=True):
	if check_lower is True and not tex['lower_index']:
		raise ValueError('Missing a lower index: ' + tex['string'])

	if check_upper is True and not tex['upper_index']:
		raise ValueError('Missing an upper index: ' + tex['string'])

	if check_lower is False:
		return tex['upper_index']
	elif check_upper is False:
		return tex['lower_index']
	elif '=' in tex['lower_index']:
		items = tex['lower_index'].split('=')
		return items[1], tex['upper_index'], items[0] 
	else:
		return tex['lower_index'], tex['upper_index'], None


def scrub(data):
	
	if type(data) == type(str()):
		return data
	elif type(data) == type(list()):
		result = data.copy()
		return [scrub(i) for i in data]			
	elif type(data) == type(dict()):
		result = data.copy()
		return { i:scrub(result[i]) for i in data if type(result[i]) in ( type(str()), type(dict()), type(list()) ) }
	else:
		return None

def dig_for(key, obj):
	if type(obj) != type(dict()): 
		return None

	result = {}
	for k in obj:
		if k == key:
			result = obj[k]
		else:
			temp = dig_for(key, obj[k])
			if temp:
				result[k] = temp

	return result

def replace_list(list_1, list_2, string):
	if type(list_1) is not type([]):
		list_1 = [list_1]

	for i in range(len(list_1)):
		string = string.replace(list_1[i], str(list_2[i]))

	return string

def get_coordinate(array, path):
	if len(path) > 0:
		return get_coordinate(array[int(path[0]) ], path[1:])
	else:
		return array

def pstring(obj, depth=1):
	result = '\n'
	if type(obj) == type(dict()):
		for k in obj:
			result += '\n'
			for i in range(0, depth):
				result += '\t'
			result += k + ': ' + pstring(obj[k], depth + 1)
	elif type(obj) == type(list()):
		for k in obj:
			result += '\n'
			for i in range(0, depth):
				result += '\t'
			result += pstring(k, depth + 1)
	else:
		return str(obj) + '\n'
	
	return result