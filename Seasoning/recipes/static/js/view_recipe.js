//Image Slider starting function
jssor_slider1_starter = function (containerId) {
	var options = {
			$AutoPlay: false,                                   //[Optional] Whether to auto play, to enable slideshow, this option must be set to true, default value is false
			$SlideDuration: 500,                                //[Optional] Specifies default duration (swipe) for slide in milliseconds, default value is 500

			$ThumbnailNavigatorOptions: {                       //[Optional] Options to specify and enable thumbnail navigator or not
				$Class: $JssorThumbnailNavigator$,              //[Required] Class to create thumbnail navigator instance
				$ChanceToShow: 2,                               //[Required] 0 Never, 1 Mouse Over, 2 Always

				$ActionMode: 1,                                 //[Optional] 0 None, 1 act by click, 2 act by mouse hover, 3 both, default value is 1
				$SpacingX: 8,                                   //[Optional] Horizontal space between each thumbnail in pixel, default value is 0
				$DisplayPieces: 10,                             //[Optional] Number of pieces to display, default value is 1
				$ParkingPosition: 360                           //[Optional] The offset position to park thumbnail
			}
	};

	var jssor_slider1 = new $JssorSlider$(containerId, options);
};


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
    var total_footprint = parseFloat($("#recipe-total-footprint").val().replace(',', '.'))*portions;
    $('.ingredient').each(function() {
        var footprint = parseFloat($(this).find('.footprint-number').text().replace(',', '.'));
        var percentage = (footprint/total_footprint)*100;
        $(this).find('.percentage-number').text(parseInt(percentage) + '%');
        $(this).find('.footprint-fill').animate({
            width: percentage + "%"
        }, 1000);
    });
}



//Make sure the '+' icons behind ingredients do their job
function fix_moreinfo_links() {
    $('.ingredient-moreinfo-link, .endangered-icon').click(function() {
        var ing_id = $(this).parents('.ingredient').find('.ingredient-id').text();
        var $moreinfo = $(this).parents('.ingredient').find('.moreinfo');
        if ($moreinfo.is(':hidden')) {
            $moreinfo.slideDown(500);
            $(this).children('img').attr('src', '/static/img/icons/less.png');
            if (!$moreinfo.hasClass('loaded')) {
                $.ajax({
                    url: ingredients_avail_ajax_url,
                    type: "POST",
                    data : {ingredient: ing_id},
                    success: function(data) {
                        $moreinfo.html(data);
                        fix_ingredient_availabilities();
                        update_tooltips();
                        $(".basic-moreinfo").each(function() {
                            var height = 0;
                            $(this).parent(".moreinfo").children().each(function() {
                                height = height + $(this).height();
                            })
                            $(this).parent(".moreinfo").animate({
                                height: height + 30,
                            });
                        });
                        $moreinfo.addClass('loaded');
                    }
                });
            }
        } else {
            $moreinfo.slideUp(500);
            $(this).children('img').attr('src', '/static/img/icons/add.png');
        }
        return false;
    });
}




// Graph Loading Functions
function load_evochart() {
	$("#charts-ajax-loader").show();
	$.ajax({
		url: '/recipes/data/fpevo/',
		type: "POST",
		dataType: "json",
		data : {recipe : recipe_id},
		success: function(data) {
			evochart.addSeries({
				name: "Vandaag",
				data: [[12*(data.doy/365), 100], [12*(data.doy/365), -5]],
				color: "#000",
				tooltip: {
					headerFormat: "",
					pointFormat: "Vandaag (" + $.datepicker.formatDate('dd-mm-yy', new Date()) + ")"
				}
			});
			evochart.addSeries({
				name: "Voetafdruk",
				data: data.footprints
			});
			evochart.yAxis[0].setExtremes(0, Math.max.apply(Math, data.footprints)*1.1);
			$("#charts-ajax-loader").hide();
		},
		cache: false
	});
}

