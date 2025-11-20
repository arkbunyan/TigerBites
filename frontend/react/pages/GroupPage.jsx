import React from "react";

const GroupsPage = () => {
  return (
    <div className="container mt-4">
      <h2 className="mb-4">Your Groups</h2>

      <div className="mb-4">
        <button className="btn btn-primary">+ Create New Group</button>
      </div>

      <p className="text-muted fst-italic">
        You are not part of any groups yet.
      </p>
    </div>
  );
};

export default GroupsPage;
