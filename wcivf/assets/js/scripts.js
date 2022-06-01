document.addEventListener("DOMContentLoaded", function(event) { 
	var feedback_form = document.forms[1]
	var feedback_form_token = feedback_form.elements[1].value
	var csrfmiddlewaretoken = feedback_form.elements[0].value
	document.querySelector('[name=found_useful]').click(function(el) {
	    var found_useful = document.querySelector(this).value;
	    fetch('/feedback/submit_initial/', {
		method: "POST",
		body: JSON.stringify(data),
		found_useful: found_useful,
		token: feedback_form_token,
		csrfmiddlewaretoken: csrfmiddlewaretoken,
		source_url: window.location.pathname
	    }).then(res => {
		console.log(body);
	    });
	});
});
    
var found_useful = feedback_form.elements[3].value
var comments = feedback_form.elements[8]

if (found_useful.value = undefined) {
	comments.style.display = 'none'
	found_useful.click(function() {
		comments.style.display = ''
	})
}