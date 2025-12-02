import React, { useEffect } from "react";

const LogoutCasLandingPage = () => {
  useEffect(() => {
    // Redirect to CAS logout after a brief moment
    const timer = setTimeout(() => {
      window.location.replace("/logoutcas");
    }, 100);

    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="container mt-5">
      <div className="row justify-content-center">
        <div className="col-md-6">
          <div className="card shadow">
            <div className="card-body text-center p-5">
              <div className="mb-4">
                <div className="spinner-border text-primary" role="status" style={{ width: "3rem", height: "3rem" }}>
                  <span className="visually-hidden">Loading...</span>
                </div>
              </div>
              <h2 className="card-title mb-3">Logging Out of CAS</h2>
              <p className="card-text text-muted mb-4">
                Please wait while we log you out of CAS...
              </p>
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

export default LogoutCasLandingPage;
