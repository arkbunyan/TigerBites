import React, { useEffect, useState } from "react";
import UserProfile from "../components/UserProfile.jsx";

export default function ProfilePage() {
  const [user, setUser] = useState(null);
  const [favoriteCuisine, setFavoriteCuisine] = useState("");
  const [editingCuisine, setEditingCuisine] = useState(false);
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
          favoriteRestaurants: data.favoriteRestaurants || [],
        };
        setUser(simpleUser);
        setFavoriteCuisine(data.favorite_cuisine || "");
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to load profile:", err);
        setError("Failed to load profile");
        setLoading(false);
      });
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

  if (loading) return <p>Loading profile...</p>;
  if (error) return <p>{error}</p>;

  return (
    <div className="profile-page container py-3">
      <h1>Profile</h1>
      <UserProfile user={user} />

      <div
        className="favorite-cuisine-section mt-4 p-3 border rounded"
        style={{ backgroundColor: "#f8f9fa" }}
      >
        <h3>Favorite Cuisine</h3>
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
    </div>
  );
}
