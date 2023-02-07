var map;

function initMap() {
    var mapOptions = {
        center: {lat: 56.11997, lng: -3.93598},
        zoom: 14
    };

    map = new google.maps.Map(document.getElementById("map"), mapOptions);
    var points = [
        {lat: 56.11997, lng: -3.93598},
        {lat: 56.1225, lng: -3.93622},
        {lat: 56.1230, lng: -3.93762},
        {lat: 56.1215, lng: -3.93876}
    ];

    var path = new google.maps.MVCArray();

    for (var i = 0; i < points.length; i++) {
        var point = new google.maps.LatLng(points[i].lat, points[i].lng);
        path.push(point);
        var marker = new google.maps.Marker({
            position: point,
            map: map
        });
    }

    var line = new google.maps.Polyline({
        path: path,
        strokeColor: "#006400",
        strokeOpacity: 1.0,
        strokeWeight: 2
    });

    line.setMap(map);
        google.maps.event.addListener(map, 'bounds_changed', function () {
            addMarker();
            // testMarker();
        });

    }

function testMarker() {
     point = new google.maps.LatLng(56, -4);
     marker = new google.maps.Marker({
         position: point,
         map: map});
}

function addMarker() {
    var coords = {lat: document.getElementById("Latitude").value, lng: document.getElementById("Longitude").value};
    var point = new google.maps.LatLng(coords.lat, coords.lng)
    var marker = new google.maps.Marker({
        position: point,
        map: map
    });
}