import mimetypes, json
from beaker.middleware import SessionMiddleware
from waitress import serve
import numpy as np
import texscript

# TODO: consider adding mongo db for saving script files as unique url's

# BUG: history is broken
def app(environ, start_response):
	length = int(environ.get('CONTENT_LENGTH', '0'))
	math = environ['wsgi.input'].read(length).decode('utf-8')
	path = environ['PATH_INFO']
	content_type = mimetypes.guess_type(path)[0] or 'text/html'

	session = environ['beaker.session']

	if environ['REQUEST_METHOD'] == 'GET':
		if path == '/' or path == '/index.html':
			status = '200 OK'
			output = open('www/index.html').read()
		else:
			try:
				status = '200 OK'
				if content_type[:5] == 'image':
					start_response(status, [('Content-Type', 'image/jpeg')])
					return environ['wsgi.file_wrapper'](open('www' + path, 'rb'), 32768)
				else:
					output = open('www' + path).read()
			except FileNotFoundError:
				status = '404 Not Found'
				output = status

	elif environ['REQUEST_METHOD'] == 'POST':			
		if path == '/compute':
			session['variables'] = {} if 'variables' not in session else session['variables']
			session['functions'] = {} if 'functions' not in session else session['functions']
			session['history'] = [] if 'history' not in session else session['history']
			
			tex = texscript.session(session['variables'], session['functions'], session['history'])

			if 'HTTP_X_NO_HISTORY' not in environ:
				tex.history.append(math)
			
			try:
				status = '200 OK'
				val = tex.compute(math)
				
				if type(val) == type(np.array([])):
					val = val.tolist()
				
				try:
					output = json.dumps(val)
				except TypeError:
					if type(val) == type(np.array([])):
						output = str(val.tolist())
					else:
						output = str(val)

				session['variables'] = tex._['variables']
				session['functions'] = [tex._['functions'][fn]['math'] for fn in tex._['functions']]
				session['history'] = tex.history
			except (ValueError, SyntaxError, IndexError) as err:
				status = '400 Bad Request'
				output = 'Invalid Tex'	
	else:
		status = '500 Internal Server Error'
		output = status

	output = output.encode('utf-8')
	
	headers = [
		('Content-type', content_type), 
		('Access-control-allow-origin', '*'), 
		('Content-Length', str(len(output)))
	]
	
	session.save()
	
	start_response(status, headers)
	return [output]

wsgi_app = SessionMiddleware(app, {
    'session.type': 'file',
    'session.cookie_expires': True,
	'session.data_dir': '/tmp'    
})

serve(wsgi_app)