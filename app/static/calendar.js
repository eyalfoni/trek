document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
      initialView: 'dayGridMonth',
      themeSystem: 'standard',
      headerToolbar: { center: 'dayGridMonth,timeGridWeek,timeGridDay', end: 'today prev,next' },
      navLinks: true,
      fixedWeekCount: false,
      events: events,
      eventClick: function(info) {
        var event_id = info.event.extendedProps.event_id
        var event_type = info.event.extendedProps.type
        $.getJSON('/event', {
            id: event_id,
            type: event_type
        }, function(data) {
            console.log(data)
            var msg = 'Join ' + data.result.user_name + "\'s " + event_type + ' now!';
            div = document.getElementById('book_now');
            if (event_type === 'flight') {
                div.innerHTML = `
                    <div id=flight_code></div>
                    <div id=departure></div>
                    <div id=arrival></div>
                    <button type="button" class="btn btn-primary">
                        <span id=book_now_msg></span>
                    </button>
                `;
                document.getElementById('book_now_msg').textContent = msg;
                document.getElementById('flight_code').textContent = 'Flight Number ' + data.result.flight_code;
                document.getElementById('departure').textContent = 'Departing ' + moment(data.result.departure).format('LLL')
                document.getElementById('arrival').textContent = 'Arriving ' + moment(data.result.arrival).format('LLL')
            } else {
                div.innerHTML = `
                    <div id=stay_name></div>
                    <div id=check_in></div>
                    <div id=check_out></div>
                    <button type="button" class="btn btn-primary">
                        <span id=book_now_msg></span>
                    </button>
                `;
                document.getElementById('book_now_msg').textContent = msg;
                document.getElementById('stay_name').textContent = data.result.stay_name;
                document.getElementById('check_in').textContent = 'Check In ' + moment(data.result.check_in).format('LL')
                document.getElementById('check_out').textContent = 'Check Out ' + moment(data.result.check_out).format('LL')
            }
            document.getElementById('book_now_msg').textContent = msg;
        })
      }
    });
    calendar.render();
});
