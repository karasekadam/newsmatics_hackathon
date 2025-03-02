import {useState, React, useEffect, use} from 'react';
import {parse, isValid} from 'date-fns';
import './App.css';
import BarChart from './BarChart';
import DatePicker from './DatePicker';
import SentimentCard from './SentimentCard'
import KeywordSelector from "./KeywordSelector";
import * as d3 from "d3";

import raw_data from "./merged.json";
import FilterList from './FilterList';

function App() {

    // constants
    const timeGrouping = ["day", "week", "month"];

    // helper functions
    const parseTime = (date) => {
        const v = parse(date, 'dd.MM.yyyy', new Date());
        if (isValid(v)) {
            return v;
        }
        return parse(`01.${date}`, 'dd.MM.yyyy', new Date());
    }

    const setDateBoundaries = (sub_object) => {
        for (var timeGroup of timeGrouping) {
            const dates = Object.keys(sub_object[timeGroup]);
            if (Object.keys(sub_object[timeGroup]) < 100 || timeGroup == "month") {
                setTimeGroupingCurrentlyUsing(timeGroup);
                setStartDate(d3.min(dates, d => parseTime(d)));
                setEndDate(d3.max(dates, d => parseTime(d)));
                return;
            }
        }
    }

    const handleTimeGroupingCurrentlyUsing = (up) => {
        if (up) {
            if (timeGroupingCurrentlyUsing == "month") {
                setTimeGroupingCurrentlyUsing("week")
            }
            if (timeGroupingCurrentlyUsing == "week") {
                setTimeGroupingCurrentlyUsing("day")
            }
        } else {
            if (timeGroupingCurrentlyUsing == "day") {
                setTimeGroupingCurrentlyUsing("week")
            }
            if (timeGroupingCurrentlyUsing == "week") {
                setTimeGroupingCurrentlyUsing("month")
            }
        }
    }

    const getCorrectData = () => {
        const filtered_data = data[selectedKeyword][selectedFilter];

        const temp = Object.keys(filtered_data[timeGroupingCurrentlyUsing]).map(date => {
            const {
                most_average_article,
                counts,
                moving_average_sentiment,
                moving_average_sentiment_10,
                neutral_count,
                positive_count,
                negative_count
            } = filtered_data[timeGroupingCurrentlyUsing][date];
            return {
                str_date: date,
                date_date: parseTime(date),
                counts: counts,
                moving_average_sentiment: moving_average_sentiment,
                moving_average_sentiment_10: moving_average_sentiment_10,
                positive_count: positive_count,
                negative_count: negative_count,
                neutral_count: neutral_count,
                most_average_article: most_average_article
            }
        });
        // return temp;
        const filtered = temp.filter(p => startDate <= p.date_date && p.date_date <= endDate);
        console.log("length", filtered.length);
        if (filtered.length < 20) {
            handleTimeGroupingCurrentlyUsing(true);
        } else if (filtered.length > 100) {
            handleTimeGroupingCurrentlyUsing(false);
        }
        return filtered;
    };

    // state
    const [data, setData] = useState({});
    const [timeGroupingCurrentlyUsing, setTimeGroupingCurrentlyUsing] = useState("day");
    const [renderApp, setRenderApp] = useState(false);
    const [brandNames, setBrandNames] = useState();
    const [possibleFilters, setPossibleFilters] = useState();
    const [selectedKeyword, setSelectedKeyword] = useState();
    const [selectedFilter, setSelectedFilter] = useState("all");
    const [startDate, setStartDate] = useState(new Date("2002-02-05"));
    const [endDate, setEndDate] = useState(new Date("2025-03-05"));
    const [filteredData, setFilteredData] = useState([]);
    const [currentArticle, setCurrentArticle] = useState(null);


    // effect
    useEffect(() => {
        if (raw_data.length == 0) {
            return;
        }

        const brand_names = Object.keys(raw_data);
        const selected_brand = brand_names[0];
        const possible_filters = Object.keys(raw_data[selected_brand]);

        setBrandNames(brand_names);
        setSelectedKeyword(selected_brand);
        setPossibleFilters(possible_filters);

        setRenderApp(true);
        setData(raw_data);
    }, []);


    useEffect(() => {
        if (Object.keys(data).length === 0) {
            return;
        }
        setDateBoundaries(data[selectedKeyword][selectedFilter]);
    }, [data]);

    useEffect(() => {
        if (Object.keys(data).length == 0) {
            return;
        }
        setFilteredData(getCorrectData(data, selectedKeyword));

    }, [startDate, endDate, selectedFilter, selectedKeyword]);

    useEffect(() => {
        console.log("trigger use");
        if (Object.keys(data).length == 0) {
            return;
        }
        setFilteredData(getCorrectData(data, selectedKeyword));

    }, [timeGroupingCurrentlyUsing]);


    return (
        <>
            {renderApp && <div className="App">
                <div id="left-column">
                    <KeywordSelector keywords={brandNames} selectedKeyword={selectedKeyword}
                                     setSelectedKeyword={setSelectedKeyword}/>
                    <DatePicker selectedDate={startDate} setSelectedDate={setStartDate}/>
                    <DatePicker selectedDate={endDate} setSelectedDate={setEndDate}/>
                    <FilterList filters={possibleFilters} selectedFilter={selectedFilter}
                                setSelectedFilter={setSelectedFilter}/>
                    {currentArticle && <SentimentCard data={currentArticle}/>}
                </div>
                <div id={"right-column"}>
                    <BarChart setCurrentArticle={setCurrentArticle} data={filteredData}
                              startDate={startDate} endDate={endDate}
                              timeGroupingCurrentlyUsing={timeGroupingCurrentlyUsing}/>
                </div>
            </div>}
        </>
    );
}

export default App;
