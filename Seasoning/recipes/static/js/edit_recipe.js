function set_default_text(i, el) {
	if ($.trim($(el).text()) == '') {
		$(el).text($(el).attr('default'));
	}
}

$(function () {
	$(".spinner-changer input").spinner({
		min: 1,
	});
	
	$(".editable-field").click(function() {
		if ($(".editing").length) {
			alert("Je bent al een veld aan t wijzigen.");
			return false;
		}
		
		var field = $(this);
		if (field.hasClass("editing")) {
			// We are currently editing this field, do nothing
			return false;
		}
		field.addClass("editing");
		
		var next_el = field.next();
		
		var input_el;
		var is_input = false;
		var is_select = false;
		var is_tarea = false;
		if (next_el.is("input")) {
			input_el = next_el;
			is_input = true;
		} else if (next_el.hasClass('ui-spinner')) {
			input_el = next_el.find("input");
			is_input = true;
		} else if (next_el.is('select')) {
			input_el = next_el;
			is_select = true;
		} else if (next_el.is('textarea')) {
			input_el = next_el;
			is_tarea = true;
		}
		
		if (input_el.length) {
			var prev_val = input_el.val();
			
			if (is_input)
				input_el.val(field.text());
			
			next_el.height(field.height());
					
			var buttons = $(".edit-recipe-buttons").clone();
			next_el.after(buttons);
			buttons.find('.accept-button').click(function() {
				buttons.hide();
				var overlay = $('<div style="position:absolute;background-color: rgba(0, 0, 0, .5);z-index:901;text-align:center;"><img src="/static/img/decoration/ajax-loader.png" style="padding-top: 5px;max-height:100%;"/></div>')
				overlay.width(next_el.outerWidth());
				overlay.height(next_el.outerHeight());
				overlay.css('top', next_el.offset().top);
				overlay.css('left', next_el.offset().left);
				$("body").append(overlay);
				$.ajax({
					type: "POST",
					url: $("#edit-recipe-form").attr('action'),
					data: $("#edit-recipe-form").serialize(),
				}).success(function(data) {
					overlay.remove();
					if (is_input)
						field.text(input_el.val());
					else if (is_select)
						field.text(input_el.children('option').filter(':selected').text());
					else if (is_tarea)
						if (data.length)
							field.html(data);
					next_el.hide()
					buttons.remove();
					field.removeClass("editing");
					set_default_text(0, field);
					field.show();
				}).error(function(jqXHR) {
					overlay.remove();
					if (jqXHR.status == 500) {
						alert(jqXHR.responseText);
					} else {
						alert('Er is een probleem opgetreden bij het contacteren van de server, probeer het later nogmaals.')
					}
					buttons.show();
				});
				return false;
			});
			buttons.find('.reject-button').click(function() {
				next_el.hide()
				buttons.remove();
				input_el.val(prev_val);
				field.removeClass("editing");
				set_default_text(0, field);
				field.show();
				
				return false;
			});
			
			field.hide();
			next_el.show();
			input_el.select();
			
			buttons.show();
		}
	}).each(set_default_text);
});