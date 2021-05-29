// adds ios class to html wrap
jQuery(document).ready(function($){
var deviceAgent = navigator.userAgent.toLowerCase();
var agentID = deviceAgent.match(/(iphone|ipod|ipad)/);
    if (agentID) {

	$('html').addClass('ios');

    }
});
