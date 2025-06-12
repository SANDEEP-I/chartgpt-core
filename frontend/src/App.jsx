import React, { useState } from 'react';
import axios from 'axios';
import Chart from './components/Chart';
import Kpi from './components/Kpi';
import { useDarkMode } from './theme';
import AppShell from './components/AppShell';
import { motion, AnimatePresence } from 'framer-motion';

const fadeInUp = {
  hidden: { opacity: 0, y: 80 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.8,
      type: 'spring',
      bounce: 0.4,
    },
  },
};

const App = () => {
  const [query, setQuery] = useState('');
  const [submittedQuery, setSubmittedQuery] = useState('');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [history, setHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  const [chartTypeOverride, setChartTypeOverride] = useState('');
  const [darkMode, setDarkMode] = useDarkMode();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setError('');
    setResponse(null);
    setSubmittedQuery(query);

    try {
      const res = await axios.post('http://127.0.0.1:8000/query/', { question: query });
      setResponse(res.data);
      setChartTypeOverride('');
      console.log("Backend response:", res.data);
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

  const chartOptions = ['bar', 'line', 'pie'];
  const effectiveChartType = chartTypeOverride || response?.chartType;

  // ✅ Normalize KPI data properly (handles both object and primitive, parse value as float)
  const normalizedKpiData = response?.type === 'kpi'
    ? (
        response?.data
          ? (
              typeof response.data === 'object'
                ? [{
                    label: response.data.label ?? 'Total Value',
                    value: parseFloat(response.data.value) || 0
                  }]
                : [{ label: 'Total Value', value: response.data }]
            )
          : [{ label: 'Total Value', value: 0 }]
      )
    : null;

  return (
    <AppShell darkMode={darkMode} toggleDarkMode={() => setDarkMode(!darkMode)}>
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

      <AnimatePresence mode="wait">
        {response?.type === 'kpi' && (
          <motion.div
            key={`kpi-${submittedQuery}`}
            initial="hidden"
            animate="visible"
            exit="hidden"
            variants={fadeInUp}
          >
            <Kpi data={normalizedKpiData} />
          </motion.div>
        )}

        {response?.type === 'chart' && (
          <motion.div
            key={`chart-${effectiveChartType}-${submittedQuery}-${JSON.stringify(response?.data)}`}
            initial="hidden"
            animate="visible"
            exit="hidden"
            variants={fadeInUp}
          >
            <div className="flex justify-end mb-4">
              <select
                value={chartTypeOverride || response.chartType}
                onChange={(e) => setChartTypeOverride(e.target.value)}
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-sm text-gray-900 dark:text-white"
              >
                {chartOptions.map((type) => (
                  <option key={type} value={type}>
                    {type.charAt(0).toUpperCase() + type.slice(1)}
                  </option>
                ))}
              </select>
            </div>
            <Chart data={response.data} chartType={effectiveChartType} />
          </motion.div>
        )}
      </AnimatePresence>
    </AppShell>
  );
};

export default App;
