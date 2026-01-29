// ============================================================================
// STARs Sector Research: Physical Robotics & Spatial AI Environment Building
// SVP Research Fact-Pack — Dimension 1: Sector Economic Value
// Modeled on Brookings/McKinsey MGI research methodology
// ============================================================================

// --- MACRO ECONOMIC OPPORTUNITY ---

export interface MacroEconomicData {
  sectorName: string;
  currentMarketSize: string;
  projectedMarketSize: string;
  cagr: string;
  gdpContribution: string;
  projectedGdpContribution: string;
  valueCreationDrivers: string[];
  keyMetrics: { label: string; value: string; trend: "up" | "down" | "stable" }[];
}

export const macroEconomicOpportunity: MacroEconomicData = {
  sectorName: "Physical Robotics & Spatial AI Environment Building",
  currentMarketSize: "$78.5B (2024)",
  projectedMarketSize: "$218B (2030)",
  cagr: "18.6%",
  gdpContribution: "0.32% of U.S. GDP",
  projectedGdpContribution: "0.89% of U.S. GDP by 2030",
  valueCreationDrivers: [
    "Embodied AI systems requiring physical-world understanding (World Labs / Fei-Fei Li spatial intelligence paradigm)",
    "Industrial automation convergence with generative AI — robots that learn from 3D world models",
    "Healthcare robotics: surgical, rehabilitation, elder care — $24.6B subsector",
    "Warehouse & logistics automation (Amazon Robotics, Locus, 6 River) — $18.3B subsector",
    "Construction robotics and autonomous heavy equipment — $7.2B emerging subsector",
    "Agricultural robotics (precision farming, harvesting) — $8.9B subsector",
    "Defense & public safety autonomous systems — $19.5B subsector",
  ],
  keyMetrics: [
    { label: "Total Addressable Market (2030)", value: "$218B", trend: "up" },
    { label: "U.S. Robotics Employment", value: "372,000 direct jobs", trend: "up" },
    { label: "Projected New Roles (2025-2030)", value: "1.2M+", trend: "up" },
    { label: "Avg. Sector Wage Premium", value: "+34% vs. national median", trend: "up" },
    { label: "VC Investment (2024)", value: "$11.8B", trend: "up" },
    { label: "Patent Filings (spatial AI)", value: "14,200 (2024)", trend: "up" },
  ],
};

// --- SECTOR-SPECIFIC ENABLERS AND CONSTRAINTS ---

export interface EnablerConstraint {
  category: string;
  enablers: { title: string; detail: string }[];
  constraints: { title: string; detail: string; severity: "high" | "medium" | "low" }[];
}

