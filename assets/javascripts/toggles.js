$(document).ready(function() {
  $('.star_data').on('click', '.star_toggles .nav-link', function(e) {
    var target = $(this);
    var cookie = target.parents(".star_toggles").data("cookie")
    var state = target.hasClass('collapsed');
    if (state) {
      target.addClass("active");
      updateToggleState(e, "add", cookie, target.attr('id'));
    } else {
      target.removeClass("active");
      updateToggleState(e, "del", cookie, target.attr('id'));
    }
  }).on('shown.bs.collapse', function(e) {
    var scope = "#" + e.target.id;
    redrawTabulator(scope);
    balancePlotlyPlots(scope);
  });
})

function updateToggleState(e, action, key, value) {
  // only update the cookie state if the user clicked a button
  if ('originalEvent' in e) {
    cookies = jumpCookies()[key]
    if (action == "add") {
      cookies.push(value);
    }
    if (action == "del") {
      cookies = cookies.filter(function(ele){
        return ele != value;
      });
    }
    jumpCookies(key, cookies)
  }
}

function showActiveTabs() {
  var cookieKeys = Object.keys(jumpCookies());
  $.each(cookieKeys, function( i, cookieKey ) {
    if (cookieKey.substr(-5) == "_tabs") {
      $.each(jumpCookies(cookieKey), function( i, v ) {
        $("#" + v).click();
      });
    }
  });
}

function redrawTabulator(scope) {
  $(scope).find(".tabulator:visible").each(function() {
    var element = $(this);
    var tabulator = window[this.id + "_tabulator"];
    if (tabulator) {
      tabulator.redraw();
    }
  });
}

function balancePlotlyPlots(scope) {
  $(scope).find(".js-plotly-plot:visible").each(function() {
    Plotly.Plots.resize(this.id);
  });
}
