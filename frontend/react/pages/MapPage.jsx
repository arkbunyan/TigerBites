import React, { useEffect, useState } from "react";
import {
  APIProvider,
  Map,
  AdvancedMarker,
  InfoWindow,
  Pin,
} from "@vis.gl/react-google-maps";
import { Link } from "react-router-dom";

const MAP_CENTER = { lat: 40.352305, lng: -74.660695 };

const MapPage = () => {
  const [locations, setLocations] = useState([]);
  const [openMarkerId, setOpenMarkerId] = useState(null);
  const [userLocation, setUserLocation] = useState(null);
  const [mapCenter, setMapCenter] = useState(MAP_CENTER);
  const [locationError, setLocationError] = useState(null);

  // Request user's geolocation
  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords;
          const userPos = { lat: latitude, lng: longitude };
          setUserLocation(userPos);
          setMapCenter(userPos);
        },
        (error) => {
          console.warn("Geolocation error:", error.message);
          setLocationError(error.message);
          // Fall back to Princeton center
          setMapCenter(MAP_CENTER);
        }
      );
    }
  }, []);

  useEffect(() => {
    fetch("/api/map")
      .then((res) => res.json())
      .then((data) => {
        console.log("Fetched restaurants:", data.restaurants);
        setLocations(data.restaurants);
      })
      .catch((err) => console.error("Fetch error:", err));
  }, []);

  return (
    <APIProvider apiKey="AIzaSyAKMIFCaA4lMg03q7j_AevC-sHcJCv7RwA">
      <Map
        mapId={"c9b7d8a75795353dfa3de5fa"}
        defaultCenter={mapCenter}
        defaultZoom={15}
        style={{ width: "100%", height: "600px" }}
        onClick={() => setOpenMarkerId(null)}
      >
        {/* User's current location marker */}
        {userLocation && (
          <AdvancedMarker
            position={userLocation}
            title="Your location"
          >
            <Pin background="#4285F4" glyphColor="#fff" borderColor="#000" />
          </AdvancedMarker>
        )}

        {locations.map((loc) => (
          <React.Fragment key={loc.id}>
            <AdvancedMarker
              position={{
                lat: Number(loc.latitude),
                lng: Number(loc.longitude),
              }}
              onClick={() => setOpenMarkerId(loc.id)}
            >
              <Pin background="#FF5F0D" glyphColor="#fff" borderColor="#000" />
            </AdvancedMarker>

            {openMarkerId === loc.id && (
              <InfoWindow
                position={{
                  lat: Number(loc.latitude),
                  lng: Number(loc.longitude),
                }}
                onCloseClick={() => setOpenMarkerId(null)}
              >
                <div style={{ padding: "8px", maxWidth: "200px" }}>
                  <h3 style={{ margin: 0 }}>
                    <Link
                      to={`/restaurants/${loc.id}`}
                      className="text-decoration-none text-primary fw-bold"
                    >
                      {loc.name}
                    </Link>
                  </h3>
                  {loc.category && <p>Category: {loc.category}</p>}
                  {loc.avg_price && <p>Average price: ${loc.avg_price}</p>}
                </div>
              </InfoWindow>
            )}
          </React.Fragment>
        ))}
      </Map>
    </APIProvider>
  );
};

export default MapPage;
