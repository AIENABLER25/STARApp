"use client";

import { regionalDistribution } from "@/data/sectorResearch";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { MapPin, Star, Building2 } from "lucide-react";

export default function RegionalDistributionSection() {
  const chartData = regionalDistribution.map((r) => ({
    region: r.region.length > 20 ? r.region.substring(0, 18) + "..." : r.region,
    jobs: r.roboticsJobs / 1000,
    avgWage: r.avgWage / 1000,
    starsScore: r.starsOpportunityScore,
  }));

  return (
    <div id="regional" className="space-y-8">
      <div className="section-card">
        <div className="flex items-center gap-3 mb-2">
          <span className="bg-blue-600 text-white text-xs font-bold px-3 py-1 rounded-full">CHAPTER 4</span>
          <h2 className="text-2xl font-bold text-gray-900">Regional Economic Distribution</h2>
        </div>
        <p className="text-gray-600 mb-8 max-w-3xl">
          Geographic analysis of robotics employment, wages, and STARs opportunity across U.S. regions.
          STARs Opportunity Score (1-10) reflects accessibility, affordability, and demand density.
        </p>

        {/* Regional Chart */}
        <div className="bg-gray-50 rounded-xl p-6 mb-8">
          <h3 className="text-lg font-semibold mb-4">Robotics Jobs & STARs Opportunity by Region</h3>
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="region" tick={{ fontSize: 11 }} angle={-20} textAnchor="end" height={80} />
              <YAxis yAxisId="left" label={{ value: "Jobs (K)", angle: -90, position: "insideLeft" }} />
              <YAxis yAxisId="right" orientation="right" domain={[0, 10]} label={{ value: "STARs Score", angle: 90, position: "insideRight" }} />
              <Tooltip />
              <Bar yAxisId="left" dataKey="jobs" fill="#2563eb" name="Robotics Jobs (K)" radius={[4, 4, 0, 0]} />
              <Bar yAxisId="right" dataKey="starsScore" fill="#059669" name="STARs Opportunity Score" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Regional Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {regionalDistribution
            .sort((a, b) => b.starsOpportunityScore - a.starsOpportunityScore)
            .map((r) => (
              <div key={r.region} className="border border-gray-200 rounded-xl p-5 bg-white">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h4 className="font-semibold text-gray-900 flex items-center gap-2">
                      <MapPin className="w-4 h-4 text-blue-600" /> {r.region}
                    </h4>
                    <p className="text-xs text-gray-500">{r.metros.join(" · ")}</p>
                  </div>
                  <div className="flex items-center gap-1 bg-emerald-100 text-emerald-700 px-2 py-1 rounded-full text-xs font-bold">
                    <Star className="w-3 h-3" /> {r.starsOpportunityScore}/10
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-2 mb-3">
                  <div className="bg-gray-50 rounded-lg p-2 text-center">
                    <p className="text-xs text-gray-500">Robotics Jobs</p>
                    <p className="font-bold text-gray-900">{(r.roboticsJobs / 1000).toFixed(0)}K</p>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-2 text-center">
                    <p className="text-xs text-gray-500">Avg. Wage</p>
                    <p className="font-bold text-gray-900">${(r.avgWage / 1000).toFixed(0)}K</p>
                  </div>
                </div>

                <div className="mb-3">
                  <p className="text-xs font-medium text-gray-700 mb-1 flex items-center gap-1">
                    <Building2 className="w-3 h-3" /> Key Employers
                  </p>
                  <div className="flex flex-wrap gap-1">
                    {r.keyEmployers.slice(0, 4).map((e) => (
                      <span key={e} className="text-xs bg-blue-50 text-blue-700 px-2 py-0.5 rounded-full">{e}</span>
                    ))}
                  </div>
                </div>

                <p className="text-xs text-gray-600">{r.highlights}</p>

                <div className="mt-3 flex gap-2">
                  <div className="flex-1">
                    <p className="text-xs text-gray-500">Infra Readiness</p>
                    <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                      <div
                        className="bg-blue-600 h-2 rounded-full"
                        style={{ width: `${r.infrastructureReadiness * 10}%` }}
                      />
                    </div>
                  </div>
                </div>
              </div>
            ))}
        </div>
      </div>
    </div>
  );
}
