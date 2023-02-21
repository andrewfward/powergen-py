let map;
let markers = [];
let path;

function initMap() {
  map = new google.maps.Map(document.getElementById("map"), {
    center: {lat: 51.5074, lng: 0.1278},
    zoom: 8,
    mapTypeId: google.maps.MapTypeId.SATELLITE,
    mapTypeControlOptions: {
      mapTypeIds: [google.maps.MapTypeId.SATELLITE],
      style: google.maps.MapTypeControlStyle.HORIZONTAL_BAR,
      position: google.maps.ControlPosition.TOP_CENTER,
    },
  });

  path = new google.maps.Polyline({
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

  function addMarker(location) {
    let marker = new google.maps.Marker({
      position: location,
      map: map,
      draggable: true,
      icon: {
        url: "https://maps.google.com/mapfiles/kml/shapes/placemark_circle.png",
        scaledSize: new google.maps.Size(30, 30),
        origin: new google.maps.Point(0, 0),
        anchor: new google.maps.Point(15, 15),
      },
    });
    markers.push(marker.getPosition());
    path.setPath(markers);

    if (markers.length > 1) {
      let lastMarkerIndex = markers.length - 2;
      let lastMarker = new google.maps.Marker({
        position: markers[lastMarkerIndex],
        map: map,
        draggable: false,
      });
      google.maps.event.addListener(marker, "drag", () => {
        markers[markers.length - 1] = marker.getPosition();
        path.setPath(markers);
        lastMarker.setPosition(markers[lastMarkerIndex]);
      });
    }

    google.maps.event.addListener(marker, "click", () => {
      let inputLabel = document.createElement("label");
      inputLabel.innerHTML = "Desired Power: ";
      inputLabel.style.display = "block";
      inputLabel.style.fontWeight = "bold";
      inputLabel.style.marginTop = "10px";

      let inputField = document.createElement("input");
      inputField.setAttribute("type", "text");
      inputField.style.width = "100%";
      inputField.style.padding = "5px";

      let container = document.createElement("div");
      container.appendChild(inputLabel);
      container.appendChild(inputField);

      let infoWindow = new google.maps.InfoWindow({
        content: container,
      });

      infoWindow.open(map, marker);

      marker.setIcon({
        url: "https://maps.google.com/mapfiles/kml/shapes/placemark_circle.png",
        scaledSize: new google.maps.Size(20, 20),
        origin: new google.maps.Point(0, 0),
        anchor: new google.maps.Point(10, 10),
      });
    });

    google.maps.event.addListener(marker, "dragstart", () => {
      marker.setIcon({
        url: "https://maps.google.com/mapfiles/kml/shapes/placemark_circle.png",
        scaledSize: new google.maps.Size(30, 30),
        origin: new google.maps.Point(0, 0),
        anchor: new google.maps.Point(15, 15),
      });
    });

    google.maps.event.addListener(marker, "dragend", () => {
      marker.setIcon({
        url: "https://maps.google.com/mapfiles/kml/shapes/placemark_circle.png",
        scaledSize: new google.maps.Size(20, 20),
        origin: new google.maps.Point(0, 0),
        anchor: new google.maps.Point(10, 10),
      });
    });
  }
}