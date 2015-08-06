from numpy.lib import scimath

def log(tex):
	if not tex['lower_index']:
		return scimath.log( tex['content'] )

	return scimath.log(tex['content']) / scimath.log(tex['lower_index'])
