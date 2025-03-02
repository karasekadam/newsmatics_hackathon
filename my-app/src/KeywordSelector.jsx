import React, { useState } from "react";
import "./KeywordSelector.css"; // You can define your custom styles in this file

const KeywordSelector = (props) => {
  const {keywords, selectedKeyword, setSelectedKeyword} = props;

  const handleChange = (event) => {
    setSelectedKeyword(event.target.value);
  };

  return (
    <div className="selector-container">
      <label htmlFor="keyword-selector">Select a keyword: </label>
      <select
        id="keyword-selector"
        value={selectedKeyword}
        onChange={handleChange}
        className="selector"
      >
        <option value="" disabled>
          Choose a keyword
        </option>
        {keywords.map((keyword, index) => (
          <option key={index} value={keyword}>
            {keyword}
          </option>
        ))}
      </select>
      <p>Selected Keyword: {selectedKeyword || "None"}</p>
    </div>
  );
};

export default KeywordSelector;