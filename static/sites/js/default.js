mapboxgl.accessToken = "pk.eyJ1IjoibmtvYmVsIiwiYSI6ImNqbzF4M3Q4ODBnZHoza254dWplOGk5ZnAifQ.TKDCR6nbv268FBi68MSbiA";
let coordinates = document.getElementById('coordinates');
const map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/nkobel/cjo4yz9ig02jm2spfbfo4ikno', // change for sending/receiving view
    center: [-122.6598, 45.5337],
    zoom: 10.3
});

let marker = new mapboxgl.Marker({
    draggable: true 
})
    .setLngLat([-122.6598, 45.5337])
    .addTo(map);

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

marker.on('dragend', onDragEnd);

const $addressField = $('#address-part');
const $addressButton = $('#address-search');
const $suggestions = $('#suggestions');
const $noAddressButton = $('#no-site-address');
const $coordSearchButton = $('#submit-coords');
const $propertyDetails = $('#property-details');

let addressCandidate = [];
let selectedSiteCoords = [];

function styleDropdown() {
    $suggestions.css({
        left: $addressField.offset().left,
        top: $addressField.offset().top + $addressField.outerHeight(),
        width: $addressField.innerWidth() + 4
    })
}

$addressField.on('keyup', function(event) {
    if(event.target.value === '') {
        $suggestions.addClass('hidden')
    } else {
        $suggestions.removeClass('hidden')
        styleDropdown()
        $(window).on('resize', styleDropdown)
    }
})

function zoomToBorder(data) {}

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
            $.get('/get_details?site_coords=' + `${selectedSiteCoords}`)
                .done(function(data) {
                    //console.log(data);
                    renderTaxlotBorder(data);
            });
        });
        $suggestions.append($li);
    });
}

function buildQueryParams(params) {
    let paramString = "?"
    for(key in params) {
        paramString += `${key}=${params[key]}&`
    }
    return paramString//.slice(0, paramString.length - 1)
}

// 735 SW ST CLAIR AVE
function renderSiteInfo(data, taxlotGeometry) {
    //console.log("data passed to renderSiteInfo():");
    console.log(data);
    console.log(taxlotGeometry);
    let MDZCodes = ['RH', 'R1', 'R2', 'R3', 'RX', 'RMP', 'RM1', 'RM2', 'RM3'];
    let MUZCodes = ['CE', 'CM1', 'CM2', 'CM3', 'CR', 'CX'];
    let isMDZ = false;
    let isMUZ = false;

    let baseZones = [];
    data.zoning.base.forEach(function(baseZone) {
        baseZones.push(baseZone.code);
    });
    
    baseZones.forEach(function(baseZone) {
        if (baseZone in MDZCodes) {
            isMDZ = true;
        }
        if (baseZone in MUZCodes) {
            isMUZ = true;
        }
    });
    

    let overlays = [];
    for (i=0; i<data.zoning.overlay.length; i++) {
        overlays.push([i].code)
    }

    $propertyDetails.text('');
    const $address = $('<div />'); // html and backslash create elements
    const $baseZones = $('<div />');
    const $yCoord = $('<div />');
    const $xCoord = $('<div />');
    
    $address.html("<strong>Site address: </strong>" + addressQueryData.candidates[0].address);
    $baseZones.html("<strong>Base zones: </strong>");
    $xCoord.html("<strong>X-coordinate: </strong>" + addressCandidate[1])
    $yCoord.html("<strong>Y-coordinate: </strong>" + addressCandidate[0])

    baseZones.forEach(function(baseZone, i) {
        if(i >= baseZones.length - 1) {
            $baseZones.append(baseZone);
        } else {
            $baseZones.append(baseZone + ", ");
        }
    });

    $propertyDetails.append($address);
    $propertyDetails.append($baseZones);
    $propertyDetails.append($xCoord);
    $propertyDetails.append($yCoord);
        //(createa  bunch of <li>s with the data I want to display)

    
}

function renderTaxlotBorder(data) {
    if (map.getLayer('taxlot')) {
        map.removeLayer('taxlot');
        map.removeSource('taxlot');
    }
    let wmRings = JSON.stringify(data.geometry.rings);
    let baseURL = "https://www.portlandmaps.com/arcgis/rest/services/Utilities/Geometry/GeometryServer/project";
    let params = {
        inSR: 3857,
        outSR: 4326,
        f: 'pjson',
        geometries: `{"geometryType":"esriGeometryPolygon","geometries":[{"rings":${wmRings},}]}`,
    };
    let paramString = buildQueryParams(params);
    let fetchURL = baseURL + paramString;
    //console.log(fetchURL)
    

    $.get(fetchURL)
        .done(function(geometryData) {
            geometryData = JSON.parse(geometryData);
            let rings = geometryData.geometries[0].rings;
            let mapboxSourceObject = {
                'type':'geojson',
                'data': {
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Polygon',
                        'coordinates': rings
                        }
                    }
                };
            // adjust styling: https://www.mapbox.com/mapbox-gl-js/style-spec/#layers
            let taxlotLayer = { 
                'id': 'taxlot',
                'type': 'line',
                'source': mapboxSourceObject,
                'layout': {},
                'paint': {
                    'line-color': '#00dff0',
                    'line-width': 4
                }
            }; 

            map.addLayer(taxlotLayer);

            let taxlotGeometry = mapboxSourceObject.data;
            renderSiteInfo(data, taxlotGeometry);
        });
}

$addressButton.on('click', function(event) {
    marker.setLngLat(addressCandidate)
            .addTo(map);
        map.flyTo({ 
            center: addressCandidate,
            zoom: 18,
        });
        $suggestions.html('');
        $.get('/get_details?site_coords=' + `${selectedSiteCoords}`)
            .done(function(data) {
                //console.log(data);
                renderTaxlotBorder(data);
        });
});

let addressQueryData = {};

$addressField.on('keydown', $.debounce(500, function(event) {
    const value = event.target.value; // same as $addressField.val()
    $.get('/search?address_part=' + value)
        .done(function(data) {
            //console.log(data);
            lat = data.candidates[0].attributes.lat;
            lng = data.candidates[0].attributes.lon;
            wmlat = data.candidates[0].location.y;
            wmlng = data.candidates[0].location.x;
            //console.log(lng, lat);
            //console.log(wmlng, wmlat);
            renderSuggestions(data);
            addressCandidate = [lng, lat];
            selectedSiteCoords = [wmlng, wmlat];
            addressQueryData = data;
            console.log(addressQueryData);
        });
}));

// $coordSearchButton.on('click', function(event) {
//     //const value = $addressField.val();
//     $.get('/get_details?site_coords=' + `${selectedSiteCoords}`)
//         .done(function(data) {
//             //console.log(data);
//             renderTaxlotBorder(data);
//         });
// });


//$coordSearchButton.on('click', function(event) {
//    query
//};
