chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.sync.get(["snapshot_api_url"], (data) => {
    if (!data.snapshot_api_url) {
      chrome.storage.sync.set({
        snapshot_api_url: "http://16.170.241.9/api",
        snapshot_dashboard_url: "http://16.170.241.9",
      });
    }
  });
});
