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

$( function () {
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
                text: 'Kbps',
                margin: 80
            }
        },
        series: series
    });
});