import React, { useState } from 'react';
import axios from 'axios';
import Chart from './Chart';
import Kpi from './Kpi';
import { useDarkMode } from './theme';

const App = () => {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [history, setHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  const [darkMode, setDarkMode] = useDarkMode();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setError('');
    try {
      const res = await axios.post('http://127.0.0.1:8000/query/', { question: query });
      setResponse(res.data);
      setHistory((prev) => {
        const updated = [query, ...prev.filter((q) => q !== query)];
        return updated.slice(0, 10);
      });
    } catch (err) {
      setError('Something went wrong.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white font-sans">

      <header className="bg-white dark:bg-gray-900 shadow-md sticky top-0 z-10 px-6 py-4 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">ChartGPT</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">Ask data questions in plain English</p>
        </div>
        <button onClick={() => setDarkMode(!darkMode)} className="text-sm bg-gray-200 dark:bg-gray-700 px-3 py-1.5 rounded">
          {darkMode ? '🌙 Dark' : '☀️ Light'}
        </button>
      </header>
      <main className="max-w-3xl mx-auto p-6">
        <div className="flex justify-end mb-2">
          <button onClick={() => setShowHistory(!showHistory)} className="text-blue-600 text-sm hover:underline">
            {showHistory ? 'Hide History' : 'Show History'}
          </button>
        </div>
        {showHistory && (
          <aside className="bg-white dark:bg-gray-800 border dark:border-gray-600 rounded p-4 mb-6 shadow">
            <h3 className="font-semibold text-gray-800 dark:text-white mb-2">Recent Queries</h3>
            <ul className="space-y-1">
              {history.map((item, i) => (
                <li key={i}>
                  <button
                    onClick={() => {
                      setQuery(item);
                      handleSubmit({ preventDefault: () => {} });
                    }}
                    className="text-sm text-blue-600 hover:underline"
                  >
                    {item}
                  </button>
                </li>
              ))}
            </ul>
          </aside>
        )}
        <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3 mb-6">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g. Show me total revenue"
            className="flex-grow px-4 py-2 rounded border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 text-black dark:text-white"
          />
          <button
            type="submit"
            disabled={loading}
            className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 transition"
          >
            {loading ? 'Loading...' : 'Ask'}
          </button>
        </form>
        {error && <div className="bg-red-200 text-red-800 p-3 rounded mb-4">{error}</div>}
{response?.type === 'kpi' && <Kpi data={response.data} />}
{response?.type === 'chart' && <Chart data={response.data} chartType={response.chartType} />}

<div className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md mt-6">
  <h1 className="text-2xl font-bold text-green-600 mb-4">
    Tailwind CSS v4 is now working!
  </h1>
  <div className="flex gap-4 flex-wrap">
    <button className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition">
      Test Button
    </button>
    <div className="px-4 py-2 bg-yellow-200 dark:bg-purple-500 rounded">
      Color Test
    </div>
    <div className="flex items-center">
      <div className="w-3 h-3 rounded-full bg-green-500 mr-2"></div>
      <span>Success Indicator</span>
    </div>
  </div>
</div>

</main>

    </div>
  );
};

export default App;