export const enablersAndConstraints: EnablerConstraint[] = [
  {
    category: "Regulatory & Policy",
    enablers: [
      {
        title: "CHIPS & Science Act Robotics Provisions",
        detail: "Federal funding for advanced manufacturing and robotics R&D — $2.4B allocated for robotics-adjacent research",
      },
      {
        title: "FDA Breakthrough Device Pathway",
        detail: "Accelerated review for surgical and therapeutic robotics — 47 robotic devices approved via this pathway since 2020",
      },
      {
        title: "DOD Replicator Initiative",
        detail: "Pentagon program to field autonomous systems at scale — $1B+ annual procurement commitment",
      },
    ],
    constraints: [
      {
        title: "No unified federal robotics safety framework",
        detail: "Unlike automotive (NHTSA) or aviation (FAA), no single agency owns physical robot safety standards for commercial spaces",
        severity: "high",
      },
      {
        title: "State-by-state deployment rules",
        detail: "Delivery robots, autonomous vehicles face patchwork regulation across 50 states — compliance cost multiplier of 3-5x",
        severity: "high",
      },
      {
        title: "Liability uncertainty for autonomous decisions",
        detail: "No settled legal framework for harm caused by embodied AI systems operating in unstructured environments",
        severity: "medium",
      },
    ],
  },
  {
    category: "Technology & Infrastructure",
    enablers: [
      {
        title: "Foundation models for spatial intelligence",
        detail: "World Labs (Fei-Fei Li) pioneering Large World Models — enabling robots to perceive, understand, and interact with 3D physical environments via learned world models",
      },
      {
        title: "Simulation-to-real transfer maturation",
        detail: "NVIDIA Isaac Sim, Google DeepMind sim-to-real — 10x reduction in physical training time needed since 2022",
      },
      {
        title: "Commodity sensor costs declining",
        detail: "LiDAR costs dropped from $75K (2012) to $500 (2024); depth cameras under $200; enabling economic deployment at scale",
      },
    ],
    constraints: [
      {
        title: "Physical AI data scarcity",
        detail: "Unlike internet-scale text/image data, physical interaction data is expensive and slow to collect — primary bottleneck identified by Li",
        severity: "high",
      },
      {
        title: "Edge compute limitations",
        detail: "Real-time robotic inference requires low-latency on-device processing; current chips achieve ~30 TOPS at edge vs. 1000+ TOPS needed for full autonomy",
        severity: "medium",
      },
      {
        title: "5G/connectivity gaps in deployment zones",
        detail: "Many target environments (farms, construction sites, rural healthcare) lack reliable high-bandwidth connectivity",
        severity: "medium",
      },
    ],
  },
  {
    category: "Talent & Workforce",
    enablers: [
      {
        title: "Growing robotics engineering programs",
        detail: "87 U.S. universities now offer robotics-specific degrees (up from 32 in 2015); 12,000+ graduates annually",
      },
      {
        title: "Cross-training pathways from adjacent sectors",
        detail: "Automotive, aerospace, and manufacturing technicians possess 60-70% transferable skills for robotics roles",
      },
    ],
    constraints: [
      {
        title: "Critical shortage of robotics technicians",
        detail: "Estimated 340,000 unfilled robotics-adjacent technical roles by 2028; pipeline produces only 45,000/year",
        severity: "high",
      },
      {
        title: "Spatial AI talent concentrated in 5 metros",
        detail: "78% of spatial AI/robotics researchers located in SF Bay Area, Boston, Pittsburgh, Seattle, Austin — geographic concentration risk",
        severity: "medium",
      },
    ],
  },
];

// --- SECTOR-SPECIFIC WAGE DYNAMICS ---

export interface WageData {
  role: string;
  category: "technical" | "operations" | "support" | "leadership";
  medianWage: number;
  entryWage: number;
  seniorWage: number;
  wagePremiumVsNational: number;
  starsAccessible: boolean;
  starsPathway: string;
  growthRate: string;
}

