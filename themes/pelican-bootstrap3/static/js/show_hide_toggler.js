$(document).ready(function () {

	$("button.toggle-start-hidden").parent().next().hide();

	$("button.toggle-start-hidden").click(function(){
                $(this).parent().next().toggle();
	    });
	
	$("button.toggle").click(function(){
                $(this).parent().next().toggle();
	    });

    });
