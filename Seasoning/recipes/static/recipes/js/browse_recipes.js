/**
 * A function that detects if a user presses the enter key when in the applied element
 */
$.fn.pressEnter = function(fn) {

    return this.each(function() {
    	$(this).unbind('enterPress');
        $(this).bind('enterPress', fn);
        $(this).keydown(function(e) {
            if(e.keyCode == 13)
            {
                e.preventDefault();
                return false;
            }
        });
        $(this).keyup(function(e){
            if(e.keyCode == 13)
            {
              $(this).trigger("enterPress");
            }
        });
    });  
};

/**
 * This timer will be reset after the user has typed his last character
 * in the search field. This prevents a buttload of queries when a user is
 * search for a long string.
 * 
 * Form and filter stuff courtesy of Codyhouse Content Filter Plugin
 * http://codyhouse.co/gem/content-filter/
 * 
 */
var timer;
var loading_next_page = false;
var no_more_pages = false;

function reset_paging() {
	$("#next-recipes-page").val(1);
}
function next_page() {
	$("#next-recipes-page").val();
}
function inc_paging() {
	$("#next-recipes-page").val(parseInt($("#next-recipes-page").val()) + 1);
}

function reset_search_results() {
	$("#browse-recipes-wrapper").empty();
}
 
function append_search_results(data) {
	$("#browse-recipes-wrapper").append($(data.result));
}

function get_recipe_search_results(page) {
	return $.ajax({
		url: get_recipes_url,
		data: $("#recipe-search-form").serialize(),
		method: 'post',
	});
}



function ajax_search_recipes() {
	reset_paging();
	
	$("#dark-overlay").fadeIn(200);
	$(".search-results-loader.top").fadeIn(200);
	
	get_recipe_search_results(1).done(function(data) {
		reset_search_results();
		
		if (data.result) {
			no_more_pages = false;
			$("#no-result").fadeOut(200);
			append_search_results(data);
		} else {
			no_more_pages = true;
			$("#no-result").fadeIn(200)
		}
		
		inc_paging();
			
	}).always(function() {
		$("#dark-overlay").fadeOut(200);
		$(".search-results-loader.top").fadeOut(200);
	});
}


function ajax_load_next_page() {
	if (!loading_next_page && !no_more_pages) {
		loading_next_page = true;
		$(".search-results-loader.bottom").fadeIn(200);
		
		get_recipe_search_results(next_page()).done(function(data) {
			
			if (data.result) {
				no_more_pages = false;
				append_search_results(data);
			} else {
				no_more_pages = true;
			}
			
			inc_paging();
			loading_next_page = false;
			
		}).always(function() {
			$(".search-results-loader.bottom").fadeOut(200);
		})
	}
}

$(function() {
	ajax_load_next_page();
	
	/**
	 * Update the recipe list when the user types a search query
	 * 
	 * If the user is typing multiple characters, we wait until he
	 * has finished typing (delay of 1s)
	 */
	// Start the timer when more than 3 chars have been typed
	$("#id_search_query").keyup(function(event) {
		if ((event.keyCode >= 65 && event.keyCode <= 90) || event.keyCode == 8) {
			var x = $(this).val().length;
			clearTimeout(timer);
			timer = setTimeout(ajax_search_recipes, 100);
		}
	});
	// Stop the timer when a new char is being typed
	$("#id_search_query").keydown(function() {
		clearTimeout(timer);
	});
	
	// Force a search by pressing the Return key when typing a query
	$("#id_search_query").pressEnter(ajax_search_recipes);
	
	
	// Auto load next page of results on scroll
	$(window).scroll(function() {
		if(($(window).scrollTop() + $(window).height()) > ($(document).height() - 500)) {
           
            ajax_load_next_page();
        }
    });
	
	
	
	// Detect click event on sorting button (Codyhouse)
	var filter_tab_placeholder = $('#sort-by-wrapper .placeholder a');
	var filter_tab_placeholder_default_value = 'Sorteren op: ';
	var filter_tab_placeholder_text = filter_tab_placeholder.text();
	
	$('#sort-by-wrapper  li').on('click', function(event){
		//detect which tab filter item was selected
		var selected_filter = $(event.target).data('type');
			
		//check if user has clicked the placeholder item
		if( $(event.target).is(filter_tab_placeholder) ) {
			(filter_tab_placeholder_default_value == filter_tab_placeholder.text()) ? filter_tab_placeholder.text(filter_tab_placeholder_text) : filter_tab_placeholder.text(filter_tab_placeholder_default_value) ;
			$('#sort-by-wrapper').toggleClass('is-open');
			
		//check if user has clicked a filter already selected 
		} else if( filter_tab_placeholder.data('type') == selected_filter ) {
			filter_tab_placeholder.text(filter_tab_placeholder_default_value + $(event.target).text());
			$('#sort-by-wrapper').removeClass('is-open');	

		} else {
			//close the dropdown and change placeholder text/data-type value
			$('#sort-by-wrapper').removeClass('is-open');
			filter_tab_placeholder.text(filter_tab_placeholder_default_value + $(event.target).text()).data('type', selected_filter);
			filter_tab_placeholder_text = $(event.target).text();
			
			//add class selected to the selected filter item
			$('#sort-by-wrapper .selected').removeClass('selected');
			$(event.target).addClass('selected');
		}
		
		return false;
	});
	
	// Update the recipes if a sort field is chosen
	$('#sort-by-wrapper li.filter a').click(function() {
		// if one of the elements of the dropdown is selected, we should
		// select the corresponding OPTION element of the sorting SELECT
		// element
		option_value = $(this).attr('data-value');
		
		$('#sort-by-wrapper select option[value="' + option_value + '"]').prop('selected', true);
		
		ajax_search_recipes();
	})
})