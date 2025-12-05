import React, { useEffect, useState } from "react";
import RestaurantDetails from "./backoffice_components/RestaurantDetails.jsx";
import ReviewForm from "./backoffice_components/ReviewForm.jsx";
import ReviewList from "./backoffice_components/ReviewList.jsx";
import { useParams } from "react-router-dom";
import MapComponent from "./backoffice_components/MapComponent.jsx";

const RestaurantPage = () => {
  const { restId } = useParams();
  const [restaurant, setRestaurant] = useState(null);
  const [menuItems, setMenuItems] = useState([]);
  const [reviews, setReviews] = useState([]);
  const [currentUsername, setCurrentUsername] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Fetch restaurant and menu
    fetch(`/api/restaurants/${restId}`, { credentials: "include" })
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => {
        setRestaurant(data.restaurant);
        setMenuItems(data.menu);
      })
      .catch((err) => {
        console.error(err);
        setError("Failed to load restaurant");
      });

    // Fetch reviews
    fetch(`/api/restaurants/${restId}/reviews`, { credentials: "include" })
      .then((res) => res.json())
      .then((data) => {
        if (data.reviews) {
          setReviews(data.reviews);
        }
      })
      .catch((err) => console.error("Failed to load reviews:", err));

    // Fetch current user
    fetch("/api/profile", { credentials: "include" })
      .then((res) => {
        if (res.ok) return res.json();
        return null;
      })
      .then((data) => {
        if (data) setCurrentUsername(data.username);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [restId]);

  const handleReviewSubmitted = (newReview) => {
    // Refresh reviews after submission
    fetch(`/api/restaurants/${restId}/reviews`, { credentials: "include" })
      .then((res) => res.json())
      .then((data) => {
        if (data.reviews) {
          setReviews(data.reviews);
        }
      })
      .catch((err) => console.error("Failed to reload reviews:", err));
  };

  const handleDeleteReview = (reviewId) => {
    setReviews(reviews.filter((r) => r.id !== reviewId));
  };

  if (loading) return <p>Loading restaurant...</p>;
  if (error) return <p>{error}</p>;

  return (
    <div>
      <RestaurantDetails restaurant={restaurant} menuItems={menuItems} />

      <div className="container mt-4">
        <hr />
        <ReviewList
          reviews={reviews}
          currentUsername={currentUsername}
          onDeleteReview={handleDeleteReview}
        />
        {restaurant && (
          <MapComponent
            latitude={restaurant.latitude}
            longitude={restaurant.longitude}
          />
        )}
      </div>
    </div>
  );
};

export default RestaurantPage;
