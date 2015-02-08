/*
 * Add a new ingredient form to the bottom of the formset
 */
function add_ingredient() {
	// Find the empty form
	var empty_form = $("#ingredients-wrapper .ingredient.empty-form");
	console.log(empty_form);
	
	// Clone it and remove the unneeded classes to get a new form
	var new_form = empty_form.clone();
	new_form.removeClass('empty-form');
	new_form.removeClass('sorting-disabled');
	
	// Update the new forms number
	var total_forms = $("#id_uses-TOTAL_FORMS");
	var new_form_number = parseInt(total_forms.val());
	updateFormNumber(new_form, new_form_number);
	
	// Update total forms counter
	total_forms.val(new_form_number + 1);
	
	// Insert before the empty form
	new_form.insertBefore(empty_form);
	
	new_form.find('.group-editable-field').each(function() {
		set_default_text(0, $(this));
	});
	
	// Fix the ingredient list
	fix_ingredient_list();
	
	return false;
}

/*
 * Add a new ingredient group to the bottom of the formset
 */
//function add_group() {
//	// Find the empty group
//	var empty_group = $("#uses-formset .group.empty-form");
//	
//	// Clone it and remove the unneeded classes to get a new group
//	var new_group = empty_group.clone();
//	new_group.removeClass("empty-form");
//	new_group.removeClass("sorting-disabled");
//	
//	// Insert after the last ingredient form
//	var last_not_empty_form = $('#uses-formset li.ingredient:not(".empty-form"), #uses-formset li.group:not(".empty-form")').last();
//	new_group.insertAfter(last_not_empty_form);
//	
//	// Fix the ingredient list
//	fix_ingredient_list();
//	
//	return false;
//}

