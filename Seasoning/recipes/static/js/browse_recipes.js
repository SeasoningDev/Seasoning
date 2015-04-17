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
	
	
	// Activate the buttons for veganism selection
	$(".veg-choice").each(function() {
		if (!$(this).children("input").prop("checked")) {
			$(this).removeClass("active");
		}
		$(this).click(function() {
			if ($(this).hasClass("active")) {
				$(this).removeClass("active");
				$(this).children("input").prop('checked', false);
			} else {
				$(this).addClass("active");
				$(this).children("input").prop('checked', true);
			}
			update_recipe_page();
			return false;
		});
	});

	// Activate the button for the include ingredients operator
	$("#incl-ings .option").click(function() {
		if (!$(this).hasClass("active")) {
			var active_option = $("#incl-ings .option.active");
			active_option.removeClass("active");
			$(this).addClass("active");
			if ($(this).hasClass("and")) {
				$("#id_include_ingredients_operator_0").click();
			} else {
				$("#id_include_ingredients_operator_1").click();
			}
		}
		update_recipe_page();
		return false;
	});
	
	function add_include_ingredient(ingredient) {
		if (ingredient && ingredient != "") {
			// If the user pressed enter while
			// in the input field, and it
			// contains text,
			// add another ingredient to the
			// filter
			var current_form_num = parseInt($("#id_include-TOTAL_FORMS").val());
			$("#id_include-TOTAL_FORMS").val(current_form_num + 1);
			var empty_form = $("#id_include-__prefix__-name");
			var new_form = empty_form.clone();
			new_form.attr("id", new_form.attr("id").replace("__prefix__", current_form_num));
			new_form.attr("name", new_form.attr("name").replace("__prefix__",current_form_num));
			new_form.val(ingredient);
			new_form.insertBefore(empty_form);
			// Display the new ingredient as
			// being in the filter
			var new_ing = $('<a href="#"><div class="filtered-ingredient">' + ingredient + '</div></a>');
			new_ing.click(function() {
				new_form.remove();
				$(this).remove();
				update_recipe_page();
				return false;
			});
			$("#included-ingredients").append(new_ing);
			update_recipe_page();
		}
	}
	
	// Activate the input field for including ingredients
	$("#advanced-search #include-ingredients-input").autocomplete({
		source: "/ingredients/ing_list/",
		minLength: 2,
		select: function(event, ui) {
			if (event.keyCode != 13) {
				add_include_ingredient(ui.item.value);
			}
		},
	});
	
	function add_exclude_ingredient(ingredient) {
		if (ingredient && ingredient != "") {
			// If the user pressed enter while
			// in the input field, and it
			// contains text,
			// add another ingredient to the
			// filter
			var current_form_num = parseInt($("#id_exclude-TOTAL_FORMS").val());
			$("#id_exclude-TOTAL_FORMS").val(current_form_num + 1);
			var empty_form = $("#id_exclude-__prefix__-name");
			var new_form = empty_form.clone();
			new_form.attr("id", new_form.attr("id").replace("__prefix__",current_form_num));
			new_form.attr("name", new_form.attr("name").replace("__prefix__",current_form_num));
			new_form.val(ingredient);
			new_form.insertBefore(empty_form);
			// Display the new ingredient as
			// being in the filter
			var new_ing = $('<a href="#"><div class="filtered-ingredient">' + ingredient + '</div></a>')
			new_ing.click(function() {
				new_form.remove();
				$(this).remove();
				update_recipe_page();
				return false;
			});
			$("#excluded-ingredients").append(new_ing);
			update_recipe_page();
		}
	}
	
	// Activate the input field for excluding ingredients
	$( "#advanced-search #exclude-ingredients-input").autocomplete({
		source: "/ingredients/ing_list/",
		minLength: 2,
		select: function(event, ui) {
			if (event.keyCode != 13) {
				add_exclude_ingredient(ui.item.value);
			}
		},
	});
	
	// Update recipe list on filter change
	$("#id_sort_field").change(update_recipe_page);
	$("input[name='cuisine']").change(update_recipe_page);
	$("input[name='course']").change(update_recipe_page);
	
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