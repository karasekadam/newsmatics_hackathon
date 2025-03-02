import {useEffect, useState} from "react";
import "./DatePicker.css";

export default function DatePicker(props) {

    // react stuff
    const {selectedDate, setSelectedDate} = props;
    const [strDate, setStrDate] = useState();
    useEffect(() => {
        setStrDate(date_to_str(selectedDate));
    }, [selectedDate]);

    // helper functions
    const date_to_str = () => selectedDate.toISOString().split('T')[0];
    const str_to_date = (str_date) => new Date(str_date);


    return (
        <div className="p-4">
            <label htmlFor="date" className="block mb-2 text-lg">
                Select a Date:
            </label>
            <input
                type="date"
                id="date"
                value={strDate}
                onChange={(e) => setSelectedDate(str_to_date(e.target.value))}
                className="border p-2 rounded-md"
            />
            {strDate && <p className="mt-2">You selected: {strDate}</p>}
        </div>
    );
}