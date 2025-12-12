import React, { useEffect, useState } from "react";
import RestaurantDetails from "../components/RestaurantDetails.jsx";
import ReviewForm from "../components/ReviewForm.jsx";
import ReviewList from "../components/ReviewList.jsx";
import { useParams } from "react-router-dom";
import MapComponent from "../components/MapComponent.jsx";

const RestaurantPage = () => {
  const { restId } = useParams();
  const [restaurant, setRestaurant] = useState(null);
  const [menuItems, setMenuItems] = useState([]);
  const [reviews, setReviews] = useState([]);
  const [currentUsername, setCurrentUsername] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAdmin, setIsAdmin] = useState(false);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [correctionText, setCorrectionText] = useState("");

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
        if (data) {
          setCurrentUsername(data.username);
          setIsAdmin(!!data.admin_status);
        }
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

  const handleCorrectionSubmit = async (e) => {
      e.preventDefault();
      try {
        const response = await fetch(`/api/restaurants/${restId}/feedback`, {
          method: "POST",
          credentials: "include",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ restId: restId, response: correctionText}),
        });

        if (!response.ok) {
          const data = await response.json();
          throw new Error(data.error || `HTTP ${response.status}`);
        }
        
        console.log("Correction submitted:", correctionText);
        alert("Thank you for your correction! We will review it shortly.");
        setShowModal(false);
        setCorrectionText("");
      } catch (err) {
        console.error("Failed to submit correction:", err);
      } 
    };

  if (loading) return <p>Loading restaurant...</p>;
  if (error) return <p>{error}</p>;

  return (
    <div>
      <RestaurantDetails
        restaurant={restaurant}
        menuItems={menuItems}
        reviews={reviews}
      />

      <div className="container mt-4">
        <hr />
        <div className="d-flex mb-3">
          <button
            className="btn btn-primary"
            onClick={() => setShowModal(true)}
          >
            Submit a correction on details or menu!
          </button>
        </div>

        {currentUsername && (
          <ReviewForm
            restaurantId={restId}
            onReviewSubmitted={handleReviewSubmitted}
          />
        )}
        <ReviewList
          reviews={reviews}
          currentUsername={currentUsername}
          isAdmin={isAdmin}
          onDeleteReview={handleDeleteReview}
        />
        {restaurant && (
          <MapComponent
            latitude={restaurant.latitude}
            longitude={restaurant.longitude}
          />
        )}
      </div>
      {showModal && (
        <div
          className="modal"
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            width: "100%",
            height: "100%",
            backgroundColor: "rgba(0, 0, 0, 0.5)",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            zIndex: 1000,
          }}
        >
          <div
            className="modal-content"
            style={{
              backgroundColor: "white",
              padding: "20px",
              borderRadius: "8px",
              width: "800px",
              width: "600px",
              boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
            }}
          >
            <h5 className="mb-3">Submit a Correction</h5>
            <textarea
              className="form-control mb-3"
              rows="4"
              maxLength={500}
              placeholder="Enter your correction here..."
              value={correctionText}
              onChange={(e) => setCorrectionText(e.target.value)}
            />
            <div className="text-end text-muted small mb-2">
              {correctionText.length}/500
            </div>
            <div className="d-flex justify-content-end">
              <button
                className="btn btn-secondary me-2"
                onClick={() => setShowModal(false)}
              >
                Cancel
              </button>
              <button
                className="btn btn-primary"
                onClick={handleCorrectionSubmit}
              >
                Submit
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RestaurantPage;
