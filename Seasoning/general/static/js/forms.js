/**
 * Functions for formsets
 * 
 * To make a formset dynamically extensible using this code, a formset element must abide
 * to the following rules:
 * 	- The element containing the entire formset must have an 'id' element with a value
 * 	  'id_formset_prefix-formset' and a class of 'formset'
 *  - The containing element must have the following (indirect) child elements:
 *  	o A managament form with a TOTAL_FORMS element (Provided by django).
 *  	o An empty form, with its ordinal numbers replaced by '__prefix__' (Provided by django).
 *  	o An element with a class of 'formset-button-container' which will contain the 
 *  	  'add a form' button.
 */
function updateFormNumber($form, number) {
	var id_regex = new RegExp('__prefix__');
	$form.find('*').each(function() {
		if ($(this).attr("for")) $(this).attr("for", $(this).attr("for").replace(id_regex,
				number));
		if (this.id) this.id = this.id.replace(id_regex, number);
		if (this.name) this.name = this.name.replace(id_regex, number);
	});
}

function add_form(formset_prefix, newforms_callback) {
	// Get the neccessary elements
	var $formset = $('#' + formset_prefix + '-formset');
	var $empty_form = $formset.find('.empty');
	
	// Find out what the new forms number is
	var $form_counter = $formset.find('#id_' + formset_prefix + '-TOTAL_FORMS');
	var new_form_number = parseInt($form_counter.val());
	
	// Create the new form
	var $new_form = $($empty_form).clone(false).removeClass('empty');
	updateFormNumber($new_form, new_form_number);
	
	// Insert the new form before the empty form
	$new_form.insertBefore($empty_form);
	// Update the amount of forms
	$form_counter.val(new_form_number + 1);
	
	if (newforms_callback) {
		newforms_callback($new_form);
	}
}

/**
 * Functions for autocomplete fields
 * 
 * To make an input field autocomplete ingredient names, give it the following attributes:
 * 
 * 	Class: autocomplete-ingredient
 */
$(document).ready(function() {
	/*
	 * Autcomplete Ingredient field
	 */
	$( "input.autocomplete-ingredient" ).each(function() {
		$(this).autocomplete({
			source: "/ingredients/ing_list/",
			minLength: 2
		});
	});
});




/**
 * -------- Extended Jquery Functions
 */


/**
 * A function that makes an element into a dynamically extensible formset
 */
$.fn.formset = function(args) {
	if (!args) {
		args = {};
	}
	$(this).each(function() {
		var prefix = $(this).attr('id').replace('-formset', '');
		
		// Make sure the total-forms attribute has the correct value after refreshing
		$(this).find('#id_' + prefix + '-TOTAL_FORMS').val($(this).find('.' + prefix + '-form').not('.empty').length)
		
		var button = $('<a href="#" id="' + prefix + '-addbtn"><img src="/static/img/icons/add.png"></a>')
		button.click(function(event) {
			add_form(prefix, args['newforms_callback']);
			return false;
		})
		$(this).find('.formset-button-container').append(button);
	})
};

/**
 * A function that detects if a user presses the enter key when in the applied element
 */
$.fn.pressEnter = function(fn) {

    return this.each(function() {  
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