from lib import re_math, util
import os, json, traceback
import numpy as np
from numpy.lib import scimath
from numpy import linalg
from scipy import integrate
from scipy.optimize import fsolve

# http://docs.scipy.org/doc/numpy/reference/generated/numpy.set_printoptions.html
# implement printopts ^

# TODO: create README.md file and include directions for embedding ts.compute() into a LaTeX document
# TODO: add differential equation solving
# TODO: explore numpy for more things to implement
# TODO: need to be able to parse_tex of the form \frac{1}{2}
# TODO: add support for multiple sums and multiple integrals

# TODO: figure out how to add to pip/python package index
# TODO: add setup.py see https://docs.python.org/3/distutils/setupscript.html
# TODO: create proper python package structure

# TODO: add loops (over arrays?) and conditionals as commands, this will make it a much more robust scripting language
# TODO: add .issubset tex operator as boolean for conditionals
# TODO: add -i and -h for interactive/help modes from command prompt

class session:
	debug = False	
	def __init__(self, variable={}, function={}, history=[]):	
		self.history = history
		self._ = {
			'commands': {
				'show': { 
					'call': self._show,
					'format': 'show [$1] [$2] ... [all]',
					'help': 'Shows available commands, functions, and variables.',
					'example': ['show', 'show commands', 'show variables e', 'show tex sum format', 'show all']
				},
				'plot': { 
					'call': self._plot,
					'format': 'plot fn [start=-10] [stop=10] [step_size=100]',
					'help': 'Returns the coordinates of the graph of a function with the given parameters',
					'example': ['plot f', 'plot x^2 -5 5', 'plot \sin{x} -\pi \pi 50']
				},
				'iterate': { 
					'call': self._iterate,
					'format': 'iterate fn init_val [iterations=10]',
					'help': 'generates the list of values that results from iterating a given function starting from an initial value a given number of times',
					'example': ['iterate x^2 0.2 25']
				},
				'solve': { 
					'call': self._solve,
					'format': 'solve [fn] [init_val=1]',
					'help': 'finds a root of a given function',
					'example': ['solve \cos{x}-x', 'solve x^3-x+3 -1']
				},
				'history': { 
					'call': lambda: '\n'.join(self.history),
					'format': 'history',
					'help': 'shows all previous input for this session',
					'example': ['history']
				},
				'session': { 
					'call': self._session,
					'format': 'session unset [list='']',
					'help': 'Used for clearing the asigned variables and functions during a session.',
					'example': ['session', 'session unset', 'session unset history']
				},
				'debug': { 
					'call': self._debug,
					'format': 'debug',
					'example': ['debug'],
					'help': 'Toggles debug mode on and off.',
				}
			},

			'operators': {
				'mod': { 
					'call': lambda x,y: x % y,
					'format': '{}\mod{}',
					'example': ['11 \mod 5'],
					'help': 'modular congruence'
				},
				'cdot': { 
					'call': lambda x,y: np.dot(x,y),
					'format': '{}\cdot{}',
					'example': ['[1,1]\cdot[1,1]'],
					'help': 'vector dot product'
				},
				'times': { 
					'call': lambda x,y: np.cross(x,y).tolist(),
					'format': '{}\\times{}',
					'example': ['[1,2,3]\\times[4,5,6]'],
					'help': 'vector cross product'
				},
				'cup': { 
					'call': lambda A, B: A.union(B),
					'format': '{}\cup{}',
					'example': ['{1,2,3}\cup{3,4,5}'],
					'help': 'union of sets'
				},
				'cap': { 
					'call': lambda A, B: A.intersection(B),
					'format': '{}\cap{}',
					'example': ['{1,2,3}\cap{3,4,5}'],
					'help': 'intersection of sets'
				},
				'in': { 
					'call': lambda x, A: x in A,
					'format': '{}\in{}',
					'example': ['1 \in {1,2,3}'],
					'help': 'is an element of'
				}
			},

			'tex': {
				'\\sum': {
					'call': lambda tex: self._reduce(tex,'+'),
					'format': '\\sum_{}^{}{}',
					'example': [],
					'help': 'sum of terms iterated over an index'
				},
				'\\prod': {
					'call': lambda tex: self._reduce(tex,'*'),
					'format': '\\prod_{}^{}{}',
					'example': [],
					'help': 'product of terms iterated over an index'
				},
				'\\sqrt': {
					'call': lambda tex: scimath.sqrt( self.compute(tex['content']) ),
					'format': '\\sqrt{}',
					'example': [],
					'help': 'square root'
				},
				'\\sin': {
					'call': lambda tex: np.sin( self.compute(tex['content']) ),
					'format': '\\sin{}',
					'example': [],
					'help': 'elementary sine function'
				},
				'\\cos': {
					'call': lambda tex: np.cos( self.compute(tex['content']) ),
					'format': '\\cos{}',
					'example': [],
					'help': 'elementary cosine function'
				},
				'\\tan': {
					'call': lambda tex: np.tan( self.compute(tex['content']) ),
					'format': '\\tan{}',
					'example': [],
					'help': 'elementary tan function'
				},
				'\\int': {
					'call': self._integral,
					'format': '\\int_{}^{}{}',
					'example': [],
					'help': 'integral of a function of one variable'
				},
				'\\det': {
					'call': self._determinate,
					'format': '\\det{}',
					'example': [],
					'help': 'determinate of a matrix'
				},
				'\\log': {
					'call': self._log,
					'format': '\\log{}',
					'example': [],
					'help': 'elementary log function to base e'
				}
			},

			'variables': {
				'\\pi': str(np.pi),
				'e': str(np.e)
			},

			'functions': {}
		}

		self._['variables'].update(variable)
		for fn in function:	self._assign(fn)


	def compute(self, math, to_string=False):
		math = math.lstrip()
		
		for q in re_math.parenthesis.finditer(math):
			inner = util.get_inner(math[q.start():])[0]
			math = math.replace('(' + inner + ')', self.compute(inner, True))

		query = math.split(' ')
		if query[0] in self._['commands']:
			return self._['commands'][query[0]]['call'](*query[1:])

		if ':=' in math:
			return self._assign(math)

		if '=' in math and not re_math.equal_sign.search(math):
			lhs, rhs = math.replace(' ', '').split('=')
			return self.compute('solve ' + lhs + '-' + rhs)

		for fn in self._['tex']:
			while fn in math:
				tex = util.parse_tex( math[math.index(fn):] )
				math = math.replace(tex['string'], str(self._['tex'][fn]['call'](tex)))

		for fn in self._['functions']: 
			while fn in math:
				inner = util.get_inner(math[len(fn)+math.index(fn):])[0]
				value = self._['functions'][fn]['call']( *self.compute('[' + inner + ']').tolist() )
				math = math.replace(fn + '(' + inner + ')', value)

		for q in re_math.variables(self._['variables']).finditer(math):
			math = math.replace(q.group(0), self._['variables'][q.group(0)])

		math = re_math.matrix_prod.sub(']\cdot[', math)

		for q in re_math.operator.finditer(math):
			if q.group('command') in self._['operators']:
				value = self._['operators'][q.group('command')]['call'](self.compute(q.group(1)), self.compute(q.group(3)))
				result = str(value) if type(value) is not type(np.array([])) else str(value.tolist())			
				math = math.replace(q.group(0), result)
			else:
				raise ValueError('Unknown Operator: ' + q.group('command'))
		
		for q in re_math.factorial.finditer(math):
			math = math.replace(q.group(0), str(self.compute( '\prod_{1}^{' + q.group(1) + '}{x}' )))

		for q in re_math.array_index.finditer(math):
			math = math.replace(q.group(0), str( util.get_coordinate(self.compute(q.group(1)).tolist(), q.group(2).split(',')) ))

		math = re_math.in_brackets.sub(r'(\1)', math)

		math = math.replace('^', '**')

		if self.debug:
			print(' '.join(query) + ' = ' + math + '\n')

		if re_math.is_valid.search(math):
			for q in re_math.imaginary_number.finditer(math):
				math = math.replace(q.group(0), q.group(1) + '*j')

			math = re_math.matrix_pow.sub(r'linalg.matrix_power(\1, int(\2))', math)
			math = re_math.number.sub(r'np.float_(\1)', math)
			math = re_math.imaginary_unit.sub('1j', math)

			while '[' in math:
				inner = util.get_inner(math[math.index('['):], '[', ']')[0]
				math = math.replace('[' + inner + ']', 'np.array(L' + inner + 'R)' )
			
			math = math.replace('L', '[').replace('R', ']')
			result = eval(math)

			if to_string:
				return str(result) if type(result) is not type(np.array([])) else str(result.tolist())

			return result
		elif math is '':
			return ''
		else:
			raise ValueError('Invalid Tex')

	def _log(self, tex):
		if not tex['lower_index']:
			return scimath.log( self.compute(tex['content']) )

		return scimath.log(self.compute(tex['content'])) / np.log(self.compute(tex['lower_index']))

	def _integral(self, tex):
		start, end, var = util.validate(tex)
		start, end = self.compute(start), self.compute(end)

		if var is None:
			var = re_math.variable_name.findall(tex)[0]

		result, err = integrate.quad(lambda x : self.compute(tex['content'].replace(var, str(x))), start, end)
		return result

	def _determinate(self, tex):
		try:
			return np.linalg.det(self.compute(tex['content']))
		except np.linalg.linalg.LinAlgError as err:
			raise ValueError(err)

	def _assign(self, math):
		q = re_math.assignment.match(math)
		name, value = q.group(1), q.group(2)

		name = name.replace(' ', '')
		if '(' in name:
			fn = name[:name.index('(')]
			if not re_math.variable_name.match(fn): raise ValueError('Invalid name')
			params = util.get_inner(name[name.index('('):])[0]
			self._['functions'][fn] = {
				'call': lambda *args : self.compute(util.replace_list(params.split(','), args, value), True),
				'math': math
			}
			result = self._['functions'][fn]['call']
		else:
			if not re_math.variable_name.match(name): raise ValueError('Invalid name')
			result = self.compute(value);
			self._['variables'][name] = str(result) if type(result) not in (type(np.array([])), type(np.matrix([]))) else str(result.tolist())			

		return result

	def _reduce(self, tex, symbol):
		start, end, var = util.validate(tex)
		start, end = np.int_(self.compute(start)), np.int_(self.compute(end))

		if var is None:
			q = re_math.var_name.findall(tex['content'])
			if len(q) is 1:
				var = q[0]
			else:
				raise ValueError('Missing variable name in lower index')

		op = np.prod if symbol == '*' else np.sum
		return str( op([self.compute(tex['content'].replace(var, str(i))) for i in range(start, end + 1)]) )


	def _anonymous(self, fn):
		if fn in self._['functions']:
			return self._['functions'][fn]['call']
		elif fn in self._['tex']:
			return self._['tex'][fn]['call']

