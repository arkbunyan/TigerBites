import { expectedError } from "@babel/core/lib/errors/rewrite-stack-trace";
import React, { useState, useEffect } from "react";

const RestaurantDetails = ({ restaurant, menuItems }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [editedRestaurant, setEditedRestaurant] = useState({
    name: "",
    category: "",
    hours: "",
    location: "",
    avg_price: "",
    yelp_rating: "",
    picture: ""
});
  const [editedMenu, setEditedMenu] = useState(menuItems || []);
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  
  useEffect(() => {
  if (restaurant) setEditedRestaurant(restaurant);
  if (menuItems) setEditedMenu(menuItems);
}, [restaurant, menuItems]);


  if (!restaurant)
    return <p className="text-center mt-4">No restaurant data provided.</p>;

  const handleRestaurantChange = (field, value) => {
    setEditedRestaurant((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleMenuChange = (index, field, value) => {
    const updatedMenu = [...editedMenu];
    updatedMenu[index][field] = value;
    setEditedMenu(updatedMenu);
  };

  // Enforce 3-digit positive integer for Avg Price (0–999)
  const handleAvgPriceChange = (value) => {
    // Strip non-digits
    let v = String(value).replace(/[^0-9]/g, "");
    // Limit to first 3 digits
    if (v.length > 3) v = v.slice(0, 3);
    // Normalize leading zeros (optional, keep as entered but numeric)
    const num = v === "" ? "" : String(Math.min(Number(v), 999));
    setEditedRestaurant((prev) => ({ ...prev, avg_price: num }));
  };

  // Allow typing a decimal gracefully (e.g., "4." or "4.5")
  const handleYelpRatingInputChange = (value) => {
    // Keep only digits and a single dot, allow partial inputs
    let s = String(value)
      .replace(/[^0-9.]/g, "")
      .replace(/\.(?=.*\.)/g, "");

    // Restrict to pattern: up to one digit before dot, and one after dot
    // but allow partial like "4." while typing
    const match = s.match(/^([0-5])?(\.([0-9])?)?$/);
    if (!match) {
      // If input exceeds bounds (e.g., first digit >5 or more decimals), ignore
      return;
    }

    setEditedRestaurant((prev) => ({ ...prev, yelp_rating: s }));
  };

  // On blur, normalize to clamped number between 0.0 and 5.0 with one decimal
  const handleYelpRatingBlur = (value) => {
    let s = String(value)
      .replace(/[^0-9.]/g, "")
      .replace(/\.(?=.*\.)/g, "");

    if (s === "") {
      setEditedRestaurant((prev) => ({ ...prev, yelp_rating: "" }));
      return;
    }

    let num = Number(s);
    if (isNaN(num)) num = 0;
    if (num < 0) num = 0;
    if (num > 5) num = 5;
    const fixed = num.toFixed(1);
    setEditedRestaurant((prev) => ({ ...prev, yelp_rating: fixed }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSaving
    try {
      const response = await fetch(`/api/restaurants/${restaurant.id}/update`, {
        method: "PUT",
        credentials: "same-origin",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ editedRestaurant }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || `HTTP ${response.status}`);
      }
      // Reset Save Status after 3 seconds
      setSaveSuccess(true)
      setTimeout(() => setSaveSuccess(false), 3000);
      const data = await response.json();
    } catch (err) {
      console.error("Failed to update restaurant:", err);
    }
    finally {
      setIsSaving(false)
    }
    };

  return (
    <div className="container my-5">
      <h2>  
        Edit {editedRestaurant.name}
      </h2>
        <div className="card shadow-sm border-0 mb-4">
          {editedRestaurant.picture && (
            <img
              src={editedRestaurant.picture}
              className="card-img-top"
              style={{
                height: "350px",
                width: "100%",
                borderTopLeftRadius: "12px",
                borderTopRightRadius: "12px",
                objectFit: "cover",
              }}
            />
          )}

          {saveSuccess && (
            <div className="alert alert-success text-center"
              style={{

              }}>
              Changes saved successfully
            </div>
          )}

          <button
            className="btn btn-primary mt-2"
            onClick={handleSubmit}
            disabled={isSaving}
          >
            {isSaving ? "Saving..." : "Save Changes"}
          </button>


          <div className="card-body">
            {/*NAME */}
            <strong>
              Name:
            </strong>
            <input
              className="form-control mb-2"
              maxLength={100}
              value={editedRestaurant.name || ""}
              onChange={(e) =>
                handleRestaurantChange("name", e.target.value)
              }
            />

            {/*CATEGORY*/}
            <strong>
              Category
            </strong>
            <input
              className="form-control mb-2"
              maxLength={100}
              value={editedRestaurant.category || ""}
              onChange={(e) =>
                handleRestaurantChange("category", e.target.value)
              }
            />

            {/*HOURS*/}
            <strong>
              Hours
            </strong>
            <input
              className="form-control mb-2"
              maxLength={100}
              value={editedRestaurant.hours || ""}
              onChange={(e) =>
                handleRestaurantChange("hours", e.target.value)
              }
            />

            {/*LOCATION*/}
            <strong>
              Location
            </strong>
            <input
              className="form-control mb-2"
              maxLength={100}
              value={editedRestaurant.location || ""}
              onChange={(e) =>
                handleRestaurantChange("location", e.target.value)
              }
            />

            {/*PRICE*/}
            <strong>
              Avg Price:
            </strong>
            <input
              type="number"
              className="form-control mb-2"
              inputMode="numeric"
              min={0}
              max={999}
              step={1}
              value={editedRestaurant.avg_price || ""}
              onChange={(e) => handleAvgPriceChange(e.target.value)}
              onBlur={(e) => handleAvgPriceChange(e.target.value)}
              title="Enter the new average price"
            />

            {/*YELP*/}
            Yelp Rating
            <input
              type="text"
              className="form-control"
              inputMode="decimal"
              value={editedRestaurant.yelp_rating || ""}
              onChange={(e) => handleYelpRatingInputChange(e.target.value)}
              onBlur={(e) => handleYelpRatingBlur(e.target.value)}
              placeholder="e.g., 4.5"
              title="Enter the new Yelp rating"
            />
          </div>
        </div>

        {/* MENU */}
        <div className="card shadow-sm border-0">
          <div className="card-body">
            <div
              onClick={() => setIsOpen(!isOpen)}
              className="d-flex justify-content-between align-items-center mb-3"
              style={{ cursor: "pointer" }}
            >
              <h3 className="card-title mb-0 text-dark">Menu</h3>
              <span
                style={{
                  fontSize: "1.2rem",
                  transition: "transform 0.2s ease",
                  transform: isOpen ? "rotate(180deg)" : "rotate(0deg)",
                }}
              >
                ▼
              </span>
            </div>

            {isOpen && (
              <>
                {editedMenu.length > 0 ? (
                  <div className="list-group">
                    {editedMenu.map((item, index) => (
                      <div
                        key={item.id || index}
                        className="list-group-item border-0 border-bottom py-3"
                      >
                        <input
                          className="form-control mb-1"
                          value={item.name}
                          onChange={(e) =>
                            handleMenuChange(index, "name", e.target.value)
                          }
                        />
                        <input
                          type="number"
                          className="form-control mb-1"
                          value={item.price || ""}
                          onChange={(e) =>
                            handleMenuChange(index, "price", e.target.value)
                          }
                        />
                        <input
                          className="form-control"
                          value={item.description || ""}
                          onChange={(e) =>
                            handleMenuChange(index, "description", e.target.value)
                          }
                        />
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-muted fst-italic">No menu yet.</p>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    );
};

export default RestaurantDetails;
