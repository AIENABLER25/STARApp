"use client";

import { wageDynamics } from "@/data/sectorResearch";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { Star, TrendingUp } from "lucide-react";

const categoryColors: Record<string, string> = {
  technical: "#2563eb",
  operations: "#059669",
  support: "#d97706",
  leadership: "#7c3aed",
};

export default function WageDynamicsSection() {
  const chartData = wageDynamics.map((w) => ({
    name: w.role.length > 25 ? w.role.substring(0, 22) + "..." : w.role,
    entry: w.entryWage / 1000,
    median: w.medianWage / 1000,
    senior: w.seniorWage / 1000,
    premium: w.wagePremiumVsNational,
    starsAccessible: w.starsAccessible,
  }));

  return (
    <div id="wages" className="space-y-8">
      <div className="section-card">
        <div className="flex items-center gap-3 mb-2">
          <span className="bg-blue-600 text-white text-xs font-bold px-3 py-1 rounded-full">CHAPTER 3</span>
          <h2 className="text-2xl font-bold text-gray-900">Sector-Specific Wage Dynamics</h2>
        </div>
        <p className="text-gray-600 mb-8 max-w-3xl">
          Wage analysis across the physical robotics value chain. STARs-accessible roles highlighted.
          All figures represent national medians; premiums calculated vs. national median wage ($48,060).
        </p>

        {/* Wage Range Chart */}
        <div className="bg-gray-50 rounded-xl p-6 mb-8">
          <h3 className="text-lg font-semibold mb-4">Wage Ranges by Role ($K)</h3>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={chartData} layout="vertical" margin={{ left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis type="number" label={{ value: "Annual Salary ($K)", position: "bottom" }} />
              <YAxis type="category" dataKey="name" width={180} tick={{ fontSize: 12 }} />
              <Tooltip formatter={(v) => `$${v}K`} />
              <Legend />
              <Bar dataKey="entry" fill="#93c5fd" name="Entry" stackId="a" />
              <Bar dataKey="median" fill="#2563eb" name="Median" />
              <Bar dataKey="senior" fill="#1e3a5f" name="Senior" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Detailed Role Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {wageDynamics.map((w) => (
            <div
              key={w.role}
              className={`p-5 rounded-xl border ${
                w.starsAccessible ? "border-emerald-200 bg-emerald-50/50" : "border-gray-200 bg-white"
              }`}
            >
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h4 className="font-semibold text-gray-900">{w.role}</h4>
                  <span
                    className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                      categoryColors[w.category] ? "bg-blue-100 text-blue-700" : ""
                    }`}
                    style={{ backgroundColor: categoryColors[w.category] + "20", color: categoryColors[w.category] }}
                  >
                    {w.category}
                  </span>
                </div>
                {w.starsAccessible && (
                  <span className="flex items-center gap-1 text-xs font-bold text-emerald-700 bg-emerald-100 px-2 py-1 rounded-full">
                    <Star className="w-3 h-3" /> STARs
                  </span>
                )}
              </div>

              <div className="grid grid-cols-3 gap-2 mb-3 text-center">
                <div className="bg-white rounded-lg p-2 border border-gray-100">
                  <p className="text-xs text-gray-500">Entry</p>
                  <p className="font-bold text-gray-900">${(w.entryWage / 1000).toFixed(0)}K</p>
                </div>
                <div className="bg-white rounded-lg p-2 border border-gray-100">
                  <p className="text-xs text-gray-500">Median</p>
                  <p className="font-bold text-gray-900">${(w.medianWage / 1000).toFixed(0)}K</p>
                </div>
                <div className="bg-white rounded-lg p-2 border border-gray-100">
                  <p className="text-xs text-gray-500">Senior</p>
                  <p className="font-bold text-gray-900">${(w.seniorWage / 1000).toFixed(0)}K</p>
                </div>
              </div>

              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Wage premium: <strong className="text-blue-700">+{w.wagePremiumVsNational}%</strong></span>
                <span className="flex items-center gap-1 text-emerald-600 font-medium">
                  <TrendingUp className="w-3 h-3" /> {w.growthRate}
                </span>
              </div>
              <p className="text-xs text-gray-500 mt-2">{w.starsPathway}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
