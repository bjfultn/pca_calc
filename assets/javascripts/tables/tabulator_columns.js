//////
// The complete set of definitions for data columns that can be displayed on the stars or candidates tabulator table.
// Also includes fancy display text (title) for tabulator headings only.
//
//
function classColumnSorter(a, b, aRow, bRow, column, dir, sorterParams) {
  var aSort = aRow.getData().class_sort;
  var bSort = bRow.getData().class_sort;

  var aNumber = typeof aSort === "number" ? aSort : parseInt(aSort, 10);
  var bNumber = typeof bSort === "number" ? bSort : parseInt(bSort, 10);

  var aEmpty = isNaN(aNumber);
  var bEmpty = isNaN(bNumber);

  if (aEmpty || bEmpty) {
    if (aEmpty && bEmpty) {
      return 0;
    }

    var alignEmpty = sorterParams && sorterParams.alignEmptyValues ? sorterParams.alignEmptyValues : "bottom";
    var emptyGoesBottom = alignEmpty === "bottom";

    if (aEmpty) {
      return emptyGoesBottom ? (dir === "asc" ? 1 : -1) : (dir === "asc" ? -1 : 1);
    }

    if (bEmpty) {
      return emptyGoesBottom ? (dir === "asc" ? -1 : 1) : (dir === "asc" ? 1 : -1);
    }
  }

  return aNumber - bNumber;
}

function competitionTableColumns() {
  return [
        {field: "id", title: "ID", visible: false, sorterParams: {alignEmptyValues: "bottom"}},
        {field: "user_name", title: "User", sorter:"string", sorterParams: {alignEmptyValues: "bottom"}},
        {field: "year", title: "Year", sorter:"string", sorterParams: {alignEmptyValues: "bottom"}},
        {field: "make", title: "Make", sorter:"string", sorterParams: {alignEmptyValues: "bottom"}},
        {field: "model", title: "Model", sorter:"string", sorterParams: {alignEmptyValues: "bottom"}},
        {field: "base_points", title: "Base Points", formatter:floatFormat, sorterParams:{alignEmptyValues:"bottom"}, formatterParams: {precision: 0}},
        {field: "tire_points", title: "Tire Points", formatter:floatFormat, sorterParams:{alignEmptyValues:"bottom"}, formatterParams: {precision: 0}},
        {field: "upgrade_points", title: "Upgrade Points", formatter:floatFormat, sorterParams:{alignEmptyValues:"bottom"}, formatterParams: {precision: 0}},
        {field: "total_points", title: "Total Points", formatter:floatFormat, sorterParams:{alignEmptyValues:"bottom"}, formatterParams: {precision: 0}},
        {field: "class", title: "Class", sorter:classColumnSorter, sorterParams: {alignEmptyValues: "bottom"}},
      ]
}
