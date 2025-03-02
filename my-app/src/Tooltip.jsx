import React from "react";
import "./Tooltip.css";

function Tooltip(props) {
  const { x, y, data, data_key } = props;
  return (
    <div
      className="tooltip"
      style={{
        left: `${x}px`,
        top: `${y}px`,
      }}
    >
      <div className="tooltip-content">
        <div><strong>Date:</strong> {data.str_date}</div>
        <div><strong>Counts:</strong> {data[data_key]}</div>
      </div>
      <div className="tooltip-arrow"></div>
    </div>
  );
}

export default Tooltip;