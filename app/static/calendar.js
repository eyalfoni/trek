function fetchEvents() {
    var selected_events = $('#events_select').val();
    var selected_travelers = $('#travelers_select').val();
    if (selected_travelers) {
        selected_travelers = selected_travelers.join()
    }
    var result;
    $.ajax({
        url: '/events',
        dataType: 'json',
        async: false,
        data: {
            trip_id: tripId,
            event_type: selected_events,
            travelers: selected_travelers
        },
        success: function(data) {
            result = data.result
        }
    })
    return result
}

function renderCalendar() {
    var result = fetchEvents();
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
      initialView: 'dayGridMonth',
      themeSystem: 'standard',
      headerToolbar: { center: 'dayGridMonth,timeGridWeek,timeGridDay', end: 'today prev,next' },
      navLinks: true,
      fixedWeekCount: false,
      events: result.events,
      initialDate: result.start_date,
      eventClick: function(info) {
        var event_id = info.event.extendedProps.event_id
        var event_type = info.event.extendedProps.type
        $.get('/event', {
            id: event_id,
            type: event_type
        }, function(data) {
            document.getElementById("event_forms").style.display = "none"; // hide the add event forms
            document.getElementById("book_now").style.display = "block";
            div = document.getElementById('book_now');
            if (event_type === 'flight') {
                var msg = 'Join ' + data.result.user_name + "\'s " + event_type + ' now!';
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
                document.getElementById('departure').textContent = 'Departing ' + moment.utc(data.result.departure).local().format('LLL')
                document.getElementById('arrival').textContent = 'Arriving ' + moment.utc(data.result.arrival).local().format('LLL')
                document.getElementById('book_now_msg').textContent = msg;
            } else if (event_type === 'stay') {
                div.innerHTML = data;
            } else {
                var msg = 'Join ' + data.result.user_name + "\'s " + event_type + ' now!';
                div.innerHTML = `
                    <div id=event_name></div>
                    <div id=start></div>
                    <div id=end></div>
                    <button type="button" class="btn btn-primary">
                        <span id=book_now_msg></span>
                    </button>
                `;
                document.getElementById('book_now_msg').textContent = msg;
                document.getElementById('event_name').textContent = data.result.event_name;
                document.getElementById('start').textContent = 'Start ' + moment.utc(data.result.start_time).local().format('LLL')
                document.getElementById('end').textContent = 'End ' + moment.utc(data.result.end_time).local().format('LLL')
                document.getElementById('book_now_msg').textContent = msg;
            }
        })
      }
    });
    calendar.render();
};

document.addEventListener('DOMContentLoaded', function() {
     renderCalendar();
});

function filterEvents(e) {
    renderCalendar();
}

function clearDropdown(e) {
    $("#travelers_select").val('default');
    $("#travelers_select").selectpicker("refresh");
    filterEvents(e);
}
