# STARApp

A comprehensive digital platform centralizing Dr. Byron Auguste's 20+ years of research, media, and advocacy work in workforce development and economic opportunity.

## Project Structure

```
STARApp/
└── auguste-archive/          # Main web application
    ├── src/
    │   ├── components/       # React components
    │   │   ├── Header.jsx
    │   │   ├── Biography.jsx
    │   │   ├── Research.jsx
    │   │   ├── Media.jsx
    │   │   ├── Speaking.jsx
    │   │   ├── Initiatives.jsx
    │   │   ├── Timeline.jsx
    │   │   └── SearchBar.jsx
    │   ├── data/
    │   │   └── augusteContent.js   # Centralized content database
    │   ├── App.jsx           # Main application
    │   └── index.css         # Styles
    ├── package.json
    └── README.md
```

## About

This application centralizes all media, narratives, and research created by Dr. Byron Auguste at [Opportunity@Work](https://opportunityatwork.org) over the last 20 years, including:

- **Research Publications**: McKinsey Global Institute reports, academic books, and research papers
- **Media Appearances**: TV, print, radio, and podcast features across 20+ major outlets
- **Speaking Engagements**: Keynote addresses and presentations at leading institutions
- **Key Initiatives**: STARs movement, "Tear the Paper Ceiling" campaign, STAR Mobility Compass
- **Biography & Timeline**: Comprehensive career history and achievements

## Quick Start

```bash
cd auguste-archive
npm install
npm run dev
```

Visit [http://localhost:5173](http://localhost:5173) to view the application.

## Build for Production

```bash
cd auguste-archive
npm run build
npm run preview
```

## Key Features

- Full-text search across all content
- Tag-based filtering for publications and initiatives
- Category navigation (Biography, Research, Media, Speaking, Initiatives, Timeline)
- Responsive design for all devices
- Direct links to original sources

## Technology

- React 18 + Vite
- Tailwind CSS
- Structured data architecture

## Documentation

See [auguste-archive/README.md](./auguste-archive/README.md) for detailed information about the application.

---

*Celebrating Dr. Byron Auguste's transformative work in economic opportunity and workforce development.*
