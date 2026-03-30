document.addEventListener('DOMContentLoaded', () => {
  const enableToggle = document.getElementById('enableToggle');
  const letterSize = document.getElementById('letterSize');
  const numericSize = document.getElementById('numericSize');
  const waistSize = document.getElementById('waistSize');
  const shoeSize = document.getElementById('shoeSize');
  const saveBtn = document.getElementById('saveBtn');
  const status = document.getElementById('status');

  // Load saved preferences
  chrome.storage.sync.get(['curveFilterPrefs'], (result) => {
    const prefs = result.curveFilterPrefs || {};

    enableToggle.checked = prefs.enabled !== false;

    if (prefs.letterSizes) setSelected(letterSize, prefs.letterSizes);
    if (prefs.numericSizes) setSelected(numericSize, prefs.numericSizes);
    if (prefs.waistSizes) setSelected(waistSize, prefs.waistSizes);
    if (prefs.shoeSizes) setSelected(shoeSize, prefs.shoeSizes);

    if (prefs.filterMode) {
      const radio = document.querySelector(`input[name="filterMode"][value="${prefs.filterMode}"]`);
      if (radio) radio.checked = true;
    }
  });

  saveBtn.addEventListener('click', () => {
    const filterMode = document.querySelector('input[name="filterMode"]:checked').value;

    const prefs = {
      enabled: enableToggle.checked,
      letterSizes: getSelected(letterSize),
      numericSizes: getSelected(numericSize),
      waistSizes: getSelected(waistSize),
      shoeSizes: getSelected(shoeSize),
      filterMode: filterMode
    };

    chrome.storage.sync.set({ curveFilterPrefs: prefs }, () => {
      status.textContent = 'Preferences saved!';
      setTimeout(() => { status.textContent = ''; }, 2000);

      // Notify active tab to re-apply filters
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (tabs[0]) {
          chrome.tabs.sendMessage(tabs[0].id, {
            type: 'CURVEFILTER_UPDATE',
            prefs: prefs
          }).catch(() => {
            // Tab might not have content script
          });
        }
      });
    });
  });
});

function getSelected(selectEl) {
  return Array.from(selectEl.selectedOptions).map(opt => opt.value);
}

function setSelected(selectEl, values) {
  Array.from(selectEl.options).forEach(opt => {
    opt.selected = values.includes(opt.value);
  });
}
