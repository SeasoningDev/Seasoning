(function( $ ){
	var last_ajax_request;
	
   $.fn.ajax_load = function(options) {
	   
	   // This is the easiest way to have default options.
	   var settings = $.extend({
		   // These are the defaults.
		   ajax_url: null,
		   form: null,
		   objects_name: "data",
		   page_field_to_update: null,
		   loader_element: null,
		   no_more_data_element_to_show: null,
		   no_results_element_to_show: null,
		   continue_ask_after_reloads: false,
		   continue_ask_element_to_show: null
	   }, options );
	   
	   var reloads_until_continue_ask = null;
	   if (settings.continue_ask_after_reloads) {
		   reloads_until_continue_ask = settings.continue_ask_after_reloads;
		   if (settings.continue_ask_element_to_show) {
			   settings.continue_ask_element_to_show.click(function() {
				   $(window).trigger('loadmore.acl');
				   return false;
			   })
		   }
	   }
	   
	   // If we are already loading new data, don't try to load more data yet
	   var loading = false;
	   
	   var wrapper = this;
	   
	   function add_data(data) {
		   wrapper.append(data);
	   }
	   
	   settings.page_field_to_update.val(0);
	   
	   function load_data(clear) {
		   if (settings.no_results_element_to_show) {
			   settings.no_results_element_to_show.hide();
		   }
		   if (settings.no_more_data_element_to_show) {
			   settings.no_more_data_element_to_show.hide();
		   }
		   if (settings.continue_ask_element_to_show) {
			   settings.continue_ask_element_to_show.hide();
		   }
		   
		   if (settings.continue_ask_after_reloads) {
			   if (reloads_until_continue_ask <= 0) {
				   if (settings.continue_ask_element_to_show) {
					   settings.continue_ask_element_to_show.show()
				   }
				   return
			   }
		   }
		   
		   // We are now loading new data
		   loading = true;
		   
		   // Get the next page
		   if (settings.page_field_to_update) {
			   settings.page_field_to_update.val(parseInt(settings.page_field_to_update.val()) + 1);
		   }
		   
		   if (last_ajax_request)
			   last_ajax_request.abort();
		   
		   if (clear) {
			   wrapper.html("");
		   }

		   settings.loader_element.show();
		   
		   last_ajax_request = $.ajax({
			   url: settings.ajax_url,
			   type : "POST",
			   data: settings.form.serialize(),
		   }).success(function(data) {
			   add_data(data);
			   reloads_until_continue_ask--;
		   }).done(function() {
			   loading = false;
		   }).error(function(jqXHR, status, error) {
			   if (status != "abort") {
	               if (settings.page_field_to_update.val() <= 1) {
					   if (settings.no_results_element_to_show) {
						   settings.no_results_element_to_show.show();
					   }
				   } else {
					   if (settings.no_more_data_element_to_show) {
						   settings.no_more_data_element_to_show.show();
					   }
				   }
			   }
		   }).always(function() {
			   settings.loader_element.hide();
		   });
	   }
	   
	   function clear_and_load_data() {
		   if (settings.continue_ask_after_reloads) {
			   reloads_until_continue_ask = settings.continue_ask_after_reloads;
		   }
		   
		   // Get the next page
		   if (settings.page_field_to_update) {
			   settings.page_field_to_update.val(0);
		   }
		   load_data(true);
	   }
	   
	   function load_more_data() {
		   if (settings.continue_ask_after_reloads) {
			   reloads_until_continue_ask = settings.continue_ask_after_reloads;
		   }
		   if (settings.continue_ask_element_to_show) {
			   settings.continue_ask_element_to_show.hide()
		   } 
		   load_data();
	   }
	   
	   if (!settings.ajax_url || !settings.form || !settings.loader_element) {
		   alert('No valid ajax url was given, ajax load will not work');
	   } else {
		   $(window).scroll(function() {
			   if (!loading && ($(document).height() - $(window).height()) - $(window).scrollTop() <= 100) {
				   load_data();
			   }
			   return true;
		   });
	   }

	   $(window).on("ajax-load-data", load_data);
	   $(window).on("ajax-clear-and-load-data", clear_and_load_data);
	   $(window).on("loadmore.acl", load_more_data);
	   
	   load_data();
	   
	   return this;
	   
   }; 
})( jQuery );
