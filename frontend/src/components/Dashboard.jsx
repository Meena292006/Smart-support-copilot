// frontend/src/components/Dashboard.jsx
import React, { useEffect, useState } from "react";
import { getHistory } from "../api.js";
import {
  BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

export default function Dashboard() {
  const [data, setData] = useState([]);
  const [stats, setStats] = useState({
    total: 0, auto: 0, escalated: 0, positive: 0, negative: 0, urgent: 0
  });

  useEffect(() => {
    const fetchData = async () => {
      const history = await getHistory();
      setData(history);

      const total = history.length;
      const auto = history.filter(m => m.auto_reply === 1).length;
      const escalated = total - auto;
      const positive = history.filter(m => m.feedback === "positive").length;
      const negative = history.filter(m => m.feedback === "negative").length;
      const urgent = history.filter(m => m.priority === "urgent").length;

      setStats({ total, auto, escalated, positive, negative, urgent });
    };

    fetchData();
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, []);

  const accuracy = stats.total > 0 ? ((stats.positive / (stats.positive + stats.negative)) * 100).toFixed(1) : 0;
  const automationRate = stats.total > 0 ? ((stats.auto / stats.total) * 100).toFixed(1) : 0;

  // Category chart data (your model output is comma-separated)
  const categoryCounts = {};
  data.forEach(m => {
    if (m.category) {
      m.category.split(',').map(c => c.trim()).forEach(cat => {
        categoryCounts[cat] = (categoryCounts[cat] || 0) + 1;
      });
    }
  });

  const categoryData = Object.keys(categoryCounts).length > 0
    ? Object.keys(categoryCounts).map(cat => ({ name: cat, value: categoryCounts[cat] }))
    : [{ name: "No Data", value: 1 }];

  const sentimentData = [
    { name: "Positive", value: stats.positive, color: "#10b981" },
    { name: "Negative", value: stats.negative, color: "#ef4444" },
    { name: "Neutral", value: stats.total - stats.positive - stats.negative, color: "#94a3b8" },
  ];

  return (
    <div className="p-6 space-y-8 bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 min-h-screen">
      <div className="text-center mb-10">
        <h1 className="text-6xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600">
          AI Support Command Center
        </h1>
        <p className="text-2xl text-gray-700 mt-3 font-medium">Powered by Your Custom ML Model</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
        {[
          { label: "Total Tickets", value: stats.total, color: "blue" },
          { label: "Auto-Resolved", value: stats.auto, rate: automationRate + "%", color: "green" },
          { label: "Accuracy", value: accuracy + "%", color: "purple" },
          { label: "Urgent Now", value: stats.urgent, color: "red", pulse: true }
        ].map((card, i) => (
          <div key={i} className="bg-white rounded-3xl shadow-2xl p-8 transform hover:scale-105 transition-all duration-300">
            <div className="text-lg text-gray-600">{card.label}</div>
            <div className={`text-6xl font-bold mt-3 text-${card.color}-600 ${card.pulse ? "animate-pulse" : ""}`}>
              {card.value}
            </div>
            {card.rate && <div className="text-sm text-gray-500 mt-2">Automation Rate: <strong>{card.rate}</strong></div>}
          </div>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Category Pie Chart */}
        <div className="bg-white rounded-3xl shadow-2xl p-8">
          <h2 className="text-3xl font-bold text-gray-800 mb-6">Tickets by Category (Your Model)</h2>
          <ResponsiveContainer width="100%" height={350}>
            <PieChart>
              <Pie
                data={categoryData}
                dataKey="value"
                nameKey="name"
                cx="50%" cy="50%"
                outerRadius={120}
                label={({ name, value }) => `${name}: ${value}`}
              >
                {categoryData.map((_, i) => (
                  <Cell key={i} fill={["#8b5cf6", "#3b82f6", "#10b981", "#f59e0b", "#ef4444"][i % 5]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Sentiment Bar Chart */}
        <div className="bg-white rounded-3xl shadow-2xl p-8">
          <h2 className="text-3xl font-bold text-gray-800 mb-6">Customer Sentiment</h2>
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={sentimentData}>
              <CartesianGrid strokeDasharray="4 4" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" radius={[20, 20, 0, 0]}>
                {sentimentData.map((entry, i) => (
                  <Cell key={i} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Live Messages */}
      <div className="bg-white rounded-3xl shadow-2xl p-8">
        <h2 className="text-3xl font-bold text-gray-800 mb-6">Live Messages</h2>
        <div className="space-y-4 max-h-96 overflow-y-auto">
          {data.slice(0, 10).map(msg => (
            <div key={msg.id} className={`p-5 rounded-2xl border-l-6 ${msg.priority === "urgent" ? "border-red-600 bg-red-50" : "border-indigo-600 bg-indigo-50"}`}>
              <div className="flex justify-between">
                <div>
                  <p className="font-bold text-gray-800">{msg.question}</p>
                  <p className="text-sm text-gray-600 mt-1">AI: {msg.response}</p>
                </div>
                <span className={`px-4 py-2 rounded-full text-xs font-bold ${msg.auto_reply === 1 ? "bg-green-600 text-white" : "bg-orange-600 text-white"}`}>
                  {msg.auto_reply === 1 ? "AI" : "Human"}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}