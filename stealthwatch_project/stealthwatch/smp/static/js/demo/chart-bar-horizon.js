// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';

// Bar Chart Example
var ctx = document.getElementById("myBarChart");
var myBarChart = new Chart(ctx, {
  type: 'horizontalBar',
  data: {
      labels: ['가', '나', '다', '라', '마', '바', '사', '아', '자', '차', '카', '타', '파', '하'],
      datasets: [{
          label: '테스트 데이터셋',
          data: [10, 3, 30, 23, 10, 5, 15, 25, 2, 4, 1, 13, 52, 23],
          borderColor: "rgba(255, 201, 14, 1)",
          backgroundColor: "rgba(255, 201, 14, 0.5)",
          fill: false,
      }]
  },
  options: {
      responsive: true,
      title: {
          display: true,
          text: '막대 차트 테스트'
      },
      tooltips: {
          mode: 'index',
          intersect: false,
      },
      hover: {
          mode: 'nearest',
          intersect: true
      },
      scales: {
          xAxes: [{
              display: true,
              scaleLabel: {
                  display: true,
                  labelString: 'x축'
              },
          }],
          yAxes: [{
              display: true,
              ticks: {
                  autoSkip: false,
              },
              scaleLabel: {
                  display: true,
                  labelString: 'y축'
              }
          }]
      }
  }
});
