function set_default_text(i, el) {
	if ($.trim($(el).text()) == '') {
		$(el).text($(el).attr('default'));
	}
}

$(function () {
	$("#portions-changer input").spinner({
		min: 1,
	});
	
	$(".editable-field").click(function() {
		if ($(".editing").length) {
			alert("Je bent al een veld aan het wijzigen.");
			return false;
		}
		
		var field = $(this);
		if (field.hasClass("editing")) {
			// We are currently editing this field, do nothing
			return false;
		}
		field.addClass("editing");
		
		var next_el = field.next();
		
		var input;
		if (next_el.is("input")) {
			input = next_el;
		} else {
			input = next_el.find("input");
		}
		
		if (input.length) {
			input.val(field.text());
		
			var buttons = $(".edit-recipe-buttons").clone();
			next_el.after(buttons);
			buttons.find('.accept-button').click(function() {
				$.ajax({
					type: "POST",
					url: $("#edit-recipe-form").attr('action'),
					data: $("#edit-recipe-form").serialize(),
				}).success(function() {
					field.text(input.val());
					next_el.hide()
					buttons.remove();
					field.removeClass("editing");
					set_default_text(0, field);
					field.show();
				}).error(function(jqXHR) {
					if (jqXHR.status == 500) {
						alert(jqXHR.responseText);
					} else {
						alert('Er is een probleem opgetreden bij het contacteren van de server, probeer het later nogmaals.')
					}
				});
				return false;
			});
			buttons.find('.reject-button').click(function() {
				next_el.hide()
				buttons.remove();
				input.val(field.text());
				field.removeClass("editing");
				set_default_text(0, field);
				field.show();
				
				return false;
			});
			
			field.hide();
			next_el.show();
			input.select();
			
			buttons.show();
		} else {
			// textarea
			var tarea;
			if (next_el.is("textarea")) {
				tarea = next_el;
			} else {
				tarea = next_el.find("textarea");
			}
			
		
			var buttons = $(".edit-recipe-buttons").clone();
			next_el.after(buttons);
			buttons.find('.accept-button').click(function() {
				$.ajax({
					type: "POST",
					url: $("#edit-recipe-form").attr('action'),
					data: $("#edit-recipe-form").serialize(),
				}).success(function(data) {
					field.html(data);
					next_el.hide()
					buttons.remove();
					field.removeClass("editing");
					set_default_text(0, field);
					field.show();
				}).error(function(jqXHR) {
					if (jqXHR.status == 500) {
						alert(jqXHR.responseText);
					} else {
						alert('Er is een probleem opgetreden bij het contacteren van de server, probeer het later nogmaals.')
					}
				});
				return false;
			});
			buttons.find('.reject-button').click(function() {
				next_el.hide()
				buttons.remove();
				field.removeClass("editing");
				set_default_text(0, field);
				field.show();
				
				return false;
			});

			next_el.css('height', field.height());
			next_el.show();
			field.hide();
			tarea.select();
			
			buttons.show();
		}
	}).each(set_default_text);
});