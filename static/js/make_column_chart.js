$(function () {
    $('#container').highcharts({
        chart: {
            type: 'column'
        },
        title: {
            text: 'Friends by Name'
        },
        subtitle: {
            text: 'Source: Facebook.com'
        },
        xAxis: {
            categories: [
                'A',
                'B',
                'C',
                'D',
                'E',
                'F',
                'G',
                'H',
                'I',
                'J',
                'K',
                'L',
                'M',
                'N',
                'O',
                'P',
                'Q',
                'R',
                'S',
                'T',
                'U',
                'V',
                'W',
                'X',
                'Y',
                'Z'
            ],
            crosshair: true,
            title: {
                text: 'Letters of the Alphabet'
            }
        },
        yAxis: {
            min: 0,
            title: {
                text: 'Friend Count'
            }
        },
        tooltip: {
            headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
            pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
                '<td style="padding:0"><b>{point.y:.1f} mm</b></td></tr>',
            footerFormat: '</table>',
            shared: true,
            useHTML: true
        },
        plotOptions: {
            column: {
                pointPadding: 0.2,
                borderWidth: 0
            }
        },
        series: [{
            name: 'Shubhi',
            data: [3,4,7,2,1,1,1,2,1,1,1,1,6,1,1,1,2,1,3,1,4,1,1,2,1,1]

        }]
    });
});
