$(document).ready(function() {
  $('.db_explorer .starter-template .nav-tabs a').on('click', function() {
    var object = $(this);
    var navTabs = object.parents('.nav-tabs');
    navTabs.find('li').removeClass("active");
    object.parent('li').addClass("active");
  });
})
