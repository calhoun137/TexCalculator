import texscript

ts = texscript.session()

did_pass_test = True

def dig_for(key, obj):
	if type(obj) != type(dict()): return None

	result = []
	for k in obj:
		if k == key:
			result += obj[key]
		else:
			temp = dig_for(key, obj[k])
			if temp:
				result += temp

	return result

for test in dig_for('example', ts._):
	try:
		ts.compute(test)
		ts.debug = False
	except (AttributeError, ValueError, SyntaxError, NameError, IndexError, TypeError) as err:
		print('Test Failed: ', test, err, '\n')
		did_pass_test = False

if did_pass_test:
	print('All tests were passed successfully')
