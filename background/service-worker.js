// CurveFilter Background Service Worker

// Set default preferences on install
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === 'install') {
    chrome.storage.sync.set({
      curveFilterPrefs: {
        enabled: true,
        letterSizes: [],
        numericSizes: [],
        waistSizes: [],
        shoeSizes: [],
        filterMode: 'gray'
      }
    });
  }
});

// Listen for messages from content scripts
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'GET_PREFS') {
    chrome.storage.sync.get(['curveFilterPrefs'], (result) => {
      sendResponse(result.curveFilterPrefs || { enabled: false });
    });
    return true; // Keep message channel open for async response
  }
});
