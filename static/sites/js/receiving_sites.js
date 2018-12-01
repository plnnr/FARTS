mapboxgl.accessToken = "pk.eyJ1IjoibmtvYmVsIiwiYSI6ImNqbzF4M3Q4ODBnZHoza254dWplOGk5ZnAifQ.TKDCR6nbv268FBi68MSbiA";
const map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/nkobel/cjo4yz9ig02jm2spfbfo4ikno', // change for sending/receiving view
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



////// Receiving site-tailored functions
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


////// Receiving site-specific variables

let siteData = null;
let siteDetails = {
    'street_address': null,
    'site_size': null,
    'building_size': null,
    'site_far': null,
    'x_coord': null,
    'y_coord': null,
    'base_zones': null,
    'base_zone_classes': null,
    'districts': null,
    'target_far': null,
    'raw_data': null,
};



////// Event listeners
$addressField.on('keyup', function(event) {
    if(event.target.value === '') {
        $suggestions.addClass('hidden')
    } else {
        $suggestions.removeClass('hidden')
        styleDropdown()
        $(window).on('resize', styleDropdown)
    }
})







function getZoneClasses(baseZones) {

    let MDZCodes = ['RH', 'R1', 'R2', 'R3', 'RX', 'RMP', 'RM1', 'RM2', 'RM3', 'RM4'];
    let MUZCodes = ['CE', 'CM1', 'CM2', 'CM3', 'CR', 'CX'];

    let isMDZ = false;
    let isMUZ = false;

    let zoneClasses = [];
    baseZones.forEach(function(baseZone) {
        if ($.inArray(baseZone, MDZCodes) >= 0) {
            isMDZ = true;
            zoneClasses.push('MDZ');
        }
        if ($.inArray(baseZone, MUZCodes) >= 0) {
            isMUZ = true;
            zoneClasses.push('MUZ');
        }
    }); 

    let zoningObject = {
        'zoneClasses': zoneClasses,
        'isMDZ': isMDZ,
        'isMUZ': isMUZ,
    };

    return zoningObject;
}

function getReceivingEligibility(zoneClasses, isMDZ, isMUZ) {

    let eligibilityText = "Not eligible to receive transfer.";

    if (isMDZ === true | isMUZ === true) {
        eligibilityText = 'Eligible for ';
        if (zoneClasses.length > 1) {
            eligibilityText = eligibilityText + "MUZ and MDZ";
        }
        else if (isMUZ === true) {
            eligibilityText = eligibilityText + "MUZ";
        }
        else if (isMDZ === true) {
            eligibilityText = eligibilityText + "MDZ";
        }
    }

    return eligibilityText
}





function receivingSiteCleanup(data) {

    let baseZones = [];
    data.landuse.zoning.base.forEach(function(baseZone) {
        baseZones.push(baseZone.code);
    });

    let zoneObject = getZoneClasses(baseZones);
    let {zoneClasses, isMDZ, isMUZ} = zoneObject;
    // let zoneClasses = zoneObject.zoneClasses;
    // let isMUZ = zoneObject.isMUZ;
    // let isMDZ = zoneObject.isMDZ;
    let eligibilityText = getReceivingEligibility(zoneClasses, isMUZ, isMDZ)

    let baseZonesAndOverlays = [];
    data.landuse.zoning.base_overlay_combination.forEach(function(baseZoneOverlay) {
        baseZonesAndOverlays.push(baseZoneOverlay.code);
    });

    let overlays = [];
    data.landuse.zoning.overlay.forEach(function(overlay) {
        overlays.push(overlay.code)
    });

    let receivingSiteObject = {
        'baseZones': baseZones,
        'baseZonesAndOverlays': baseZonesAndOverlays,
        'overlays': overlays,
        'eligibilityText': eligibilityText,
        'zoneClasses': zoneClasses,
        'isMUZ': isMUZ,
        'isMDZ': isMDZ,
    }

    return receivingSiteObject
}



