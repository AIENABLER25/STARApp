/**
 * CurveFilter - Shared content script utilities
 * Used across all site-specific content scripts.
 */

const CurveFilter = {
  prefs: null,

  /**
   * Initialize the filter: load prefs and listen for updates.
   * @param {object} siteAdapter - Site-specific adapter with methods:
   *   - getProductCards(): returns NodeList/Array of product card elements
   *   - getAvailableSizes(card): returns array of size strings for a product card
   *   - observeChanges(callback): sets up MutationObserver for dynamic content
   */
  async init(siteAdapter) {
    this.adapter = siteAdapter;

    // Load preferences
    this.prefs = await this.loadPrefs();

    if (!this.prefs || !this.prefs.enabled) return;

    // Apply filters
    this.applyFilters();

    // Watch for dynamic page changes (infinite scroll, AJAX navigation)
    if (siteAdapter.observeChanges) {
      siteAdapter.observeChanges(() => this.applyFilters());
    }

    // Listen for preference updates from popup
    chrome.runtime.onMessage.addListener((message) => {
      if (message.type === 'CURVEFILTER_UPDATE') {
        this.prefs = message.prefs;
        this.clearFilters();
        if (this.prefs.enabled) {
          this.applyFilters();
        }
      }
    });
  },

  loadPrefs() {
    return new Promise((resolve) => {
      chrome.runtime.sendMessage({ type: 'GET_PREFS' }, (prefs) => {
        resolve(prefs);
      });
    });
  },

  /**
   * Get all user sizes as a flat normalized array for matching.
   */
  getUserSizes() {
    if (!this.prefs) return [];
    const sizes = [
      ...(this.prefs.letterSizes || []),
      ...(this.prefs.numericSizes || []),
      ...(this.prefs.waistSizes || []),
      ...(this.prefs.shoeSizes || [])
    ];
    return sizes.map(s => this.normalizeSize(s));
  },

  /**
   * Normalize a size string for comparison.
   * Trims whitespace, lowercases, removes common prefixes like "US", "EU".
   */
  normalizeSize(size) {
    return String(size)
      .trim()
      .toLowerCase()
      .replace(/^(us|eu|uk)\s*/i, '')
      .replace(/\s+/g, '');
  },

  /**
   * Check if any of the product's available sizes match the user's sizes.
   */
  hasMatchingSize(availableSizes) {
    const userSizes = this.getUserSizes();
    if (userSizes.length === 0) return true; // No sizes set = show everything

    const normalizedAvailable = availableSizes.map(s => this.normalizeSize(s));

    return userSizes.some(userSize =>
      normalizedAvailable.some(available =>
        available === userSize ||
        available.includes(userSize) ||
        userSize.includes(available)
      )
    );
  },

  /**
   * Apply filter classes to all product cards on the page.
   */
  applyFilters() {
    const cards = this.adapter.getProductCards();
    if (!cards || cards.length === 0) return;

    const mode = this.prefs.filterMode || 'gray';
    let matchCount = 0;
    let totalCount = 0;

    cards.forEach(card => {
      totalCount++;
      const sizes = this.adapter.getAvailableSizes(card);

      // If we can't determine sizes, don't filter
      if (sizes.length === 0) return;

      const matches = this.hasMatchingSize(sizes);

      if (matches) {
        matchCount++;
        card.classList.remove('curvefilter-unavailable', 'curvefilter-hidden');
        if (mode === 'badge') {
          card.classList.add('curvefilter-available');
        }
      } else {
        card.classList.remove('curvefilter-available');
        if (mode === 'hide') {
          card.classList.add('curvefilter-hidden');
        } else if (mode === 'gray') {
          card.classList.add('curvefilter-unavailable');
        }
      }
    });

    this.showStatusBar(matchCount, totalCount);
  },

  /**
   * Remove all filter classes.
   */
  clearFilters() {
    document.querySelectorAll('.curvefilter-unavailable, .curvefilter-hidden, .curvefilter-available').forEach(el => {
      el.classList.remove('curvefilter-unavailable', 'curvefilter-hidden', 'curvefilter-available');
    });
    const bar = document.querySelector('.curvefilter-bar');
    if (bar) bar.remove();
  },

  /**
   * Show a status bar at the bottom of the page.
   */
  showStatusBar(matchCount, totalCount) {
    let bar = document.querySelector('.curvefilter-bar');
    if (!bar) {
      bar = document.createElement('div');
      bar.className = 'curvefilter-bar';

      const closeBtn = document.createElement('button');
      closeBtn.className = 'curvefilter-bar-close';
      closeBtn.textContent = '\u00d7';
      closeBtn.addEventListener('click', () => bar.remove());

      const text = document.createElement('span');
      text.className = 'curvefilter-bar-text';

      bar.appendChild(text);
      bar.appendChild(closeBtn);
      document.body.appendChild(bar);
    }

    const text = bar.querySelector('.curvefilter-bar-text');
    text.textContent = `CurveFilter: ${matchCount} of ${totalCount} items in your size`;
  }
};
