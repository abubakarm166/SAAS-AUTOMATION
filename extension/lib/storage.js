const STORAGE_KEYS = {
  apiUrl: "snapshot_api_url",
  dashboardUrl: "snapshot_dashboard_url",
  token: "snapshot_token",
  email: "snapshot_email",
};

const DEFAULTS = {
  apiUrl: "https://snapshotanalytics.io/api",
  dashboardUrl: "https://snapshotanalytics.io",
};

function normalizeApiUrl(raw) {
  let url = (raw || DEFAULTS.apiUrl).trim().replace(/\/$/, "");
  if (!url) url = DEFAULTS.apiUrl;
  if (/^https?:\/\/16\.170\.241\.9(?::8000)?$/i.test(url) || /^https?:\/\/16\.170\.241\.9\/api$/i.test(url)) {
    url = DEFAULTS.apiUrl;
  }
  if (/^https?:\/\/snapshotanalytics\.io$/i.test(url)) {
    url = `${url}/api`;
  }
  return url.replace(/\/$/, "");
}

function normalizeDashboardUrl(raw) {
  let url = (raw || DEFAULTS.dashboardUrl).trim().replace(/\/$/, "");
  if (!url || /^https?:\/\/16\.170\.241\.9(?::3000)?$/i.test(url)) {
    url = DEFAULTS.dashboardUrl;
  }
  return url.replace(/\/$/, "");
}

async function getSettings() {
  const data = await chrome.storage.sync.get(Object.values(STORAGE_KEYS));
  return {
    apiUrl: normalizeApiUrl(data[STORAGE_KEYS.apiUrl] || DEFAULTS.apiUrl),
    dashboardUrl: normalizeDashboardUrl(data[STORAGE_KEYS.dashboardUrl] || DEFAULTS.dashboardUrl),
    token: data[STORAGE_KEYS.token] || "",
    email: data[STORAGE_KEYS.email] || "",
  };
}

async function saveSettings(partial) {
  const payload = {};
  if (partial.apiUrl !== undefined) payload[STORAGE_KEYS.apiUrl] = normalizeApiUrl(partial.apiUrl);
  if (partial.dashboardUrl !== undefined) {
    payload[STORAGE_KEYS.dashboardUrl] = normalizeDashboardUrl(partial.dashboardUrl);
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
