const STORAGE_KEYS = {
  apiUrl: "snapshot_api_url",
  dashboardUrl: "snapshot_dashboard_url",
  token: "snapshot_token",
  email: "snapshot_email",
};

const DEFAULTS = {
  apiUrl: "http://16.170.241.9/api",
  dashboardUrl: "http://16.170.241.9",
};

async function getSettings() {
  const data = await chrome.storage.sync.get(Object.values(STORAGE_KEYS));
  return {
    apiUrl: (data[STORAGE_KEYS.apiUrl] || DEFAULTS.apiUrl).replace(/\/$/, ""),
    dashboardUrl: (data[STORAGE_KEYS.dashboardUrl] || DEFAULTS.dashboardUrl).replace(/\/$/, ""),
    token: data[STORAGE_KEYS.token] || "",
    email: data[STORAGE_KEYS.email] || "",
  };
}

async function saveSettings(partial) {
  const payload = {};
  if (partial.apiUrl !== undefined) payload[STORAGE_KEYS.apiUrl] = partial.apiUrl.replace(/\/$/, "");
  if (partial.dashboardUrl !== undefined) {
    payload[STORAGE_KEYS.dashboardUrl] = partial.dashboardUrl.replace(/\/$/, "");
  }
  if (partial.token !== undefined) payload[STORAGE_KEYS.token] = partial.token;
  if (partial.email !== undefined) payload[STORAGE_KEYS.email] = partial.email;
  await chrome.storage.sync.set(payload);
}

async function clearAuth() {
  await chrome.storage.sync.remove([STORAGE_KEYS.token, STORAGE_KEYS.email]);
}

if (typeof globalThis !== "undefined") {
  globalThis.STORAGE_KEYS = STORAGE_KEYS;
  globalThis.getSettings = getSettings;
  globalThis.saveSettings = saveSettings;
  globalThis.clearAuth = clearAuth;
}