# TODO: fix this so that it actually scopes the variables instead of not allowing them
		variables = [q for q in set(re_math.var_name.findall(fn)) if q not in self._['tex'] and q not in self._['variables'] and q not in self._['functions']]
		
		return lambda *args : self.compute( util.replace_list(variables, args, fn) )

	def _debug(self):
		self.debug = not self.debug
		return 'debug: ' + str(self.debug)

	def _show(self, *args):
		result = self._
		
		for i in args:
			if i != 'all':
				try:
					result = result[i]
				except (KeyError, TypeError):
					attempt = util.dig_for(i, result)
					if len(attempt) > 0:
						return util.scrub(attempt)
					else:
						return 'Key not found: ' + i

		if type(result) is not type(str()) and (len(args) == 0 or args[-1] != 'all'):
			result = ', '.join(util.scrub(result))
	
		return util.scrub(result)

	def _session(self, arg='', name=''):
		if arg == '':
			return self.compute('show commands session all')
		elif arg == 'unset':
			if name is '':
				self.__init__()
				self.history = []
			elif name == 'history':
				self.history = []
			elif name == 'functions':				
				self.__init__(self._['variables'],{},self.history)
			# elif name == 'variables':
			# 	self.__init__(...)
			else:
				raise ValueError('Invalid command')


	# TODO: add support for functions of 2 variables
	# PLAN: 
	# use recursive function to build all combinations of possible inputs, and accept type list for start/stop and do in order that function is written.
	def _plot(self, fn, start='-10', stop='10', steps='100'):
		start, stop, steps = self.compute(start), self.compute(stop), self.compute(steps)
		pos = start
		step_size = (stop - start) / steps;
		result = []

		while pos < stop:
			result.append([pos, self._anonymous(fn)(str(pos))])
			pos += step_size

		return result	

	def _iterate(self, fn, arg, depth):
		if type(arg) == type(str()):
			arg = arg.split(',')
			arg = [self.compute(i) for i in arg]

		if len(arg) == self.compute(depth):
			return arg
		else:
			arg.append( self._anonymous(fn)(str(arg[-1])) )
			return self._iterate(fn, arg, depth)

	def _solve(self, fn, *init_val):
		if len(init_val) == 0:
			init_val = [1]

		return fsolve(self._anonymous(fn), [self.compute(str(x)) for x in init_val])

if __name__ == '__main__':
	import sys
	ts = session()

	def run(path):
		try:
			f = open(path).read()
			for line in f.split('\n'):
				ts.history.append(line)
				print('>> ' + line)
				echo(line)	
		except FileNotFoundError as err:
			print(err)

	def echo(math):
		try:
			result = ts.compute(math)
			result = str(result) if type(result) not in ( type(dict()), type(list()) ) else util.pstring(result)
			print(result + '\n')
		except (AttributeError, ValueError, SyntaxError, NameError, IndexError, TypeError) as err:
			if ts.debug:
				print(traceback.format_exc())
			else:
				print(str(err) + '\n')

	def console():
		while True:
			try:
				query = input('TeX >> ')
				ts.history.append(query)
				echo(query)
			except EOFError:
				print()
				sys.exit()

	if len(sys.argv) is 1:	
		print('Type "show all" for help\n')
		console()
	elif len(sys.argv) is 2:
		if sys.argv[1] == '-h':
			print(ts.compute('show all'))
		else:
			run(sys.argv[1])
	elif len(sys.argv) is 3:
		if sys.argv[1] in ['-c', 'cmd']:
			echo(sys.argv[2])
		if sys.argv[1] == '-i':
			run(sys.argv[2])
			console()

