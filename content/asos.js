/**
 * CurveFilter - ASOS Site Adapter
 *
 * ASOS product listing pages use a grid of product cards.
 * Each card contains size information in data attributes or
 * within the product details section.
 */

(function () {
  const asosAdapter = {
    /**
     * Get all product cards on the current page.
     * ASOS uses article elements or divs with specific data attributes for products.
     */
    getProductCards() {
      // ASOS product listing selectors (multiple fallbacks)
      return document.querySelectorAll(
        '[data-auto-id="productTile"], ' +
        'article[class*="productCard"], ' +
        'div[class*="product-card"], ' +
        'li[class*="product"] > article, ' +
        'section[class*="listing"] article'
      );
    },

    /**
     * Extract available sizes from a product card.
     * ASOS sometimes embeds size info in the card, or we parse from
     * size selector buttons/text within the card.
     */
    getAvailableSizes(card) {
      const sizes = [];

      // Method 1: Look for size elements within the card
      const sizeElements = card.querySelectorAll(
        '[class*="size"], [data-auto-id*="size"], span[class*="Size"]'
      );
      sizeElements.forEach(el => {
        const text = el.textContent.trim();
        if (text && text.length < 10) {
          sizes.push(text);
        }
      });

      // Method 2: Check for data attributes
      const sizeData = card.getAttribute('data-sizes') || card.getAttribute('data-available-sizes');
      if (sizeData) {
        try {
          const parsed = JSON.parse(sizeData);
          if (Array.isArray(parsed)) {
            sizes.push(...parsed.map(s => typeof s === 'object' ? s.name || s.size : String(s)));
          }
        } catch (e) {
          // Not JSON, try comma-separated
          sizes.push(...sizeData.split(',').map(s => s.trim()));
        }
      }

      // Method 3: Parse from aria-label or title attributes
      const ariaLabel = card.getAttribute('aria-label') || '';
      const sizeMatch = ariaLabel.match(/sizes?\s*:?\s*([^,]+(?:,\s*[^,]+)*)/i);
      if (sizeMatch) {
        sizes.push(...sizeMatch[1].split(',').map(s => s.trim()));
      }

      // Method 4: Look for structured data in script tags within the card
      const scriptTags = card.querySelectorAll('script[type="application/ld+json"]');
      scriptTags.forEach(script => {
        try {
          const data = JSON.parse(script.textContent);
          if (data.offers) {
            const offers = Array.isArray(data.offers) ? data.offers : [data.offers];
            offers.forEach(offer => {
              if (offer.size) sizes.push(offer.size);
            });
          }
        } catch (e) {
          // Ignore parse errors
        }
      });

      return [...new Set(sizes)]; // Deduplicate
    },

    /**
     * Observe DOM changes for dynamically loaded content (infinite scroll).
     */
    observeChanges(callback) {
      const observer = new MutationObserver((mutations) => {
        let hasNewProducts = false;
        for (const mutation of mutations) {
          if (mutation.addedNodes.length > 0) {
            for (const node of mutation.addedNodes) {
              if (node.nodeType === 1 && (
                node.matches?.('[data-auto-id="productTile"]') ||
                node.querySelector?.('[data-auto-id="productTile"]')
              )) {
                hasNewProducts = true;
                break;
              }
            }
          }
          if (hasNewProducts) break;
        }
        if (hasNewProducts) {
          // Debounce to avoid excessive re-filtering
          clearTimeout(this._debounceTimer);
          this._debounceTimer = setTimeout(callback, 300);
        }
      });

      // Observe the main content area
      const target = document.querySelector('[class*="productList"], main, #chrome-app-root') || document.body;
      observer.observe(target, { childList: true, subtree: true });
    }
  };

  // Initialize after a short delay to ensure page is ready
  setTimeout(() => CurveFilter.init(asosAdapter), 1000);
})();
