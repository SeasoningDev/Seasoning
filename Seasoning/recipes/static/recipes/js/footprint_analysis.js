var parseDate = d3.time.format("%Y-%m-%d").parse;

var color_group_by_ingredient = d3.scale.category20c();
var color_group_by_source = d3.scale.category20b();

var stack = d3.layout.stack()
			         .values(function(d) { return d.footprints; });

var x, y;
var fb_svg, area;
var current_date, max_footprint;
var source_wrapper, ingredient_wrapper;

$(function() {
	// Calculate size of the graph
	var margin = {top: 20, right: 50, bottom: 30, left: 80},
	width = $("#footprint-breakdown").width() - margin.left - margin.right,
	height = 450 - margin.top - margin.bottom;
	
	
	
	// Data scale functions
	x = d3.time.scale()
			       .range([0, width]);

	y = d3.scale.linear()
			        .range([height, 0]);

	
	// Axes functions
	var xAxis = d3.svg.axis()
					  .scale(x)
					  .orient("bottom")
					  .tickFormat(d3.time.format("%b"));;

	var yAxis = d3.	svg.axis()
					   .scale(y)
					   .orient("left");
	
	

	// Add the svg graph to the page
	fb_svg = d3.select("#footprint-breakdown")
				.append("svg")
				   .attr("width", width + margin.left + margin.right)
				   .attr("height", height + margin.top + margin.bottom)
				.append("g")
					.attr("transform", "translate(" + margin.left + "," + margin.top + ")");

	area = d3.svg.area()
					.x(function(d) { return x(d.date); })
					.y0(function(d) { return y(d.y0); })
					.y1(function(d) { return y(d.y0 + d.y); })
					.interpolate('monotone');
	
	
	
	// Get the data
	d3.json(recipe_footprint_breakdown_data_url, function(data) {
		current_date = parseDate(data.current_date);
		var footprint_data = data.footprint_data;
		
		/**
		 * Footprint data format:
		 * 	[{date: "yyyy-mm-dd",
		 *    ing_1_name: {footprint_type_1: x,
		 *                 footprint_type_2: y,
		 *                 ...},
		 *    ing_2_name: {footprint_type_1: z,
		 *    			   ...},
		 *    ...
		 *    }, ...]
		 */
	
		// Get the names of every ingredient and sort them alphabetically
		var ingredient_names = d3.keys(footprint_data[0]).filter(function(key) { return key !== "date"; }).sort();
	
		color_group_by_ingredient.domain(ingredient_names);
		
		
		// Group the footprints by ingredient and put then in a new data structure
		/**
		 * Data format:
		 *  [{name: "ing_1_name",
		 *    footprints: [{date: "yyyy-mm-dd",
		 *    			y: x+y,
		 *    			y0: 0},
		 *    			...]
		 *    },
		 *    ...]
		 */
		var footprints_grouped_by_ingredient = stack(color_group_by_ingredient.domain().map(function(name) {
			return {
				name: name,
				footprints: footprint_data.map(function(d) {
					return {
						date: parseDate(d.date),
						y: d3.sum(d3.values(d[name]))
					};
				})
			};
		}));
	
		// Get the names of every source and sort them alphabetically
		var source_names = d3.keys(d3.values(footprint_data[0]).filter(function(d) {return typeof d == 'object';})[0]).sort();
		
		color_group_by_source.domain(source_names);
		
		
		// Group the footprints by source and put then in a new data structure
		/**
		 * Data format:
		 *  [{name: "source_1_name",
		 *    footprints: [{date: "yyyy-mm-dd",
		 *    			y: x+y,
		 *    			y0: 0},
		 *    			...]
		 *    },
		 *    ...]
		 */
		var footprints_grouped_by_source = stack(color_group_by_source.domain().map(function(name) {
			return {
				name: name,
				footprints: footprint_data.map(function(d) {
					return {
						date: parseDate(d.date),
						y: d3.sum(d3.values(d), function(e) { return e[name]; })
					};
				})
			};
		}));
		
		
		
		// Scale the axes so all data will be visible
		max_footprint = d3.max(footprints_grouped_by_ingredient[footprints_grouped_by_ingredient.length - 1].footprints, function(d) { return d.y0 + d.y })
		
		x.domain(d3.extent(footprint_data, function(d) { return parseDate(d.date); }));
		y.domain([0, 1.2 * max_footprint]);
		

		
		// Draw x-axis
		fb_svg.append("g")
				.attr("class", "x axis")
				.attr("transform", "translate(0," + height + ")")
				.call(xAxis);

		// Draw y-axis
		fb_svg.append("g")
				.attr("class", "y axis")
				.call(yAxis);

		//Create Y axis label
		fb_svg.append("text")
				.attr("transform", "rotate(-90)")
				.attr("y", 0-margin.left)
				.attr("x",0 - (height / 2))
				.attr("dy", "1em")
				.style("text-anchor", "middle")
				.text("Voetafdruk (kgCO2 per portie)");

		source_wrapper = render_footprint_breakdown_data(footprints_grouped_by_source, color_group_by_ingredient);
		
		ingredient_wrapper = render_footprint_breakdown_data(footprints_grouped_by_ingredient, color_group_by_source);
		
		switch_footprint_graphs();
	});
	
});

