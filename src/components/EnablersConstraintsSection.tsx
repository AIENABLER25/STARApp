"use client";

import { enablersAndConstraints } from "@/data/sectorResearch";
import { CheckCircle, AlertTriangle, XCircle } from "lucide-react";

const severityIcon = {
  high: <XCircle className="w-4 h-4 text-red-500 flex-shrink-0 mt-0.5" />,
  medium: <AlertTriangle className="w-4 h-4 text-amber-500 flex-shrink-0 mt-0.5" />,
  low: <CheckCircle className="w-4 h-4 text-gray-400 flex-shrink-0 mt-0.5" />,
};

const severityBadge = {
  high: "bg-red-100 text-red-700",
  medium: "bg-amber-100 text-amber-700",
  low: "bg-gray-100 text-gray-600",
};

export default function EnablersConstraintsSection() {
  return (
    <div id="enablers" className="space-y-8">
      <div className="section-card">
        <div className="flex items-center gap-3 mb-2">
          <span className="bg-blue-600 text-white text-xs font-bold px-3 py-1 rounded-full">CHAPTER 2</span>
          <h2 className="text-2xl font-bold text-gray-900">Sector-Specific Enablers & Constraints</h2>
        </div>
        <p className="text-gray-600 mb-8 max-w-3xl">
          Analysis of regulatory, technological, and workforce factors shaping the physical robotics & spatial AI sector.
          Modeled on Brookings/McKinsey constraint analysis framework.
        </p>

        <div className="space-y-8">
          {enablersAndConstraints.map((ec) => (
            <div key={ec.category} className="border border-gray-200 rounded-xl overflow-hidden">
              <div className="bg-gray-50 px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">{ec.category}</h3>
              </div>
              <div className="grid md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-gray-200">
                {/* Enablers */}
                <div className="p-6">
                  <h4 className="text-sm font-bold text-emerald-700 uppercase tracking-wide mb-4 flex items-center gap-2">
                    <CheckCircle className="w-4 h-4" /> Enablers
                  </h4>
                  <div className="space-y-4">
                    {ec.enablers.map((e, i) => (
                      <div key={i}>
                        <p className="font-semibold text-sm text-gray-900">{e.title}</p>
                        <p className="text-sm text-gray-600 mt-1">{e.detail}</p>
                      </div>
                    ))}
                  </div>
                </div>
                {/* Constraints */}
                <div className="p-6">
                  <h4 className="text-sm font-bold text-red-700 uppercase tracking-wide mb-4 flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4" /> Constraints
                  </h4>
                  <div className="space-y-4">
                    {ec.constraints.map((c, i) => (
                      <div key={i}>
                        <div className="flex items-center gap-2 mb-1">
                          {severityIcon[c.severity]}
                          <p className="font-semibold text-sm text-gray-900">{c.title}</p>
                          <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${severityBadge[c.severity]}`}>
                            {c.severity}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 ml-6">{c.detail}</p>
                      </div>
                    ))}
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
