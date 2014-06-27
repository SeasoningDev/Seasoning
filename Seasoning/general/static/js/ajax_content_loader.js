(function( $ ){
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
	   }, options );
	   
	   // If we are already loading new data, don't try to load more data yet
	   var loading = false;
	   
	   var wrapper = this;
	   
	   function add_data(data) {
		   wrapper.append(data);
	   }
	   
	   settings.page_field_to_update.val(0);
	   $(window).unbind('scroll');
	   
	   function load_data() {
		   // We are now loading new data
		   loading = true;
		   
		   // Get the next page
		   if (settings.page_field_to_update) {
			   settings.page_field_to_update.val(parseInt(settings.page_field_to_update.val()) + 1);
		   }

		   settings.loader_element.show();
		   
		   $.ajax({
			   url: settings.ajax_url,
			   type : "POST",
			   data: settings.form.serialize(),
			   success: add_data,
		   }).done(function() {
			   loading = false;
		   }).error(function() {
			   if (settings.no_more_data_element_to_show) {
				   settings.no_more_data_element_to_show.show();
			   }
		   }).always(function() {
			   settings.loader_element.hide();
		   });
	   }
	   
	   if (!settings.ajax_url || !settings.form || !settings.loader_element) {
		   alert('No valid ajax url was given, ajax load will not work');
	   } else {
		   $(window).bind('scroll', function() {
			   if (!loading && ($(document).height() - $(window).height()) - $(window).scrollTop() <= 100) {
				   load_data();
			   }
			   return;
		   });
	   }
	   
	   $(window).on("ajax-load-data", load_data);
	   
	   load_data();
	   
	   return this;
	   
   }; 
})( jQuery );