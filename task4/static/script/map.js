var map;

ymaps.ready(init);

const COMPANY_TYPE_PRESETS = {
    "SUPPLIER": '#ccf15aff',
    "COMPETITOR": '#ff0000',
    "CUSTOMER":  '#29ce13ff',
    "OTHER": '#000000ff',
}

function init() {
    map = new ymaps.Map("map", {
        center: [0, 0],
        zoom: 7
    });
    app_markers();
}

function add_GeoObject(coordinates, properties = {}, company_type="OTHER") {
    const color = COMPANY_TYPE_PRESETS[company_type] || '#000000ff';
    const marker = new ymaps.GeoObject({
        geometry: {
            type: "Point",
            coordinates: [coordinates[1], coordinates[0]]
        },
        properties: properties,
    }, {
        preset: "islands#circleDotIcon",
        iconColor: color,
        draggable: false,
    });
    if (marker) {
        map.geoObjects.add(marker);
    }
}

function app_markers() {
    const mapElement = document.getElementById('map');
    if(!mapElement) {
        console.error('Element map not found.');
        return;
    }
    const locations = JSON.parse(mapElement.getAttribute('data-locations'));
    if(!locations) {
        console.error('Element with data-locations attribute in map not found.');
        return;
    }
    locations.forEach(location => { 
        if (!location) {
            console.warn('Invalid coordinates:', locations);
            return;
        }
        location.COORDINATES.forEach(coordinates => { // since GeoCoder returns several addresses
            if (coordinates && coordinates.length === 2) {
                add_GeoObject(coordinates, {
                    balloonContent: location.TITLE || 'Локация без имени',
                    hintContent: location.ADDRESS || ''
                }, location.COMPANY_TYPE);
            } else {
                var warning = "location.COORDINATES doesnt't exist."
                if(coordinates) warning = "location.COORDINATES exists."
                console.warn('Invalid coordinates:', coordinates, "." , warning, "length is ", location.COORDINATES.length);
            }
        });
    });
    if (locations.length > 0) {
        if(!map.geoObjects) return;
        map.setBounds(map.geoObjects.getBounds(), {
            checkZoomRange: true,
            zoomMargin: 50
        });
    }
}