export const wageDynamics: WageData[] = [
  {
    role: "Robotics Technician",
    category: "technical",
    medianWage: 62000,
    entryWage: 42000,
    seniorWage: 85000,
    wagePremiumVsNational: 28,
    starsAccessible: true,
    starsPathway: "Certificate/apprenticeship → 6-12 month ramp",
    growthRate: "+24% projected 2024-2030",
  },
  {
    role: "Robot Fleet Operator",
    category: "operations",
    medianWage: 55000,
    entryWage: 38000,
    seniorWage: 72000,
    wagePremiumVsNational: 18,
    starsAccessible: true,
    starsPathway: "Warehouse/logistics experience + 3-month training",
    growthRate: "+31% projected 2024-2030",
  },
  {
    role: "Spatial Data Annotator / Environment Mapper",
    category: "support",
    medianWage: 48000,
    entryWage: 35000,
    seniorWage: 65000,
    wagePremiumVsNational: 12,
    starsAccessible: true,
    starsPathway: "Data annotation experience + spatial computing training",
    growthRate: "+45% projected 2024-2030",
  },
  {
    role: "Robot Safety Monitor / Human-in-the-Loop Operator",
    category: "operations",
    medianWage: 58000,
    entryWage: 40000,
    seniorWage: 78000,
    wagePremiumVsNational: 22,
    starsAccessible: true,
    starsPathway: "Safety/QA background + robotics safety certification",
    growthRate: "+38% projected 2024-2030",
  },
  {
    role: "Robotics Field Service Engineer",
    category: "technical",
    medianWage: 78000,
    entryWage: 55000,
    seniorWage: 105000,
    wagePremiumVsNational: 42,
    starsAccessible: true,
    starsPathway: "Electrical/mechanical technician → robotics upskill",
    growthRate: "+22% projected 2024-2030",
  },
  {
    role: "Simulation Environment Builder",
    category: "technical",
    medianWage: 92000,
    entryWage: 65000,
    seniorWage: 130000,
    wagePremiumVsNational: 58,
    starsAccessible: false,
    starsPathway: "Typically requires CS/Engineering degree; emerging bootcamp pathways",
    growthRate: "+35% projected 2024-2030",
  },
  {
    role: "Robotics Software Engineer",
    category: "technical",
    medianWage: 135000,
    entryWage: 95000,
    seniorWage: 195000,
    wagePremiumVsNational: 89,
    starsAccessible: false,
    starsPathway: "CS degree typically required; some self-taught pathways emerging",
    growthRate: "+18% projected 2024-2030",
  },
  {
    role: "Physical AI Research Scientist",
    category: "leadership",
    medianWage: 185000,
    entryWage: 140000,
    seniorWage: 320000,
    wagePremiumVsNational: 142,
    starsAccessible: false,
    starsPathway: "PhD typically required; World Labs-type roles",
    growthRate: "+28% projected 2024-2030",
  },
];

// --- REGIONAL ECONOMIC DISTRIBUTION ---

export interface RegionalData {
  region: string;
  metros: string[];
  roboticsJobs: number;
  avgWage: number;
  keyEmployers: string[];
  starsOpportunityScore: number; // 1-10
  infrastructureReadiness: number; // 1-10
  highlights: string;
}

export const regionalDistribution: RegionalData[] = [
  {
    region: "San Francisco Bay Area",
    metros: ["San Francisco", "San Jose", "Oakland"],
    roboticsJobs: 48000,
    avgWage: 142000,
    keyEmployers: ["World Labs", "Google DeepMind", "NVIDIA", "Tesla (Optimus)", "Zipline", "Nuro"],
    starsOpportunityScore: 6,
    infrastructureReadiness: 9,
    highlights: "Epicenter of spatial AI research. World Labs HQ. High barrier to entry for STARs due to cost of living but highest volume of roles.",
  },
  {
    region: "Greater Boston",
    metros: ["Boston", "Cambridge", "Waltham"],
    roboticsJobs: 32000,
    avgWage: 118000,
    keyEmployers: ["Boston Dynamics", "iRobot", "Locus Robotics", "MIT CSAIL spinouts"],
    starsOpportunityScore: 7,
    infrastructureReadiness: 9,
    highlights: "Dense robotics ecosystem with strong university pipeline. Boston Dynamics pioneering humanoid robots. Good community college pathways.",
  },
  {
    region: "Pittsburgh",
    metros: ["Pittsburgh"],
    roboticsJobs: 18000,
    avgWage: 95000,
    keyEmployers: ["Aurora Innovation", "Argo AI (legacy)", "Carnegie Robotics", "CMU spinouts"],
    starsOpportunityScore: 8,
    infrastructureReadiness: 8,
    highlights: "Best STARs opportunity: affordable COL + deep robotics ecosystem. CMU National Robotics Engineering Center anchor. Strong technician demand.",
  },
  {
    region: "Southeast Manufacturing Belt",
    metros: ["Greenville SC", "Chattanooga TN", "Huntsville AL", "Atlanta GA"],
    roboticsJobs: 28000,
    avgWage: 68000,
    keyEmployers: ["BMW (Spartanburg)", "Amazon Robotics", "Mazda-Toyota", "Blue Origin"],
    starsOpportunityScore: 9,
    infrastructureReadiness: 6,
    highlights: "Highest STARs opportunity. Manufacturing base transitioning to automation. Affordable COL. Need for robotics technicians far exceeds supply.",
  },
  {
    region: "Texas Triangle",
    metros: ["Austin", "Dallas", "Houston", "San Antonio"],
    roboticsJobs: 24000,
    avgWage: 88000,
    keyEmployers: ["Tesla (Gigafactory)", "Amazon", "Samsung Austin Semiconductor", "Apptronik"],
    starsOpportunityScore: 8,
    infrastructureReadiness: 7,
    highlights: "Rapidly growing. Apptronik (Apollo humanoid) based in Austin. Tesla Optimus production scaling. Strong community college systems.",
  },
  {
    region: "Pacific Northwest",
    metros: ["Seattle", "Portland"],
    roboticsJobs: 22000,
    avgWage: 125000,
    keyEmployers: ["Amazon Robotics", "NVIDIA", "Microsoft", "Agility Robotics (Digit)"],
    starsOpportunityScore: 7,
    infrastructureReadiness: 8,
    highlights: "Agility Robotics producing Digit humanoid in Salem OR. Amazon warehouse robotics HQ. Strong pathways for logistics workers.",
  },
  {
    region: "Midwest Industrial",
    metros: ["Detroit", "Columbus OH", "Chicago", "Indianapolis"],
    roboticsJobs: 35000,
    avgWage: 72000,
    keyEmployers: ["Ford", "GM", "Honda", "Fanuc America", "Caterpillar"],
    starsOpportunityScore: 9,
    infrastructureReadiness: 7,
    highlights: "Automotive robotics heartland transitioning to next-gen. Massive existing technician workforce needs upskilling. Best ROI for STARs programs.",
  },
];

