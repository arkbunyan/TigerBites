import React, { useState } from "react";
import {
  APIProvider,
  Map,
  AdvancedMarker,
  InfoWindow,
  Pin,
} from "@vis.gl/react-google-maps";
import { Link } from "react-router-dom";

export default function MapComponent({ latitude, longitude }) {
  const [openMarkerId, setOpenMarkerId] = useState(null);

  const position = { lat: latitude, lng: longitude };
  const mapsKey = process.env.GOOGLE_MAPS_KEY;

  return (
    <APIProvider apiKey={mapsKey}>
      <div className="map">
        <h4 className="mb-3">Location</h4>
        <Map
          mapId={"TBMAPDETAILS"}
          defaultCenter={position}
          defaultZoom={18}
          style={{ width: "100%", height: "600px" }}
        >
          <AdvancedMarker
            position={position}
            onClick={() => setOpenMarkerId(true)}
          >
            <Pin background="#FF5F0D" glyphColor="#fff" borderColor="#000" />
          </AdvancedMarker>

          {openMarkerId && (
            <InfoWindow
              position={position}
              onCloseClick={() => setOpenMarkerId(false)}
            >
              <div style={{ padding: "8px", maxWidth: "200px" }}>
                <h3 style={{ margin: 0 }}>
                  <Link
                    to={`https://maps.google.com/?q=${latitude},${longitude}`}
                  >
                    View on Google Maps
                  </Link>
                </h3>
              </div>
            </InfoWindow>
          )}
        </Map>
      </div>
    </APIProvider>
  );
}
