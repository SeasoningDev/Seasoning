/**
* This function makes an ajax-post request to get an updated list of
* recipes conforming to the users' search parameters
* 
* @param page
*  If present, the given page of results is shown
*  If not, the first page of results is shown
*/
function update_page(page) {
   var url;
   if (page) {
       url = window.location + "?page=" + page;
   } else {
       url = window.location;
   }
   
   if ($("form").length == 0) {
       // No Form present
       $.ajax({
           type : "GET",
           url : url,
           success : function(data) {
               // The url returns full html
               $(".summaries-wrapper").html(data);
           }
       });
   } else {
       $.ajax({
           type : "POST",
           url : url,
           data : $("form").serialize(),
           success : function(data) {
               // The url returns full html
               $(".summaries-wrapper").html(data);
           }
       });
   }
   if ($(document).scrollTop() > $(".summaries-wrapper").offset().top - 80)
	   $('html,body').animate({scrollTop: $(".summaries-wrapper").offset().top - 80},'slow');
   return false;
};