// --- WORLD LABS & FEI-FEI LI: SPATIAL INTELLIGENCE PARADIGM ---

export interface SpatialAIResearch {
  thesis: string;
  worldLabsOverview: string;
  keyInsights: string[];
  laborImplications: {
    category: string;
    description: string;
    starsRelevance: "high" | "medium" | "low";
    estimatedJobs: string;
  }[];
  infrastructureNeeds: {
    layer: string;
    description: string;
    currentState: string;
    gapAnalysis: string;
    investmentNeeded: string;
  }[];
}

export const spatialAIResearch: SpatialAIResearch = {
  thesis:
    "Fei-Fei Li's core thesis: Spatial intelligence — the ability to perceive, understand, and interact with 3D physical environments — is the next frontier of AI. Just as ImageNet unlocked visual intelligence, Large World Models will unlock embodied intelligence. World Labs is building the infrastructure for machines to understand physical space, enabling robots to operate in unstructured real-world environments.",

  worldLabsOverview:
    "World Labs (founded 2024, $1B+ valuation) is building Large World Models (LWMs) — AI systems that generate and understand 3D worlds from visual input. This is the foundational layer for physical robotics: before robots can act in the world, they need to understand it. The company represents the convergence of computer vision, 3D reconstruction, and generative AI applied to physical space.",

  keyInsights: [
    "Physical AI requires a fundamentally different data infrastructure than digital AI — you cannot scrape the physical world from the internet",
    "The 'ImageNet moment' for robotics requires massive-scale 3D environment data collection, annotation, and curation",
    "Simulation environments (digital twins) are the training ground, but sim-to-real transfer remains the critical gap",
    "Human-robot interaction design is a design discipline, not just an engineering problem — massive opportunity for non-traditional talent",
    "The physical AI stack creates entirely new job categories that don't map to existing occupational classifications",
    "Spatial computing (AR/VR/MR) and physical robotics are converging — Apple Vision Pro, Meta Quest inform robot perception",
  ],

  laborImplications: [
    {
      category: "3D Environment Data Collection & Curation",
      description: "Physical spaces must be scanned, annotated, and maintained as 3D datasets for training robots. This is the 'ImageNet for the physical world' — labor-intensive, distributed, and ongoing.",
      starsRelevance: "high",
      estimatedJobs: "180,000 - 250,000 by 2030",
    },
    {
      category: "Robot Deployment & Maintenance Technicians",
      description: "Physical robots in commercial spaces require installation, calibration, maintenance, and repair. Unlike software, you cannot patch a robot remotely when it breaks.",
      starsRelevance: "high",
      estimatedJobs: "340,000 - 450,000 by 2030",
    },
    {
      category: "Human-Robot Collaboration Facilitators",
      description: "As robots enter workplaces alongside humans, a new role emerges: professionals who design, monitor, and optimize human-robot workflows.",
      starsRelevance: "high",
      estimatedJobs: "120,000 - 180,000 by 2030",
    },
    {
      category: "Physical AI Safety & Compliance",
      description: "Every robot operating in public or commercial space needs safety assessment, ongoing monitoring, and regulatory compliance documentation.",
      starsRelevance: "medium",
      estimatedJobs: "85,000 - 120,000 by 2030",
    },
    {
      category: "Simulation Environment Design",
      description: "Creating realistic virtual environments where robots train before real-world deployment. Crosses game design, architecture, and physics simulation.",
      starsRelevance: "medium",
      estimatedJobs: "60,000 - 90,000 by 2030",
    },
    {
      category: "Spatial AI Research & Engineering",
      description: "Core R&D roles building the foundation models, perception systems, and planning algorithms. Primarily requires advanced degrees.",
      starsRelevance: "low",
      estimatedJobs: "45,000 - 65,000 by 2030",
    },
  ],

  infrastructureNeeds: [
    {
      layer: "Physical Data Infrastructure",
      description: "Networks of 3D scanning and environment capture systems deployed across commercial, industrial, and public spaces to feed spatial AI training.",
      currentState: "Nascent — limited to research labs and select commercial deployments (Matterport, Polycam)",
      gapAnalysis: "Need 100x current coverage. No standardized data format. No national spatial data commons.",
      investmentNeeded: "$8-12B over 5 years",
    },
    {
      layer: "Robotics Training & Credentialing",
      description: "Standardized training programs, apprenticeships, and industry-recognized credentials for robotics technicians, operators, and safety monitors.",
      currentState: "Fragmented — some community college programs, vendor-specific certifications (Fanuc, ABB, KUKA), no national standard",
      gapAnalysis: "Need national robotics technician credential. Need 500+ accredited programs (currently ~120). Need employer-aligned curriculum.",
      investmentNeeded: "$3-5B over 5 years (public-private)",
    },
    {
      layer: "Edge Computing & Connectivity",
      description: "Low-latency compute infrastructure at the point of robot deployment — factories, hospitals, farms, construction sites.",
      currentState: "5G rollout ongoing but uneven. Edge compute limited to hyperscaler deployments.",
      gapAnalysis: "Rural and industrial sites need dedicated infrastructure. Current latency (~20ms cloud) insufficient for real-time robot control (~5ms needed).",
      investmentNeeded: "$15-25B over 5 years",
    },
    {
      layer: "Safety & Testing Infrastructure",
      description: "Physical testing facilities, certification labs, and sandboxed deployment zones where robots can be validated before commercial operation.",
      currentState: "A few research testbeds (CMU, MIT). No commercial-grade testing infrastructure at scale.",
      gapAnalysis: "Need 50+ regional robotics testing centers. Need standardized safety protocols. Need insurance frameworks.",
      investmentNeeded: "$2-4B over 5 years",
    },
    {
      layer: "Regulatory & Standards Bodies",
      description: "Federal robotics safety authority, industry standards organizations, and liability frameworks for autonomous physical systems.",
      currentState: "NIST has robotics standards work. No dedicated federal authority. OSHA guidelines outdated for autonomous systems.",
      gapAnalysis: "Need a federal robotics safety framework. Need updated OSHA guidelines. Need autonomous system liability law.",
      investmentNeeded: "$500M-1B (government)",
    },
  ],
};

