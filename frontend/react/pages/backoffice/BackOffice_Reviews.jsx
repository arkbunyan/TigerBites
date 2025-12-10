import React, { useEffect, useState } from "react";
import ReviewList from "./backoffice_components/ReviewList.jsx";

const BackOffice_Reviews = () => {
  const [reviews, setReviews] = useState(null);
  
  useEffect(() => {
      fetch("/api/reviews")
        .then((res) => res.json())
        .then((data) => {
        if (data.reviews) {
          setReviews(data.reviews);
        }
      });
    }, []);

  const onDeleteReview = (reviewId) => {
  setReviews(reviews.filter((r) => r.id !== reviewId));
};

    return (
    <div>
      <ReviewList reviews={reviews} onDeleteReview={onDeleteReview} /> 
    </div>
  );

};

export default BackOffice_Reviews;