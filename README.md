# CurveFilter - Chrome Extension

**"See only what fits. Shop only what's yours."**

CurveFilter is a Chrome browser extension that filters fashion sites to show only items available in your size. Set your sizes once, and every supported fashion site automatically highlights or hides items based on your fit.

## Features

- **Size Profiles**: Set letter sizes (XS–5X), numeric US sizes (0–32), waist/pants sizes, and shoe sizes
- **Three Display Modes**:
  - **Hide** — completely removes items not in your size
  - **Gray Out** — dims unavailable items so you can still browse them
  - **Badge** — marks items available in your size with a green checkmark
- **Real-time Filtering** — works with infinite scroll and dynamic page loads
- **Status Bar** — shows how many items on the page match your size

## Supported Sites (MVP)

| Site | Status |
|------|--------|
| ASOS | Supported |
| Nordstrom | Supported |
| Zara | Supported |

## Installation (Developer Mode)

1. Clone or download this repository
2. Open Chrome and go to `chrome://extensions/`
3. Enable **Developer mode** (toggle in top-right)
4. Click **Load unpacked**
5. Select the `STARApp` folder
6. The CurveFilter icon will appear in your toolbar

## Usage

1. Click the CurveFilter icon in your Chrome toolbar
2. Select your sizes across any/all categories
3. Choose your preferred display mode
4. Click **Save Preferences**
5. Visit any supported fashion site — filtering happens automatically

## Project Structure

```
STARApp/
├── manifest.json              # Chrome extension manifest (v3)
├── background/
│   └── service-worker.js      # Background service worker
├── popup/
│   ├── popup.html             # Extension popup UI
│   ├── popup.css              # Popup styles
│   └── popup.js               # Popup logic & preference management
├── content/
│   ├── shared.js              # Core filtering engine
│   ├── curvefilter.css         # Injected page styles
│   ├── asos.js                # ASOS site adapter
│   ├── nordstrom.js           # Nordstrom site adapter
│   └── zara.js                # Zara site adapter
└── icons/
    ├── icon16.png
    ├── icon48.png
    └── icon128.png
```

## How It Works

1. **Content scripts** are injected into supported fashion sites
2. Each site has an **adapter** that knows how to find product cards and extract size information from that site's specific DOM structure
3. The **shared engine** compares available sizes against your saved preferences
4. Items are classified as matching or not, and the chosen display mode is applied
5. A **MutationObserver** watches for new products loaded via infinite scroll or AJAX navigation

## Adding New Sites

To add support for a new retailer:

1. Create a new file in `content/` (e.g., `content/newsite.js`)
2. Implement the adapter interface:
   - `getProductCards()` — returns product card DOM elements
   - `getAvailableSizes(card)` — extracts size strings from a card
   - `observeChanges(callback)` — watches for dynamically loaded content
3. Add the site to `manifest.json`:
   - Add URL pattern to `host_permissions`
   - Add a new entry to `content_scripts`

## Tech Stack

- Chrome Extension Manifest V3
- Vanilla JavaScript (no frameworks)
- Chrome Storage Sync API for cross-device preferences
- MutationObserver for SPA/dynamic content support
