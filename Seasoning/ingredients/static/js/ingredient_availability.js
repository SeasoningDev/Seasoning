/**
 * This function will transform the bare availability data into
 * eyecandy
 */
function fix_ingredient_availabilities() {
		// Fix every element showing availability data on the page
		$(".ingredient-availability").each(function() {
			if ($(this).hasClass("transformed")) {
				return;
			}
			$(this).addClass("transformed");
			
			// The preservability of this ingredient
			var preservability = Math.round(parseInt($(this).find(".available-in-preservability").text(), 10) / 30);
	        
			// The first available in indicator should have certain margins and a border
		    var first = true;
		    
		    // Markup every available in in this element
		    $(this).children(".available-in").each(function() {
		    	if (first) {
		    		$(this).css('border-top', '1px solid #DDD');
		    		$(this).css('padding-top', '5px');
		    		first = false;
		    	}
		    	
		    	// This should only be 1
		        $(this).find(".availability-indicator").each(function() {
		        	// The month when this availability starts
		            var from = parseInt($(this).children(".available-from").text(), 10);
		            // The month when this availability ends
		            var until = parseInt($(this).children(".available-until").text(), 10);
		            
		            // The month when this availability ends with preservability accounted for
		            var extended_until = (until + preservability - 1) % 12 + 1;
		            
		            // The percentage of the width every month gets
		            var width_p_month = 8.33;
		            
		            // The percentage where the availability indicator starts
		            var from_point = width_p_month * (from - 1);
		            
		            // Clear this element
		            $(this).html("");
		            
		            // Check if we need 2 availability indicators for this available in
		            if (from > (until + 1) ) {
		                var second_indicator = $(this).clone();
		                $(this).css("left", from_point + "%");
		                $(this).css("width", (width_p_month * (12 - from + 1)) + "%");
		                
		                second_indicator.insertAfter($(this));
		                second_indicator.css("left", 0);
		                second_indicator.css("width", (width_p_month * (until)) + "%");
		            } else {
		            	var width;
		                if (from == (until + 1)) {
		                    // The ingredient is available all year round
		                    from_point = 0;
		                    width = 100;
		                } else {
		                	width = width_p_month * (until - from + 1);
		                }
		                $(this).css("left", from_point + "%");
		                $(this).css("width", width + "%");
		            }
		            
		            // Add preservability bars
		            if (preservability > 0 && from != (until + 1)) {
		            	// preservability > 0: We only need to display a preservability bar if the ingredient is preservable
		            	// from != (until + 1): No need to display preservability if the ingredient is available all year
		            	
		                var preservability_indicator = $(this).clone();
		                preservability_indicator.addClass('preservability');
		                
		                if (extended_until > until) {
		                    // We did not wrap around by adding preservability
		                	
		                    preservability_indicator.css("left", ((until * width_p_month) - 1) + "%");
		                    pres_width = preservability * width_p_month + 1;
		                    preservability_indicator.css("width", pres_width + "%");
		                } else {
		                    // preservability wraps around availability
		                    // Create a second preservability indicator
		                	preservability_indicator_2 = preservability_indicator.clone();
		                    
		                	// First goes from 'until' month to last month
		                    preservability_indicator.css("left", (until * width_p_month) + "%");
		                    preservability_indicator.css("width", ((12 - until) * width_p_month) + "%");
		                    
		                    // Second goes from first month to 'extended until' month
		                    preservability_indicator_2.css("left", 0);
		                    preservability_indicator_2.css("width", (extended_until * width_p_month) + "%");
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