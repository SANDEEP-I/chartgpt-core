// AppShell.jsx
import React from 'react';
import { motion } from 'framer-motion';

const fadeIn = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { duration: 0.4 } },
};

const AppShell = ({ children, darkMode, toggleDarkMode }) => {
  return (
    <motion.div
      className="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white font-sans"
      initial="hidden"
      animate="show"
      variants={fadeIn}
    >
      <header className="backdrop-blur bg-white/70 dark:bg-gray-900/70 shadow-md sticky top-0 z-10 px-6 py-4 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">ChartGPT</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">Ask data questions in plain English</p>
        </div>
        <button
          onClick={toggleDarkMode}
          className="text-sm bg-gray-200 dark:bg-gray-700 px-3 py-1.5 rounded hover:scale-105 transition"
        >
          {darkMode ? '🌙 Dark' : '☀️ Light'}
        </button>
      </header>

      <main className="max-w-3xl mx-auto p-6">{children}</main>
    </motion.div>
  );
};

export default AppShell;
