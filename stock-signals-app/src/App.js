import React, { useState } from "react";
import axios from "axios";
import './App.css';

function App() {
  const [endDate, setEndDate] = useState("");
  const [buySignals, setBuySignals] = useState([]);
  const [loading, setLoading] = useState(false);  // State to manage loading

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);  // Start loading

    try {
      const response = await axios.post("http://localhost:5000/calculate", {
        endDate: endDate
      });
      setBuySignals(response.data);
    } catch (error) {
      console.error("Error fetching buy signals:", error);
    } finally {
      setLoading(false);  // Stop loading once the API call is finished
    }
  };

  return (
    <div className="App">
      <h1>Stock Buy Signal Analyzer</h1>
      <form onSubmit={handleSubmit}>
        <label>
          End Date (YYYY-MM-DD):
          <input
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            required
          />
        </label>
        <button type="submit">Get Buy Signals</button>
      </form>

      {/* Show loading spinner if loading is true */}
      {loading && (
        <div className="loader"></div>
      )}

      {/* Display the buy signals when they are available */}
      {!loading && buySignals.length > 0 && (
        <div>
          <h2>Buy Signals:</h2>
          <ul>
            {buySignals.map((signal, index) => (
              <li key={index}>
                {signal.stockSymbol} - Buy Price: {signal.buyPrice} on {signal.date}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;