var source = true;
function switch_footprint_graphs() {
	if (source) {
		show_ingredient_data();
		source = false;
	} else {
		show_source_data();
		source = true;
	}
}
function show_source_data() {
	source_wrapper.transition().duration(1000).style('opacity', 1);
	ingredient_wrapper.transition().duration(1000).style('opacity', 0);
}
function show_ingredient_data() {
	source_wrapper.transition().duration(1000).style('opacity', 0);
	ingredient_wrapper.transition().duration(1000).style('opacity', 1);
}



function render_footprint_breakdown_data(footprint_data, colors) {
	
	var wrapper = fb_svg.append("g").style('opacity', 0);
	
	// Draw the footprint area for each ingredient
	var ingredient = wrapper.selectAll(".footprint_type")
							.data(footprint_data).enter()
								.append("g")
									.attr("class", "footprint_type");
	ingredient.append("path")
				.attr("class", "area")
				.attr("d", function(d) { return area(d.footprints); })
				.style("fill", function(d) { return colors(d.name); });
	
	
	
	// Draw labels for each ingredient
	var data_label_height = 25;
	ingredient.append("text")
				.datum(function(d) { return {name: d.name, value: d.footprints[d.footprints.length - 1]}; })
				.attr("transform", function(d) { return "translate(" + x(d.value.date) + "," + y(0) + ")"; })
				.attr("x", 10)
				.attr("dy", function() {
					data_label_height = data_label_height - 30;
					return data_label_height;
				})
				.text(function(d) { return d.name; })

	// Draw lines from the labels to their respective ingredient area
	var data_label_height = 20;
	wrapper.selectAll(".label-line")
			.data(footprint_data).enter()
				.append("line")
					.attr("class", "label-line")
					.datum(function(d) {
						return {
							name: d.name, 
							one_to_last_d: d.footprints[d.footprints.length - 2],
							last_d: d.footprints[d.footprints.length - 1]};
						})
					.attr("x1", function(d) { return x(d.one_to_last_d.date)})
					.attr("y1", function(d) {
						return y(d.one_to_last_d.y0 + (d.one_to_last_d.y / 2));
					})
					.attr("x2", function(d) { return x(d.last_d.date) + 5 })
					.attr("y2", function() {
						data_label_height = data_label_height - 30;
						return y(0) + data_label_height;
					})



	// Draw a line representing the current moment in the timeline
	wrapper.append("g")
			.attr("class", "current-date")
			.append("line")
			.attr("x1", x(current_date)).attr("x2", x(current_date))
			.attr("y1", y(0)).attr("y2", y(1.05 * max_footprint))
	
	wrapper.append("text")
			.attr("transform", "translate(" + x(current_date) + "," + y(1.1 * max_footprint) + ")")
			.attr("text-anchor", "middle")
			.text("Vandaag");
	
	return wrapper;
}






/**
* Relative Footprint Graph
*/
var width, height;
var y;
var rf_svg;
var all_recipes, course_recipes, veg_recipes, both_recipes;

$(function() {
	var margin = {top: 10, right: 30, bottom: 30, left: 30}
	width = $("#relative-footprint").width() - margin.left - margin.right,
	height = 400 - margin.top - margin.bottom;
	
	// Get the data
	d3.json(recipe_relative_footprint_data_url, function(data) {
		var footprint_data = data.all_recipes_footprints;
		
		// Make the svg element
		rf_svg = d3.select("#relative-footprint").append("svg")
		    .attr("width", width + margin.left + margin.right)
		    .attr("height", height + margin.top + margin.bottom)
		  .append("g")
		    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

		all_recipes = render_relative_footprint_data(data.this_recipes_footprint,
													 data.all_recipes_footprints,
													 data.all_recipes_distribution);
		course_recipes = render_relative_footprint_data(data.this_recipes_footprint,
													    data.same_course_recipes_footprints,
													    data.same_course_recipes_distribution);
		veg_recipes = render_relative_footprint_data(data.this_recipes_footprint,
													 data.same_veganism_recipes_footprints,
													 data.same_veganism_recipes_distribution);
		both_recipes = render_relative_footprint_data(data.this_recipes_footprint,
													  data.both_same_recipes_footprints,
													  data.both_same_recipes_distribution);
		
		show_all_recipes_data();
	
	});
	
});

