$(function() {
	$("#info-button").click(function() {
		var body = $("body");
		
		body.toggleClass("st-menu-open");
		
		if (body.hasClass("st-menu-open")) {
			$(".st-container .st-menu").css("top", ($(window).scrollTop() + 60) + 'px');
			
			
		}
	});
	
	$(".info-overlay").click(function() {
		$(".st-container").removeClass("st-menu-open");
	});
});