import React, { useEffect, useState } from "react";
import UserProfile from "../components/UserProfile.jsx";
import ReviewList from "../components/ReviewList.jsx";

export default function ProfilePage() {
  const [user, setUser] = useState(null);
  const [favoriteCuisine, setFavoriteCuisine] = useState("");
  const [editingCuisine, setEditingCuisine] = useState(false);
  const [reviews, setReviews] = useState([]);
  const [currentUsername, setCurrentUsername] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [updateMessage, setUpdateMessage] = useState("");

  useEffect(() => {
    // Fetch user profile data from the API
    fetch("/api/profile", { credentials: "same-origin" })
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => {
        // Map backend response to the simple shape expected by UserProfile
        const simpleUser = {
          name: data.fullname || data.firstname || data.username || "",
          email: data.email || "",
        };
        setUser(simpleUser);
        setCurrentUsername(data.username);
        setFavoriteCuisine(data.favorite_cuisine || "");
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to load profile:", err);
        setError("Failed to load profile");
        setLoading(false);
      });

    // Fetch user's reviews
    fetch("/api/users/reviews", { credentials: "same-origin" })
      .then((res) => {
        if (res.ok) return res.json();
        return null;
      })
      .then((data) => {
        if (data && data.reviews) {
          setReviews(data.reviews);
        }
      })
      .catch((err) => console.error("Failed to load reviews:", err));
  }, []);

  const handleSaveCuisine = async () => {
    try {
      const response = await fetch("/api/profile", {
        method: "PUT",
        credentials: "same-origin",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ favorite_cuisine: favoriteCuisine }),
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      setFavoriteCuisine(data.favorite_cuisine);
      setEditingCuisine(false);
      setUpdateMessage("Favorite cuisine updated!");
      setTimeout(() => setUpdateMessage(""), 3000);
    } catch (err) {
      console.error("Failed to update cuisine:", err);
      setUpdateMessage("Failed to update favorite cuisine");
      setTimeout(() => setUpdateMessage(""), 3000);
    }
  };

  const handleDeleteReview = (reviewId) => {
    setReviews(reviews.filter((r) => r.id !== reviewId));
  };

  if (loading) return <p>Loading profile...</p>;
  if (error) return <p>{error}</p>;

  return (
    <div className="profile-page container py-3">
      <h1 className="mb-4 fw-bold border-bottom pb-2">Profile</h1>
      <UserProfile user={user} />

      <div
        className="favorite-cuisine-section mt-4 p-3 border rounded"
        style={{ backgroundColor: "#f8f9fa" }}
      >
        <h3 className="mb-3">Favorite Cuisine</h3>
        {editingCuisine ? (
          <div className="input-group mb-2">
            <input
              type="text"
              className="form-control"
              value={favoriteCuisine}
              onChange={(e) => setFavoriteCuisine(e.target.value)}
              placeholder="e.g., Italian, Mexican, Asian..."
            />
            <button
              className="btn"
              style={{
                backgroundColor: "#FF5F0D",
              }}
              onClick={handleSaveCuisine}
            >
              Save
            </button>
            <button
              className="btn btn-secondary"
              onClick={() => setEditingCuisine(false)}
            >
              Cancel
            </button>
          </div>
        ) : (
          <div>
            <p>
              <strong>{favoriteCuisine || "Not set"}</strong>
            </p>
            <button
              className="btn btn-sm"
              style={{ backgroundColor: "#FF5F0D" }}
              onClick={() => setEditingCuisine(true)}
            >
              Edit
            </button>
          </div>
        )}
        {updateMessage && (
          <div className="alert alert-info mt-2" role="alert">
            {updateMessage}
          </div>
        )}
      </div>

      <div className="my-reviews-section mt-4">
        <h3>My Reviews</h3>
        <ReviewList
          reviews={reviews}
          currentUsername={currentUsername}
          onDeleteReview={handleDeleteReview}
        />
      </div>
    </div>
  );
}
