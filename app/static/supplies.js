jQuery(document).ready(function($) {
    $(".clickable-row").click(function(e) {
        console.log(e.currentTarget.id)
        window.location = `/supplies/${tripId}/${e.currentTarget.id}`
    });
});
