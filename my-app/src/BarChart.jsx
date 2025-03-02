import React, {useEffect, useRef, useState} from "react";
import * as d3 from "d3";
import Tooltip from "./Tooltip";
import "./BarChart.css";

const BarChart = (props) => {
    const {setCurrentArticle, data, startDate, endDate, timeGroupingCurrentlyUsing} = props;

    // state & ref
    const svgRef = useRef(null);
    const [tooltip, setTooltip] = useState(null);

    // effect
    useEffect(() => {
        if (!data || data.length === 0) return;

        // Clear previous SVG content
        d3.select(svgRef.current).selectAll("*").remove();

        // constants
        const margin = {top: 20, right: 20, bottom: 50, left: 70};
        const width = 1000 - margin.left - margin.right;
        const height = 600 - margin.top - margin.bottom;
        const barWidth = width / data.length;
        const max_third_height = height / 3;
        const baseline = height / 2;
        const barWidthWithPadding = barWidth - Math.ceil(barWidth / 5);

        // Determine maximum values
        const maxPositive = d3.max(data, d => d.positive_count);
        const maxNegative = d3.max(data, d => d.negative_count);
        const maxNeutral = d3.max(data, d => d.neutral_count);

        // --------------------------------------------------------------
        // scaling functions

        // from date to x
        const x = d3
            .scaleTime()
            .domain([startDate, endDate])
            .rangeRound([0, (data.length - 1) * barWidth])

        // scale neutral bar to correct height
        const scaleNeutral = d3
            .scaleLinear()
            .domain([0, maxNeutral])
            .range([0, max_third_height]);

        // Create separate scales for the positive and negative sections
        const yScalePositive = d3
            .scaleLinear()
            .domain([0, maxPositive])
            .range([0, max_third_height]);

        const yScaleNegative = d3
            .scaleLinear()
            .domain([0, maxNegative])
            .range([0, max_third_height]);

        // Create y-axis scales for display
        const yAxisScalePositive = d3
            .scaleLinear()
            .domain([0, Math.max(maxPositive, maxNegative)])
            .range([baseline, baseline - height / 2]);

        const yAxisScaleNegative = d3
            .scaleLinear()
            .domain([0, Math.max(maxPositive, maxNegative)])
            .range([baseline, baseline + height / 2]);

        // --------------------------------------------------------------
        // creating html

        // create svg
        const svg = d3
            .select(svgRef.current)
            .attr("class", "chart-svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", `translate(${margin.left},${margin.top})`);

        // Add Y axis for positive values (above the baseline)
        svg.append("g")
            .attr("class", "y-axis positive-axis")
            .call(d3.axisLeft(yAxisScalePositive)
                .ticks(5)
                .tickFormat(d => Math.abs(d)));

        // Add Y axis for negative values (below the baseline)
        svg.append("g")
            .attr("class", "y-axis negative-axis")
            .call(d3.axisLeft(yAxisScaleNegative)
                .ticks(5)
                .tickFormat(d => Math.abs(d)));

        // Simple index-based x-scale for bar placement
        const xBarScale = d3
            .scaleBand()
            .domain(d3.range(data.length))
            .range([0, width])
            .padding(0.1);

        // groups for stacked chart
        const barGroups = svg.selectAll(".bar-group")
            .data(data)
            .enter()
            .append("g")
            .attr("class", "bar-group");


        // change label based on zoom of the data
        const getAxisLabel = (date) => {
            switch (timeGroupingCurrentlyUsing) {
                case "day":
                    return new Intl.DateTimeFormat("en-US", {
                        month: "long",
                        day: "numeric"
                    }).format(date);
                case "week":
                    const month = date.getMonth() + 1; // getMonth() is 0-based, so add 1
                    const year = date.getFullYear();
                    return `${month}/${year}`;
                case "month":
                    return date.getFullYear();
            }
        }

        // --- Positive rectangle (drawn above baseline) ---
        barGroups.append("rect")
            .attr("class", "positive")
            .attr("x", (d) => x(d.date_date))
            .attr("y", baseline)
            .attr("width", barWidthWithPadding)
            .attr("height", 0)
            .attr("fill", "#4daf4aa0")
            .on("click", (event, d) => {
                setCurrentArticle(d);
            })
            .transition()
            .duration(800)
            .ease(d3.easeCubic)
            .attr("y", d => baseline - scaleNeutral(d.neutral_count) / 2 - yScalePositive(d.positive_count))
            .attr("height", d => yScalePositive(d.positive_count));

        // --- Neutral rectangle (centered on the baseline) ---
        barGroups.append("rect")
            .attr("class", "neutral")
            .attr("x", (d) => x(d.date_date))
            // Center the neutral rectangle around the baseline
            .attr("y", baseline)
            .attr("width", barWidthWithPadding)
            .attr("height", 0)
            .attr("fill", "#377eb8a0")
            .on("mouseover", function (event, d) {
                const rectBounds = this.getBoundingClientRect();
                setTooltip({
                    x: rectBounds.left + window.scrollX + rectBounds.width / 2 - 47,
                    y: rectBounds.top + window.scrollY - 50,
                    data: d,
                    data_key: "positive_count",
                });
                d3.select(this).classed("hover", true);
            })
            .on("mouseout", function () {
                setTooltip(null);
                d3.select(this).classed("hover", false);
            })
            .transition()
            .duration(800)
            .ease(d3.easeCubic)
            .attr("y", d => baseline - scaleNeutral(d.neutral_count) / 2)
            .attr("height", d => scaleNeutral(d.neutral_count));

        // --- Negative rectangle (drawn below baseline) ---
        barGroups.append("rect")
            .attr("class", "negative")
            .attr("x", (d) => x(d.date_date))
            // Starting at the baseline; height extends downward.
            .attr("y", baseline)
            .attr("width", barWidthWithPadding)
            .attr("height", 0)
            .attr("fill", "#e41a1ca0")
            .on("mouseover", function (event, d) {
                const rectBounds = this.getBoundingClientRect();
                setTooltip({
                    x: rectBounds.left + window.scrollX + rectBounds.width / 2 - 47,
                    y: rectBounds.top + window.scrollY - 50,
                    data: d,
                    data_key: "positive_count",
                });
                d3.select(this).classed("hover", true);
            })
            .on("mouseout", function () {
                setTooltip(null);
                d3.select(this).classed("hover", false);
            })
            .transition()
            .duration(800)
            .ease(d3.easeCubic)
            .attr("y", d => baseline + scaleNeutral(d.neutral_count) / 2)
            .attr("height", d => yScaleNegative(d.negative_count));

        // --- Sentiment Line Chart (average_sentiment) ---
        // Create a y-scale for average_sentiment that spans the full height of the chart.
        const sentimentExtent = d3.extent(data, d => d.moving_average_sentiment_10);
        const sentimentScale = d3.scaleLinear()
            .domain(sentimentExtent)
            .range([height, 0]);

        // Define the line generator for average_sentiment.
        const line = d3.line()
            .x(d => x(d.date_date) + barWidthWithPadding / 2)
            .y(d => sentimentScale(d.moving_average_sentiment_10));

        // Append the sentiment line path to the svg.
        svg.append("path")
            .datum(data)
            .attr("class", "sentiment-line")
            .attr("fill", "none")
            .attr("stroke", "#333333")
            .attr("stroke-width", 2)
            .attr("d", line)
            .attr("stroke-dasharray", function () {
                return this.getTotalLength();
            })
            .attr("stroke-dashoffset", function () {
                return this.getTotalLength();
            })
            .transition()
            .duration(2400)
            .ease(d3.easeCubic)
            .attr("stroke-dashoffset", 0);

        // ----

        // middle line
        svg.append("line")
            .attr("class", "baseline")
            .attr("x1", 0)
            .attr("y1", baseline)
            .attr("x2", width)
            .attr("y2", baseline)
            .attr("stroke", "#333")
            .attr("stroke-width", 1)
            .attr("stroke-dasharray", "4,4");

        // Add y-axis label
        svg.append("text")
            .attr("transform", "rotate(-90)")
            .attr("y", -margin.left + 20)
            .attr("x", -height / 2)
            .attr("text-anchor", "middle")
            .text("Count");

        // Add x-axis with dates
        // Date format for display
        const dateFormat = d3.timeFormat("%b %d");

        // Create x-axis
        const xScale = d3.scaleBand()
            .domain(data.map((d, i) => i))
            .range([0, width]);

        // Create a custom axis with controlled number of ticks
        const xAxis = svg.append("g")
            .attr("class", "x-axis")
            .attr("transform", `translate(0,${height + 60})`);

        // Calculate appropriate tick interval based on data length
        const tickInterval = Math.ceil(data.length / 10); // Show at most 10 ticks

        // Add tick marks at appropriate intervals
        data.forEach((d, i) => {
            if (i % tickInterval === 0 || i === data.length - 1) {
                const xPos = xBarScale(i) + xBarScale.bandwidth() / 2;
                console.log("data axis", d);

                // Add date label
                xAxis.append("text")
                    .attr("x", xPos)
                    .attr("y", 20)
                    .attr("text-anchor", "middle")
                    .attr("transform", `rotate(90, ${xPos}, 10)`) // Rotate text vertically
                    // .text(d.date ? dateFormat(new Date(d.date)) : `Day ${i+1}`);
                    .text(getAxisLabel(d.date_date));
            }
        });

        // Add x-axis label
        svg.append("text")
            .attr("x", width / 2)
            .attr("y", height + 140)
            .attr("text-anchor", "middle")
            .text("Date");

    }, [data]); // Re-render when data changes


    return <>
        {tooltip &&
            <Tooltip x={tooltip.x} y={tooltip.y} data={tooltip.data} data_key={tooltip.data_key}/>}
        <svg ref={svgRef}></svg>
    </>;
};

export default BarChart;