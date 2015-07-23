$(function() {
	
	var demo_window_template = $('<div class="alert alert-info alert-demo"></div>');
	var button_template = $('<a href="#" class="btn btn-primary btn-demo"></a>');
	
	function demo_window(free) {
		var w = demo_window_template.clone();
		
		if (!free)
			$("body").append(w);
		
		return w;
	}
	function demo_button() {
		return button_template.clone();
	}
	

	
	// Open advanced search if the user prefers the advanced box open
	if (localStorage.skip_demo === 'true') {
		return
	}
	
	
	var intro_window = demo_window();
	intro_window.css('bottom', '30px').css('right', '30px');
	intro_window.html('<p>Hallo en welkom op Seasoning!</p><p>Ik zie dat dit de eerste keer is dat je ons bezoekt, en dan kan het allemaal nogal een beetje verwarrend zijn. Had je graag een beetje uitleg bij de werking van onze website?</p>');
	intro_demo_yes = demo_button().text('Ja, graag')
	intro_window.append(intro_demo_yes);
	intro_demo_no = demo_button().text('Nee, bedankt')
	intro_window.append(intro_demo_no);
	
	intro_demo_yes.click(function() {
		
		intro_window.fadeOut(500, function() {
			$(this).remove();
			
			start_demo_intro();
		});
		
		return false;
	})
	
	
	intro_demo_no.click(function() {
		// Save the users preference
		localStorage.skip_demo = true;
		
		intro_window.fadeOut(500, function() {
			$(this).remove();
		});
		
		return false;
	});
	
	intro_window.fadeIn(500);
	
	
	// Actual Demo starts
	
	
	// 1. Wat doet seasoning
	function start_demo_intro() {
		var demo_w_1 = demo_window();
		demo_w_1.html('<p><b>Ok, laten we beginnen!</b></p><p>Seasoning probeert het voor jou makkelijk te maken elke dag een duurzame keuze te maken voor je eten.</p>');
		
		var next_btn = demo_button().text('Verder');
		demo_w_1.append(next_btn);
		
		demo_w_1.css('top', 'calc(50% - ' + demo_w_1.height()/2 + 'px').css('left', 'calc(50% - 300px)');
		
		demo_w_1.fadeIn(500);
		next_btn.click(function() {
			demo_w_1.fadeOut(500, function() {
				$(this).remove();
				
				start_basic_functions();
			});
			
			return false;
		})
		
		// Show small button to restart demo at any time
	
	}
	
	// 2. Basis functionaliteit uitleggen (voetafdruk categorie, sorteren, naar een recept gaan
	function start_basic_functions() {
		var bf_w_1 = demo_window()
		bf_w_1.append($("<p>Seasoning berekent voor elk recept een voetafdruk op basis van de ingrediënt die nodig zijn tijdens de bereiding. Deze voetafdruk past zich automatisch aan doorheen het jaar naargelang bepaalde ingrediënten in seizoen zijn of net van heel ver moeten komen.</p>"));
		bf_w_1.append($("<p>Omdat het meestal nog altijd niet erg duidelijk is of een recept met een voetafdruk van 0.6kgCO2/portie nu een duurzame keuze is of niet, delen we vervolgens de recepten op in 5 categoriëen:"));
		var recipes = $("<ul></ul>");
		recipes.append($("<li><b>A+</b>: Een zeer duurzaam recept, <b>beter</b> dan 90% van de recepten op Seasoning</li>"));
		recipes.append($("<li><b>A</b>: Een duurzaam recept, <b>beter</b> dan 75% van de recepten op Seasoning</li>"));
		recipes.append($("<li><b>B</b>: Een gemiddeld recept, <b>beter</b> dan 50% van de recepten op Seasoning</li>"));
		recipes.append($("<li><b>C</b>: Een belastend recept, <b>slechter</b> dan 50% van de recepten op Seasoning</li>"));
		recipes.append($("<li><b>D</b>: Een zeer belastend recept, <b>slechter</b> dan 75% van de recepten op Seasoning</li>"));
		
		bf_w_1.append(recipes);
		
		bf_w_1.append($("<p>Kiezen voor een recept van categorie <b>A+</b> in plaats van eentje van <b>D</b> is ongeveer hetzelfde voor het milieu als 300km minder rijden met je wagen<sup>*</sup>"))
		
		var next_btn_1 = demo_button().text('Verder');
		bf_w_1.append(next_btn_1);
		
		bf_w_1.css('top', 'calc(50% - ' + bf_w_1.height()/2 + 'px').css('left', 'calc(50% - 300px)');
		bf_w_1.fadeIn(200);
		
		next_btn_1.click(function() {
			var bf_w_2 = demo_window(true);
			bf_w_2.addClass('arrow left');
			bf_w_2.html("<p>De duurzaamheids categorie van een recept staat hier. Zo kan je in een oogopslag zien welke</p>");
			
			var next_btn_2 = demo_button().text('Ok');
			bf_w_2.append(next_btn_2);
			
			$(".recipe-preview-wrapper .recipe-preview").first().append(bf_w_2);
			bf_w_2.css('bottom', 125 - bf_w_2.outerHeight()/2 + 'px').css('left', 'calc(100% + 5px)').css('width', '400px');
			
			bf_w_1.fadeOut(500, function() {
				$(this).remove();
				
				bf_w_2.fadeIn(200);
				next_btn_2.click(function() {
					var bf_w_3 = demo_window();
					bf_w_3.html("<p>Deze knop laat je toe de recepten te sorteren.</p>");
					bf_w_3.addClass('arrow left');
					
					var next_btn_3 = demo_button().text('Verder')
					bf_w_3.append(next_btn_3);
					
					$("#sort-by-wrapper").append(bf_w_3);
					bf_w_3.css('top', 'calc(50% - ' + bf_w_3.outerHeight()/2 + 'px)').css('left', 'calc(100% + 5px)').css('width', '400px');
					
					bf_w_2.fadeOut(500, function() {
						$(this).remove();
						
						bf_w_3.fadeIn(200)
						next_btn_3.click(function() {
							var bf_w_4 = demo_window(true);
							bf_w_4.html("<p>Hier kan je dingen intypen om naar recepten met een bepaalde naam te zoeken</p>");
							bf_w_4.addClass('arrow left');
							
							var next_btn_4 = demo_button().text('Verder');
							bf_w_4.append(next_btn_4);
							
							$("#base-recipe-search").append(bf_w_4);
							bf_w_4.css('top', 'calc(50% - ' + (10 + bf_w_4.outerHeight()/2) + 'px)').css('left', 'calc(100% + 10px)').css('width', '400px');
							
							bf_w_3.fadeOut(500, function() {
								$(this).remove();
								
								bf_w_4.fadeIn(500);
								next_btn_4.click(function() {
									var bf_w_5 = demo_window(true);
									bf_w_5.html("<p>En hier moet je klikken als je een recept wil zien</p>");
									bf_w_5.addClass('arrow left');
									
									var next_btn_5 = demo_button().text('Verder');
									bf_w_5.append(next_btn_5);
									
									$(".recipe-preview-wrapper .recipe-preview").first().append(bf_w_5);
									bf_w_5.css('bottom', 'calc(50% - ' + bf_w_5.outerHeight()/2 + 'px)').css('left', 'calc(100% + 10px)').css('width', '400px');
									
									bf_w_4.fadeOut(500, function() {
										$(this).remove();
										
										bf_w_5.fadeIn(500);
										next_btn_5.click(function() {
											var bf_w_6 = demo_window();
											bf_w_6.html("<p>Had je graag nog meer uitleg gehad?</p>")
											
											var btn_again = demo_button().text('Ik had dit graag nog eens gezien');
											btn_again.addClass('btn-block');
											bf_w_6.append(btn_again);
											
											var btn_more_1 = demo_button().text('Ik wil uitleg krijgen over het geavanceerd zoeken');
											btn_more_1.addClass('btn-block disabled');
											bf_w_6.append(btn_more_1);
											
											var btn_more_2 = demo_button().text('Ik wil graag meer weten over de voetafdruk en ecologische impact van recepten');
											btn_more_2.addClass('btn-block disabled');
											bf_w_6.append(btn_more_2);
											
											var btn_enough = demo_button().text('Ik weet genoeg');
											btn_enough.addClass('btn-block');
											bf_w_6.append(btn_enough);
											
											bf_w_6.css('top', 'calc(50% - ' + bf_w_6.height()/2 + 'px').css('left', 'calc(50% - 300px)');
											
											bf_w_5.fadeOut(200, function() {
												$(this).remove();
												
												bf_w_6.fadeIn(200);
												
												btn_again.click(function() {
													bf_w_6.fadeOut(200, function() {
														$(this).remove();
														
														start_demo_intro();
													});
													
													return false;
												});
												
												btn_enough.click(function() {
													bf_w_6.fadeOut(200, function() {
														$(this).remove();
													})
												})
												
											});
											
											return false;
										});
									});
									
									return false;
								});
							});
							
							return false;
						});
					});
					
					return false;
				});
			});
			
			return false;
		});
	}
	
	// 3. Gevorderd zoeken
	
	// 4. Stats for nerds
	
	
});
