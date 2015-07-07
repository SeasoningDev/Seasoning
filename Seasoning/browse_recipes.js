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

function update_recipe_page() {
	$(window).trigger("ajax-clear-and-load-data");
}

function replace_prefix(el, id) {
	el.attr('id', el.attr('id').replace('__prefix__', id));
	el.attr('name', el.attr('name').replace('__prefix__', id));
}

$(document).ready(function() {
	
	

	// Open advanced search
	$('.cd-filter-trigger').on('click', function() {
		$('#id_advanced_search').prop('checked', true);

		// Save the users preference
		localStorage.advanced_search = true;
		
		triggerFilter(true);
		return false;
	});
	
	// Open advanced search if the user prefers the advanced box open
	if (localStorage.advanced_search === 'true') {
		$('.cd-filter-trigger').click();
	}
	
	// Close advanced search
	$('.cd-filter .cd-close').on('click', function() {
		$('#id_advanced_search').prop('checked', false);
		
		// Save the users preference
		localStorage.advanced_search = false;
		
		triggerFilter(false);
		return false;
	});

	function triggerFilter($bool) {
		var elementsToTrigger = $([$('.cd-filter-trigger'), $('.cd-filter'), $('.cd-tab-filter'), $('.cd-gallery')]);
		elementsToTrigger.each(function(){
			$(this).toggleClass('filter-is-visible', $bool);
		});
	}
	
	


	// Detect click event on sorting button (Codyhouse)
	var filter_tab_placeholder = $('.cd-tab-filter .placeholder a'),
		filter_tab_placeholder_default_value = 'Sorteren op...',
		filter_tab_placeholder_text = filter_tab_placeholder.text();
	
	$('.cd-tab-filter li').on('click', function(event){
		//detect which tab filter item was selected
		var selected_filter = $(event.target).data('type');
			
		//check if user has clicked the placeholder item
		if( $(event.target).is(filter_tab_placeholder) ) {
			(filter_tab_placeholder_default_value == filter_tab_placeholder.text()) ? filter_tab_placeholder.text(filter_tab_placeholder_text) : filter_tab_placeholder.text(filter_tab_placeholder_default_value) ;
			$('.cd-tab-filter').toggleClass('is-open');

		//check if user has clicked a filter already selected 
		} else if( filter_tab_placeholder.data('type') == selected_filter ) {
			filter_tab_placeholder.text($(event.target).text());
			$('.cd-tab-filter').removeClass('is-open');	

		} else {
			//close the dropdown and change placeholder text/data-type value
			$('.cd-tab-filter').removeClass('is-open');
			filter_tab_placeholder.text($(event.target).text()).data('type', selected_filter);
			filter_tab_placeholder_text = $(event.target).text();
			
			//add class selected to the selected filter item
			$('.cd-tab-filter .selected').removeClass('selected');
			$(event.target).addClass('selected');
		}
		
		return false;
	});
	
	
	

	// Close a filter group dropdown inside lateral .cd-filter 
	$('.cd-filter-block h4').on('click', function(){
		$(this).toggleClass('closed').siblings('.cd-filter-content').slideToggle(300);
		
		return false;
	})
	
	
	
	
	/**
	 * SORTING
	 */
	$('#sort-field-wrapper li.filter a').click(function() {
		// if one of the elements of the dropdown is selected, we should
		// select the corresponding OPTION element of the sorting SELECT
		// element
		option_value = $(this).attr('data-value');
		
		$('#sort-field-wrapper select option[value="' + option_value + '"]').prop('selected', true);
		
		update_recipe_page();
	})
	
	
	/**
	 * Activate filter elements
	 */
	$("#special-inputs input").change(function() {
		update_recipe_page();
	})
	
	$("#incl-ing-operator").click(update_recipe_page);
	
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
			console.log(parseInt(total_forms) + 1);
			$('#id_include-TOTAL_FORMS').val(parseInt(total_forms) + 1);
			
			new_ing.insertBefore($('.incl-ing-template'));
			
			$(".ui-menu-item").hide();
	        
			event.preventDefault(); 
	        $(this).val('');
	        
	        update_recipe_page();
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
			console.log(parseInt(total_forms) + 1);
			$('#id_exclude-TOTAL_FORMS').val(parseInt(total_forms) + 1);
			
			new_ing.insertBefore($('.excl-ing-template'));
			
			$(".ui-menu-item").hide();
	        
			event.preventDefault(); 
	        $(this).val('');
	        
	        update_recipe_page();
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
	
	$(".boolean-inputs input").change(update_recipe_page);
	
	/**
	 * Update the recipe list when the user types a search query
	 * 
	 * If the user is typing multiple characters, we wait until he
	 * has finished typing (delay of 1s)
	 */
	// Start the timer when more than 3 chars have been typed
	$("#id_search_string").keyup(function(event) {
		if ((event.keyCode >= 65 && event.keyCode <= 90) || event.keyCode == 8) {
			var x = $(this).val().length;
			clearTimeout(timer);
			timer = setTimeout(update_recipe_page, 100);
		}
	});
	// Stop the timer when a new char is being typed
	$("#id_search_string").keydown(function() {
		clearTimeout(timer);
	});
	
	// Force a search by pressing the Return key when typing a query
	$("#id_search_string").pressEnter(function() {
		update_recipe_page();
	});
	
	update_recipe_page();
});