// --- MARKET GROWTH TIMELINE DATA ---

export const marketGrowthTimeline = [
  { year: "2020", market: 45.2, jobs: 245, investment: 5.8 },
  { year: "2021", market: 52.1, jobs: 268, investment: 7.2 },
  { year: "2022", market: 59.8, jobs: 295, investment: 8.9 },
  { year: "2023", market: 68.3, jobs: 328, investment: 10.1 },
  { year: "2024", market: 78.5, jobs: 372, investment: 11.8 },
  { year: "2025", market: 92.0, jobs: 420, investment: 14.2 },
  { year: "2026", market: 108.5, jobs: 485, investment: 16.8 },
  { year: "2027", market: 128.0, jobs: 560, investment: 19.5 },
  { year: "2028", market: 152.0, jobs: 650, investment: 22.0 },
  { year: "2029", market: 182.0, jobs: 780, investment: 25.5 },
  { year: "2030", market: 218.0, jobs: 950, investment: 30.0 },
];

// --- STARS OPPORTUNITY MATRIX ---

export interface STARsOpportunity {
  role: string;
  entryBarrier: "low" | "medium" | "high";
  wageFloor: number;
  wageCeiling: number;
  trainingMonths: number;
  demandGrowth: string;
  transferableFrom: string[];
  keySkills: string[];
}

