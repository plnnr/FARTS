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
    addressCandidateLngLat[0] = lngLat.lng;
    addressCandidateLngLat[1] = lngLat.lat;
    $xCoord.html("<strong>X-coordinate: </strong>" + addressCandidateLngLat[1])
    $yCoord.html("<strong>Y-coordinate: </strong>" + addressCandidateLngLat[0])
}

let marker = new mapboxgl.Marker({
    draggable: true 
})
    .setLngLat([-122.6598, 45.5337])
    .addTo(map);

marker.on('dragend', onDragEnd);

function styleDropdown() {
    $suggestions.css({
        left: $addressField.offset().left,
        top: $addressField.offset().top + $addressField.outerHeight(),
        width: $addressField.innerWidth() + 4
    })
}

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

/////// Modal jquery selectors and event listeners

const $modal = $('#modal-confirm-add');
const $span = $('.modal.close')

$confirmButton.on('click', function() {
    $modal.css({ display: "block" });
})

$span.on('click', function() {
    $modal.css({ display: "none" });
})

window.onclick = function(e) {
    if (e.target == $modal) {
        $modal.css({ display: "none" });
    }
}

////// Sending site-specific variables

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
    'transfer_purpose': null, // sending site only
    'transferrable_far': null, // sending site only
    'raw_data': null,
};

////// Sending site-tailored functions

function getSendingEligibility(zoneClasses, isMDZ, isMUZ, planDistrictCodes) {

    // let forbiddenDistrictCodes = ["CC", "CCSA"];

    let eligibilityObject = {
        'eligible': false,
        'eligibleZoneClasses': null,
        'eligibilityText': "Not eligible to send transfer.",
    };

    if (isMDZ === true | isMUZ === true) {

        if (zoneClasses.length > 1) {
            eligibilityObject.eligible = true;
            eligibilityObject.eligibilityText = "Eligible to send to mixed-use zones and multi-dwelling zones.";
            eligibilityObject.eligibleZoneClasses = ['MUZ', 'MDZ'];
        }
        else if (isMUZ === true) {
            eligibilityObject.eligible = true;
            eligibilityObject.eligibilityText = "Eligible to send to mixed-use zones.";
            eligibilityObject.eligibleZoneClasses = ['MUZ'];
        }
        else if (isMDZ === true) {
            eligibilityObject.eligible = true;
            eligibilityObject.eligibilityText = "Eligible to send to multi-dwelling zones.";
            eligibilityObject.eligibleZoneClasses = ['MDZ'];
        }

        /////// Only valid for receiving sites.
        // planDistrictCodes.forEach(function(code) {
        //     if ($.inArray(code, forbiddenDistrictCodes) >= 0) {
        //         eligibilityObject.isEligible = false;
        //         eligibilityObject.eligibilityText = "Not eligible to receive transfer.";
        //         eligibilityObject.eligibleZoneClasses = null;
        //     }
        // });
    }

    return eligibilityObject
}

function sendingSiteCleanup(data) {

    let baseZones = [];
    data.landuse.zoning.base.forEach(function(baseZone) {
        baseZones.push(baseZone.code);
    });

    let overlays = [];
    data.landuse.zoning.overlay.forEach(function(overlay) {
        overlays.push(overlay.code)
    });

    let planDistrictCodes = [];
    data.landuse.zoning.plan_district.forEach(function(district) {
        planDistrictCodes.push(district.code)
    });

    let baseZonesAndOverlays = [];
    data.landuse.zoning.base_overlay_combination.forEach(function(baseZoneOverlay) {
        baseZonesAndOverlays.push(baseZoneOverlay.code);
    });

    let zoneObject = getZoneClasses(baseZones);
    let {zoneClasses, isMDZ, isMUZ} = zoneObject;
    let {eligible, eligibleZoneClasses, eligibilityText} = getSendingEligibility(zoneClasses, isMDZ, isMUZ, planDistrictCodes);

    let sendingSiteObject = {
        'baseZones': baseZones,
        'baseZonesAndOverlays': baseZonesAndOverlays,
        'planDistrictCodes': planDistrictCodes,
        'overlays': overlays,
        'eligible': eligible,
        'eligibleZoneClasses': eligibleZoneClasses,
        'eligibilityText': eligibilityText,
        'zoneClasses': zoneClasses,
        'isMUZ': isMUZ,
        'isMDZ': isMDZ,
    }

    return sendingSiteObject
}

