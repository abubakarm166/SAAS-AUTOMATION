const els = {
  apiUrl: document.getElementById("api-url"),
  dashboardUrl: document.getElementById("dashboard-url"),
  email: document.getElementById("email"),
  password: document.getElementById("password"),
  saveBtn: document.getElementById("save-btn"),
  loginBtn: document.getElementById("login-btn"),
  logoutBtn: document.getElementById("logout-btn"),
  message: document.getElementById("message"),
};

function showMessage(text, type = "success") {
  els.message.textContent = text;
  els.message.className = `message ${type}`;
  els.message.classList.remove("hidden");
}

async function load() {
  const settings = await getSettings();
  els.apiUrl.value = settings.apiUrl;
  els.dashboardUrl.value = settings.dashboardUrl;
  els.email.value = settings.email;
}

els.saveBtn.addEventListener("click", async () => {
  await saveSettings({
    apiUrl: els.apiUrl.value.trim(),
    dashboardUrl: els.dashboardUrl.value.trim(),
    email: els.email.value.trim(),
  });
  showMessage("Settings saved");
});

els.loginBtn.addEventListener("click", async () => {
  try {
    await saveSettings({
      apiUrl: els.apiUrl.value.trim(),
      dashboardUrl: els.dashboardUrl.value.trim(),
    });
    await login(els.email.value.trim(), els.password.value);
    showMessage("Signed in successfully");
  } catch (error) {
    showMessage(error.message, "error");
  }
});

els.logoutBtn.addEventListener("click", async () => {
  await clearAuth();
  els.password.value = "";
  showMessage("Signed out");
});

document.addEventListener("DOMContentLoaded", load);