function fix_ing_units(ing_row) {
	$.ajax({
		url: ingredient_units_url,
		type: "POST",
		data: {
			ing_id: ing_row.find('.ingredient-id-input').val()
		},
	    success: function(data) {
			var $options = ing_row.find('select');
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
}

var ing_edit_func = function() {
	if ($(".editing").length) {
		alert("Je bent al een veld aan het wijzigen.");
		$("html, body").animate({scrollTop: ($('.editing').offset().top - 100) + 'px'}, '500');
		return false;
	}
	
	var ing = $(this);
	if (ing.hasClass("editing")) {
		// We are currently editing this field, do nothing
		return false;
	}
	ing.addClass("editing");
	ing.unbind('click');
	
	var prev_unit_val = ing.find('select').val();

	$(this).find('.group-editable-field').each(function() {
		var el = $(this);
		var field = $(this).next('input, select');
		
		if (field.is('input')) {
			field.val(el.text().replace(',', '.'));
		}
		
		el.hide();
		field.show().click(function(event) {
			event.stopPropagation();
		});
		field.height(el.height());
	});
	
	var buttons = $(".edit-recipe-buttons").clone();
	ing.after(buttons);
	

	buttons.find('.accept-button').click(function() {
		var par = $(this).parent().parent();
		
		// Check if the given ingredient is in the database, if not, confirm that
		// this is intentional
		var ing_in_db = true;
		var id_input = par.find('.ingredient-id-input'); 
		var unit_input = par.find('select');
		if (unit_input.val() == '') {
			alert('Gelieve een eenheid op te geven.');
			return false;
		} else if (id_input.val() == '') {
			ing_in_db = false;
			var ok = confirm('Het opgegeven ingrediënt werd niet teruggevonden in onze database. Ons team zal ' +
							 'dit zo snel mogelijk in orde proberen te brengen, maar in de tussentijd zal dit ' +
							 'recept enkel voor jou zichtbaar zijn.');
			if (!ok)
				return false;
		} else {
			// TODO: check of de eenheid kan gebruikt worden met dit ingredient
		}
		
		buttons.hide();
		
		// Hide any autocompleting tooltips
		$(".ui-autocomplete").hide();
		
		// Show a loading overlay while the field is being saved
		var overlay = $('<div style="position:absolute;background-color: rgba(0, 0, 0, .5);z-index:901;text-align:center;"><img src="/static/img/decoration/ajax-loader.png" style="padding-top: 5px;max-height:100%;"/></div>')
		overlay.width(ing.outerWidth());
		overlay.height(ing.outerHeight());
		overlay.css('top', ing.offset().top);
		overlay.css('left', ing.offset().left);
		$("body").append(overlay);
		
		// Save the form
		$.ajax({
			type: "POST",
			url: $("#edit-recipe-form").attr('action'),
			data: $("#edit-recipe-form").serialize(),
		}).success(function(data) {
			overlay.remove();
			
			if (data == '') {
				ing.find('.group-editable-field').each(function() {
					el = $(this);
					field = el.next('input, select');
					
					if (field.is('select')) {
						el.text(field.children('option').filter(':selected').text());
					}
					
					field.unbind('click');
					field.hide();
					
					set_default_text(0, el);
					el.show()
				});
				ing.removeClass("editing");
				ing.click(ing_edit_func);
			} else {
				$("#edit-ingredients-container").html(data);
				
				fix_ingredient_list();
			}
			buttons.remove();
		}).error(function(jqXHR) {
			overlay.remove();
			
			if (jqXHR.status == 500) {
				alert(jqXHR.responseText);
			} else {
				alert('Er is een probleem opgetreden bij het contacteren van de server, probeer het later nogmaals.')
			}
			
			// Show the buttons again in case of error
			buttons.show()
		});
		
		return false;
	});
	
	
	buttons.find('.reject-button').click(function() {
		ing.find('.group-editable-field').each(function() {
			el = $(this);
			field = el.next('input, select');
			
			field.unbind('click');
			field.hide();
			
			set_default_text(0, el);
			el.show()
		});
		
		ing.find('select').val(prev_unit_val);
		
		buttons.remove();
		ing.removeClass("editing");
		ing.click(ing_edit_func);
		
		return false;
	});
	
	buttons.show();
	
	
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
	
//	// Get all ingredient forms and groups (except the empty ones)
//	var lis = $("#uses-formset #sortable-ingredients li:not('.column-labels, .empty-form')");
//	
//	// Hide the labels at the start if they are redundant because of group labels
//	if (lis.first().hasClass("group")) {
//		$("#uses-formset #sortable-ingredients .column-labels").hide();
//    } else {
//    	$("#uses-formset #sortable-ingredients .column-labels").show();
//    }
//	
//	// Assign a group to every ingredient form
//	var group_name = "";
//	var found_group = false;
//	lis.each(function() {
//		if ($(this).hasClass("group")) {
//			// This is a group li, all ingredients between this li and the next group li should belong to this group
//			group_name = $(this).find(".group-name").val();
//			found_group = true;
//        } else if ($(this).hasClass("ingredient")) {
//        	// Assign the current group to this ingredient
//        	$(this).find("input.group").val(group_name);
//        	// If this ingredient is in a group, indent the form
//        	if (found_group) {
//        		$(this).css('padding-left', '50px');
//            } else {
//            	$(this).css('padding-left', '30px');
//            }
//        }
//    });
//    
//	$("#sortable-ingredients .group input").each(function() {
//		// Change a group name when the user presses enter while editing it
//		$(this).pressEnter(function() {
//			$(this).blur();
//		});
//		// When a group name has changed, fix the ingredient list
//		$(this).unbind('blur');
//		$(this).blur(fix_ingredient_list);
//		
//	});
//    
//	$("#sortable-ingredients .group input").blur(function() {
//		fix_ingredient_list();
//    });
    
	// Add delete functionality to ingredient forms
	$("#ingredients-wrapper .ingredient .delete-button").click(function() {
		var ing = $(this).parents('.ingredient');
		
		var delete_checkbox = $(this).children("input");
		delete_checkbox.prop('checked', true);
		
		// Show a loading overlay while the field is being saved
		var overlay = $('<div style="position:absolute;background-color: rgba(0, 0, 0, .5);z-index:901;text-align:center;"><img src="/static/img/decoration/ajax-loader.png" style="padding-top: 5px;max-height:100%;"/></div>')
		overlay.width(ing.outerWidth());
		overlay.height(ing.outerHeight());
		overlay.css('top', ing.offset().top);
		overlay.css('left', ing.offset().left);
		$("body").append(overlay);
		
		$.ajax({
			type: "POST",
			url: $("#edit-recipe-form").attr('action'),
			data: $("#edit-recipe-form").serialize(),
		}).success(function(data) {
			overlay.remove();
			$("#edit-ingredients-container").html(data);
			
			fix_ingredient_list();
			
		}).error(function(jqXHR) {
			overlay.remove();
			
			if (jqXHR.status == 500) {
				alert(jqXHR.responseText);
			} else {
				alert('Er is een probleem opgetreden bij het contacteren van de server, probeer het later nogmaals.')
			}
		});
		return false;
    });
    
	// Add autocomplete functionality to ingredient forms
	$("input.keywords-searchbar").each(function() {
		$(this).autocomplete({
			source: ingredient_list_url,
			minLength: 2,
			search: function(event, ui) {
				$(this).addClass('loading');
			},
			open: function(event, ui) {
				$(this).removeClass('loading');

				if ($(event.target).is(':not(:focus)'))
					$('.ui-autocomplete').hide();
			},
			focus: function(event, ui) {
				if (event.keyCode) {
					var textinput = $(event.target)
					textinput.val(ui.item.label);
					textinput.parent().find('.ingredient-id-input').val(ui.item.value);
					
					return false;
				}	
			},
			select: function(event, ui) {
				var textinput = $(event.target)
				textinput.val(ui.item.label);
				textinput.parent().find('.ingredient-id-input').val(ui.item.value);
				
				$(ui.target).blur();
				return false;
			},
			response: function(event, ui) {
				var textinput = $(event.target);
				textinput.removeClass('loading');
				
				$.each(ui.content, function(index, match) {
					if (match.label.toUpperCase() === textinput.val().trim().toUpperCase()) {
						textinput.parent().find('.ingredient-id-input').val(match.value);
						fix_ing_units(textinput.parent().parent());
					}
				});
			},
        }).on('input', function(event) {
			var textinput = $(event.target);
			textinput.parent().find('.ingredient-id-input').val('');
        }).pressEnter(function(event) {
			$(this).blur();
        }).unbind('blur').blur(function() {
        	$(this).removeClass('loading');
			$(".ui-autocomplete").hide();
        	var par = $(this).parent().parent();
        	
	    	fix_ing_units(par);
		})
    });

	$('.edit-ingredient').click(ing_edit_func);
	
	$('.ingredient input').focus(function() {
		$(this).select();
	})
}

$(document).ready(function() {
	// Make the ingredients and groups sortable
//	sort_options = {
//		stop: fix_ingredient_list,
//		items: ".ingredient:not(.empty-row)",
//		handle: ".move-button",
//	}
//	var userAgent = navigator.userAgent.toLowerCase();
//	if(userAgent.match(/firefox/)) {
//		sort_options["start"] = function (event, ui) {
//			ui.item.css('margin-top', $(window).scrollTop() ); 
//		};
//		sort_options["beforeStop"] = function (event, ui) { ui.item.css('margin-top', 0 ); };
//	}
//	
//	$( "#ingredients-wrapper #ingredients" ).sortable(sort_options);
//	$( "#ingredients-wrapper #ingredients" ).disableSelection();
        
	// Fix the list
	fix_ingredient_list();
	
	// Add functionality to the add buttons
	$("#add-ingredient-button").click(add_ingredient);
//	$("#add-ingredientgroup-button").click(add_group);
});