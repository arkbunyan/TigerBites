import React, { useEffect, useState } from "react";

const FeedbackList = ({ responses, currentUsername, onDeleteResponse }) => {
  const [restaurantNames, setRestaurantNames] = useState({});

  // Fetch a restaurant name
  const getRestaurantName = async (restaurantId) => {
    try {
      const res = await fetch(`/back_office/restaurants/${restaurantId}`, {
        method: "GET",
        credentials: "include",
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const data = await res.json();
      return data.restaurant.name;
    } catch (err) {
      console.error("Failed to fetch restaurant name:", err);
      return "";
    }
  };

  // Load restaurant names for all responses
  useEffect(() => {
    const loadNames = async () => {
      const names = {};

      for (const r of responses) {
        if (r.restaurant_id && !restaurantNames[r.restaurant_id]) {
          names[r.restaurant_id] = await getRestaurantName(r.restaurant_id);
        }
      }

      if (Object.keys(names).length > 0) {
        setRestaurantNames((prev) => ({ ...prev, ...names }));
      }
    };

    if (responses && responses.length > 0) {
      loadNames();
    }
  }, [responses]);

  // Delete handler
  const handleDelete = async (responseId) => {
    if (!window.confirm("Delete this feedback?")) return;

    try {
      const res = await fetch(`/api/feedback/${responseId}`, {
        method: "DELETE",
        credentials: "same-origin",
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      onDeleteResponse?.(responseId);
    } catch (err) {
      console.error("Failed to delete response:", err);
      alert("Failed to delete response");
    }
  };

  // Format date
  const formatDate = (dateString) =>
    new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });

  if (!responses || responses.length === 0) {
    return <div className="alert alert-info">No feedback found.</div>;
  }

  return (
    <div className="response-list">
      <h4 className="mb-3">Feedback ({responses.length})</h4>
      {responses.map((r) => (
        <div key={r.id} className="card mb-3">
          <div className="card-body">
            <div className="d-flex justify-content-between">
              <h5 className="card-title">{r.fullname || r.username}</h5>
              <small className="text-muted">{formatDate(r.created_at)}</small>
              <button
                className="btn btn-sm btn-outline-danger"
                onClick={() => handleDelete(r.id)}
              >
                Delete
              </button>
            </div>

            {r.response && <p>{r.response}</p>}

            {r.restaurant_id && (
              <small className="text-muted">
                Restaurant:{" "}
                {restaurantNames[r.restaurant_id] || "Loading..."}
              </small>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

export default FeedbackList;
