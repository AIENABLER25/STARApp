"use client";

import { spatialAIResearch } from "@/data/sectorResearch";
import { Brain, Users, Shield, Wrench, Landmark, Wifi } from "lucide-react";

const layerIcons: Record<string, React.ReactNode> = {
  "Physical Data Infrastructure": <Brain className="w-5 h-5 text-blue-600" />,
  "Robotics Training & Credentialing": <Users className="w-5 h-5 text-emerald-600" />,
  "Edge Computing & Connectivity": <Wifi className="w-5 h-5 text-violet-600" />,
  "Safety & Testing Infrastructure": <Shield className="w-5 h-5 text-amber-600" />,
  "Regulatory & Standards Bodies": <Landmark className="w-5 h-5 text-rose-600" />,
};

const relevanceColor = {
  high: "bg-emerald-100 text-emerald-700 border-emerald-200",
  medium: "bg-amber-100 text-amber-700 border-amber-200",
  low: "bg-gray-100 text-gray-600 border-gray-200",
};

export default function SpatialAISection() {
  const d = spatialAIResearch;

  return (
    <div id="spatial-ai" className="space-y-8">
      {/* Thesis & World Labs */}
      <div className="section-card">
        <div className="flex items-center gap-3 mb-2">
          <span className="bg-indigo-600 text-white text-xs font-bold px-3 py-1 rounded-full">DEEP DIVE</span>
          <h2 className="text-2xl font-bold text-gray-900">Spatial Intelligence & World Labs</h2>
        </div>

        <div className="bg-indigo-50 border border-indigo-200 rounded-xl p-6 mb-6">
          <h3 className="font-semibold text-indigo-900 mb-2">Core Thesis (Fei-Fei Li)</h3>
          <p className="text-sm text-indigo-800 leading-relaxed">{d.thesis}</p>
        </div>

        <div className="bg-gray-50 border border-gray-200 rounded-xl p-6 mb-6">
          <h3 className="font-semibold text-gray-900 mb-2">World Labs Overview</h3>
          <p className="text-sm text-gray-700 leading-relaxed">{d.worldLabsOverview}</p>
        </div>

        <div>
          <h3 className="text-lg font-semibold mb-4">Key Research Insights</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {d.keyInsights.map((insight, i) => (
              <div key={i} className="flex items-start gap-3 p-4 bg-white rounded-lg border border-gray-200">
                <span className="bg-indigo-600 text-white text-xs font-bold w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                  {i + 1}
                </span>
                <p className="text-sm text-gray-700">{insight}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Labor Implications */}
      <div className="section-card">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Labor Infrastructure for Robot-Enabled Environments</h2>
        <p className="text-gray-600 mb-6 max-w-3xl">
          New job categories emerging from the spatial AI / physical robotics convergence.
          These roles largely do not exist in current BLS occupational classifications.
        </p>

        <div className="space-y-4 mb-8">
          {d.laborImplications.map((li, i) => (
            <div key={i} className="border border-gray-200 rounded-xl p-5 bg-white">
              <div className="flex items-start justify-between mb-2">
                <h4 className="font-semibold text-gray-900">{li.category}</h4>
                <div className="flex items-center gap-2">
                  <span className={`text-xs px-2 py-0.5 rounded-full font-medium border ${relevanceColor[li.starsRelevance]}`}>
                    STARs: {li.starsRelevance}
                  </span>
                  <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full font-bold">
                    {li.estimatedJobs}
                  </span>
                </div>
              </div>
              <p className="text-sm text-gray-600">{li.description}</p>
            </div>
          ))}
        </div>

        {/* Infrastructure Needs */}
        <h3 className="text-xl font-bold text-gray-900 mb-4">Infrastructure Investment Needed</h3>
        <p className="text-gray-600 mb-6 max-w-3xl">
          Five layers of infrastructure must be built to enable a world where robots operate in physical spaces at scale.
          Total estimated investment: $29-47B over 5 years.
        </p>

        <div className="space-y-4">
          {d.infrastructureNeeds.map((infra, i) => (
            <div key={i} className="border border-gray-200 rounded-xl overflow-hidden">
              <div className="bg-gray-50 px-6 py-4 border-b border-gray-200 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  {layerIcons[infra.layer] || <Wrench className="w-5 h-5 text-gray-600" />}
                  <h4 className="font-semibold text-gray-900">{infra.layer}</h4>
                </div>
                <span className="text-sm font-bold text-blue-700 bg-blue-50 px-3 py-1 rounded-full">
                  {infra.investmentNeeded}
                </span>
              </div>
              <div className="p-6 grid md:grid-cols-3 gap-4">
                <div>
                  <p className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-1">Description</p>
                  <p className="text-sm text-gray-700">{infra.description}</p>
                </div>
                <div>
                  <p className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-1">Current State</p>
                  <p className="text-sm text-gray-700">{infra.currentState}</p>
                </div>
                <div>
                  <p className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-1">Gap Analysis</p>
                  <p className="text-sm text-gray-700">{infra.gapAnalysis}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
