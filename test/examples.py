import texscript

ts = texscript.session()

def dig_for(key, obj):
	result = []

	for k in obj:
		if k == key:
			result.append(obj[key])
		else:
			temp = dig_for(key, obj[k])
			if len(temp) > 0:
				result.append(temp)

	return result

dig_for('example', self._)