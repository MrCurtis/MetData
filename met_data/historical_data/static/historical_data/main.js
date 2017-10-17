update()
var selectorPanel = $("#selector-panel");
selectorPanel.change(update);

function update(){
    var value_type = getSelectedValueType();
    var regions = getSelectedRegions();
    getDataFromServer(value_type, regions)
}

function getSelectedValueType() {
    return $('input[name=value-type]:radio:checked').val();
};

function getSelectedRegions(){
    return $('input[name=region]:checkbox:checked').map(function() {
	    return $(this).val();
    }).get().join("-");
    
};

function colourMapper(region){
    console.log("region", region)
    var map = {
        "UK": "black",
        "England": "blue",
        "Scotland": "red",
        "Wales": "green"
    }
    console.log(map[region])
    return map[region]
}

function createDisplayData(data){
    console.log("This bit running")
    var labels = data["labels"];
    var series = data["series"];
    return series.map((s) => {
        return {
	    type: "scatter",
	    mode: "lines",
	    name: s["name"],
	    x: labels,
	    y: s["data"],
	    line: {color: colourMapper(s["name"])}}
    });
};

function success(data){
    var plot_data = createDisplayData(data);
    var layout = {
        xaxis:{
	    autorange: true,
	    rangeslider: {range: [data["series"][0], data["series"][300]]},
	    }
        }
    Plotly.newPlot('tester', plot_data, layout);
};

function getDataFromServer(value_type, regions){
    $.ajax({
        url: "http://localhost:8000/time-series/"+value_type+"/"+regions+"",
        success: success,
        dataType: "json"
    });
};
