/**
 * CurveFilter - Zara Site Adapter
 *
 * Zara uses a React-based SPA with product grids.
 * Products often load dynamically and size info may be
 * embedded in data attributes or fetched via API.
 */

(function () {
  const zaraAdapter = {
    /**
     * Get all product cards on the current page.
     */
    getProductCards() {
      return document.querySelectorAll(
        'li[class*="product"], ' +
        'a[class*="product-link"], ' +
        'div[class*="product-card"], ' +
        'section[class*="product-grid"] li, ' +
        'ul[class*="product-grid"] > li, ' +
        'div[data-productid], ' +
        'article[class*="product"]'
      );
    },

    /**
     * Extract available sizes from a Zara product card.
     */
    getAvailableSizes(card) {
      const sizes = [];

      // Method 1: Size list elements
      const sizeElements = card.querySelectorAll(
        '[class*="size"], [class*="Size"], [data-size]'
      );
      sizeElements.forEach(el => {
        // Skip if out of stock / crossed out
        const isUnavailable = el.classList.toString().includes('unavailable') ||
          el.classList.toString().includes('crossed') ||
          el.classList.toString().includes('disabled') ||
          el.getAttribute('aria-disabled') === 'true';

        if (!isUnavailable) {
          const sizeVal = el.getAttribute('data-size') || el.textContent.trim();
          if (sizeVal && sizeVal.length < 10) {
            sizes.push(sizeVal);
          }
        }
      });

      // Method 2: Product data attributes
      const productData = card.getAttribute('data-product') || card.getAttribute('data-info');
      if (productData) {
        try {
          const data = JSON.parse(productData);
          if (data.sizes) {
            data.sizes.forEach(s => {
              if (s.availability !== 'out_of_stock') {
                sizes.push(s.name || s.size || String(s));
              }
            });
          }
          if (data.availableSizes) {
            sizes.push(...data.availableSizes);
          }
        } catch (e) {
          // Not valid JSON
        }
      }

      // Method 3: Structured data
      const scriptTags = card.querySelectorAll('script[type="application/ld+json"]');
      scriptTags.forEach(script => {
        try {
          const data = JSON.parse(script.textContent);
          if (data.offers) {
            const offers = Array.isArray(data.offers) ? data.offers : [data.offers];
            offers.forEach(offer => {
              if (offer.size && offer.availability !== 'https://schema.org/OutOfStock') {
                sizes.push(offer.size);
              }
            });
          }
        } catch (e) {
          // Ignore
        }
      });

      // Method 4: Size buttons/labels in hover or expanded view
      const buttons = card.querySelectorAll('button, [role="option"]');
      buttons.forEach(btn => {
        const text = btn.textContent.trim();
        const sizePattern = /^(XXS|XS|S|M|L|XL|XXL|1X|2X|3X|4X|5X|\d{1,2}(\.5)?|EU\s*\d{2,3})$/i;
        if (sizePattern.test(text) && !btn.disabled) {
          sizes.push(text);
        }
      });

      return [...new Set(sizes)];
    },

    /**
     * Observe DOM changes for Zara's SPA navigation and infinite scroll.
     */
    observeChanges(callback) {
      const observer = new MutationObserver((mutations) => {
        let hasNewProducts = false;
        for (const mutation of mutations) {
          if (mutation.addedNodes.length > 0) {
            for (const node of mutation.addedNodes) {
              if (node.nodeType === 1 && (
                node.matches?.('li[class*="product"]') ||
                node.querySelector?.('li[class*="product"]') ||
                node.matches?.('div[data-productid]') ||
                node.querySelector?.('div[data-productid]')
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

      const target = document.querySelector('main, [id*="app"], [class*="product-grid"]') || document.body;
      observer.observe(target, { childList: true, subtree: true });

      // Also re-apply on URL changes (SPA navigation)
      let lastUrl = location.href;
      const urlObserver = new MutationObserver(() => {
        if (location.href !== lastUrl) {
          lastUrl = location.href;
          setTimeout(callback, 500);
        }
      });
      urlObserver.observe(document.querySelector('head > title') || document.head, {
        childList: true, subtree: true, characterData: true
      });
    }
  };

  setTimeout(() => CurveFilter.init(zaraAdapter), 1000);
})();
