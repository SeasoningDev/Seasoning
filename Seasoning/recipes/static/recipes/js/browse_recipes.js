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

function replace_prefix(el, id) {
	el.attr('id', el.attr('id').replace('__prefix__', id));
	el.attr('name', el.attr('name').replace('__prefix__', id));
}

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
	$("#end-buttons").fadeOut(200);
}
function next_page() {
	return parseInt($("#next-recipes-page").val());
}
function inc_paging() {
	$("#next-recipes-page").val(next_page() + 1);
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

function show_result_count(count) {
	$("#result-count #count").text(count);
	$("#result-count").fadeIn(200);
}



function ajax_search_recipes() {
	loading_next_page = true;
	
	reset_paging();
	$("#result-count").fadeOut(200);
	
	$("#dark-overlay").fadeIn(200);
	$(".search-results-loader.top").fadeIn(200);
	
	get_recipe_search_results(1).done(function(data) {
		reset_search_results();
		
		if (data.result) {
			no_more_pages = false;
			$("#no-results").fadeOut(200);
			append_search_results(data);
		} else {
			no_more_pages = true;
			$("#no-results").fadeIn(200);
		}
		
		show_result_count(data.result_count);
		
		inc_paging();
		loading_next_page = false;
			
	}).always(function() {
		$("#dark-overlay").fadeOut(200);
		$(".search-results-loader.top").fadeOut(200);
	});
}


function ajax_load_next_page() {
	if (!loading_next_page && !no_more_pages) {
		loading_next_page = true;
		$(".search-results-loader.bottom").fadeIn(200);
		
		var np = next_page();
		
		get_recipe_search_results(np).done(function(data) {
			
			if (data.result) {
				no_more_pages = false;
				append_search_results(data);
			}
			if (!data.has_next) {
				no_more_pages = true;
				$("#end-buttons").fadeIn(200);
			}
			
			if (np == 1) {
				show_result_count(data.result_count);
				if (!data.result)
					$("#no-results").fadeIn(200);
			}
			
			
			inc_paging();
			loading_next_page = false;
			
		}).always(function() {
			$(".search-results-loader.bottom").fadeOut(200);
		})
	}
}

$(function() {
	reset_paging();
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
		//check if user has clicked the placeholder item
		if( $(event.target).is(filter_tab_placeholder) ) {
			(filter_tab_placeholder_default_value == filter_tab_placeholder.text()) ? filter_tab_placeholder.text(filter_tab_placeholder_text) : filter_tab_placeholder.text(filter_tab_placeholder_default_value) ;
			$('#sort-by-wrapper').toggleClass('is-open');
			
		//check if user has clicked a filter already selected 
		} else {
			filter_tab_placeholder.text(filter_tab_placeholder_default_value + $(event.target).text());
			$('#sort-by-wrapper').removeClass('is-open');	
			
			//add class selected to the selected filter item
			$('#sort-by-wrapper .selected').removeClass('selected');
			$(event.target).addClass('selected');

		}
		
		return false;
	});
	
	$("body").click(function() {
		filter_tab_placeholder.text(filter_tab_placeholder_default_value + $('#sort-by-wrapper .selected').text());
		$("#sort-by-wrapper").removeClass('is-open');
	})
	
	// Update the recipes if a sort field is chosen
	$('#sort-by-wrapper li.filter a').click(function() {
		// if one of the elements of the dropdown is selected, we should
		// select the corresponding OPTION element of the sorting SELECT
		// element
		option_value = $(this).attr('data-value');
		
		$('#sort-by-wrapper select option[value="' + option_value + '"]').prop('selected', true);
		
		ajax_search_recipes();
	})
	
	
	
	// Open advanced search
	$('#advanced-search-btn').on('click', function() {
		// Save the users preference
		localStorage.advanced_search = true;
		
		triggerFilter(true);
		
		var spacer = $(".advanced-search-spacer")
		spacer.css('width', $('.cd-filter').css('width'));
		spacer.css('height', $('.cd-filter').css('height'));
		return false;
	});
	
	// Open advanced search if the user prefers the advanced box open
	if (localStorage.advanced_search === 'true') {
		$('#advanced-search-btn').click();
	}
	
	// Close advanced search
	$('#advanced-search-close-btn').on('click', function() {
		$('#id_advanced_search').prop('checked', false);
		
		// Save the users preference
		localStorage.advanced_search = false;
		
		triggerFilter(false);
		
		$(".advanced-search-spacer").css('width', 0);
		return false;
	});
	
	// Open and close advanced search on mobile
	$("#advanced-search-btn-mobile").click(function() {
		if (!$('.cd-filter').hasClass('filter-is-visible')) {
			triggerFilter(true);
		} else {
			triggerFilter(false);
		}
	})

	function triggerFilter($bool) {
		var elementsToTrigger = $([$('.cd-filter-trigger'), $('.cd-filter'), $('.cd-tab-filter'), $('#browse-recipes-wrapper'), $("#advanced-search-close-btn"), $("#overlay-wrapper")]);
		elementsToTrigger.each(function(){
			$(this).toggleClass('filter-is-visible', $bool);
		});
	}
	
	
	
	/**
	 * Advanced Search Bar functions
	 */

	// Close a filter group dropdown inside lateral .cd-filter 
	$('.cd-filter-block h4').on('click', function(){
		$(this).toggleClass('closed').siblings('.cd-filter-content').slideToggle(300);
		
		return false;
	})
	
	/**
	 * Activate filter elements
	 */
	$("#special-inputs input").change(function() {
		ajax_search_recipes();
	})
	
	$("#incl-ing-operator input").change(function() {
		ajax_search_recipes()
	});
	
	$("#incl-ingredients-input").autocomplete({
		source: ingredient_names_url,
		select: function(event, ui) {
			var new_ing = $("#incl-ingredients .incl-ing-template").clone().removeClass('incl-ing-template');
			var new_ing_input = new_ing.find('input'); 
			var parent_div = new_ing.parent();
			
			var total_forms = $('#id_include-TOTAL_FORMS').val();
			replace_prefix(new_ing_input, total_forms);
			new_ing_input.val(ui.item.label);
			new_ing.find('.ing-name .text').text(ui.item.label);
			
			$('#id_include-TOTAL_FORMS').val(parseInt(total_forms) + 1);
			
			new_ing.insertBefore($('.incl-ing-template'));
			
			$(".ui-menu-item").hide();
	        
			event.preventDefault(); 
	        $(this).val('');
	        
	        ajax_search_recipes();
		},
		focus: function(event, ui) { 
			event.preventDefault();
		},
		search: function() {
			$(this).parent().find('.ajax-loader').show();
		},
		response: function() {
			$(this).parent().find('.ajax-loader').hide();
		}
	});
	
	$("#excl-ingredients-input").autocomplete({
		source: ingredient_names_url,
		select: function(event, ui) {
			var new_ing = $("#excl-ingredients .excl-ing-template").clone().removeClass('excl-ing-template');
			var new_ing_input = new_ing.find('input'); 
			var parent_div = new_ing.parent();
			
			var total_forms = $('#id_exclude-TOTAL_FORMS').val();
			replace_prefix(new_ing_input, total_forms);
			new_ing_input.val(ui.item.label);
			new_ing.find('.ing-name .text').text(ui.item.label);
			
			$('#id_exclude-TOTAL_FORMS').val(parseInt(total_forms) + 1);
			
			new_ing.insertBefore($('.excl-ing-template'));
			
			$(".ui-menu-item").hide();
	        
			event.preventDefault(); 
	        $(this).val('');
	        
	        ajax_search_recipes();
		},
		focus: function(event, ui) { 
			event.preventDefault();
		},
		search: function() {
			$(this).parent().find('.ajax-loader').show();
		},
		response: function() {
			$(this).parent().find('.ajax-loader').hide();
		}
	});
	
	$(".boolean-inputs input").change(ajax_search_recipes);
	
	
	
	
	// AFFIX of advanced search bar
	function offset_func_asb(el) {
		if (el.hasClass('affix-top'))
			return 100
			
		return 160;
	}
	var asb = $("#advanced-search-bar")
	asb.affix({
		offset: {
			top: offset_func_asb,
		}
	})
	$("#advanced-search-bar").on('affix.bs.affix', function() {
		$("#advanced-search-bar-spacer").show();
	});
	$("#advanced-search-bar").on('affix-top.bs.affix', function() {
		$("#advanced-search-bar-spacer").hide();
	});
	
	var filters = $('.cd-filter');
	var scrolltop;
	var dir = 0;
	$(window).scroll(function() {
		if ($("#overlay-wrapper").outerHeight() <= $(".cd-filter").outerHeight()) {
			if (filters.css('top') != 210) {
				filters.css('top', '210px');
				filters.css('position', 'absolute');
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
				
				filters.css('top', filters.offset().top + 'px');
				filters.css('position', 'absolute');
			}
			
			if (filters.css('position') != 'fixed' && (filters.offset().top - scrolltop) < 60) {
				if (scrolltop + $(window).height() > filters.offset().top + filters.outerHeight()) {
					filters.css('position', 'fixed');
					filters.css('top', Math.min(60, ($(window).height() - filters.outerHeight())) + 'px');
				}
			}
			
		} else if (scrolltop < prev_scrolltop) {
			// Scrolling up
			if (dir <= 0) {
				// We werent scrolling up before
				dir = 1;
				
				filters.css('top', filters.offset().top + 'px');
				filters.css('position', 'absolute');
			}
			
			if (filters.css('position') != 'fixed' && filters.offset().top > 212) {
				if (scrolltop + 110 <= filters.offset().top) {
					filters.css('position', 'fixed');
					filters.css('top', '110px');
				}
			} else if (filters.offset().top <= 210) {
				filters.css('top', '210px');
				filters.css('position', 'absolute');
			}
		}
	});
})