var demo_window_template = $('<div class="alert alert-info alert-demo"></div>');
var button_template = $('<a href="#" class="btn btn-primary btn-demo"></a>');


function show_demo_window(window_id) {

	function demo_window() {
		return demo_window_template.clone();
	}
	function demo_button() {
		return button_template.clone();
	}
	
	var window_template = $(window_id);
	
	var demo_window = demo_window().append(window_template.clone());
	demo_window.addClass(window_template.attr('id'))
	
	$("body").append(demo_window);
	demo_window.fadeIn(500);
	
	demo_window.find("a.btn").each(function() {
		$(this).click(function() {
			show_demo_window($(this).data('next'));
			
			demo_window.fadeOut(500, function() {
				$(this).remove();
			})
		})
	})
}

$(function() {
	
	show_demo_window("#demo-start");
	
});
