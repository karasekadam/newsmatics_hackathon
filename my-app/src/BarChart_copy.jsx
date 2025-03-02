import React, { useEffect, useRef, useState } from "react";
import * as d3 from "d3";
import Tooltip from "./Tooltip";
import "./BarChart.css";

const BarChart = (props) => {

  // data
  const { data } = props;

  // react stuff
  const svgRef = useRef(null);
  const [startDate, setStartDate] = useState();
  const [endDate, setEndDate] = useState();
  const [tooltip, setTooltip] = useState(null);

  useEffect(() => {
    setStartDate(d3.min(data, d => d.date_date));
    setEndDate(d3.max(data, d => d.date_date));
  }, []);

  // constants
  const width = 500;
  const height = 300;
  const barWidth = width / (data.length + 1);

  // functions
  const xScale = d3
    .scaleTime()
    .domain([startDate, endDate])
    .rangeRound([0, data.length * barWidth])

  const yScale = d3.scaleLinear()
    .domain([0, d3.max(data, d => d.counts)])
    .range([height, 0]);

  const colorScale = d3.scaleSequential(d3.interpolateRdYlGn)
    .domain([-1, 1]);


  // svg
  const svg = d3.select("body").selectAll("svg").data([data]);

  svg.exit().remove();

  const svgEnter = svg.enter().append("svg")
    .attr("class", "chart-svg")  // Added class for styling
    .attr("width", width)
    .attr("height", height);

  svgEnter.merge(svg)
    .attr("width", width)
    .attr("height", height)
    .selectAll("rect")
    .data(data)
    .join("rect")
    .attr("class", "bar")  // Added class for styling
    .attr("x", d => xScale(d.date_date))
    .attr("y", d => yScale(d.counts))
    .attr("width", barWidth)
    .attr("height", d => height - yScale(d.counts))
    .attr("fill", d => "red")
    .on("mouseover", function (event, d) {
      const bar = d3.select(this);
      const rectBounds = bar.node().getBoundingClientRect();

      setTooltip({
        x: rectBounds.left + rectBounds.width / 2 - 50,  // Center the tooltip on the bar
        y: rectBounds.top - 28,  // Position it above the bar
        data: d,
      });

      bar.classed("hover", true);  // Apply hover effect
    })
    .on("mouseout", function () {
      setTooltip(null);
      d3.select(this).classed("hover", false);  // Remove hover effect
    });

  svgEnter.merge(svg)
    .selectAll(".date-label")
    .data(data)
    .join("text")
    .attr("class", "date-label")  // Added class for styling
    .attr("x", d => xScale(d.date_date) + barWidth / 2)  // Center the text on the bar
    .attr("y", height - 5)  // Position the text just below the x-axis
    .attr("text-anchor", "middle")  // Center the text horizontally
    .attr("font-size", "10px")  // Set the font size
    .text(d => d.str_date);  // Use the `str_date` field for the label


  // end
  return <>
    {tooltip && <Tooltip x={tooltip.x} y={tooltip.y} data={tooltip.data} />}
    <svg ref={svgRef}></svg>
  </>;
};

export default BarChart;