$(function() {
	var body = $("body");
	
	$("#info-button").click(function() {
		body.toggleClass("st-menu-open");
	});
	
	$(".info-overlay").click(function() {
		body.removeClass("st-menu-open");
	});
	
	var infobar = $('.st-menu');
	var scrolltop;
	var dir = 0;
	$(window).scroll(function() {
		// Calculate length of page without infobar
		var h_determining_el = Math.max($("#overlay-wrapper").outerHeight(), $(".cd-filter").outerHeight());
		
		if (h_determining_el + 210 <= infobar.outerHeight() + 60) {
			if (infobar.css('top') != 60 || infobar.css('position') != 'absolute') {
				infobar.css('top', '60px');
				infobar.css('position', 'absolute');
			}
			return
		}
			
		if (!scrolltop)
			scrolltop = $(window).scrollTop();
		
		var prev_scrolltop = scrolltop;
		scrolltop = $(window).scrollTop();
		
		if (scrolltop > prev_scrolltop) {
			// Scrolling down
			if (dir >= 0) {
				// We weren't scrolling down before
				dir = -1;
				
				// Lock the elements position on the page so we scroll to the bottom of it
				infobar.css('top', infobar.offset().top + 'px');
				infobar.css('position', 'absolute');
			}
			
			
			if (infobar.css('position') != 'fixed' && (infobar.offset().top - scrolltop) < 110) {
				if (scrolltop + $(window).height() > infobar.offset().top + infobar.outerHeight()) {
					infobar.css('position', 'fixed');
					infobar.css('top', Math.min(110, ($(window).height() - infobar.outerHeight())) + 'px');
				}
			}
			
		} else if (scrolltop < prev_scrolltop) {
			// Scrolling up
			if (dir <= 0) {
				// We werent scrolling up before
				dir = 1;
				
				// Lock the elements position on the page so we scroll to the top of it
				infobar.css('top', infobar.offset().top + 'px');
				infobar.css('position', 'absolute');
			}
			
			// Check if we have scrolled to the top of the element
			if (infobar.css('position') != 'fixed' && infobar.offset().top > 62) {
				if (scrolltop + 60 <= infobar.offset().top) {
					infobar.css('position', 'fixed');
					infobar.css('top', '60px');
				}
			} else if (infobar.offset().top <= 60) {
				// Never let the element go higher than this on the page
				infobar.css('top', '60px');
				infobar.css('position', 'absolute');
			}
		}
	});
});