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

        // create the save button
        let saveButton = document.createElement("button");
        saveButton.innerHTML = "Save";
        saveButton.style.display = "block";
        saveButton.style.marginTop = "10px";

        let container = document.createElement("div");
        container.appendChild(saveButton);

        let infoWindow = new google.maps.InfoWindow({
            content: container,
        });

        google.maps.event.addListener(marker, "click", () => {
            // open the info window with the save button
            infoWindow.open(map, marker);

            marker.setIcon({
                url: "https://maps.google.com/mapfiles/kml/shapes/placemark_circle.png",
                scaledSize: new google.maps.Size(20, 20),
                origin: new google.maps.Point(0, 0),
                anchor: new google.maps.Point(10, 10),
            });

            // add a click event listener to the save button
            saveButton.addEventListener("click", () => {
                // send a POST request to the server to store the point
                let xhr = new XMLHttpRequest();
                xhr.open("POST", "/store-point", true);
                xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
                xhr.onreadystatechange = function () {
                    if (xhr.readyState === 4 && xhr.status === 200) {
                        let response = JSON.parse(xhr.responseText);
                        if (response.success) {
                            // if the point was saved successfully, close the info window and reset the marker icon
                            infoWindow.close();
                            marker.setIcon({
                                url: "https://maps.google.com/mapfiles/kml/shapes/placemark_circle.png",
                                scaledSize: new google.maps.Size(30, 30),
                                origin: new google.maps.Point(0, 0),
                                anchor: new google.maps.Point(15, 15),
                            });
                        }
                    }
                };
                xhr.send("lat=" + location.lat() + "&lng=" + location.lng() + "&label=Marker");
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

