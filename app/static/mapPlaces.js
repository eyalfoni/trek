var input = document.getElementById("pac-input");
var searchBox = new google.maps.places.SearchBox(input);


searchBox.addListener("places_changed", function() {
    var places = searchBox.getPlaces();

    if (places.length == 0) {
      return;
    } else if (places.length !== 1) {
      alert('Please select a location from the dropdown.')
      return
    }

    places.forEach(function(place) {
        if (!place.geometry) {
        console.log("Returned place contains no geometry");
        return;
      }
      console.log(place)
    })
})
