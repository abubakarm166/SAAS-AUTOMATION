const els = {
  userLabel: document.getElementById("user-label"),
  loginPanel: document.getElementById("login-panel"),
  jobPanel: document.getElementById("job-panel"),
  statusPanel: document.getElementById("status-panel"),
  loginEmail: document.getElementById("login-email"),
  loginPassword: document.getElementById("login-password"),
  loginBtn: document.getElementById("login-btn"),
  settingsBtn: document.getElementById("settings-btn"),
  sourceUrl: document.getElementById("source-url"),
  addressList: document.getElementById("address-list"),
  addAddressBtn: document.getElementById("add-address-btn"),
  scanBtn: document.getElementById("scan-btn"),
  recipientEmail: document.getElementById("recipient-email"),
  submitBtn: document.getElementById("submit-btn"),
  statusTitle: document.getElementById("status-title"),
  statusDetail: document.getElementById("status-detail"),
  dashboardLink: document.getElementById("dashboard-link"),
  newJobBtn: document.getElementById("new-job-btn"),
  message: document.getElementById("message"),
};

let pollTimer = null;

function showMessage(text, type = "error") {
  els.message.textContent = text;
  els.message.className = `message ${type}`;
  els.message.classList.remove("hidden");
}

function clearMessage() {
  els.message.classList.add("hidden");
}

function showPanel(panel) {
  [els.loginPanel, els.jobPanel, els.statusPanel].forEach((el) => el.classList.add("hidden"));
  panel.classList.remove("hidden");
}

function createAddressRow(value = "") {
  const row = document.createElement("div");
  row.className = "address-row";

  const input = document.createElement("input");
  input.type = "text";
  input.className = "input address-input";
  input.placeholder = "123 Main St, City, ST 12345";
  input.value = value;

  const removeBtn = document.createElement("button");
  removeBtn.type = "button";
  removeBtn.className = "remove-btn";
  removeBtn.textContent = "×";
  removeBtn.title = "Remove";
  removeBtn.addEventListener("click", () => {
    const rows = els.addressList.querySelectorAll(".address-row");
    if (rows.length <= 1) {
      input.value = "";
      return;
    }
    row.remove();
  });

  row.appendChild(input);
  row.appendChild(removeBtn);
  return row;
}

function setAddresses(addresses) {
  els.addressList.innerHTML = "";
  const values = addresses.length ? addresses : [""];
  values.forEach((addr) => els.addressList.appendChild(createAddressRow(addr)));
}

function getAddresses() {
  return [...els.addressList.querySelectorAll(".address-input")]
    .map((input) => input.value.trim())
    .filter(Boolean);
}

async function getActiveTab() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  return tab;
}

async function scanCurrentPage() {
  clearMessage();
  const tab = await getActiveTab();
  if (!tab?.id) {
    showMessage("No active tab found");
    return;
  }

  els.sourceUrl.value = tab.url || "";

  try {
    const response = await chrome.tabs.sendMessage(tab.id, { type: "extract_addresses" });
    if (!response?.ok) {
      showMessage(response?.error || "Could not scan this page");
      return;
    }
    if (response.addresses?.length) {
      setAddresses(response.addresses);
      showMessage(`Found ${response.addresses.length} address(es)`, "success");
    } else {
      showMessage("No addresses found — enter manually", "error");
    }
  } catch {
    showMessage("Reload the page and try again (extension needs a fresh page load)");
  }
}

async function initJobPanel() {
  const tab = await getActiveTab();
  els.sourceUrl.value = tab?.url || "";
  setAddresses([""]);
  els.recipientEmail.value = "";
  showPanel(els.jobPanel);
  await scanCurrentPage();
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer);
    pollTimer = null;
  }
}

async function pollJob(jobId) {
  stopPolling();
  pollTimer = setInterval(async () => {
    try {
      const job = await getJob(jobId);
      els.statusTitle.textContent = `Job ${job.status}`;
      els.statusDetail.textContent = job.error_message || `Job ID: ${job.id}`;
      if (job.status === "completed" || job.status === "failed") {
        stopPolling();
      }
    } catch (error) {
      stopPolling();
      showMessage(error.message);
    }
  }, 3000);
}

async function submitJob() {
  clearMessage();
  const addresses = getAddresses();
  if (!addresses.length) {
    showMessage("At least one address is required");
    return;
  }

  els.submitBtn.disabled = true;
  try {
    const payload = {
      source_url: els.sourceUrl.value.trim() || undefined,
      inputs: {
        ...DEFAULT_JOB_INPUTS,
        addresses,
        recipient_email: els.recipientEmail.value.trim() || null,
      },
    };
    const job = await createJob(payload);
    const { dashboardUrl } = await getSettings();
    els.dashboardLink.href = `${dashboardUrl}/jobs/${job.id}`;
    els.statusTitle.textContent = `Job ${job.status}`;
    els.statusDetail.textContent = `Job ID: ${job.id}`;
    showPanel(els.statusPanel);
    pollJob(job.id);
  } catch (error) {
    if (error.status === 401) {
      await clearAuth();
      showPanel(els.loginPanel);
      showMessage("Session expired — sign in again");
      return;
    }
    if (error.status === 402) {
      showMessage("Active subscription required — open billing in dashboard");
      return;
    }
    showMessage(error.message);
  } finally {
    els.submitBtn.disabled = false;
  }
}

async function init() {
  els.settingsBtn.addEventListener("click", () => chrome.runtime.openOptionsPage());
  els.loginBtn.addEventListener("click", async () => {
    clearMessage();
    els.loginBtn.disabled = true;
    try {
      await login(els.loginEmail.value.trim(), els.loginPassword.value);
      const { email } = await getSettings();
      els.userLabel.textContent = email;
      await initJobPanel();
    } catch (error) {
      showMessage(error.message);
    } finally {
      els.loginBtn.disabled = false;
    }
  });
  els.scanBtn.addEventListener("click", scanCurrentPage);
  els.addAddressBtn.addEventListener("click", () => {
    els.addressList.appendChild(createAddressRow());
  });
  els.submitBtn.addEventListener("click", submitJob);
  els.newJobBtn.addEventListener("click", async () => {
    stopPolling();
    clearMessage();
    await initJobPanel();
  });

  const { token, email } = await getSettings();
  if (token) {
    els.userLabel.textContent = email || "Signed in";
    await initJobPanel();
  } else {
    els.userLabel.textContent = "Not signed in";
    showPanel(els.loginPanel);
  }
}

document.addEventListener("DOMContentLoaded", init);
