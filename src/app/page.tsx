"use client";

import { useState } from "react";
import MacroEconomicSection from "@/components/MacroEconomicSection";
import EnablersConstraintsSection from "@/components/EnablersConstraintsSection";
import WageDynamicsSection from "@/components/WageDynamicsSection";
import RegionalDistributionSection from "@/components/RegionalDistributionSection";
import SpatialAISection from "@/components/SpatialAISection";
import STARsOpportunitySection from "@/components/STARsOpportunitySection";

const sections = [
  { id: "macro", label: "Macro Economic" },
  { id: "enablers", label: "Enablers & Constraints" },
  { id: "wages", label: "Wage Dynamics" },
  { id: "regional", label: "Regional Distribution" },
  { id: "spatial-ai", label: "Spatial AI & World Labs" },
  { id: "stars", label: "STARs Opportunities" },
];

export default function Home() {
  const [activeSection, setActiveSection] = useState("macro");

  const scrollTo = (id: string) => {
    setActiveSection(id);
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="gradient-header text-white">
        <div className="max-w-7xl mx-auto px-6 py-10">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-xs bg-white/20 px-3 py-1 rounded-full font-medium">SVP RESEARCH</span>
            <span className="text-xs bg-white/10 px-3 py-1 rounded-full">Brookings / McKinsey MGI Methodology</span>
          </div>
          <h1 className="text-3xl md:text-4xl font-bold mb-2">
            Sector Economic Value: Physical Robotics & Spatial AI
          </h1>
          <p className="text-blue-200 max-w-3xl text-sm md:text-base">
            Deep sector research on the labor infrastructure needed to enable a world where robots
            in physical space are activated — informed by Dr. Fei-Fei Li&apos;s spatial intelligence
            paradigm and World Labs&apos; Large World Model approach.
          </p>
          <div className="mt-4 flex items-center gap-4 text-xs text-blue-300">
            <span>Fact-Pack Dimension 1: Sector Economic Value</span>
            <span className="w-1 h-1 bg-blue-400 rounded-full" />
            <span>Physical Robotics & Spatial AI Environment Building</span>
          </div>
        </div>

        {/* Navigation */}
        <div className="max-w-7xl mx-auto px-6 pb-4">
          <nav className="flex gap-1 overflow-x-auto">
            {sections.map((s) => (
              <button
                key={s.id}
                onClick={() => scrollTo(s.id)}
                className={`nav-link whitespace-nowrap ${activeSection === s.id ? "active" : "text-blue-200"}`}
              >
                {s.label}
              </button>
            ))}
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8 space-y-8">
        <MacroEconomicSection />
        <EnablersConstraintsSection />
        <WageDynamicsSection />
        <RegionalDistributionSection />
        <SpatialAISection />
        <STARsOpportunitySection />

        {/* Footer Note */}
        <div className="bg-gray-100 rounded-xl p-6 text-center text-sm text-gray-600">
          <p className="font-semibold text-gray-900 mb-1">Research Methodology Note</p>
          <p>
            This fact-pack follows the Brookings Institution / McKinsey Global Institute (MGI) sector analysis framework.
            Data synthesized from BLS, Census Bureau, NSF, industry reports, and academic research.
            Body of work will encompass 5-6 sectors (1 sector per fact-pack). This edition: Physical Robotics & Spatial AI.
          </p>
        </div>
      </main>
    </div>
  );
}
