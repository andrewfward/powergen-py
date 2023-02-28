let map;

function initMap() {
  map = new google.maps.Map(document.getElementById("map"), {
    center: { lat: 51.5074, lng: 0.1278 },
    zoom: 8,
  });

  let markers = [];
  let path = new google.maps.Polyline({
    path: markers,
    geodesic: true,
    strokeColor: "#FF0000",
    strokeOpacity: 1.0,
    strokeWeight: 2,
  });
  path.setMap(map);

  google.maps.event.addListener(map, "click", (event) => {
    addMarker(event.latLng);
  });

  google.maps.event.addListener(map, "bounds_changed", (event) => {
    // addMarker({{x}}.latLng)
    // {% for x in nodes_locs %}
    // {% endfor %}
    //});

  function addMarker(location) {
    let marker = new google.maps.Marker({
      position: location,
      map: map,
      draggable: true,
    });
    markers.push(marker.getPosition());
    path.setPath(markers);

    google.maps.event.addListener(marker, "dragend", () => {
      markers[markers.indexOf(marker.getPosition())] = marker.getPosition();
      path.setPath(markers);
    });
  }
}
