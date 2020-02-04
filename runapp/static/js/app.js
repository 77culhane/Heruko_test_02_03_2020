function buildPlot() {
    /* data route */
  var url = "/runquery";
  d3.json(url).then(function(response) {

    console.log(response);

  });
}

buildPlot();
