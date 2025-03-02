// FilterList.jsx
import React from 'react';
import './FilterList.css';

const FilterList = ({filters, selectedFilter, setSelectedFilter}) => {
    return (
        <div className="filter-container">
            <div className="filter-list">
                {filters.map((filter) => (
                    <button
                        key={filter}
                        className={`filter-pill ${filter === selectedFilter ? 'selected' : ''}`}
                        onClick={() => setSelectedFilter(filter)}
                    >
                        {filter}
                    </button>
                ))}
            </div>
        </div>
    );
};

export default FilterList;