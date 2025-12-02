import React from "react";

const LogoutCasPage = () => {
  const handleReturnToTigerBites = (e) => {
    e.preventDefault();
    // Force a complete page reload to trigger CAS login
    window.location.replace("/");
  };

  return (
    <div className="container mt-5">
      <div className="row justify-content-center">
        <div className="col-md-6">
          <div className="card shadow">
            <div className="card-body text-center p-5">
              <div className="mb-4">
                <i className="bi bi-check-circle-fill text-success" style={{ fontSize: "4rem" }}></i>
              </div>
              <h2 className="card-title mb-3">Successfully Logged Out</h2>
              <p className="card-text text-muted mb-4">
                You have been logged out of both TigerBites and CAS.
              </p>
              <hr className="my-4" />
              <p className="text-muted mb-4">
                To access TigerBites again, you will need to log in with your Princeton credentials.
              </p>
              <button 
                onClick={handleReturnToTigerBites}
                className="btn btn-primary btn-lg"
              >
                <i className="bi bi-arrow-left-circle me-2"></i>
                Return to TigerBites
              </button>
              <div className="mt-4 pt-4 border-top">
                <small className="text-muted">
                  Created by the TigerBites Team
                </small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LogoutCasPage;
