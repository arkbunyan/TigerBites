import React, { useState } from "react";

const SearchForm = ({ onSearch }) => {
  const [name, setName] = useState("");
  const [category, setCategory] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    onSearch({ name, category });
  };

  return (
    <form onSubmit={handleSubmit}>
      <table>
        <tbody>
          <tr>
            <td>Search:</td>
            <td>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                autoFocus
              />
            </td>
          </tr>
          <tr>
            <td>Category:</td>
            <td>
              <input
                type="text"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
              />
            </td>
          </tr>
        </tbody>
      </table>
      <button type="submit">Go</button>
    </form>
  );
};

export default SearchForm;
