var chart;
var series = [
    { name: 'sent', data: [] },
    { name: 'recv', data: [] }
]

function requestData() {
    $.ajax({
        url: '/sysinfodata2',
        success: function (data) {
            console.log(data)
            var series = chart.series[0],
                shift = series.data.length > 20; // shift if the series is longer than 20

            // add the point
            chart.series[0].addPoint(data.sent, true, shift);
            chart.series[1].addPoint(data.recv, true, shift);

            // call it again after one second
            setTimeout(requestData, 2000);
        },
        error: function () {
            console.log("error");
        },
        cache: false
    });
}

$(function () {
    chart = new Highcharts.Chart({
        chart: {
            renderTo: 'container',
            defaultSeriesType: 'spline',
            events: {
                load: requestData
            }
        },
        title: {
            text: 'Realtime Network I/O'
        },
        xAxis: {
            type: 'datetime',
            tickPixelInterval: 150,
            maxZoom: 20 * 1000
        },
        yAxis: {
            minPadding: 0.2,
            maxPadding: 0.2,
            title: {
                text: 'Mbps',
                margin: 80
            }
        },
        tooltip: {
            headerFormat: '<b>{series.name}</b><br/>',
            pointFormat: '{point.y}Mbps'
        },
        series: series
    });
});

// $('#button').click(function () {
//     var max = chart.yAxis[0].max;
//     var min = chart.yAxis[0].min;
//     max += 10;
//     chart.yAxis[0].setExtremes(min, max);
// });

// $('#button1').click(function () {
//     var max = chart.yAxis[0].max;
//     var min = chart.yAxis[0].min;
//     min -= 10;
//     chart.yAxis[0].setExtremes(min, max);
// });