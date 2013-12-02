/*
 * Edit Ingredient functions
 */
function check_ing_type() {
	sel = $('#id_type');
	
	if (sel.val() == 1) {
		$('.field-preservability').show();
		$('.field-preservation_footprint').show();
		$('#available_in_country-group').show();
	} else {
		$('.field-preservability').hide();
		$('.field-preservation_footprint').hide();
		$('#available_in_country-group').hide();
	}
	
	if (sel.val() == 2) {
		$('#available_in_sea-group').show();
	} else {
		$('#available_in_sea-group').hide();
	}
}

/**
 * Function executed when the page is ready (but maybe not fully loaded)
 */
$(document).ready(function() {
	/*
	 * Only applicable to Ingredient admin page
	 */
	ing_reg = /\/admin\/ingredients\/ingredient\/\d*\//
	if (ing_reg.test(window.location.href)) {
		$('#body').css('width', '1200px');
	}
	$('<div id="synonym-row" class="form-row"></div>').insertAfter('div.field-plural_name');
	$('#synonym-group').appendTo($('#synonym-row'));
	
	check_ing_type();	
	$('#id_type').change(function() {
		check_ing_type()
	});
	
	/*
	 * Only applicable to Static Pages admin page
	 */
	static_reg = /\/admin\/general\/staticpage\/\d*\//
	if (static_reg.test(window.location.href)) {
		$('<br class="clear" /><div id="preview-title">Preview:</div><div id="static-page-preview"></div>').insertAfter('#content-main');
		$('#static-page-preview').html($('#id_body_html').val());
		$('#id_body_html').change(function() {
			$('#static-page-preview').html($('#id_body_html').val());
		});
	}
		
	
});