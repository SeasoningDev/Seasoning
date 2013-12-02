/**
 * This timer will be reset after the user has typed his last character
 * in the search field. This prevents a buttload of queries when a user is
 * search for a long string.
 */
var timer;

$(document).ready(function() {
	
	// Toggle the Advanced Search Window
	$("#advanced-link").click(function() {
		if ($("#advanced-search").is(":visible")) {
			// Hide
			$("#advanced-search").slideUp(1000, function() {
				$("#advanced-link").text("Geavanceerd Zoeken");
				$("#browse-recipe-summaries-wrapper").css("width", "960px");
				$("#id_advanced_search").val("False");
			});
		} else {
			// Show
			$("#browse-recipe-summaries-wrapper").css("width", "720px");
			$("#advanced-search").slideDown(1000);
			$("#advanced-link").text("Niet-geavanceerd zoeken");
			$("#id_advanced_search").val("True");
		}
		return false;
	});

	// Activate the buttons that change the order direction
	$(".order-arrow").click(function() {
		if (!$(this).hasClass("active")) {
			var active_order_arrow = $(".order-arrow.active");
			active_order_arrow.removeClass("active");
			$(this).addClass("active");
			if ($(this).hasClass("up")) {
				$("#id_sort_order_0").click();
			} else {
				$("#id_sort_order_1").click();
			}
		}
		update_page();
		return false;
	});

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
			update_page();
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
		update_page();
		return false;
	});

	// Activate the input field for including ingredients
	$("#include-ingredients-input").pressEnter(function() {
		if ($(this).val() != "") {
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
			new_form.val($(this).val());
			new_form.insertBefore(empty_form);
			// Display the new ingredient as
			// being in the filter
			var new_ing = $('<a href="#"><div class="filtered-ingredient">' + $(this).val() + '</div></a>');
			new_ing.click(function() {
				new_form.remove();
				$(this).remove();
				update_page();
				return false;
			});
			$("#included-ingredients").append(new_ing);
			$(this).val("");
			update_page();
		}
	});
	
	// Activate the input field for excluding ingredients
	$("#exclude-ingredients-input").pressEnter(function() {
		if ($(this).val() != "") {
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
			new_form.val($(this).val());
			new_form.insertBefore(empty_form);
			// Display the new ingredient as
			// being in the filter
			var new_ing = $('<a href="#"><div class="filtered-ingredient">' + $(this).val() + '</div></a>')
			new_ing.click(function() {
				new_form.remove();
				$(this).remove();
				update_page();
				return false;
			});
			$("#excluded-ingredients").append(new_ing);
			$(this).val("");
			update_page();
		}
	});
	
	// Update recipe list on filter change
	$("#id_sort_field").change(update_page);
	$("input[name='cuisine']").change(update_page);
	$("input[name='course']").change(update_page);
	
	/**
	 * Update the recipe list when the user types a search query
	 * 
	 * If the user is typing multiple characters, we wait until he
	 * has finished typing (delay of 1s)
	 */
	// Start the timer when more than 3 chars have been typed
	$("#id_search_string").keyup(function() {
		if ($(this).val().length >= 3) {
			timer = setTimeout(update_page, 1000);
		}
	});
	// Stop the timer when a new char is being typed
	$("#id_search_string").keydown(function() {
		clearTimeout(timer);
	});
	
	// Force a search by pressing the Return key when typing a query
	$("#id_search_string").pressEnter(function() {
		update_page;
		// Stop the timer when a search is being forced
		timer = clearTimeout(timer);
	});
});