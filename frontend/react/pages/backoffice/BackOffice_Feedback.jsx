import React, { useEffect, useState } from "react";
import FeedbackList from "./backoffice_components/FeedbackList.jsx";

const BackOffice_Feedback = () => {
  const [responses, setFeedback] = useState(null);
  
  useEffect(() => {
      fetch("/api/feedback")
        .then((res) => res.json())
        .then((data) => {
        if (data.responses) {
          setFeedback(data.responses);
        }
      });
    }, []);
   const onDeleteResponse = (responseId) => {  
        setFeedback(responses.filter((r) => r.id !== responseId));  
   };

    return (
    <div>
      <FeedbackList responses={responses} onDeleteResponse={onDeleteResponse}/> 
    </div>
  );

};

export default BackOffice_Feedback;