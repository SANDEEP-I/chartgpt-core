import React from 'react';

const Kpi = ({ data }) => (
  <div className="bg-gray-100 p-4 rounded shadow text-center">
    <h2 className="text-xl font-semibold">{data.label}</h2>
    <p className="text-3xl font-bold mt-2">{data.value}</p>
  </div>
);

export default Kpi;
