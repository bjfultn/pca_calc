$(document).ready(function() {
  $('.star_page').keyup('.simple_filter .simple_filter_input', function(e) {
    var input = $(e.target);
    var search = input.val();
    var tableVarName =  input.parents('.tabulator_group').find('.tabulator').attr('id') + '_tabulator';
    var tabulator = window[tableVarName];
    if (tabulator) {
      if (search != '') {
        tabulator.setFilter(matchAny, {value: search});
      } else {
        tabulator.clearFilter();
      }
    }
  });

  $('.star_page').on('click', '.simple_filter_clear', function(e) {
    var button = $(e.target);
    var input = button.parents('.tabulator_group').find('.simple_filter_input')
    var tableVarName =  button.parents('.tabulator_group').find('.tabulator').attr('id') + '_tabulator';
    var tabulator = window[tableVarName];
    if (tabulator) {
      input.val('');
      tabulator.clearFilter();
    }
  });
});

function matchAny(data, filterParams){
  //data - the data for the row being filtered
  //filterParams - params object passed to the filter
  var match = false;
  for(var key in data){
    if (JSON.stringify(data[key]).search(filterParams.value) != -1) {
      match = true;
    }
  }
  return match;
}
