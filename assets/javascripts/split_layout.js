$(document).ready(function() {
  $(document).on('dblclick', '.gutter-horizontal', function(e) {
    var gutters = $('.gutter-horizontal');
    var gutterIndex = gutters.index($(this));
    var currentSizes = splitLayout.obj.getSizes();
    var startSizes = splitLayout.sizes;
    var targetSizes = splitLayout.obj.getSizes();

    if (currentSizes[gutterIndex] <= 1) {
      var addeddSpace = startSizes[gutterIndex];
      targetSizes[gutterIndex] = addeddSpace;
      targetSizes[targetSizes.length - 1] -= addeddSpace;
    } else {
      var removedSpace = currentSizes[gutterIndex];
      targetSizes[gutterIndex] = 0;
      targetSizes[targetSizes.length - 1] += removedSpace;
    }
    splitLayout.obj.setSizes(targetSizes);
    splitRedrawTabulator();
  });
})

function gridSplit(cols, sizes, minSize) {
  splitLayout = {
    cols: cols,
    sizes: sizes,
    minSize: minSize,
    obj: Split(cols, {
      elementStyle: (dimension, size, gutterSize) => ({
        'max-width': `calc(${size}% - 15px)`,
      }),
      sizes: sizes,
      minSize: minSize,
      gutterSize: 8,
      snapOffset: 0,
      cursor: 'col-resize',
      onDragEnd: function(sizes) {
        splitRedrawTabulator();
      },
    }),
  }
}

function splitRedrawTabulator() {
  if ($.trim($('.star_data').html())) {
    redrawTabulator('.star_data');
  }
}
