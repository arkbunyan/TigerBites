import React, { useState } from "react";

const ReviewForm = ({ restaurantId, onReviewSubmitted }) => {
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const MAX_LEN = 500;
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      const response = await fetch(`/api/restaurants/${restaurantId}/reviews`, {
        method: "POST",
        credentials: "same-origin",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ rating, comment }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || `HTTP ${response.status}`);
      }

      const data = await response.json();
      setComment("");
      setRating(5);
      if (onReviewSubmitted) {
        onReviewSubmitted(data.review);
      }
    } catch (err) {
      console.error("Failed to submit review:", err);
      setError(err.message || "Failed to submit review");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="review-form card p-3 mb-4">
      <h4>Leave a Review</h4>
      <form onSubmit={handleSubmit}>
        <div className="mb-3">
          <label htmlFor="rating" className="form-label">
            Rating
          </label>
          <select
            id="rating"
            className="form-select"
            value={rating}
            onChange={(e) => setRating(parseInt(e.target.value))}
            required
          >
            <option value={5}>⭐⭐⭐⭐⭐ (5 - Excellent)</option>
            <option value={4}>⭐⭐⭐⭐ (4 - Very Good)</option>
            <option value={3}>⭐⭐⭐ (3 - Good)</option>
            <option value={2}>⭐⭐ (2 - Fair)</option>
            <option value={1}>⭐ (1 - Poor)</option>
          </select>
        </div>
        <div className="mb-3">
          <label htmlFor="comment" className="form-label">
            Comment
          </label>
          <textarea
            id="comment"
            className="form-control"
            rows="3"
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="Share your experience..."
            maxLength={MAX_LEN}
          />
          <div className="form-text text-end">{comment.length}/{MAX_LEN}</div>
        </div>
        {error && <div className="alert alert-danger">{error}</div>}
        <button
          type="submit"
          className="btn btn-primary"
          disabled={submitting}
        >
          {submitting ? "Submitting..." : "Submit Review"}
        </button>
      </form>
    </div>
  );
};

export default ReviewForm;
