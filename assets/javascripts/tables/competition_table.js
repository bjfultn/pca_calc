function initCompetitionTable() {
  var data_url = "/api/competition";
  var data = {};
  $.when(
    $.get(data_url, function(result) {
      data = result;
    })
  ).then(function() {
      competition_table_tabulator = new Tabulator("#competition_table", {
      data: data,
      tooltips: true,
      height: "82vh",
      layout: "fitDataFill",
      persistenceID:"competition_table_ID",
      persistenceMode:'cookie',
      persistentLayout: true,
      movableColumns: true, //enable user movable columns
      persistentSort: true,
      persistentFilter: false, // Custom filters are not persistent
      ajaxFiltering: true,
      rowClick: function(e, row) {
        // e - the click event object
        // row - row component for the clicked row

        var data = row.getData(); // Get the data for the clicked row
        var carId = data.id; // Assuming each row data has an 'id' property that corresponds to the car's ID

        // Navigate to the desired URL using window.location
        window.location.href = `/garage/view/${carId}/`;
      },
      initialSort: [
        {column:"total_points", dir:"dsc"},
      ],
      columns: competitionTableColumns(),
      });
  })
  .fail(function(xhr, status, error) {
    console.log(xhr);
    console.log(status);
    console.log(error);
  });
}
