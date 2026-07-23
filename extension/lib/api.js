async function apiRequest(path, options = {}, auth = true) {
  const { apiUrl, token } = await getSettings();
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };
  if (auth && token) headers.Authorization = `Bearer ${token}`;

  const response = await fetch(`${apiUrl}${path}`, { ...options, headers });
  let body = null;
  const text = await response.text();
  if (text) {
    try {
      body = JSON.parse(text);
    } catch {
      body = { detail: text };
    }
  }

  if (!response.ok) {
    const detail = body?.detail ?? response.statusText;
    const message = Array.isArray(detail)
      ? detail.map((d) => d.msg || JSON.stringify(d)).join(", ")
      : String(detail);
    const error = new Error(message);
    error.status = response.status;
    throw error;
  }
  return body;
}

async function login(email, password) {
  const data = await apiRequest(
    "/auth/login",
    { method: "POST", body: JSON.stringify({ email, password }) },
    false,
  );
  await saveSettings({ token: data.access_token, email });
  return data;
}

async function createJob(payload) {
  return apiRequest("/jobs", { method: "POST", body: JSON.stringify(payload) });
}

async function getJob(jobId) {
  return apiRequest(`/jobs/${jobId}`);
}

if (typeof globalThis !== "undefined") {
  globalThis.apiRequest = apiRequest;
  globalThis.login = login;
  globalThis.createJob = createJob;
  globalThis.getJob = getJob;
}
