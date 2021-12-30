// Call the dataTables jQuery plugin
$(document).ready(function() {
  $('#dataTable').DataTable({
    responsive: true
  });
  $('#dataTable2').DataTable({
    "order": [[ 2, "desc" ]]
  });
});
