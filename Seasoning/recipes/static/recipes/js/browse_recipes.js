function load_more_recipes() {
	$(".ajax-loader").show();
	$("#end-buttons").hide();
	
	var next_recipes_page = parseInt($("#next-recipes-page").val());
	
	$.getJSON(
		get_recipes_url,
		{'page': next_recipes_page},
		function(data) {
			$("#browse-recipes-wrapper").append($(data.result));
			$(".ajax-loader").hide();
			$("#end-buttons").show();
			
			$("#next-recipes-page").val(next_recipes_page + 1);
			
			if (!data.more_pages)
				$("#show-more-recipes-btn a").addClass("disabled");
		}
	)	
}

$(function() {
	load_more_recipes();
	
	$("#show-more-recipes-btn").click(function() {
		if (!$(this).find('a').hasClass('disabled'))
			load_more_recipes();
		
		return false;
	});
})