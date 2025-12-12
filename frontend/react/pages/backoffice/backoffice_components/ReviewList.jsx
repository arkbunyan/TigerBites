import React from "react";

const ReviewList = ({ reviews, currentUsername, onDeleteReview }) => {
  const handleDelete = async (reviewId) => {
    if (!window.confirm("Are you sure you want to delete this review?")) {
      return;
    }

    try {
      const response = await fetch(`/api/reviews/${reviewId}/admin_delete`, {
        method: "DELETE",
        credentials: "same-origin",
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      if (onDeleteReview) {
        onDeleteReview(reviewId);
      }
    } catch (err) {
      console.error("Failed to delete review:", err);
      alert("Failed to delete review");
    }
  };

  const renderStars = (rating) => {
    return "⭐".repeat(rating);
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  if (!reviews || reviews.length === 0) {
    return (
      <div className="alert alert-info">
        No reviews to display.
      </div>
    );
  }

  return (
    <div className="review-list">
      <h4 className="mb-3">Reviews ({reviews.length})</h4>
      {reviews.map((review) => (
        <div key={review.id} className="card mb-3">
          <div className="card-body">
            <div className="d-flex justify-content-between align-items-start">
              <div>
                <h5 className="card-title mb-1">
                  {review.fullname || review.firstname || review.username}
                </h5>
                <div className="text-warning mb-2">
                  {renderStars(review.rating)}
                </div>
              </div>
              <div className="text-end">
                <small className="text-muted">
                  {formatDate(review.created_at)}
                </small>
              {(
                  <button
                    className="btn btn-sm btn-outline-danger ms-2"
                    onClick={() => handleDelete(review.id)}
                  >
                    Delete
                  </button>
                )}
              </div>
            </div>
            {review.comment && <p className="card-text">{review.comment}</p>}
            {review.restaurant_name && (
              <small className="text-muted">
                Restaurant: {review.restaurant_name}
              </small>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

export default ReviewList;
