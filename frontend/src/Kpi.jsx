import React from 'react';

const Kpi = ({ data }) => (
  <div className="text-center bg-gray-100 dark:bg-gray-800 p-6 rounded shadow text-xl">
    <div className="font-semibold">{data.label}</div>
    <div className="text-3xl font-bold mt-2">{data.value}</div>
  </div>
);

export default Kpi;
