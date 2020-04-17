$(document).ready(function () {
    draw_table()
});

function draw_table() {
    $('#table_body').html('');
    $.getJSON('http://127.0.0.1:5000/get_all', function (data) {
        $.each(data, function (key, val) {
            let row = "";
            let team = "";
            $.each(val, function (key, val) {
                if (key === 'team_name'){
                    team = val;
                }
                if (key === 'logo'){
                    row += '<td><img alt="' + team + '" src="' + val + '" width="100" height="100"></td>';
                } else {
                    row += '<td>' + val + '</td>';
                }
            });
            $('#table_body').append('<tr>' + row + '</tr>');
        });
    });
}
