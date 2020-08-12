var input = document.getElementById("pac-input");
var searchBox = new google.maps.places.SearchBox(input);
var place;

searchBox.addListener("places_changed", function() {
    var places = searchBox.getPlaces();

    if (places.length == 0) {
      return;
    } else if (places.length !== 1) {
      alert('Please select a location from the dropdown.')
      return
    }

    place = places[0]
    if (!place.geometry) {
        console.log("Returned place contains no geometry");
        return;
    }
})

function addStay(e) {
    e.preventDefault();
    var formData = $('#hotel_form_id').serialize()
    delete place.reviews
    formData += '&place=' + encodeURIComponent(JSON.stringify(place));
    $.ajax({
      type: "POST",
      url: '/add/hotel/'+tripId.toString(),
      data: formData,
      success: function(data) {
            renderCalendar();
            document.getElementById("hotel_form_id").reset();
      },
      dataType: 'json',
      processData: false
    });
    return false;
}

var event_input = document.getElementById("event-input");
var eventSearchBox = new google.maps.places.SearchBox(event_input);
var event_place;

eventSearchBox.addListener("places_changed", function() {
    var eventPlaces = eventSearchBox.getPlaces();

    if (eventPlaces.length == 0) {
      return;
    } else if (eventPlaces.length !== 1) {
      alert('Please select a location from the dropdown.')
      return
    }

    event_place = eventPlaces[0]
    if (!event_place.geometry) {
        console.log("Returned place contains no geometry");
        return;
    }
})

function addEvent(e) {
    e.preventDefault();
    var formData = $('#event_form_id').serialize()
    delete event_place.reviews
    formData += '&place=' + encodeURIComponent(JSON.stringify(event_place));
    $.ajax({
      type: "POST",
      url: '/add/event/'+tripId.toString(),
      data: formData,
      success: function(data) {
            renderCalendar();
            document.getElementById("event_form_id").reset();
      },
      dataType: 'json',
      processData: false
    });
    return false;
}