/**
        Unused for now
        function load_relchart() {
            $("#charts-ajax-loader").show();
            $.ajax({
                url: '/recipes/data/fprel/',
                type: "POST",
                dataType: "json",
                data : {recipe : recipe_id},
                success: function(data) {
                    relchart.addSeries({
                    	name: "De voetafdruk van dit recept",
                    	data: [[data.fp, 100], [data.fp, -5]],
                    	tooltip: {
                    		headerFormat: "",
                    		pointFormat: "De voetafdruk van dit recept (" + Math.round(data.fp*100)/100 + "kgCO²)"
                    	}
                    });
                    relchart.addSeries({
                      name: "Alle recepten",
                      data: data.all_fps,
                      pointInterval: data.interval_length,
                    });
                    relchart.addSeries({
                      name: "Enkel {{ recipe.get_course_display }}en",
                      data: data.cat_fps,
                      pointInterval: data.interval_length,
                    });
                    relchart.addSeries({
                      name: "Enkel {{ recipe.get_veganism_display }}e gerechten",
                      data: data.veg_fps,
                      pointInterval: data.interval_length,
                    });
                    relchart.xAxis[0].setExtremes(0, data.max_fp, true);
                    relchart.yAxis[0].setExtremes(0, data.all_fps[0]*1.1);
                    $("#charts-ajax-loader").hide();
                },
                cache: false
            });
        }
 */



var tab_1_loaded = false;
var ingredient_reload_timer;
$(function() {
	
	$("#upload-image-form input#id_image").change(function() {
		$("#upload-image-form").submit();
	}).click(function(event) {
		event.stopPropagation();
	});

	$("#portions-spinner").spinner({
		min: 1,
		change: function() {
			clearTimeout(ingredient_reload_timer);
			ingredient_reload_timer = setTimeout(load_ingredient_list, 1000);
		},
		spin: function() {
			clearTimeout(ingredient_reload_timer);
			ingredient_reload_timer = setTimeout(load_ingredient_list, 1000);
		},
	});

	$('#portions-spinner').change(function() {
		load_ingredient_list();
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
	
	evochart = new Highcharts.Chart({
		chart: {
			renderTo: 'recipe-fpevo-chart',
			type: 'spline',
		},
		plotOptions: {
			spline: {
				//pointPlacement: "on"
			}
		},
		title: {
			text: 'Verloop voetafdruk doorheen het jaar',
			style: {
				color: '#333'
			}
		},
		legend: {
			enabled: false
		},
		xAxis: {
			title: {
				text: 'Maand',
				style: {
					fontWeight: 'normal',
					color: '#333'
				}
			},
			min: 1,
			max: 12,
			categories: ['prejan', 'Jan', 'Feb', 'Maa', 'Apr', 'Mei', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dec', 'postdec']
		},
		yAxis: {
			title: {
				text: 'Voetafdruk (kgCO2)',
				style: {
					fontWeight: 'normal',
					color: '#333'
				}
			},
			min: 0
		},
		tooltip: {
			valueSuffix: ' kgCO2 per 4 porties'
		},
		colors: [
		         '#629B31'
		         ],
	});
	/**
        	Unused for now
            relchart = new Highcharts.Chart({
                chart: {
                    renderTo: 'recipe-fprel-chart',
                    type: 'line',
                },
                title: {
                    text: 'Voetafdruk relatief t.o.v. andere recepten',
                    style: {
                        color: '#333'
                    }
                },
                legend: {
                    layout: 'vertical',
                    align: 'right',
                    verticalAlign: 'top',
                    floating: true,
                    y: 30,
                    backgroundColor: "#FFF"
                },
                xAxis: {
                    title: {
                        text: 'Voetafdruk (kgCO2)',
                        style: {
                            fontWeight: 'normal',
                            color: '#333'
                        }
                    },
                    min: 0,
                    max: 1,
                },
                yAxis: {
                    title: {
                        text: 'Aantal recepten met deze voetafdruk',
                        style: {
                            fontWeight: 'normal',
                            color: '#333'
                        }
                    },
                    min: 0,
                    tickInterval: 10,
                },
                tooltip: {
                    headerFormat: "",
                    pointFormat: '<span style="color:{series.color}">{series.name}</span>'
                },
                colors: [
                    "#000", '#629B31', '#386312', '#C0E2A2'
                ]
            });
	 */
    load_evochart();
    
    $("#recipe-images .jssort01 .jssort01 > div:nth-child(2)").each(function () {
    	$(this).width($(this).width() + 50);
    	$(this).append(
    			'<div style="width: 42px; height: 42px; top: 0px; right: 0; position: absolute; overflow: hidden;">' +
    				'<div class="p" style="position: absolute; width: 42px; height: 42px; top: 0; left: 0;" u="prototype">' + 
    					'<div class="w">' + 
    						'<img class="add-image-thumb" src="' + static_url + 'img/decoration/add_image.png" u="thumb" ' + 
    						     'style="width: 100%; height: 100%; border: medium none; position: absolute; top: 0px; left: 0px;cursor:pointer" />' +
    			'</div></div></div>')
    	
    });
    
    $(".add-image-thumb").click(function() {
		$("#upload-image-form input#id_image").click();
		return false;
    })
});