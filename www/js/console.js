// TODO: fix this code up and make it nice and well organized
// 		 one big thing is to break the code up into seperate files
// 			- main.js
// 			- controller.js
// 			- console.js (a singleton object with anon constructor)


// TODO: add web gl for 3d function plotting
// TODO: add responsive design for mobile web (try to do in pure css with @media)
// TODO: make mobile web as much like an app as possible
// TODO: add sidebars for desktop version
// TODO: add ability to expand input prompt to a textarea and write/run a script
// TODO: add 'format' key to functions in python, and use that to populate a calculator on the home page
// TODO: add support for shift + enter, and have checkbox for press enter to send.  (to enable multi-line scripts)

// ----
// TODO: add formatQuery function, and update in real time a query box.  On compute, leave query fixed and only show result in answer area
// ---
$(function() {
	
	var spamControl = true,
		index = 0,
		commandHistory = [],
		prevQuery = '',
		reCommand,
		btns;

	function addBtns(btns, title, opts) {
		opts = opts || {};

		var name, 
			html = '<div class="btn-group"><h5 class="btn-group-title">' + title + '</h5>';
		
		for (var fn in btns) {
			name = (opts.showName) ? fn : '$' + btns[fn].format + '$';
			html += '<p class="btn tex-btn" title="' + btns[fn].help + '" data-format="' + btns[fn].format + '">' + name + '</p>' 
		}

		html += '</div>';

		$('#calculator').prepend(html);

	}

	$('#calculator').on('click', '.tex-btn', function(event) {
		event.preventDefault()
		// need to add at cursor position!  hmm how to do that?
		replaceSelection($(this).data('format'));
		$('#prompt').focus();
		setSelectionRange($('#prompt')[0], $(this).data('format').indexOf('{') + 1)
	});

	MathJax.Hub.Config({
		messageStyle: "none",
		tex2jax: {
		  inlineMath: [["$","$"]]
		}
	});

// TODO: make these always appear in the same order, right now its async so order is random
	(function init() {
		var asyncCount = 0;
		var checkAsync = function() {
			if (++asyncCount > 4) {
				MathJax.Hub.Queue(['Typeset',MathJax.Hub, 'calculator'])();
			}
		}

		compute('history', function(cmds) {
			commandHistory = cmds.split('\n')
			index = commandHistory.length
			checkAsync();
		}, {'X-NO-HISTORY': 'True'});

		compute('show commands', function(cmds) {
			reCommand = new RegExp('^' + cmds.split(', ').join('|'));
			checkAsync();
		}, {'X-NO-HISTORY': 'True'});

		compute('show commands all', function(btns) {
			addBtns(btns, 'Commands', { showName: true });
			checkAsync();
		}, {'X-NO-HISTORY': 'True'});
		
		compute('show operators all', function(btns) {
			addBtns(btns, 'Operators');	
			checkAsync();
		}, {'X-NO-HISTORY': 'True'});
		
		compute('show tex all', function(btns) {
			addBtns(btns, 'Functions');
			checkAsync();
		}, {'X-NO-HISTORY': 'True'});
	})();

	function replaceSelection(str) {
		var pos = (str.indexOf('{') + 1) || 1,
			el = $('#prompt')[0],
			prompt = $('#prompt').val(),
			val = prompt.substr(el.selectionStart, el.selectionEnd - el.selectionStart),
			newVal = prompt.substr(0, el.selectionStart) + str.substr(0, pos) + val + str.substr(pos) + prompt.substr(el.selectionEnd)

		console.log(val);

		$('#prompt').val(newVal);
	}

	function setSelectionRange(input, selectionStart, selectionEnd) {
	  selectionEnd = selectionEnd || selectionStart;
	  if (input.setSelectionRange) {
	    input.focus();
	    input.setSelectionRange(selectionStart, selectionEnd);
	  }
	  else if (input.createTextRange) {
	    var range = input.createTextRange();
	    range.collapse(true);
	    range.moveEnd('character', selectionEnd);
	    range.moveStart('character', selectionStart);
	    range.select();
	  }
	}

	function getParameterByName(name) {
	    name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
	    var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
	        results = regex.exec(location.search);
	    return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
	}

	if (query = getParameterByName('q')) {
		query = atob(query);
		$('#prompt').val(query)
		submit();
	}

	function plot(data) {
		try {
			data = data;
			showGraph([{
				values: data.map(function(a) {
					return {
						x: a[0],
						y: a[1]
					}
				}),
				key: $('#prompt').val(),
				color: '#ff7f0e'
			}]);
		} catch(err) {
			console.log('err', err)
		}
	}

	function showGraph(chartData) {
		$('#chart').show();
		nv.addGraph(function() {
			var chart = nv.models.lineChart()
			            .margin({left: 100})  
			            .useInteractiveGuideline(true)  
			            .showLegend(true)    
			            .showYAxis(true)     
			            .showXAxis(true);    


			chart.xAxis     
			  .tickFormat(d3.format(',r'));

			chart.yAxis     
			  .tickFormat(d3.format('.02f'));

			d3.select('#chart svg')    
			  .datum(chartData)      
			  .call(chart);          

			nv.utils.windowResize(function() { chart.update() });
			return chart;
		});
	}

	function compute(str, callback, headers) {
		prevQuery = str;

		$.ajax({
			url: '/compute',
			type: 'POST',
			headers: headers,
			data: str,
			success: function(response) {
				try {
					callback(JSON.parse(response));
				} catch(e) {
					callback(response);
				}

			},
			error: function(err) {
				callback('  ' + err.responseText + '  ')
			}
		});
	}

	function parseQuery(val) {
		var result;

		cmd = ( match = val.match(reCommand) ) ? match[0] : '';

		switch (cmd) {
			case 'plot':
			case 'iterate':
				var items = val.split(' ');
				return '<p>' + cmd + ' $ ' + (items[1] || '') + ' $ ' + (items[2] || '') + ' ' + (items[3] || '') + ' ' + (items[4] || '');		
			case 'history':
			case 'show':
			case 'session':
				return '<p>' + val + '</p>';
			default:
				return '<p>$ ' + val + ' $</p>';
		}

	}

	function formatMatrix(arr) {
		result = '\\begin{bmatrix}';

		for(var i in arr) {
			if( Array.isArray(arr[i]) ) {
				result += arr[i].join(' & ') + ' \\\\ '
			} else {
				result += arr[i]
				if( 1 + i < arr.length ) {
					result += ' & '
				} else {
					result += ' \\\\ '
				}
			}
		}

		return result + '\\end{bmatrix}';
	}

	window.compute = compute
	window.formatMatrix = formatMatrix

	function submit() {
		var $prompt = $('#prompt'),
			$query = $('#query'),
			$result = $('#result'),
			val = $prompt.val()
		
		commandHistory.push(val);	
		index = commandHistory.length;
		
		if (val === 'clear') {
			$query.html(' ');
			$result.html(' ');
			$prompt.val('');
		} else if( spamControl ) {
			spamControl = false;

			$result.html(' ');
			$('#chart svg').html(' ');
			$('#chart').hide();

			$prompt.val('');
			$prompt.focus();			
			window.setTimeout(function() {
				spamControl = true;
			}, 500);

			compute(val, function(response) {
				cmd = ( match = val.match(reCommand) ) ? match[0] : '';
				switch (cmd) {
					case 'session':
						if (val === 'session unset' || val === 'session unset history') {
							commandHistory = []
							index = 0
						}
					case 'plot':
						plot(response);
						break;
					case 'history':
					case 'show':
						if (typeof response === 'object') {
							response = JSON.stringify(response, null, '\t');
						}

						$result.html('<pre>' + response + '</pre>');
						break;
					case 'iterate':
						var items = val.split(' ');

						$result.html('<p>$$ ' + response + ' $$</p>');
						break;
					default:
						if (Array.isArray(response)) {
							response = formatMatrix(response);
						}

						response = response.replace(/j/g, 'i');

						$result.html('<p>$$ ' + response + ' $$</p>');		
						break;
				}

				MathJax.Hub.Queue(['Typeset',MathJax.Hub, 'result'])();
			});
		}
	}

	$('#save').click(function() {
		q = btoa(prevQuery);
		window.location = '/?q=' + q
	});


	$('#plot').click(function() {
		$('#prompt').val('plot ' + $('#prompt').val());
		submit();
	});

	$('#compute').click(submit);
		
	$('#prompt').focus();

	$('#prompt').keyup(function(event) {
		if (event.keyCode !== 13) {		
			$('#query').html(parseQuery($(this).val()));
			MathJax.Hub.Queue(['Typeset',MathJax.Hub, 'query'])();
		}
	});

	$('#prompt').keydown(function(event) {
		switch (event.keyCode) {
			case 13:
				event.preventDefault();
				submit();
				break;
			case 38:
				event.preventDefault();
				if (index > 0) {
					$('#prompt').val(commandHistory[--index]);
				}
				break;
			case 40:
				if (index < commandHistory.length) {
					$('#prompt').val(commandHistory[++index]);
				}
				break;
			case 57:
				if (this.selectionStart !== this.selectionEnd) {				
					event.preventDefault();
					replaceSelection('()');
				}
				break;
			default:
				console.log('keyCode', event.keyCode)
				break;
		}
	});
});