function show_all_recipes_data() {
	all_recipes.transition().duration(1000).style('opacity', 1);
	course_recipes.transition().duration(1000).style('opacity', 0);
	veg_recipes.transition().duration(1000).style('opacity', 0);
	both_recipes.transition().duration(1000).style('opacity', 0);
}
function show_course_recipes_data() {
	all_recipes.transition().duration(1000).style('opacity', 0);
	course_recipes.transition().duration(1000).style('opacity', 1);
	veg_recipes.transition().duration(1000).style('opacity', 0);
	both_recipes.transition().duration(1000).style('opacity', 0);
}
function show_veg_recipes_data() {
	all_recipes.transition().duration(1000).style('opacity', 0);
	course_recipes.transition().duration(1000).style('opacity', 0);
	veg_recipes.transition().duration(1000).style('opacity', 1);
	both_recipes.transition().duration(1000).style('opacity', 0);
}
function show_both_recipes_data() {
	all_recipes.transition().duration(1000).style('opacity', 0);
	course_recipes.transition().duration(1000).style('opacity', 0);
	veg_recipes.transition().duration(1000).style('opacity', 0);
	both_recipes.transition().duration(1000).style('opacity', 1);
}
	


function render_relative_footprint_data(this_recipes_footprint, footprint_data, distribution_data) {
	
	// Get the normal distribution parameters
	var mean = distribution_data.filter(function(d) { return d.parameter == 0})[0].parameter_value;
	var std = distribution_data.filter(function(d) { return d.parameter == 0})[0].parameter_value;
	
	
	
	// Create a wrapper to contain this subgraph
	var wrapper = rf_svg.append("g").style('opacity', 0);
	

	
	// Create an x-axis scale
	var x = d3.scale.linear()
	    .domain([0, d3.max(footprint_data)])
	    .range([0, width]);
	
	// Create an x-axis
	var xAxis = d3.svg.axis()
	    .scale(x)
	    .orient("bottom");
	
	// Draw the x-axis
	wrapper.append("g")
	    .attr("class", "x axis")
	    .attr("transform", "translate(0," + height + ")")
	    .call(xAxis);
	
	
	
	// Generate a histogram using uniformly-spaced bins.
	var histogram_data = d3.layout.histogram()
	    							.bins(x.ticks(d3.max([10, Math.floor(footprint_data.length / 10)])))
	    							(footprint_data);
	
	
	
	// Create a y axis scale
	var max_y = d3.max(histogram_data, function(d) { return d.y; });
	y = d3.scale.linear()
	    .domain([0, 1.2 * max_y])
	    .range([height, 0]);
	
	
	
	
	
	var bar = wrapper.selectAll(".bar")
					    .data(histogram_data)
					  .enter().append("g")
					    .attr("class", "bar")
					    .attr("transform", function(d) { return "translate(" + x(d.x) + "," + y(d.y) + ")"; });

	bar.append("rect")
	    .attr("x", 1)
	    .attr("width", x(histogram_data[0].dx) - 1)
	    .attr("height", function(d) { return height - y(d.y); });
	
	var distribution_y = d3.scale.linear()
    .domain([0, 1.2 * (1 / (std * Math.sqrt(2 * Math.PI)))])
    .range([height, 0]);
	
	var line = d3.svg.line()
    	.x(function(d) { return x(d.x); })
    	.y(function(d) { return distribution_y((1/(std * Math.sqrt(2 * Math.PI))) * Math.exp(-Math.pow(d.x - mean, 2)/(2 * Math.pow(std, 2)))); })
    	.interpolate("basis");
	
	wrapper.append("path")
		.datum(x.ticks(Math.floor(footprint_data.length / 5)).map(function(d) { return {x: d}}))
		.attr("d", line)
		.attr("class", "distribution-line");


	// Draw a line representing the current moment in the timeline
	wrapper.append("g")
			.attr("class", "current-date")
			.append("line")
			.attr("x1", x(this_recipes_footprint)).attr("x2", x(this_recipes_footprint))
			.attr("y1", y(0)).attr("y2", y(1.05 * max_y))
	
	wrapper.append("text")
			.attr("transform", "translate(" + x(this_recipes_footprint) + "," + y(1.1 * max_y) + ")")
			.attr("text-anchor", "middle")
			.text("De voetafdruk van dit recept");
	
	
	return wrapper;
	
}
