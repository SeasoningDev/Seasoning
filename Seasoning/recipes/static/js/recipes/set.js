// ----------------------------------------------------------------------------
// markItUp!
// ----------------------------------------------------------------------------
// Copyright (C) 2008 Jay Salvat
// http://markitup.jaysalvat.com/
// ----------------------------------------------------------------------------
mySettings = {
    nameSpace:          'markdown', // Useful to prevent multi-instances CSS conflict
    previewHandler:  function(text) {
    	markdown_preview = $('.markdown-preview');
    	$.ajax({
    		url: '/recipes/markdownpreview/',
    		type: "POST",
    		data: {data : text},
    		success: function(data) {
    			if (markdown_preview.length > 0) {
    	    		markdown_preview.remove();
    	    	}	
    			$(data).insertAfter($('div.markdown'));
    		} 
	    });
    },
    onShiftEnter:       {keepDefault:false, openWith:'\n\n'},
    markupSet: [
        {name:'Titel', key:"1", openWith:'#### ', placeHolder:'Typ hier een titel...' },
        {name:'Vetgedrukt', key:"B", openWith:'**', closeWith:'**', placeHolder:'Vetgedrukte tekst'},
        {name:'Schuingedrukt', key:"I", openWith:'_', closeWith:'_', placeHolder:'Schuingedrukte tekst'},
        {separator:'---------------' },
        {name:'Ongenummerde lijst', openWith:'- ' },
        {name:'Genummerde lijst', openWith: function(markItUp) {
        	var lines = markItUp.textarea.value.split('\n');
        	var cursor = markItUp.textarea.selectionStart;
        	var search_pos = 0;
        	var search_line = -1;
        	do {
        		search_line++;
        		search_pos = search_pos + lines[search_line].length + 1;
        	} while (search_pos <= cursor);
        	last_line = search_line - 1;
        	while ((last_line >= 0) && (lines[last_line] == "")) {
        		last_line--;
        	}
        	last_line_whitespace = lines[last_line].match(/^\ */);
        	this_line_whitespace = lines[search_line].match(/^\ */);
        	if ((last_line_whitespace >= this_line_whitespace) && (last_line >= 0) && (match = lines[last_line].match(/^\ *\d+\.\ /))) {
        		num = parseInt(match[0].match(/\d+/));
        		return match[0].replace(num, num + 1);
        	}
            return "1. ";
        }},
        {name:'Toon/verberg voorbeeld', call: 'preview', className:"preview"}
    ]
}