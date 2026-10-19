chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.sync.set({
    snapshot_api_url: "https://snapshotanalytics.io/api",
    snapshot_dashboard_url: "https://snapshotanalytics.io",
  });
});
