import React from 'react';

const Kpi = ({ data }) => {
  return (
    <div className="bg-white dark:bg-gray-800 p-10 rounded-xl shadow-md text-center max-w-2xl mx-auto">
      {data && data.length > 0 ? (
        <>
          <div className="text-3xl font-semibold text-gray-700 dark:text-gray-300">
            {data[0].label}
          </div>
          <div className="text-5xl font-bold text-green-600 mt-4">
            {parseFloat(data[0].value).toLocaleString()}
          </div>
        </>
      ) : (
        <div>No data</div>
      )}
    </div>
  );
};

export default Kpi;
