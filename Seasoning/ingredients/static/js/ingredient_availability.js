
	function fix_ingredient_availabilities() {
		$(".ingredient-availability").each(function() {
			$(this).height(parseInt($(this).find(".number-of-groups").text())*30 + 25);
		    var offset_top = 20;
		    var first = true;
		    $(this).children(".available-in").each(function() {
		    	$(this).css("top", offset_top);
		        offset_top = offset_top + 30;
		        var extra_top = 0;
		        if (first) {
		    		$(this).css('border-top', '1px solid #DDD');
		    		$(this).css('padding-top', '10px');
		    		first = false;
		    		offset_top = offset_top + 10;
		    		extra_top = 10;
		    	}
		        var preservability = Math.round(parseInt($(".available-in-preservability").text()) / 30);
		        $(this).children(".availability-indicator").each(function() {
		            var from = parseInt($(this).children(".available-from").text());
		            var until = parseInt($(this).children(".available-until").text());
		            var extended_until = (until + preservability - 1) % 12 + 1;
		            
		            var total_width = ($(".month.alpha").width() + 1) * 12;
		            var from_point = total_width * ((from-1)/12);
		            var until_point = total_width * (until/12);
		            var left_margin = parseInt($(".month.alpha").css("margin-left").replace("px", ""));
		            $(this).html("");
		            
		            if (from > (until + 1) ) {
		                var second_indicator = $(this).clone();
		                $(this).css("left", left_margin);
		                $(this).css("width", until_point);
		                $(this).css("top", extra_top + "px");
		                second_indicator.insertAfter($(this));
		                second_indicator.css("left", from_point + left_margin);
		                second_indicator.css("width", total_width - from_point);
		                second_indicator.css("top", extra_top + "px");
		            } else {
		                if (from == (until + 1)) {
		                    // The ingredient is available all year round
		                    var from_point = total_width * (0/12);
		                    var until_point = total_width * (12/12);
		                }
		                $(this).css("left", from_point + left_margin);
		                $(this).css("width", until_point - from_point);
		                $(this).css("top", extra_top + "px");
		            }
		            
		            // Add preservability bars
		            if (preservability > 0 && from != (until + 1)) {
		            	// preservability > 0: We only need to display a preservability bar if the ingredient is preservable
		            	// from != (until + 1): No need to display preservability if the ingredient is available all year
		                var preservability_indicator = $(this).clone();
		                preservability_indicator.addClass('preservability');
		                if (extended_until > until) {
		                    // We did not wrap around by adding preservability
		                    preservability_indicator.css("left", left_margin + until_point - 20);
		                    pres_width = total_width * (preservability/12) + 20;
		                    preservability_indicator.css("width", pres_width);
		                } else {
		                    // preservability wraps around availability
		                    preservability_indicator_2 = preservability_indicator.clone()
		                    preservability_indicator.css("left", left_margin + until_point - 20);
		                    preservability_indicator.css("width", total_width - until_point + 20);
		                    preservability_indicator_2.css("left", left_margin);
		                    preservability_indicator_2.css("width", total_width * (extended_until/12));
		                    preservability_indicator_2.insertAfter($(this));
		                }
		                preservability_indicator.insertAfter($(this));
		            }
		        });
		        
		    });
		});
	}
	
	function update_tooltips() {
		$(".availability-indicator").tooltip({
			content: function() {
				return $(this).attr('title');
			}
		});
	}
	
$(document).ready(function() {

	fix_ingredient_availabilities();
	update_tooltips();
	
});