// good example: 735 SW ST CLAIR AVE
function renderSiteInfo(data, taxlotGeometry) {
    //console.log("data passed to renderSiteInfo():");
    console.log(data);
    console.log(taxlotGeometry);

    siteData = data;
    siteData.taxlotGeometry = taxlotGeometry

    let { baseZones, baseZonesAndOverlays, overlays, eligibilityText, zoneClasses, isMUZ, isMDZ} = receivingSiteCleanup(data);

    let siteSize = data.assessor.general.total_land_area_sqft;
    let bldgSize = data.property.summary.sqft;
    let siteFAR = bldgSize / siteSize;

    // console.log(overlays)

    $propertyDetails.text('');
    const $address = $('<div />'); // html and backslash create elements
    const $baseZonesAndOverlays = $('<div />');
    const $yCoord = $('<div />');
    const $xCoord = $('<div />');
    const $siteSize = $('<div />');
    const $bldgSize = $('<div />');
    const $siteFAR = $('<div />');
    const $siteEligibility = $('<div />').addClass('eligibility');

    
    $address.html("<strong>Address: </strong>" + addressQueryData.candidates[0].address);
    $baseZonesAndOverlays.html("<strong>Base + overlay zones: </strong>");
    $xCoord.html("<strong>X-coordinate: </strong>" + addressCandidate[1]);
    $yCoord.html("<strong>Y-coordinate: </strong>" + addressCandidate[0]);
    $siteSize.html("<strong>Site size: </strong>" + numberWithCommas(siteSize) + " sqft");
    $bldgSize.html("<strong>Building size: </strong>" + numberWithCommas(bldgSize) + " sqft");
    $siteFAR.html("<strong>Effective FAR: </strong>" + siteFAR.toFixed(2)); // add two decimal places
    $siteEligibility.html("<strong>Site eligibility: " + eligibilityText);

    baseZonesAndOverlays.forEach(function(baseZone, i) {
        if(i >= baseZonesAndOverlays.length - 1) {
            $baseZonesAndOverlays.append(baseZone);
        } else {
            $baseZonesAndOverlays.append(baseZone + ", ");
        }
    });

    $propertyDetails.append($address);
    $propertyDetails.append($baseZonesAndOverlays);
    $propertyDetails.append($xCoord);
    $propertyDetails.append($yCoord);
    $propertyDetails.append($siteSize);
    $propertyDetails.append($bldgSize);
    $propertyDetails.append($siteFAR);
    $propertyDetails.append($siteEligibility);
        //(createa  bunch of <li>s with the data I want to display)

    siteDetails.street_address = addressQueryData.candidates[0].address;
    siteDetails.site_size = siteSize;
    siteDetails.building_size = bldgSize;
    siteDetails.site_far = siteFAR;
    siteDetails.x_coord = addressCandidate[1];
    siteDetails.y_coord = addressCandidate[0];
    siteDetails.base_zones = baseZones;
    siteDetails.base_zone_classes = zoneClasses;
    siteDetails.districts = ''; // TO-DO: change later
    siteDetails.target_far = 200 ; // TO-DO: change later
    siteDetails.raw_data = siteData;

    console.log('site details object: ')
    console.log(siteDetails)
    
}

$confirmButton.on('click', function(event) {
    $.ajax({
        method: 'POST',
        url: '/sites/register/receiving-site/record_receiving_site',
        data: JSON.stringify(siteDetails),
        contentType : 'application/json',
    })
        .done(function(data) {
            console.log(data)
        });
});

function renderTaxlotBorder(data) {
    if (map.getLayer('taxlot')) {
        map.removeLayer('taxlot');
        map.removeSource('taxlot');
    }
    let wmRings = JSON.stringify(data.landuse.geometry.rings);
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

            let taxlotGeometry = mapboxSourceObject.data; // geojson object
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
    $.get('/sites/get_details?site_coords=' + `${selectedSiteCoords}`)
        .done(function(data) {
            console.log(data);
            renderTaxlotBorder(data);
    });
});

let addressQueryData = {};

$addressField.on('keydown', $.debounce(500, function(event) {
    const value = event.target.value; // same as $addressField.val()
    $.get('/sites/search?address_part=' + value)
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
//     $.get('/sites/get_details?site_coords=' + `${selectedSiteCoords}`)
//         .done(function(data) {
//             //console.log(data);
//             renderTaxlotBorder(data);
//         });
// });


//$coordSearchButton.on('click', function(event) {
//    query
//};