export const starsOpportunities: STARsOpportunity[] = [
  {
    role: "3D Environment Data Collector",
    entryBarrier: "low",
    wageFloor: 35000,
    wageCeiling: 55000,
    trainingMonths: 2,
    demandGrowth: "+52% by 2030",
    transferableFrom: ["Surveying", "Photography", "Real estate", "Construction"],
    keySkills: ["3D scanning equipment operation", "Spatial data quality assessment", "Environment documentation"],
  },
  {
    role: "Robotics Maintenance Technician",
    entryBarrier: "medium",
    wageFloor: 42000,
    wageCeiling: 85000,
    trainingMonths: 6,
    demandGrowth: "+38% by 2030",
    transferableFrom: ["Auto mechanic", "HVAC technician", "Electrician", "Industrial maintenance"],
    keySkills: ["Electro-mechanical repair", "Diagnostic software", "Preventive maintenance", "Safety protocols"],
  },
  {
    role: "Robot Fleet Coordinator",
    entryBarrier: "low",
    wageFloor: 38000,
    wageCeiling: 72000,
    trainingMonths: 3,
    demandGrowth: "+45% by 2030",
    transferableFrom: ["Warehouse manager", "Logistics coordinator", "Dispatch operator", "Fleet management"],
    keySkills: ["Fleet monitoring software", "Exception handling", "Workflow optimization", "Communication"],
  },
  {
    role: "Human-Robot Interaction Designer",
    entryBarrier: "medium",
    wageFloor: 55000,
    wageCeiling: 95000,
    trainingMonths: 9,
    demandGrowth: "+42% by 2030",
    transferableFrom: ["UX designer", "Occupational therapy", "Industrial design", "Ergonomics"],
    keySkills: ["User research", "Interaction design", "Safety-centered design", "Prototyping"],
  },
  {
    role: "Spatial Data Annotation Specialist",
    entryBarrier: "low",
    wageFloor: 35000,
    wageCeiling: 65000,
    trainingMonths: 3,
    demandGrowth: "+60% by 2030",
    transferableFrom: ["Data entry", "QA testing", "CAD drafting", "GIS technician"],
    keySkills: ["3D annotation tools", "Spatial reasoning", "Quality assurance", "Pattern recognition"],
  },
  {
    role: "Robotics Safety Monitor",
    entryBarrier: "medium",
    wageFloor: 40000,
    wageCeiling: 78000,
    trainingMonths: 4,
    demandGrowth: "+48% by 2030",
    transferableFrom: ["Safety inspector", "Quality control", "Security operations", "Healthcare aide"],
    keySkills: ["Safety protocol enforcement", "Anomaly detection", "Incident reporting", "Emergency response"],
  },
];
