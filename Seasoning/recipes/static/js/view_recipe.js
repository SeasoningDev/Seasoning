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
 
// Function to check file size before uploading.
function before_imageform_submit() {
	//check whether browser fully supports all File API
    if (window.File && window.FileReader && window.FileList && window.Blob) {
    	if( !$('#id_image').val()) {
    		alert("Geen afbeelding opgegeven.");
    		return false
    	}
        
    	var fsize = $('#id_image')[0].files[0].size; //get file size
    	var ftype = $('#id_image')[0].files[0].type; // get file type
        

    	//allow only valid image file types
    	switch(ftype) {
    	case 'image/png': case 'image/gif': case 'image/jpeg': case 'image/pjpeg':
    		break;
    	default:
    		alert(ftype + ": Dit bestandstype wordt niet ondersteund. Gelieve een afbeelding van een van volgende formaten te uploaden: png, gif, jpg, jpeg");
    	return false
    	}
        
    	// Allowed file size is less than 1 MB (1048576)
    	if(fsize>1048576) {
    		alert(fsize +"MB: Het opgegeven bestand is te groot. De maximale bestandsgrootte is 1MB");
    		return false
    	}
                
    	$("#image-upload-progress").fadeIn(500);
    } else {
    	//Output error to older browsers that do not support HTML5 File API
    	alert("Gelieve uw browser naar een nieuwere versie te updaten indien u afbeeldingen wil uploaden.");
    	return false;
    }
}

function image_upload_progress(event, position, total, percentComplete) {
	//Progress bar
    $("#image-upload-progress .progress-bar").width(percentComplete + '%'); //update progressbar percent complete
    $("#image-upload-progress-text").text(percentComplete + '%'); //update status text
}



im_x = 0;
im_y = 0;
im_w = 0;
im_h = 0;
img_id = null;

function image_upload_success(resp) {
	
	setTimeout(function() {
		$("#image-upload-progress").fadeOut(500);

		$("#image-upload-crop-modal #uploaded-image-preview").attr('src', resp.url);
		$("#image-upload-crop-modal").modal({
			backdrop: 'static',
		});
		
		img_id = resp.image_id;
		
		var img = $("#image-upload-crop-modal img");
		
		img.Jcrop({
			aspectRatio: 1170/400,
			setSelect: [0, 0, 1170, 400],
			onChange: function (c) {
				im_x = c.x / img.width();
				im_y = c.y / img.height();
				im_w = c.w / img.width();
				im_h = c.h / img.height();
			}
		});
		
		
	}, 1000);
}

function close_uploaded_image_crop(event) {
	var c = confirm('Wil je dit venster echt sluiten? Je afbeelding zal in dit geval niet aan het recept toegevoegd worden.');
	if (c) {
		return $("#image-upload-crop-modal").modal('hide');
	} else {
		return false;
	}
}

function finish_uploaded_image_crop() {
	var c = confirm('Ben je zeker dat je deze afbeelding wil opslaan? Je kan hierna geen wijzigingen meer aanbrengen.');
	if (c) {
	    var the_url = finish_recipe_image_url.replace('/0000/', '/' + img_id + '/');
	    $.ajax({
	    	url: the_url,
            type: "POST",
            data : {x: im_x,
            		y: im_y,
            		w: im_w,
            		h: im_h},
            success: function() {
        		$("#image-upload-crop-modal").modal('hide');
        		location.reload();
            },
            error: function() {
            	alert('Er is een fout opgetreden bij het contacteren van de server, probeer later opnieuw. Indien deze fout zich blijft voordien mag u steeds contact opnemen met de beheerders.');
            }
        });
	} else {
		return false;
	}
}


var ingredient_reload_timer;
var tab_1_loaded = false;

$(function() {
	var image_upload_options = {
		dataType: 'json',
		beforeSubmit: before_imageform_submit,  // pre-submit callback
		uploadProgress: image_upload_progress,
		success: image_upload_success,
		resetForm: true        // reset the form after successful submit
	};
	
	$("#upload-image-form input#id_image").change(function() {
		//Ajax Submit form           
		$("#upload-image-form").ajaxSubmit(
			image_upload_options
		)
		// return false to prevent standard browser submit and page navigation
	    return false;
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