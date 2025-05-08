$(document).ready(function() {
  $("#filter-add").click(addFancyTableFilter);
  $("#filter-value").on("keyup", function(e) {
    if (e.keyCode === 13) {
      e.preventDefault();
      $("#filter-add").click();
    }
  });
  $(".fancy_table_filter .active_filters").on("click", ".fa", removeFancyTableFilter);
});

function addFancyTableFilter() {
  var name = $("#filter-field option:selected").text();
  var field = $("#filter-field").val();
  var operator = $("#filter-operator").val();
  var value = $("#filter-value").val();
  var tabulator = $(".fancy_table_filter").data("tabulator")

  if (value != "") {
    addFilterToCookies(name, field, operator, value, tabulator);
    addActiveFiltersElement(name, field, operator, value);
    addTabulatorFilter(field, operator, value, tabulator);
    $("#filter-value").val("");
  }
}

function removeFancyTableFilter(e) {
  var element = $(this).parents(".filter");
  var field = element.data("field");
  var operator = element.data("operator");
  var value = element.data("value").toString();
  var filterParams = tabulatorFilterParams(field, operator, value);
  var tabulator = $(".fancy_table_filter").data("tabulator")

  removeFilterFromCookies(field, operator, value, tabulator);
  window[tabulator].removeFilter(filterParams);
  element.remove();
  updateStarsTableCount();
}

function addFilterToCookies(name, field, operator, value, tabulator) {
  var filters = jumpCookies(tabulator);
  filters.push({name:name, field:field, operator:operator, value:value});
  jumpCookies(tabulator, filters);
}

function removeFilterFromCookies(field, operator, value, tabulator) {
  var filters = jumpCookies(tabulator);
  var filtered = filters.filter(function(filter, i, a) {
    return !(
      filter.field == field &&
      filter.operator == operator &&
      filter.value == value
    );
  });
  jumpCookies(tabulator, filtered);
}

function addActiveFiltersElement(name, field, operator, value) {
  html = `<span data-field="${field}" data-operator="${operator}" data-value="${value}" class="filter">${name} ${operator} ${value} <i class="fa fa-times-circle"></i></span>`
  $(".fancy_table_filter .active_filters").append(html);
}

function addTabulatorFilter(field, operator, value, tabulator) {
  var filterParams = tabulatorFilterParams(field, operator, value);
  window[tabulator].addFilter(filterParams);
  updateStarsTableCount();
}

function tabulatorFilterParams(field, operator, value) {
  if (field == "Star_name" && operator == "like") {
    var filterParams = [
      [
        {field:"Star_name", type:operator, value:value},
        {field:"othernames", type:operator, value:value}
      ]
    ]
  } else {
    var filterParams = [
      {field:field, type:operator, value:value}
    ]
  }
  return filterParams;
}

function applyFiltersFromCookies() {
  var tabulator = $(".fancy_table_filter").data("tabulator")
  var filters = jumpCookies(tabulator);
  $(".active_filters .filter").remove();
  Object.values(filters).forEach(function(filter) {
    addActiveFiltersElement(filter.name, filter.field, filter.operator, filter.value);
    addTabulatorFilter(filter.field, filter.operator, filter.value, tabulator);
  });
}
