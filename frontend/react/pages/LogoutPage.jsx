import React from "react";

const LogoutPage = () => {
  const handleReturnToTigerBites = (e) => {
    e.preventDefault();
    // Force a complete page reload to trigger re-authentication
    window.location.replace("/");
  };

  return (
    <div className="container mt-5">
      <div className="row justify-content-center">
        <div className="col-md-6">
          <div className="card shadow">
            <div className="card-body text-center p-5">
              <div className="mb-4">
                <i className="bi bi-box-arrow-right text-warning" style={{ fontSize: "4rem" }}></i>
              </div>
              <h2 className="card-title mb-3">Logged Out of TigerBites</h2>
              <p className="card-text text-muted mb-4">
                You have been logged out of the TigerBites application, but you are still logged into CAS.
              </p>
              <hr className="my-4" />
              <p className="text-muted mb-4">
                You can revisit TigerBites or log out of CAS completely.
              </p>
              <div className="d-grid gap-2">
                <button 
                  onClick={handleReturnToTigerBites}
                  className="btn btn-primary btn-lg"
                >
                  <i className="bi bi-arrow-left-circle me-2"></i>
                  Return to TigerBites
                </button>
                <a href="/logout_cas_landing" className="btn btn-outline-secondary">
                  <i className="bi bi-shield-lock me-2"></i>
                  Logout of CAS
                </a>
              </div>
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

export default LogoutPage;
