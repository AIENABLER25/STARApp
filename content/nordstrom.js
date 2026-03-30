/**
 * CurveFilter - Nordstrom Site Adapter
 *
 * Nordstrom product pages use a grid layout with product cards
 * that contain size and availability information.
 */

(function () {
  const nordstromAdapter = {
    /**
     * Get all product cards on the current page.
     */
    getProductCards() {
      return document.querySelectorAll(
        'article[class*="product"], ' +
        'div[class*="product-card"], ' +
        'div[class*="ProductCard"], ' +
        'section[class*="product-results"] article, ' +
        'div[data-testid*="product"], ' +
        'div[class*="search-product"]'
      );
    },

    /**
     * Extract available sizes from a Nordstrom product card.
     */
    getAvailableSizes(card) {
      const sizes = [];

      // Method 1: Size swatches/buttons
      const sizeButtons = card.querySelectorAll(
        'button[class*="size"], [class*="SizeOption"], [data-testid*="size"]'
      );
      sizeButtons.forEach(btn => {
        if (!btn.disabled && !btn.classList.toString().includes('unavailable')) {
          const text = btn.textContent.trim();
          if (text && text.length < 10) {
            sizes.push(text);
          }
        }
      });

      // Method 2: Size text within the card
      const sizeElements = card.querySelectorAll(
        '[class*="size"], [class*="Size"]'
      );
      sizeElements.forEach(el => {
        const text = el.textContent.trim();
        // Match common size patterns
        const sizePattern = /^(XXS|XS|S|M|L|XL|XXL|1X|2X|3X|4X|5X|\d{1,2}(\.5)?|One Size)$/i;
        if (sizePattern.test(text)) {
          sizes.push(text);
        }
      });

      // Method 3: Data attributes
      const sizeData = card.getAttribute('data-sizes');
      if (sizeData) {
        try {
          const parsed = JSON.parse(sizeData);
          if (Array.isArray(parsed)) {
            sizes.push(...parsed.map(s => typeof s === 'object' ? s.label || s.name : String(s)));
          }
        } catch (e) {
          sizes.push(...sizeData.split(',').map(s => s.trim()));
        }
      }

      // Method 4: Structured data
      const scriptTags = card.querySelectorAll('script[type="application/ld+json"]');
      scriptTags.forEach(script => {
        try {
          const data = JSON.parse(script.textContent);
          if (data.offers) {
            const offers = Array.isArray(data.offers) ? data.offers : [data.offers];
            offers.forEach(offer => {
              if (offer.size) sizes.push(offer.size);
              if (offer.availability && offer.availability.includes('OutOfStock')) return;
            });
          }
        } catch (e) {
          // Ignore parse errors
        }
      });

      // Method 5: Look for size info in nested links or spans
      const allText = card.querySelectorAll('span, a');
      allText.forEach(el => {
        const text = el.textContent.trim();
        const multiSizePattern = /^((?:XXS|XS|S|M|L|XL|XXL|1X|2X|3X|4X|5X|\d{1,2}(?:\.5)?)\s*[-–]\s*(?:XXS|XS|S|M|L|XL|XXL|1X|2X|3X|4X|5X|\d{1,2}(?:\.5)?))$/;
        if (multiSizePattern.test(text)) {
          // Size range like "14-24" or "S-XL"
          sizes.push(...expandSizeRange(text));
        }
      });

      return [...new Set(sizes)];
    },

    /**
     * Observe DOM changes for dynamically loaded content.
     */
    observeChanges(callback) {
      const observer = new MutationObserver((mutations) => {
        let hasNewProducts = false;
        for (const mutation of mutations) {
          if (mutation.addedNodes.length > 0) {
            for (const node of mutation.addedNodes) {
              if (node.nodeType === 1 && (
                node.matches?.('article[class*="product"]') ||
                node.querySelector?.('article[class*="product"]') ||
                node.matches?.('div[class*="product-card"]') ||
                node.querySelector?.('div[class*="product-card"]')
              )) {
                hasNewProducts = true;
                break;
              }
            }
          }
          if (hasNewProducts) break;
        }
        if (hasNewProducts) {
          clearTimeout(this._debounceTimer);
          this._debounceTimer = setTimeout(callback, 300);
        }
      });

      const target = document.querySelector('main, [id*="app"], [class*="product-results"]') || document.body;
      observer.observe(target, { childList: true, subtree: true });
    }
  };

  /**
   * Expand a size range (e.g., "14-24") into individual sizes.
   */
  function expandSizeRange(rangeStr) {
    const parts = rangeStr.split(/\s*[-–]\s*/);
    if (parts.length !== 2) return [rangeStr];

    const start = parseInt(parts[0]);
    const end = parseInt(parts[1]);

    if (isNaN(start) || isNaN(end)) return parts;

    const sizes = [];
    for (let i = start; i <= end; i += 2) {
      sizes.push(String(i));
    }
    return sizes;
  }

  setTimeout(() => CurveFilter.init(nordstromAdapter), 1000);
})();
