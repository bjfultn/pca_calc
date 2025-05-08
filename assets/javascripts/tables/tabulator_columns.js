//////
// The complete set of definitions for data columns that can be displayed on the stars or candidates tabulator table.
// Also includes fancy display text (title) for tabulator headings only.
//

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
        {field: "class", title: "Class", sorter:"string", sorterParams: {alignEmptyValues: "bottom"}},
      ]
}