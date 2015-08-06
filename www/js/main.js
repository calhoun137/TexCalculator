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
$(function() {
	
	var prevQuery = '';

	MathJax.Hub.Config({
		messageStyle: "none",
		tex2jax: {
		  inlineMath: [["$","$"]]
		}
	});

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

});