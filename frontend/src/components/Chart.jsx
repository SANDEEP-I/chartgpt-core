import React, { useRef } from 'react';
import {
  LineChart, Line,
  BarChart, Bar,
  XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer,
} from 'recharts';
import * as htmlToImage from 'html-to-image';
import download from 'downloadjs';

const Chart = ({ data, chartType }) => {
  const chartRef = useRef();

  const handleExportImage = async () => {
    if (!chartRef.current) return;
    const blob = await htmlToImage.toBlob(chartRef.current);
    if (blob) download(blob, 'chart.png');
  };

  const handleExportCSV = () => {
    const csv = ['Label,Value'];
    data.forEach(row => {
      csv.push(`${row.name},${row.value}`);
    });
    const blob = new Blob([csv.join('\n')], { type: 'text/csv' });
    download(blob, 'chart-data.csv');
  };

  return (
    <div className="bg-white dark:bg-gray-900 p-4 rounded-xl shadow-md">
      <div className="flex justify-end mb-2 gap-2">
        <button
          onClick={handleExportImage}
          className="text-sm px-3 py-1 rounded bg-blue-500 text-white hover:bg-blue-600"
        >
          Export PNG
        </button>
        <button
          onClick={handleExportCSV}
          className="text-sm px-3 py-1 rounded bg-gray-700 text-white hover:bg-gray-800"
        >
          Export CSV
        </button>
      </div>
      <div ref={chartRef}>
        <ResponsiveContainer width="100%" height={400}>
          {chartType === 'line' ? (
            <LineChart data={data}>
              <CartesianGrid stroke="#e5e7eb" strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Line
                type="monotone"
                dataKey="value"
                stroke="#4f46e5"
                strokeWidth={3}
                animationDuration={800}
              />
            </LineChart>
          ) : (
            <BarChart data={data}>
              <CartesianGrid stroke="#e5e7eb" strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar
                dataKey="value"
                fill="#4f46e5"
                radius={[6, 6, 0, 0]}
                animationDuration={800}
              />
            </BarChart>
          )}
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default Chart;
