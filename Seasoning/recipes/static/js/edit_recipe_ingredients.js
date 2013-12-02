/*
 * Add a new ingredient form to the bottom of the formset
 */
function add_ingredient() {
	// Find the empty form
	var empty_form = $("#uses-formset .ingredient.empty-form");
	
	// Clone it and remove the unneeded classes to get a new form
	var new_form = empty_form.clone();
	new_form.removeClass('empty-form');
	new_form.removeClass('sorting-disabled');
	
	// Update the new forms number
	var total_forms = $("#id_ingredients-ingredients-TOTAL_FORMS");
	var new_form_number = parseInt(total_forms.val());
	updateFormNumber(new_form, new_form_number);
	
	// Update total forms counter
	total_forms.val(new_form_number + 1);
	
	// Insert after the last ingredient form
	var last_not_empty_form = $('#uses-formset li.ingredient:not(".empty-form"), #uses-formset li.group:not(".empty-form")').last();
	new_form.insertAfter(last_not_empty_form);
	
	// Fix the ingredient list
	fix_ingredient_list();
	
	return false;
}

/*
 * Add a new ingredient group to the bottom of the formset
 */
function add_group() {
	// Find the empty group
	var empty_group = $("#uses-formset .group.empty-form");
	
	// Clone it and remove the unneeded classes to get a new group
	var new_group = empty_group.clone();
	new_group.removeClass("empty-form");
	new_group.removeClass("sorting-disabled");
	
	// Insert after the last ingredient form
	var last_not_empty_form = $('#uses-formset li.ingredient:not(".empty-form"), #uses-formset li.group:not(".empty-form")').last();
	new_group.insertAfter(last_not_empty_form);
	
	// Fix the ingredient list
	fix_ingredient_list();
	
	return false;
}

/**
 * This function fixes the ingredient list. It handles the following cases:
 * 	- Hides or show the first label, depending on wether there is a group that already provides labels at the top
 *  - Assigns the correct group to every ingredient form and indent them if needed
 *  - Make sure this function is called again when a group has changed
 *  - Add delete functionality to the delete buttons
 *  - Add autocomplete functionality to ingredient forms
 */
function fix_ingredient_list() {
	// Get all ingredient forms and groups (except the empty ones)
	var lis = $("#uses-formset #sortable-ingredients li:not('.column-labels, .empty-form')");
	
	// Hide the labels at the start if they are redundant because of group labels
	if (lis.first().hasClass("group")) {
		$("#uses-formset #sortable-ingredients .column-labels").hide();
    } else {
    	$("#uses-formset #sortable-ingredients .column-labels").show();
    }
	
	// Assign a group to every ingredient form
	var group_name = "";
	var found_group = false;
	lis.each(function() {
		if ($(this).hasClass("group")) {
			// This is a group li, all ingredients between this li and the next group li should belong to this group
			group_name = $(this).find(".group-name").val();
			found_group = true;
        } else if ($(this).hasClass("ingredient")) {
        	// Assign the current group to this ingredient
        	$(this).find("input.group").val(group_name);
        	// If this ingredient is in a group, indent the form
        	if (found_group) {
        		$(this).css('padding-left', '50px');
            } else {
            	$(this).css('padding-left', '30px');
            }
        }
    });
    
	// Change a group name when the user presses enter while editing it
	$("#sortable-ingredients .group input").pressEnter(function() {
		$(this).blur();
    });
    
	// When a group name has changed, fix the ingredient list
	$("#sortable-ingredients .group input").blur(function() {
		fix_ingredient_list();
    });
    
	// Add delete functionality to ingredient forms
	$("#sortable-ingredients .ingredient .delete-button").click(function() {
		var delete_checkbox = $(this).children("input");
		if (delete_checkbox.length) {
			$(this).parents("li").hide()
        } else {
        	$(this).parents("li").remove();
        }
		delete_checkbox.val("True");
		return false;
    });
    
	// Add delete functionality to group forms 
	$("#sortable-ingredients .group .delete-button").click(function() {
		$(this).parents("li").remove();
		fix_ingredient_list();
		return false;
    });
    
	// Add autocomplete functionality to ingredient forms
	$("input.keywords-searchbar").each(function() {
		$(this).autocomplete({
			source: "/ingredients/ing_list/",
			minLength: 2
        });
		$(this).blur(function() {
	    	$.ajax({
	    		url: '/recipes/ingunits/',
	    		type: "POST",
	    		data: {ingredient_name: $(this).val()},
	    		context: this,
	    	    success: function(data) {
	    			var $options = $(this).closest('li').find('select');
	    			var selected_id = $options.find('option:selected').val();
	    			$options.empty();
	    			$("<option value=\"\">---------</option>").appendTo($options);
	    			$.each($.parseJSON(data), function(id, val) {
	    				var option_string = "<option value=\"" + id.toString() + "\"";
	    				if (selected_id == id) {
	    					option_string = option_string + " selected=\"selected\"";
	    				}
	    				option_string = option_string + ">" + val + "</option>";
	    				$(option_string).appendTo($options);
	    			});
	    		} 
		    });
		})
    });
}   

$(document).ready(function() {
	// Make the ingredients and groups sortable
	$( "#sortable-ingredients" ).sortable({
		stop: fix_ingredient_list,
		items: "li:not(.sorting-disabled)",
		handle: ".move-handle"
    });
	$( "#sortable" ).disableSelection();
        
	// Fix the list
	fix_ingredient_list();
	
	// Add functionality to the add buttons
	$(".add-ingredient-button").click(add_ingredient);
	$(".add-ingredientgroup-button").click(add_group);
});