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
