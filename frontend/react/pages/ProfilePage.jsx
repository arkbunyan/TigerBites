import React, { useEffect, useState } from "react";
import UserProfile from "../components/UserProfile.jsx";
import ReviewList from "../components/ReviewList.jsx";

export default function ProfilePage() {
  const [user, setUser] = useState(null);
  const [favoriteCuisine, setFavoriteCuisine] = useState([]);
  const [editingCuisine, setEditingCuisine] = useState(false);
  const [newCuisineInput, setNewCuisineInput] = useState("");
  const [allergies, setAllergies] = useState([]);
  const [editingAllergies, setEditingAllergies] = useState(false);
  const [newAllergyInput, setNewAllergyInput] = useState("");
  const [dietaryRestrictions, setDietaryRestrictions] = useState([]);
  const [editingDietaryRestrictions, setEditingDietaryRestrictions] =
    useState(false);
  const [newDietaryRestrictionInput, setNewDietaryRestrictionInput] =
    useState("");
  const [reviews, setReviews] = useState([]);
  const [currentUsername, setCurrentUsername] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  // Separate update messages per preference block
  const [cuisineMessage, setCuisineMessage] = useState("");
  const [allergyMessage, setAllergyMessage] = useState("");
  const [dietaryMessage, setDietaryMessage] = useState("");

  const commonCuisines = [
    "Italian",
    "Mexican",
    "Chinese",
    "Japanese",
    "Thai",
    "Indian",
    "American",
    "Mediterranean",
    "French",
    "Korean",
    "Vietnamese",
    "Greek",
    "Spanish",
    "Middle Eastern",
    "Soul Food",
    "BBQ",
  ];

  const commonAllergies = [
    "Peanuts",
    "Tree Nuts",
    "Milk",
    "Eggs",
    "Wheat",
    "Soy",
    "Fish",
    "Shellfish",
    "Sesame",
    "Gluten",
    "Lactose",
  ];

  const commonDietaryRestrictions = [
    "Vegetarian",
    "Vegan",
    "Gluten-Free",
    "Dairy-Free",
    "Nut-Free",
    "Pescatarian",
  ];

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
        setFavoriteCuisine(
          Array.isArray(data.favorite_cuisine) ? data.favorite_cuisine : []
        );
        setAllergies(Array.isArray(data.allergies) ? data.allergies : []);
        setDietaryRestrictions(
          Array.isArray(data.dietary_restrictions)
            ? data.dietary_restrictions
            : []
        );
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
      setFavoriteCuisine(
        Array.isArray(data.favorite_cuisine) ? data.favorite_cuisine : []
      );
      setEditingCuisine(false);
      setNewCuisineInput("");
      setCuisineMessage("Favorite cuisines updated!");
      setTimeout(() => setCuisineMessage(""), 3000);
    } catch (err) {
      console.error("Failed to update cuisines:", err);
      setCuisineMessage("Failed to update favorite cuisines");
      setTimeout(() => setCuisineMessage(""), 3000);
    }
  };

  const handleAddCuisine = () => {
    const trimmed = newCuisineInput.trim();
    if (trimmed && !favoriteCuisine.includes(trimmed)) {
      setFavoriteCuisine([...favoriteCuisine, trimmed]);
      setNewCuisineInput("");
    }
  };

  const handleSelectCommonCuisine = (cuisine) => {
    if (!favoriteCuisine.includes(cuisine)) {
      setFavoriteCuisine([...favoriteCuisine, cuisine]);
    }
  };

  const handleRemoveCuisine = (cuisineToRemove) => {
    setFavoriteCuisine(favoriteCuisine.filter((c) => c !== cuisineToRemove));
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleAddCuisine();
    }
  };

  const handleSaveAllergies = async () => {
    try {
      const response = await fetch("/api/profile", {
        method: "PUT",
        credentials: "same-origin",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ allergies: allergies }),
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      setAllergies(Array.isArray(data.allergies) ? data.allergies : []);
      setEditingAllergies(false);
      setNewAllergyInput("");
      setAllergyMessage("Allergies updated!");
      setTimeout(() => setAllergyMessage(""), 3000);
    } catch (err) {
      console.error("Failed to update allergies:", err);
      setAllergyMessage("Failed to update allergies");
      setTimeout(() => setAllergyMessage(""), 3000);
    }
  };

  const handleAddAllergy = () => {
    const trimmed = newAllergyInput.trim();
    if (trimmed && !allergies.includes(trimmed)) {
      setAllergies([...allergies, trimmed]);
      setNewAllergyInput("");
    }
  };

  const handleRemoveAllergy = (allergyToRemove) => {
    setAllergies(allergies.filter((a) => a !== allergyToRemove));
  };

  const handleSelectCommonAllergy = (allergy) => {
    if (!allergies.includes(allergy)) {
      setAllergies([...allergies, allergy]);
    }
  };

  const handleAllergyKeyPress = (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleAddAllergy();
    }
  };

  const handleSelectCommonDietaryRestriction = (restriction) => {
    if (!dietaryRestrictions.includes(restriction)) {
      setDietaryRestrictions([...dietaryRestrictions, restriction]);
    }
  };

  const handleDietaryRestrictionKeyPress = (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleAddDietaryRestriction();
    }
  };

  const handleAddDietaryRestriction = () => {
    const trimmed = newDietaryRestrictionInput.trim();
    if (trimmed && !dietaryRestrictions.includes(trimmed)) {
      setDietaryRestrictions([...dietaryRestrictions, trimmed]);
      setNewDietaryRestrictionInput("");
    }
  };

  const handleRemoveDietaryRestriction = (restrictionToRemove) => {
    setDietaryRestrictions(
      dietaryRestrictions.filter((r) => r !== restrictionToRemove)
    );
  };

  const handleSaveDietaryRestrictions = async () => {
    try {
      const response = await fetch("/api/profile", {
        method: "PUT",
        credentials: "same-origin",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ dietary_restrictions: dietaryRestrictions }),
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      setDietaryRestrictions(
        Array.isArray(data.dietary_restrictions)
          ? data.dietary_restrictions
          : []
      );
      setEditingDietaryRestrictions(false);
      setNewDietaryRestrictionInput("");
      setDietaryMessage("Dietary restrictions updated!");
      setTimeout(() => setDietaryMessage(""), 3000);
    } catch (err) {
      console.error("Failed to update dietary restrictions:", err);
      setDietaryMessage("Failed to update dietary restrictions");
      setTimeout(() => setDietaryMessage(""), 3000);
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
        <h3 className="mb-3">Favorite Cuisines</h3>
        {editingCuisine ? (
          <div>
            <div className="mb-3">
              {favoriteCuisine.length > 0 ? (
                <div className="d-flex flex-wrap gap-2 mb-2">
                  {favoriteCuisine.map((cuisine, index) => (
                    <span
                      key={index}
                      className="badge bg-secondary d-flex align-items-center"
                      style={{ fontSize: "0.9rem", padding: "0.5rem" }}
                    >
                      {cuisine}
                      <button
                        type="button"
                        className="btn-close btn-close-white ms-2"
                        style={{ fontSize: "0.6rem" }}
                        onClick={() => handleRemoveCuisine(cuisine)}
                        aria-label="Remove"
                      ></button>
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-muted fst-italic">
                  No cuisines selected yet.
                </p>
              )}
            </div>

            {/* Quick select from common cuisines */}
            <div className="mb-3">
              <label className="form-label small text-muted">
                Quick select:
              </label>
              <div className="d-flex flex-wrap gap-2">
                {commonCuisines
                  .filter((c) => !favoriteCuisine.includes(c))
                  .map((cuisine) => (
                    <button
                      key={cuisine}
                      type="button"
                      className="btn btn-sm btn-outline-secondary"
                      onClick={() => handleSelectCommonCuisine(cuisine)}
                    >
                      + {cuisine}
                    </button>
                  ))}
              </div>
            </div>

            {/* Custom input */}
            <div className="input-group mb-2">
              <input
                type="text"
                className="form-control"
                value={newCuisineInput}
                onChange={(e) => setNewCuisineInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Or type your own..."
              />
              <button
                className="btn btn-outline-secondary"
                onClick={handleAddCuisine}
              >
                Add
              </button>
            </div>
            <div className="d-flex gap-2">
              <button
                className="btn"
                style={{
                  backgroundColor: "#FF5F0D",
                  color: "white",
                }}
                onClick={handleSaveCuisine}
              >
                Save
              </button>
              <button
                className="btn btn-secondary"
                onClick={() => {
                  setEditingCuisine(false);
                  setNewCuisineInput("");
                  // Reset to original values from server
                  fetch("/api/profile", { credentials: "same-origin" })
                    .then((res) => res.json())
                    .then((data) => {
                      setFavoriteCuisine(
                        Array.isArray(data.favorite_cuisine)
                          ? data.favorite_cuisine
                          : []
                      );
                    });
                }}
              >
                Cancel
              </button>
            </div>
          </div>
        ) : (
          <div>
            {favoriteCuisine.length > 0 ? (
              <div className="d-flex flex-wrap gap-2 mb-3">
                {favoriteCuisine.map((cuisine, index) => (
                  <span
                    key={index}
                    className="badge"
                    style={{
                      backgroundColor: "#FF5F0D",
                      fontSize: "0.9rem",
                      padding: "0.5rem",
                    }}
                  >
                    {cuisine}
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-muted fst-italic">Not set</p>
            )}
            <button
              className="btn btn-sm"
              style={{ backgroundColor: "#FF5F0D", color: "white" }}
              onClick={() => setEditingCuisine(true)}
            >
              Edit
            </button>
          </div>
        )}
        {cuisineMessage && (
          <div className="alert alert-info mt-2" role="alert">
            {cuisineMessage}
          </div>
        )}
      </div>

      <div
        className="allergies-section mt-4 p-3 border rounded"
        style={{ backgroundColor: "#fff5f5" }}
      >
        <h3 className="mb-3">Allergies</h3>
        {editingAllergies ? (
          <div>
            <div className="mb-3">
              {allergies.length > 0 ? (
                <div className="d-flex flex-wrap gap-2 mb-2">
                  {allergies.map((allergy, index) => (
                    <span
                      key={index}
                      className="badge bg-danger d-flex align-items-center"
                      style={{ fontSize: "0.9rem", padding: "0.5rem" }}
                    >
                      {allergy}
                      <button
                        type="button"
                        className="btn-close btn-close-white ms-2"
                        style={{ fontSize: "0.6rem" }}
                        onClick={() => handleRemoveAllergy(allergy)}
                        aria-label="Remove"
                      ></button>
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-muted fst-italic">
                  No allergies specified yet.
                </p>
              )}
            </div>

            {/* Quick select from common allergies */}
            <div className="mb-3">
              <label className="form-label small text-muted">
                Quick select:
              </label>
              <div className="d-flex flex-wrap gap-2">
                {commonAllergies
                  .filter((a) => !allergies.includes(a))
                  .map((allergy) => (
                    <button
                      key={allergy}
                      type="button"
                      className="btn btn-sm btn-outline-danger"
                      onClick={() => handleSelectCommonAllergy(allergy)}
                    >
                      + {allergy}
                    </button>
                  ))}
              </div>
            </div>

            {/* Custom input */}
            <div className="input-group mb-2">
              <input
                type="text"
                className="form-control"
                value={newAllergyInput}
                onChange={(e) => setNewAllergyInput(e.target.value)}
                onKeyPress={handleAllergyKeyPress}
                placeholder="Or type your own..."
              />
              <button
                className="btn btn-outline-danger"
                onClick={handleAddAllergy}
              >
                Add
              </button>
            </div>
            <div className="d-flex gap-2">
              <button className="btn btn-danger" onClick={handleSaveAllergies}>
                Save
              </button>
              <button
                className="btn btn-secondary"
                onClick={() => {
                  setEditingAllergies(false);
                  setNewAllergyInput("");
                  // Reset to original values from server
                  fetch("/api/profile", { credentials: "same-origin" })
                    .then((res) => res.json())
                    .then((data) => {
                      setAllergies(
                        Array.isArray(data.allergies) ? data.allergies : []
                      );
                    });
                }}
              >
                Cancel
              </button>
            </div>
          </div>
        ) : (
          <div>
            {allergies.length > 0 ? (
              <div className="d-flex flex-wrap gap-2 mb-3">
                {allergies.map((allergy, index) => (
                  <span
                    key={index}
                    className="badge bg-danger"
                    style={{
                      fontSize: "0.9rem",
                      padding: "0.5rem",
                    }}
                  >
                    {allergy}
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-muted fst-italic">None specified</p>
            )}
            <button
              className="btn btn-sm btn-danger"
              onClick={() => setEditingAllergies(true)}
            >
              Edit
            </button>
          </div>
        )}
        {allergyMessage && (
          <div className="alert alert-info mt-2" role="alert">
            {allergyMessage}
          </div>
        )}
      </div>

      <div
        className="dietary-restrictions-section mt-4 p-3 border rounded"
        style={{ backgroundColor: "#f0f8ff" }}
      >
        <h3 className="mb-3">Dietary Restrictions</h3>
        {editingDietaryRestrictions ? (
          <div>
            <div className="mb-3">
              {dietaryRestrictions.length > 0 ? (
                <div className="d-flex flex-wrap gap-2 mb-2">
                  {dietaryRestrictions.map((restriction, index) => (
                    <span
                      key={index}
                      className="badge bg-info d-flex align-items-center"
                      style={{ fontSize: "0.9rem", padding: "0.5rem" }}
                    >
                      {restriction}
                      <button
                        type="button"
                        className="btn-close btn-close-black ms-2"
                        style={{ fontSize: "0.6rem" }}
                        onClick={() =>
                          handleRemoveDietaryRestriction(restriction)
                        }
                        aria-label="Remove"
                      ></button>
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-muted fst-italic">
                  No restrictions specified yet.
                </p>
              )}
            </div>

            {/* Quick select from common dietary restrictions */}
            <div className="mb-3">
              <label className="form-label small text-muted">
                Quick select:
              </label>
              <div className="d-flex flex-wrap gap-2">
                {commonDietaryRestrictions
                  .filter((r) => !dietaryRestrictions.includes(r))
                  .map((restriction) => (
                    <button
                      key={restriction}
                      type="button"
                      className="btn btn-sm btn-outline-info"
                      onClick={() =>
                        handleSelectCommonDietaryRestriction(restriction)
                      }
                    >
                      + {restriction}
                    </button>
                  ))}
              </div>
            </div>

            {/* Custom input */}
            <div className="input-group mb-2">
              <input
                type="text"
                className="form-control"
                value={newDietaryRestrictionInput}
                onChange={(e) => setNewDietaryRestrictionInput(e.target.value)}
                onKeyPress={handleDietaryRestrictionKeyPress}
                placeholder="Or type your own..."
              />
              <button
                className="btn btn-outline-info"
                onClick={handleAddDietaryRestriction}
              >
                Add
              </button>
            </div>
            <div className="d-flex gap-2">
              <button
                className="btn btn-info"
                onClick={handleSaveDietaryRestrictions}
              >
                Save
              </button>
              <button
                className="btn btn-secondary"
                onClick={() => {
                  setEditingDietaryRestrictions(false);
                  setNewDietaryRestrictionInput("");
                  // Reset to original values from server
                  fetch("/api/profile", { credentials: "same-origin" })
                    .then((res) => res.json())
                    .then((data) => {
                      setDietaryRestrictions(
                        Array.isArray(data.dietary_restrictions)
                          ? data.dietary_restrictions
                          : []
                      );
                    });
                }}
              >
                Cancel
              </button>
            </div>
          </div>
        ) : (
          <div>
            {dietaryRestrictions.length > 0 ? (
              <div className="d-flex flex-wrap gap-2 mb-3">
                {dietaryRestrictions.map((restriction, index) => (
                  <span
                    key={index}
                    className="badge bg-info"
                    style={{
                      fontSize: "0.9rem",
                      padding: "0.5rem",
                    }}
                  >
                    {restriction}
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-muted fst-italic">None specified</p>
            )}
            <button
              className="btn btn-sm btn-info"
              onClick={() => setEditingDietaryRestrictions(true)}
            >
              Edit
            </button>
          </div>
        )}
        {dietaryMessage && (
          <div className="alert alert-info mt-2" role="alert">
            {dietaryMessage}
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
