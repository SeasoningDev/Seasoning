function upvote() {
	$.ajax({
		url: upvote_url,
	}).success(function(data) {
		$("#upvote-count").text(data);
		$("#upvote-button").hide();
		$("#downvote-button").show();
	});
}

function downvote() {
	$.ajax({
		url: downvote_url,
	}).success(function(data) {
		$("#upvote-count").text(data);
		$("#downvote-button").hide();
		$("#upvote-button").show();
	});
}



// Load the ingredient list
function load_ingredient_list() {
	// Show loader icon
    $("#ingredients-wrapper").addClass('loading');
	
	// Get required parameters for ajax request
	var portions = $('#portions-changer input').val();
    var updated_recipe_portions_url = recipe_portions_url.replace('/0000/', '/' + portions + '/');
    
    
    // Do ajax
    $.ajax(updated_recipe_portions_url,
           {'recipe': recipe_id,
            'portions': portions})
    .done(function(data) {
    	// Show instructions warning if the portions are not the default amount
        if (portions != orig_recipe_portions) {
            $('#instructions-warning').slideDown('1000');
        } else {
            $('#instructions-warning').slideUp('1000');
        }
        var parsed_data = $.parseJSON(data);
        
        // Update the ingredient list
        $("#ingredients-wrapper").removeClass('loading');
        
        $('#ingredients').fadeOut(400, function() {
        	$(this).html(parsed_data['ingredient_list'])
        	       .fadeIn(400, function() {
        
		        adjust_footprint_percentages();
		        fix_moreinfo_links();
		    });
        });
    }).fail(function() {
       alert('Er is iets misgegaan bij het contacteren van de server. Probeer het later opnieuw...')
    });
}




// Correctly display the contributed percentage of each ingredient to the total recipe footprint
function adjust_footprint_percentages() {
	var portions = parseInt($("#portions-changer input").val());
    var total_footprint = parseFloat($("#recipe-total-footprint").val().replace(',', '.'));
    $('.ingredient').each(function() {
        var footprint = parseFloat($(this).find('.footprint-number').text().replace(',', '.'));
        var percentage = (footprint/total_footprint)*100;
        $(this).find('.percentage-number').text(parseInt(percentage) + '%');
        $(this).find('.progress-bar').animate({
            width: percentage + "%"
        }, 1000);
    });
}



//Make sure the '+' icons behind ingredients do their job
function fix_moreinfo_links() {
    $('.ingredient-moreinfo-link, .endangered-icon').click(function() {
    	var $ing = $(this).parents('.ingredient');
    	
        var ing_id = $ing.find('.ingredient-id').text();
        var $moreinfo = $ing.find('.moreinfo');
        
        if ($moreinfo.is(':hidden')) {
            $(this).children('.more').hide();
            $(this).children('.less').show();
            
            if (!$moreinfo.hasClass('loaded')) {
            	$moreinfo.height('70px');
                $.ajax({
                    url: ingredients_avail_ajax_url,
                    type: "POST",
                    data : {ingredient: ing_id},
                    success: function(data) {
                        $moreinfo.html(data);
                        fix_ingredient_availabilities();
                        update_tooltips();
                        $moreinfo.find(".basic-moreinfo").each(function() {
                            var height = 0;
                            $(this).parent(".moreinfo").children().each(function() {
                                height = height + $(this).height();
                            })
                            $(this).parent(".moreinfo").animate({
                                height: height + 35,
                            });
                        });
                        $moreinfo.addClass('loaded');
                    }
                });
            }
        } else {
            $(this).children('.less').hide();
            $(this).children('.more').show();
        }
    });
}

/**
 * A function that detects if a user presses the enter key when in the applied element
 */
$.fn.pressEnter = function(fn) {

    return this.each(function() {
    	$(this).unbind('enterPress');
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


var ingredient_reload_timer;
var tab_1_loaded = false;

$(function() {
	
	$("#upload-image-form input#id_image").change(function() {
		$("#upload-image-form").submit();
	}).click(function(event) {
		event.stopPropagation();
	});

	$("#portions-spinner").spinner({
		min: 1,
		change: load_ingredient_list,
		stop: function() {
			$this = $(this);
			clearTimeout(ingredient_reload_timer);
			ingredient_reload_timer = setTimeout(function() {
				$this.blur();
			}, 1000);
		},
	}).pressEnter(function() {
		$this = $(this);
		clearTimeout(ingredient_reload_timer);
		ingredient_reload_timer = setTimeout(function() {
			$this.blur();
		}, 1000);
	});
    
	
	load_ingredient_list();
	
	$( "#chart-tabs" ).tabs({
		/* activate: function(event, ui) {
                    if (ui.newTab.index() == 1 && !tab_1_loaded) {
                        load_relchart();
                        tab_1_loaded = true;
                    }
                } */
	});
    
    $(".add-image-thumb").click(function() {
		$("#upload-image-form input#id_image").click();
		return false;
    })
    
    $(".remove-image-button").click(function(e) {
    	e.stopPropagation();
    	return confirm('Weet u zeker dat u deze afbeelding wil verwijderen?');
    })
    
    $(".popover-element").popover({
    	container: '#graphic-information'
    });
});