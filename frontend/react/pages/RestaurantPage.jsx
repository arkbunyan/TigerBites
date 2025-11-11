import React, { useEffect, useState } from "react";
import RestaurantDetails from "../components/RestaurantDetails.jsx";
import { useParams } from "react-router-dom";

const RestaurantPage = () => {
  const { restId } = useParams();
  const [restaurant, setRestaurant] = useState(null);
  const [menuItems, setMenuItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(`/api/restaurants/${restId}`, { credentials: "include" })
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => {
        setRestaurant(data.restaurant);
        setMenuItems(data.menu);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setError("Failed to load restaurant");
        setLoading(false);
      });
  }, [restId]);

  if (loading) return <p>Loading restaurant...</p>;
  if (error) return <p>{error}</p>;

  return <RestaurantDetails restaurant={restaurant} menuItems={menuItems} />;
};

export default RestaurantPage;
