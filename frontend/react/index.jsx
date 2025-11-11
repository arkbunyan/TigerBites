import React from "react";
import ReactDOM from "react-dom/client";

import "bootstrap/dist/css/bootstrap.min.css";
import App from "./App.jsx";

let domRoot = document.getElementById("root");
let reactRoot = ReactDOM.createRoot(domRoot);

reactRoot.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
