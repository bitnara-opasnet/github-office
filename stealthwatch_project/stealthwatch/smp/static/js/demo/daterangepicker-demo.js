// Call the dataTables jQuery plugin
  $(document).ready(function() {
    $('input[name="datetimes"]').daterangepicker({
      timePicker: true,
      startDate: moment().startOf('hour'),
      endDate: moment().startOf('hour').add(32, 'hour'),
      locale: {
      format: 'M/DD hh:mm A'
      }
  });
  });
  