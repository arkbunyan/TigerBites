import React, { useEffect, useState } from "react";
import {
  APIProvider,
  Map,
  AdvancedMarker,
  Pin,
} from "@vis.gl/react-google-maps";

export default function MapComponent({ latitude, longitude }) {
  const position = { lat: latitude, lng: longitude };
  return (
    <APIProvider apiKey="AIzaSyAKMIFCaA4lMg03q7j_AevC-sHcJCv7RwA">
      <div className="map">
        <h4 className="mb-3">Location</h4>
        <Map
          mapId={"TBMAPDETAILS"}
          defaultCenter={position}
          defaultZoom={18}
          style={{ width: "100%", height: "600px" }}
        >
          <AdvancedMarker position={position}>
            <Pin background="#FF5F0D" glyphColor="#fff" borderColor="#000" />
          </AdvancedMarker>
        </Map>
      </div>
    </APIProvider>
  );
}
