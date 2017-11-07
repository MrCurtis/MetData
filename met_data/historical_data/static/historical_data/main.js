/**Retrieves data fron the server and displays it as a plot line-graph.*/
(function (){
	updatePlot();
	$("#selector-panel").change(updatePlot);

	function updatePlot(){
	    var value_type = getSelectedValueType();
	    var regions = getSelectedRegions();
	    getDataFromServer(value_type, regions);
	}

	function getSelectedValueType() {
	    return $("input[name=value-type]:radio:checked").val();
	}

	function getSelectedRegions(){
	    return $("input[name=region]:checkbox:checked").map(function() {
		return $(this).val();
	    }).get().join("-");
	}

	var colourMapper = {
	    "UK": "black",
	    "England": "blue",
	    "Scotland": "red",
	    "Wales": "green"
	};

	function getDataFromServer(value_type, regions){
	    $.ajax({
		url: "http://localhost:8000/time-series/"+value_type+"/"+regions,
		success: plotData,
		dataType: "json"
	    });
	}

	function createDisplayData(data){
	    return data.series.map((s) => {
		return {
		    type: "scatter",
		    mode: "lines",
		    name: s.name,
		    x: data.labels,
		    y: s.data,
		    line: {color: colourMapper[s.name]}};
	    });
	}

	function plotData(data){
	    var plot_data = createDisplayData(data);
	    var layout = {
		xaxis:{
		    autorange: true,
		    rangeslider: {range: [data.series[0], data.series[300]]}
		    }
		};
	    Plotly.newPlot("plot", plot_data, layout);
	}
})();
