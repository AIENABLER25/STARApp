"use client";

import { macroEconomicOpportunity, marketGrowthTimeline } from "@/data/sectorResearch";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from "recharts";
import { TrendingUp, DollarSign, Users, Briefcase, Lightbulb, FileText } from "lucide-react";

const iconMap: Record<string, React.ReactNode> = {
  "Total Addressable Market (2030)": <DollarSign className="w-5 h-5 text-blue-600" />,
  "U.S. Robotics Employment": <Users className="w-5 h-5 text-emerald-600" />,
  "Projected New Roles (2025-2030)": <Briefcase className="w-5 h-5 text-violet-600" />,
  "Avg. Sector Wage Premium": <TrendingUp className="w-5 h-5 text-amber-600" />,
  "VC Investment (2024)": <Lightbulb className="w-5 h-5 text-rose-600" />,
  "Patent Filings (spatial AI)": <FileText className="w-5 h-5 text-cyan-600" />,
};

export default function MacroEconomicSection() {
  const d = macroEconomicOpportunity;

  return (
    <div id="macro" className="space-y-8">
      <div className="section-card">
        <div className="flex items-center gap-3 mb-2">
          <span className="bg-blue-600 text-white text-xs font-bold px-3 py-1 rounded-full">CHAPTER 1</span>
          <h2 className="text-2xl font-bold text-gray-900">Macro Economic Opportunity</h2>
        </div>
        <p className="text-gray-600 mb-6 max-w-3xl">
          {d.sectorName} — from {d.currentMarketSize} to {d.projectedMarketSize} at {d.cagr} CAGR.
          Sector GDP contribution projected to grow from {d.gdpContribution} to {d.projectedGdpContribution}.
        </p>

        {/* Key Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
          {d.keyMetrics.map((m) => (
            <div key={m.label} className="stat-card flex items-start gap-4">
              <div className="p-2 bg-gray-50 rounded-lg">{iconMap[m.label]}</div>
              <div>
                <p className="text-sm text-gray-500">{m.label}</p>
                <p className="text-xl font-bold text-gray-900">{m.value}</p>
                <span className="text-xs text-emerald-600 font-medium flex items-center gap-1">
                  <TrendingUp className="w-3 h-3" /> Growing
                </span>
              </div>
            </div>
          ))}
        </div>

        {/* Market Growth Chart */}
        <div className="bg-gray-50 rounded-xl p-6 mb-8">
          <h3 className="text-lg font-semibold mb-4">Market Growth Trajectory (2020-2030)</h3>
          <ResponsiveContainer width="100%" height={350}>
            <LineChart data={marketGrowthTimeline}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="year" />
              <YAxis yAxisId="left" label={{ value: "Market Size ($B)", angle: -90, position: "insideLeft" }} />
              <YAxis yAxisId="right" orientation="right" label={{ value: "Jobs (thousands)", angle: 90, position: "insideRight" }} />
              <Tooltip />
              <Legend />
              <Line yAxisId="left" type="monotone" dataKey="market" stroke="#2563eb" strokeWidth={3} name="Market Size ($B)" dot={{ r: 4 }} />
              <Line yAxisId="right" type="monotone" dataKey="jobs" stroke="#059669" strokeWidth={3} name="Direct Jobs (K)" dot={{ r: 4 }} />
              <Line yAxisId="left" type="monotone" dataKey="investment" stroke="#d97706" strokeWidth={2} name="VC Investment ($B)" strokeDasharray="5 5" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Value Creation Drivers */}
        <div>
          <h3 className="text-lg font-semibold mb-4">Value Creation Drivers</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {d.valueCreationDrivers.map((driver, i) => (
              <div key={i} className="flex items-start gap-3 p-4 bg-blue-50 rounded-lg border border-blue-100">
                <span className="bg-blue-600 text-white text-xs font-bold w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                  {i + 1}
                </span>
                <p className="text-sm text-gray-700">{driver}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
