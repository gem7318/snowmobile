// resize header based on orientation changes
$(window).resize(function() {
   $("div[class=md-container]").width($(window).width());
   $("header[data-md-component=header]").width($(window).width());
   $("footer[class=md-footer]").width($(window).width());
});