function renderSiteInfo(data, taxlotGeometry) {
    // good example: 735 SW ST CLAIR AVE
    //console.log("data passed to renderSiteInfo():");
    console.log(data);
    console.log(taxlotGeometry);

    siteData = data;
    siteData.taxlotGeometry = taxlotGeometry

    let { baseZones, baseZonesAndOverlays, planDistrictCodes, overlays, eligible, 
        eligibleZoneClasses, eligibilityText, zoneClasses, isMUZ, isMDZ
    } = sendingSiteCleanup(data);

    let siteAddress = data.property.summary.site_address_full;
    let siteSize = data.assessor.general.total_land_area_sqft;
    let bldgSize = data.property.summary.sqft;
    let siteFAR = bldgSize / siteSize;

    // console.log(overlays)

    $propertyDetails.text('');
    const $address = $('<div />').addClass('site-address'); // html and backslash create elements
    const $baseZonesAndOverlays = $('<div />');
    const $yCoord = $('<div />');
    const $xCoord = $('<div />');
    const $siteSize = $('<div />');
    const $bldgSize = $('<div />');
    const $siteFAR = $('<div />');
    const $siteEligibility = $('<div />').addClass('eligibility');
    const $maxFARToTransfer = $('<div />').addClass('max-far');

    
    $address.html(siteAddress + "<br />");
    $baseZonesAndOverlays.html("<strong>Base + overlay zones: </strong>");
    $xCoord.html("<strong>X-coordinate: </strong>" + addressCandidateLngLat[1]);
    $yCoord.html("<strong>Y-coordinate: </strong>" + addressCandidateLngLat[0]);
    $siteSize.html("<strong>Site size: </strong>" + numberWithCommas(siteSize) + " sqft");
    $bldgSize.html("<strong>Building size: </strong>" + numberWithCommas(bldgSize) + " sqft");
    $siteFAR.html("<strong>Effective FAR: </strong>" + siteFAR.toFixed(2) + "<br />"); // add two decimal places
    $siteEligibility.html("<strong>Site eligibility: </strong>" + eligibilityText + "<br />");
    $maxFARToTransfer.html("<strong>Maximum transferrable area: </strong>" + numberWithCommas(siteSize) + " sqft");

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
    $propertyDetails.append($maxFARToTransfer);
    
    siteDetails.street_address = addressQueryData.candidates[0].address;
    siteDetails.site_size = siteSize;
    siteDetails.building_size = bldgSize;
    siteDetails.site_far = siteFAR;
    siteDetails.x_coord = addressCandidateLngLat[1];
    siteDetails.y_coord = addressCandidateLngLat[0];
    siteDetails.base_zones = baseZones;
    siteDetails.base_zone_classes = zoneClasses;
    siteDetails.districts = ''; // TO-DO: change later
    siteDetails.transferrable_far = 800 ; // TO-DO: change later
    // siteDetails.transfer_purpose = 1; // TO-DO: change later (also, corresponds to choice code)
    siteDetails.raw_data = siteData;

    console.log('site details object: ')
    console.log(siteDetails)
}


////// Event listeners
let addressQueryData = {};

$addressField.on('keydown', $.debounce(500, function(event) {
    const value = event.target.value; // same as $addressField.val()
    $.get('/sites/search?address_part=' + value)
        .done(function(data) {
            // //console.log(data);
            // lat = data.candidates[0].attributes.lat;
            // lng = data.candidates[0].attributes.lon;
            // wmlat = data.candidates[0].location.y;
            // wmlng = data.candidates[0].location.x;
            // //console.log(lng, lat);
            // //console.log(wmlng, wmlat);
            renderSuggestions(data);
            // addressCandidateLngLat = [lng, lat];
            // selectedSiteCoords = [wmlng, wmlat];
            addressQueryData = data;
            console.log(addressQueryData);
        });
}));

let addressCandidateLngLat = [];
let selectedSiteCoords = [];
function renderSuggestions(data) {
    $suggestions.html(''); // set HTML to be nothing for already-created element
    data.candidates.forEach(function(candidate) {
        console.log(candidate.address)
        const $li = $('<li />'); // html and backslash create elements
        $li.text(candidate.address);
        $li.on('click', function() {
            $propertyDetails.text('');
            $('html, body').animate({
                scrollTop: $("#step-2").offset().top-$(".top-bar").height()*1.5
            }, 300);

            let lat = candidate.attributes.lat;
            let lng = candidate.attributes.lon;
            let wmlat = candidate.location.y;
            let wmlng = candidate.location.x;

            //renderSuggestions(data);

            addressCandidateLngLat = [lng, lat];
            selectedSiteCoords = [wmlng, wmlat];

            $addressField.val(candidate.address);
            marker.setLngLat(addressCandidateLngLat)
                .addTo(map);
            map.flyTo({ 
                center: addressCandidateLngLat,
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

$addressButton.on('click', function(event) {
    console.log($addressField.val())
    marker.setLngLat(addressCandidateLngLat)
            .addTo(map);
    map.flyTo({ 
        center: addressCandidateLngLat,
        zoom: 18,
    });
    $suggestions.html('');
    $.get('/sites/get_details?site_coords=' + `${selectedSiteCoords}`)
        .done(function(data) {
            console.log(data);
            renderTaxlotBorder(data);
    });
});

// Hide/unhide address suggestions
$addressField.on('keyup', function(event) {
    if(event.target.value === '') {
        $suggestions.addClass('hidden')
    } else {
        $suggestions.removeClass('hidden')
        styleDropdown()
        $(window).on('resize', styleDropdown)
    }
})

$confirmButton.on('click', function(event) {
    siteDetails.transfer_purpose = $('#transfer-purpose').val()
    $.ajax({
        method: 'POST',
        url: '/sites/register/sending-site/record_sending_site',
        data: JSON.stringify(siteDetails),
        contentType : 'application/json',
    })
        .done(function(data) {
            console.log(data)
        });
});
