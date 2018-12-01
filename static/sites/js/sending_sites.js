mapboxgl.accessToken = "pk.eyJ1IjoibmtvYmVsIiwiYSI6ImNqbzF4M3Q4ODBnZHoza254dWplOGk5ZnAifQ.TKDCR6nbv268FBi68MSbiA";
const map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/nkobel/cjp4w486b18fr2snyjbymbh0g', 
    center: [-122.6598, 45.5337],
    zoom: 10.3
});

const coordinates = document.getElementById('coordinates');

const $addressField = $('#address-part');
const $addressButton = $('#address-search');
const $suggestions = $('#suggestions');
const $noAddressButton = $('#no-site-address');
const $coordSearchButton = $('#submit-coords');
const $propertyDetails = $('#property-details');
const $confirmButton = $('#confirm-button');

///////// Utility functions /////////

function numberWithCommas(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function buildQueryParams(params) {
    let paramString = "?"
    for(key in params) {
        paramString += `${key}=${params[key]}&`
    }
    return paramString//.slice(0, paramString.length - 1)
}

function onDragEnd() {
    // Search for parcel details based on lat-long
    let lngLat = marker.getLngLat();
    //coordinates.style.display = 'block';
    //coordinates.innerHTML = 'Longitude: ' + lngLat.lng + '<br />Latitude: ' + lngLat.lat;
    addressCandidate[0] = lngLat.lng;
    addressCandidate[1] = lngLat.lat;

    // TO-DO: Fix rendering to page. Perhaps put the content in another div with class='coordinates'
    // and query the class, and then change the inner html of each element.
    $xCoord.html("<strong>X-coordinate: </strong>" + addressCandidate[1])
    $yCoord.html("<strong>Y-coordinate: </strong>" + addressCandidate[0])
}

function styleDropdown() {
    $suggestions.css({
        left: $addressField.offset().left,
        top: $addressField.offset().top + $addressField.outerHeight(),
        width: $addressField.innerWidth() + 4
    })
}

let marker = new mapboxgl.Marker({
    draggable: true 
})
    .setLngLat([-122.6598, 45.5337])
    .addTo(map);

marker.on('dragend', onDragEnd);


$addressField.on('keyup', function(event) {
    if(event.target.value === '') {
        $suggestions.addClass('hidden')
    } else {
        $suggestions.removeClass('hidden')
        styleDropdown()
        $(window).on('resize', styleDropdown)
    }
})





////// Sending site-tailored functions
let addressCandidate = [];
let selectedSiteCoords = [];
function renderSuggestions(data) {
    $suggestions.html(''); // set HTML to be nothing for already-created element
    data.candidates.forEach(function(candidate) {
        console.log(candidate.address)
        const $li = $('<li />'); // html and backslash create elements
        $li.text(candidate.address);
        $li.on('click', function() {
            $('html, body').animate({
                scrollTop: $("#step-2").offset().top-$(".top-bar").height()*1.5
            }, 300);
            $addressField.val(candidate.address);
            marker.setLngLat(addressCandidate)
                .addTo(map);
            map.flyTo({ 
                center: addressCandidate,
                zoom: 18,
            });
            $suggestions.html('');
            $.get('/sites/get_details?site_coords=' + `${selectedSiteCoords}`)
                .done(function(data) {
                    // console.log(data);
                    renderTaxlotBorder(data);
            });
        });
        $suggestions.append($li);
    });
}