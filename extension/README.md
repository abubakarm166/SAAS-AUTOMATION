# SnapShot Chrome Extension (Manifest V3)

Capture the current page URL, scan for US property addresses, and submit jobs to the SnapShot API.

## Features

- Sign in with your SnapShot account (JWT stored in `chrome.storage.sync`)
- Auto-fills **source URL** from the active tab
- **Scan page** extracts likely street addresses from visible text
- Submit job → Celery worker processes it → view status in dashboard

## Install (developer / unpacked)

1. Open Chrome → `chrome://extensions`
2. Enable **Developer mode**
3. Click **Load unpacked**
4. Select this `extension/` folder

## Configure

1. Click extension **⚙ Settings** (or right-click icon → Options)
2. Set:
   - **API base URL:** `http://16.170.241.9/api` (nginx proxy) or `http://16.170.241.9:8000` (direct)
   - **Dashboard URL:** `http://16.170.241.9`
3. Sign in with your SnapShot email/password

## Usage

1. Open an auction or listing page in Chrome
2. Click the SnapShot extension icon
3. Review scanned addresses (edit or add manually)
4. Click **Create job**
5. **Open in dashboard** to download reports when complete

## Security

- No API keys or secrets in the extension — only user JWT after login
- Tokens stored in `chrome.storage.sync` (Chrome account sync)
- For production, use HTTPS API + dashboard URLs

## CORS

The extension calls the API directly via `host_permissions`, so browser CORS does not apply. The dashboard CORS settings are unrelated.

## Chrome Web Store

For private team use, distribute the unpacked folder or pack as `.crx`. Public listing requires Web Store review and a one-time developer fee.

## Project layout

```
extension/
  manifest.json       MV3 manifest
  popup.html/js/css   Main UI
  options.html/js     API URL + login
  content.js          Page address scanner
  background.js       Install defaults
  lib/
    api.js            API client
    storage.js        Settings + auth
    address.js        Address regex extraction
    defaults.js       Default job financial inputs
```
