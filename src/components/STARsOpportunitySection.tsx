"use client";

import { starsOpportunities } from "@/data/sectorResearch";
import { Clock, TrendingUp, ArrowRight } from "lucide-react";

const barrierColor = {
  low: "bg-emerald-100 text-emerald-700",
  medium: "bg-amber-100 text-amber-700",
  high: "bg-red-100 text-red-700",
};

export default function STARsOpportunitySection() {
  return (
    <div id="stars" className="space-y-8">
      <div className="section-card">
        <div className="flex items-center gap-3 mb-2">
          <span className="bg-emerald-600 text-white text-xs font-bold px-3 py-1 rounded-full">STARs FOCUS</span>
          <h2 className="text-2xl font-bold text-gray-900">STARs Opportunity Matrix</h2>
        </div>
        <p className="text-gray-600 mb-8 max-w-3xl">
          Priority roles for STARs (Skilled Through Alternative Routes) in the physical robotics sector.
          These roles offer $50K+ wage ceilings with training periods under 12 months.
        </p>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {starsOpportunities.map((opp) => (
            <div key={opp.role} className="border border-emerald-200 rounded-xl p-6 bg-emerald-50/30">
              <div className="flex items-start justify-between mb-4">
                <h4 className="font-bold text-lg text-gray-900">{opp.role}</h4>
                <span className={`text-xs px-2 py-1 rounded-full font-bold ${barrierColor[opp.entryBarrier]}`}>
                  {opp.entryBarrier} barrier
                </span>
              </div>

              <div className="grid grid-cols-3 gap-3 mb-4">
                <div className="bg-white rounded-lg p-3 text-center border border-gray-100">
                  <p className="text-xs text-gray-500">Wage Floor</p>
                  <p className="font-bold text-gray-900">${(opp.wageFloor / 1000).toFixed(0)}K</p>
                </div>
                <div className="bg-white rounded-lg p-3 text-center border border-gray-100">
                  <p className="text-xs text-gray-500">Wage Ceiling</p>
                  <p className="font-bold text-emerald-700">${(opp.wageCeiling / 1000).toFixed(0)}K</p>
                </div>
                <div className="bg-white rounded-lg p-3 text-center border border-gray-100">
                  <p className="text-xs text-gray-500 flex items-center justify-center gap-1"><Clock className="w-3 h-3" /> Training</p>
                  <p className="font-bold text-gray-900">{opp.trainingMonths}mo</p>
                </div>
              </div>

              <div className="flex items-center gap-2 mb-3">
                <TrendingUp className="w-4 h-4 text-emerald-600" />
                <span className="text-sm font-semibold text-emerald-700">{opp.demandGrowth}</span>
              </div>

              <div className="mb-3">
                <p className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-2">Transfer From</p>
                <div className="flex flex-wrap gap-1">
                  {opp.transferableFrom.map((t) => (
                    <span key={t} className="text-xs bg-blue-50 text-blue-700 px-2 py-0.5 rounded-full flex items-center gap-1">
                      <ArrowRight className="w-2.5 h-2.5" /> {t}
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <p className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-2">Key Skills</p>
                <div className="flex flex-wrap gap-1">
                  {opp.keySkills.map((s) => (
                    <span key={s} className="text-xs bg-gray-100 text-gray-700 px-2 py-0.5 rounded-full">{s}</span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
