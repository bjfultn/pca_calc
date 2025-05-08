Tabulator.prototype.extendModule("filter", "filters", {
    "!like":  function like(filterVal, rowVal, rowData, filterParams) {
		if (filterVal === null || typeof filterVal === "undefined") {
			return rowVal === filterVal ? true : false;
		} else {
			if (typeof rowVal !== 'undefined' && rowVal !== null) {
				return String(rowVal).toLowerCase().indexOf(filterVal.toLowerCase()) == -1;
			} else {
				return false;
			}
		}
	}
});

function starUrl(cell, formatterParams, onRendered) {
  //cell - the cell component
  //formatterParams - parameters set for the column
  //onRendered - function to call when the formatter has been rendered
  var url_slug = $.trim(cell.getValue().toLowerCase().replace(/ /g, "-"));
  return `<a class='star_link' href='/star/${url_slug}' data-slug='${url_slug}'>${cell.getValue()}</a>`
}

function ticUrl(cell, formatterParams, onRendered) {
  //cell - the cell component
  //formatterParams - parameters set for the column
  //onRendered - function to call when the formatter has been rendered
  var val = cell.getValue()
  if (val == null) {
      return null
  } else {
      return "<a target='_blank' href='https://exofop.ipac.caltech.edu/tess/target.php?id=" + val + "'>" + val + "</a>";
  }
}

function toiUrl(cell, formatterParams, onRendered) {
  //cell - the cell component
  //formatterParams - parameters set for the column
  //onRendered - function to call when the formatter has been rendered
  var val = cell.getValue()
  if (val == null) {
      return null
  } else {
      return "<a target='_blank' href='https://exofop.ipac.caltech.edu/tess/target.php?toi=" + cell.getValue() + "'>" + cell.getValue() + "</a>";
  }
}

function floatFormat(cell, formatterParams, onRendered) {
  //cell - the cell component
  //formatterParams - parameters set for the column
  //onRendered - function to call when the formatter has been rendered
  var precision = (typeof formatterParams.precision !== 'undefined') ?  formatterParams.precision : 2;
  var num = cell.getValue();
  if (num) {
    return num.toFixed(precision);
  } else {
    return ""
  }
}


function remainingFormat(cell, formatterParams, onRendered) {
  //cell - the cell component
  //formatterParams - parameters set for the column
  //onRendered - function to call when the formatter has been rendered
  var precision = (typeof formatterParams.precision !== 'undefined') ?  formatterParams.precision : 2;
  var num = cell.getValue();
  if (num > 0) {
    return num.toFixed(precision);
  } else {
    num = 0;
    return num.toFixed(precision);
  }
}


function logsheetLine(cell, formatterParams, onRendered) {
  //cell - the cell component
  //formatterParams - parameters set for the column
  //onRendered - function to call when the formatter has been rendered
  return "<span class='pre'>" + cell.getValue() + "</span>";
}

function spectraUrl(cell, formatterParams, onRendered) {
  //cell - the cell component
  //formatterParams - parameters set for the column
  //onRendered - function to call when the formatter has been rendered
  var chip = cell.getData().chip;
  var slug = formatterParams.star_slug;
  var file = cell.getValue()[chip];
  if (file) {
    var filename = file.split("/")[file.split("/").length - 1];
    var url = "/download/" + slug + "?file=" + file + "&filename=" + filename;
    var html = "<a href='" + url + "'><i class='fa fa-download'></i> " + filename + "</a>"
    return html;
  } else {
    return "";
  }
}

function ExoFOPFileUrl(cell, formatterParams, onRendered) {
  //cell - the cell component
  //formatterParams - parameters set for the column
  //onRendered - function to call when the formatter has been rendered
  var celldata = cell.getValue()
  var file_name = celldata.split("|")[0]
  var file_id = celldata.split("|")[1]

  return "<a target='_blank' href='https://exofop.ipac.caltech.edu/tess/get_file.php?id=" + file_id + "'><i class='fa fa-download'></i> " + file_name + "</a>";
}

function spectraUrlSorter(a, b, aRow, bRow, column, dir, sorterParams) {
  //a, b - the two values being compared
  //aRow, bRow - the row components for the values being compared (useful if you need to access additional fields in the row data for the sort)
  //column - the column component for the column being sorted
  //dir - the direction of the sort ("asc" or "desc")
  //sorterParams - sorterParams object from column definition array

  var alignEmptyValues = sorterParams.alignEmptyValues;
  var emptyAlign = 0;
  var aChip = aRow.getData().chip
  var bChip = bRow.getData().chip

  if (!a[aChip]) {
    emptyAlign = !b[bChip] ? 0 : -1;
  } else if (!b[bChip]) {
    emptyAlign = 1;
  } else {
    var aPath = a[aChip].split("/")
    var aFile = aPath[aPath.length - 1];
    var bPath = b[bChip].split("/")
    var bFile = bPath[bPath.length - 1];

    return String(aFile).toLowerCase().localeCompare(String(bFile).toLowerCase());
  }

  if (alignEmptyValues === "top" && dir === "desc" || alignEmptyValues === "bottom" && dir === "asc") {
    emptyAlign *= -1;
  }

  return emptyAlign;
}


var sumOverStars = function(values, data, calcParams){
    //values - array of column values
    //data - all table data
    //calcParams - params passed from the column definition object

    var calc = 0;
    var stars_counted = [];
    var i = 0;

    values.forEach(function(value){
        var star_name = data[i].Star_name;
        if (!stars_counted.includes(star_name, 0)){
            calc = calc + value;
            stars_counted.push(star_name);
        }
        i ++;
    });

    return calc;
}

var countOverStars = function(values, data, calcParams){
    //values - array of column values
    //data - all table data
    //calcParams - params passed from the column definition object

    var calc = 0;
    var stars_counted = [];
    var i = 0;

    values.forEach(function(value){
        var star_name = data[i].Star_name;
        if (!stars_counted.includes(star_name, 0)){
            calc++
            stars_counted.push(star_name);
        }
        i ++;
    });

    return calc;
}


function starCount(cell){
    //cell - the cell component
    var celldata = cell.getValue()

    if (celldata == 1) {
        return celldata + " star"
    } else {
        return  celldata + " stars";
    }
}

function plCount(cell){
    //cell - the cell component
    var celldata = cell.getValue()

    if (celldata == 1) {
        return celldata + " planet"
    } else {
        return  celldata + " planets";
    }
}

function fitsLink(cell, formatterParams, onRendered) {
  //cell - the cell component
  //formatterParams - parameters set for the column
  //onRendered - function to call when the formatter has been rendered

  if (cell.getValue()) {
    var parts = cell.getValue().split("/")
    var segment = parts[2]
    var filename = parts[parts.length - 1]
    var path = `/fits/${segment}/${filename}`
    return `<a target='_blank' href='${path}'>${filename}</a>`
  } else {
    return ""
  }
}
