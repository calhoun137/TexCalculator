import re

def variables(items):
	return re.compile( '(?<![a-zA-Z0-9])(?:' + '|'.join(items).replace('\\', '\\\\') + ')(?![a-zA-Z0-9])' )

tex = re.compile(r'\\(?P<command>[a-zA-Z]{1,})')
parenthesis = re.compile(r'(?<![a-zA-Z])\(')
index = re.compile(r'(_|\^|{)')
number = re.compile(r'(?<![0-9])(-{0,1}[0-9]{1,}\.{0,1}[0-9]{0,}(?:e-|e\+|e){0,1}[0-9]{0,})')
in_brackets = re.compile(r'\{([^,}]*)\}')
factorial = re.compile(number.pattern + '!')
imaginary_number = re.compile(number.pattern + '(?:i|j)')
imaginary_unit = variables(['i','j'])
is_valid = re.compile(r'(?=^(?:[0-9+-/\*%\.\(\)\[\]=<>,ije \{\}]|and|or|not|is|True|False|set|print|int){1,}$)')
control = re.compile(r'(?:if|elif|else|for|while|range)')
term = re.compile(r'(?:, *|set|[0-9\.\(\)\[\]\-,ije\{\}]){1,}')
operator = re.compile('(' + term.pattern + ')' + ' *' + tex.pattern + ' *' + '(' + term.pattern + ')')
matrix_prod = re.compile(r'] *\*\ *\[')
matrix_pow = re.compile('(' + term.pattern + r'])\*\*([0-9]*)')
variable_name = re.compile(r'(?!^\d)(?!^[eij]$)^\\{0,1}[a-zA-Z0-9]{1,}$')
var_name = re.compile(r'(?![eij\d])(\\{0,1}[a-zA-Z0-9]{1,})')
array_index = re.compile(r'(\[.*\])_{{0,1}([0-9,]{1,})}{0,1}')
assignment = re.compile(r'(.*) *:= *(.*)')
equal_sign = re.compile(r'(?:<=|>=|==|\{.*=.*\})')