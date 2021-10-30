// LEAFLET
var map = L.map('leaflet-map').setView([45.3, 5.883], 15);

var openTopoMap = L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
	maxZoom: 17,
	attribution: 'Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, <a href="http://viewfinderpanoramas.org">SRTM</a> | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a> (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)'
});

var Esri_WorldImagery = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
	attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
});

map.addLayer(openTopoMap);
map.addControl(new L.Control.Layers( {
    'OSM Topo': openTopoMap,
    'EsriWorldImagery': Esri_WorldImagery
    }, {})
);

jsonLayer = L.geoJson(igc_geojson, {
  style: {
    //color: '#ff0000',
    weight: 1,
    opacity: 1
  }
}).addTo(map);


var el = L.control.elevation();
el.addTo(map);
var gjl = L.geoJson(igc_geojson,{
    onEachFeature: el.addData.bind(el)
}).addTo(map);

map.fitBounds(jsonLayer.getBounds());


// CESIUM
function toggle3DMap() {
    $("#cesiumContainer").toggle();
    $("#toggleButton").toggle();

    Cesium.Ion.defaultAccessToken = cesium_key

45.3, 5.883
    var extent = Cesium.Rectangle.fromDegrees(5.8825, 45.25, 5.8835, 45.35);

    Cesium.Camera.DEFAULT_VIEW_RECTANGLE = extent;
    Cesium.Camera.DEFAULT_VIEW_FACTOR = 0;

    var terrainProvider = Cesium.createWorldTerrain();
    var viewer = new Cesium.Viewer('cesiumContainer', {
        terrainProvider: terrainProvider,
        shouldAnimate: true,
    });
    viewer.scene.globe.depthTestAgainstTerrain = true;

    /* update data : if a point is below ground, set it a little above ground level */
    var positions = [];
    for (var i = 0; i < igc_czml[1].position.cartographicDegrees.length / 4; i++){
        positions[i] = Cesium.Cartographic.fromDegrees(
                igc_czml[1].position.cartographicDegrees[(i*4)+1],
                igc_czml[1].position.cartographicDegrees[(i*4)+2]
        );
    }

    var promise = Cesium.sampleTerrainMostDetailed(terrainProvider, positions);
    Cesium.when(promise, function(updatedPositions) {
        // positions[0].height and positions[1].height have been updated.
        // updatedPositions is just a reference to positions.
        for (var i = 0; i < positions.length; i++) {
            /* update height only if below the terrain height received */
            if (igc_czml[1].position.cartographicDegrees[(i*4)+3] < positions[i].height) {
                igc_czml[1].position.cartographicDegrees[(i*4)+3] = positions[i].height + 5;
            }
        }

        var dataSource = Cesium.CzmlDataSource.load(igc_czml);

        /* now that we have clean data, add it to the viewer */
        viewer.dataSources.add(dataSource).then(function (ds) {
            viewer.trackedEntity = ds.entities.getById("path");
        });
    });

    // viewer.zoomTo(dataSource);

    // $(viewer._animation.container).css('visibility', 'hidden');
    // $(viewer._timeline.container).css('visibility', 'hidden');
    viewer.forceResize();
}

