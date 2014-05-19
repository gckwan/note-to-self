  var mostRecentMarker = null;
  var mostRecentInfoWindow = null;
  var map = null;

  /* Contains all reminder markers. Maps from index (starting from 0) to the marker element. */
  var reminders = {};
  var id = $('.entry').length;

  function initialize() {
    var markers = [];
    map = new google.maps.Map(document.getElementById('map-canvas'), {
      mapTypeId: google.maps.MapTypeId.ROADMAP
    });

    bound1_lat = "37.437445";
    bound1_lng = "-122.170341";
    bound2_lat = "37.425449";
    bound2_lng = "-122.162273";

    var defaultBounds = new google.maps.LatLngBounds(
      new google.maps.LatLng(bound1_lat, bound1_lng),
      new google.maps.LatLng(bound2_lat, bound2_lng));
    map.fitBounds(defaultBounds);

    $('#map-bound1-lat').val(bound1_lat);
    $('#map-bound1-lng').val(bound1_lng);
    $('#map-bound2-lat').val(bound2_lat);
    $('#map-bound2-lng').val(bound2_lng);

    // Create the search box and link it to the UI element.
    var input = /** @type {HTMLInputElement} */(
        document.getElementById('pac-input'));
    map.controls[google.maps.ControlPosition.TOP_LEFT].push(input);

    var searchBox = new google.maps.places.SearchBox(
      /** @type {HTMLInputElement} */(input));

    // [START region_getplaces]
    // Listen for the event fired when the user selects an item from the
    // pick list. Retrieve the matching places for that item.
    google.maps.event.addListener(searchBox, 'places_changed', function() {
      var places = searchBox.getPlaces();

      for (var i = 0, marker; marker = markers[i]; i++) {
        marker.setMap(null);
      }

      // For each place, get the icon, place name, and location.
      markers = [];
      var bounds = new google.maps.LatLngBounds();
      for (var i = 0, place; place = places[i]; i++) {
        var image = {
          url: place.icon,
          size: new google.maps.Size(71, 71),
          origin: new google.maps.Point(0, 0),
          anchor: new google.maps.Point(17, 34),
          scaledSize: new google.maps.Size(25, 25)
        };

        // Create a marker for each place.
        var marker = new google.maps.Marker({
          map: map,
          icon: image,
          title: place.name,
          position: place.geometry.location
        });

        markers.push(marker);

        bounds.extend(place.geometry.location);
      }

      map.fitBounds(bounds);
    });
    // [END region_getplaces]

    // Bias the SearchBox results towards places that are within the bounds of the
    // current map's viewport.
    google.maps.event.addListener(map, 'bounds_changed', function() {
      var bounds = map.getBounds();
      searchBox.setBounds(bounds);
    });

    google.maps.event.addListener(map, 'rightclick', function(event) {
      mostRecentMarker = placeMarker("Set reminder?", event.latLng, map);
      console.log('adding a place marker');

      $('#reminder-lat').val(event.latLng.lat());
      $('#reminder-lng').val(event.latLng.lng());
      $('#add-reminder-container').show();
    });
    addReminderMarkers(map);
  }



  function placeMarker(name, location, map) {
    var marker = new google.maps.Marker({
        position: location,
        map: map
    });

    var infowindow = new google.maps.InfoWindow();
    var mostRecentInfoWindow = infowindow;
    infowindow.open(map, this);

    google.maps.event.addListener(marker, 'click', function() {
      infowindow.setContent(name);
      infowindow.open(map, this);
    });

    return marker;
    //map.setCenter(location);
  }




  function addReminderMarkers(map) {
    $('.entry').each(function(i, el) {
      var name = $(this).children('.name').text();
      var latitude = $(this).children('.latitude').text();
      var longitude = $(this).children('.longitude').text();

      var latLng = new google.maps.LatLng(latitude, longitude);

      var marker = placeMarker(name, latLng, map);
      reminders[i] = marker;
    });
  }


  var removeRem = function removeReminder() {
    var clickedId = parseInt($(this).data('id'), 10);
    var marker = reminders[clickedId];

    marker.setMap(null);
    $(this).parents('tr').remove();
  };



  /* When the user presses the button to add a reminder, add a new
     entry to the reminders table, add a new marker to the map with
     the reminder title, and add the marker to the markers object. */
  $('#add-reminder').click(function() {
  	$("#reminder-id").val(id);
    var name = $('#reminder-name').val();
    $("#sent-reminder-name").val(name);
    var lat = $('#reminder-lat').val();
    var lng = $('#reminder-lng').val();
    console.log(lat);
    console.log(lng);

    var deleteButton = $('<button>').addClass('delete').text('Delete').attr('data-id', id);
    deleteButton.click(removeRem);

    $('#reminders tbody').append(
      $('<tr>').append($('<td>').text(name))
               .append($('<td>').text(lat))
               .append($('<td>').text(lng))
               .append($('<td>').append(deleteButton))
      );
    $('#add-reminder-container').hide();

    mostRecentMarker.setMap(null);
    $('#reminder-name').val('');
    var marker = placeMarker(name, new google.maps.LatLng(lat, lng), map);
    reminders[id++] = marker;
  });

  /* When the user presses cancel to stop adding a reminder, remove the marker
     generated from the map and hide the add reminders container. */
  $('#cancel').click(function() {
    mostRecentMarker.setMap(null);
    $('#add-reminder-container').hide();
  });

  $(".delete").click(removeRem);

  $(document).ready(function() {
    initialize();
  });
