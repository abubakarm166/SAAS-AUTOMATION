# SnapShot Property Report  
## User Guide

| | |
|---|---|
| **Prepared for** | Hatem & SnapShot subscribers |
| **Prepared by** | Dextersol |
| **Product** | SnapShot — Cloud-Hosted Property Report Automation |
| **Status** | Live / completed |
| **Date** | September 2026 |

This guide explains how to use SnapShot every day. For formal project handover and acceptance, see the **Delivery Document**.

---

## 1. What SnapShot does

SnapShot generates professional **property reports** in the cloud.

You (or your subscribers):

1. Sign up and subscribe  
2. Submit one or more US property addresses  
3. Wait while the cloud system builds the report  
4. **Download** the PDF and Excel from the dashboard  
5. Optionally **receive the same files by email** (when a recipient email is entered)

No Windows PC or remote desktop is required for end users — only a web browser (and Chrome if using the extension).

---

## 2. Web dashboard

### 2.1 Sign up / log in

1. Open the SnapShot dashboard in your browser.  
2. **Sign up** with email and password (at least 8 characters), or **Log in** if you already have an account.

### 2.2 Subscribe (required to create jobs)

1. Go to **Billing**.  
2. Complete **Stripe Checkout** for the plan.  
3. When the subscription is **active**, you can create jobs.

Without an active subscription, the system will send you to Billing when you try to create a job.

### 2.3 Create a job

1. Open **New job**.  
2. (Optional) Paste the auction / listing **source URL**.  
3. Enter **Recipient email** if you want the reports emailed when the job finishes.  
4. Add one or more **property addresses**.  
5. Adjust financial assumptions if needed, or keep the defaults:  
   - Interest rate, loan years  
   - Discount %, closing costs, money down  
   - Operating expenses, vacancy, lender LTV  
   - Rehab / refinance estimates, holding months  
6. Click **Create job**.

### 2.4 Track status

| Status | Meaning |
|--------|---------|
| **Queued** | Waiting for the cloud worker |
| **Running** | Report is being generated |
| **Completed** | Ready — download and/or check email |
| **Failed** | Something went wrong; see the error or contact support |

### 2.5 Download reports

On the **job detail** page, when status is **Completed**:

- Download the **Property Report (PDF)**  
- Download the **Listings Report Data (Excel)**  

### 2.6 Job history

The **Dashboard** lists your past and current jobs. Each user only sees their own jobs.

---

## 3. Email delivery

Email is **working** on the completed platform.

| Requirement | Detail |
|-------------|--------|
| When it sends | After a job **completes** successfully |
| What is sent | PDF property report(s) + Excel listings file |
| From address | Your configured SnapShot sending mailbox (e.g. reports@…) |
| How to enable for a job | Fill in **Recipient email** when creating the job |

**Tips**

- If the field is left empty, the job still completes and files remain available for **download** — email is simply not sent.  
- Check **Spam / Junk** if the message is delayed.  
- Use a real inbox you can access for testing.

---

## 4. Chrome extension

Use the extension when you are already on an auction or listing page.

### 4.1 Install (team / private)

1. Chrome → `chrome://extensions`  
2. Enable **Developer mode**  
3. **Load unpacked** → select the SnapShot extension folder provided by Dextersol  
4. Pin the icon to the toolbar if you like  

### 4.2 Configure once

1. Open extension **Options / Settings**.  
2. Confirm the API and Dashboard URLs given for your environment.  
3. Sign in with your SnapShot account.

### 4.3 Create a job from a page

1. Open the listing / auction page.  
2. Click the **SnapShot** icon.  
3. Confirm the page URL.  
4. **Scan page** for addresses; edit or add manually.  
5. Add recipient email if you want email delivery.  
6. **Create job** → open the dashboard to track and download.

The extension never stores your RentCast, Google Maps, or other server API keys — only your login session.

---

## 5. Reports you get

| File | Contents |
|------|----------|
| **Property Report (PDF)** | Full analysis — imagery, calculations, charts (aligned with your original tool) |
| **Listings Report Data (Excel)** | Spreadsheet summary / listings data |

Same outputs are available via **dashboard download** and (when recipient is set) **email attachment**.

---

## 6. Billing (quick reference)

| Topic | Detail |
|-------|--------|
| Provider | Stripe |
| Where | Dashboard → **Billing** |
| Rule | Active (or trialing) subscription required to create jobs |
| Cards | Handled by Stripe — not stored in SnapShot |

---

## 7. Troubleshooting

| Problem | What to try |
|---------|-------------|
| Cannot create a job | Check **Billing** — subscription must be active |
| Job stuck on queued | Worker may be offline — contact your operator / Dextersol |
| Job failed | Read the error on the job page; fix address data and retry |
| No email received | Confirm **recipient email** was set; check spam; confirm job is **Completed** |
| Extension cannot sign in | Recheck API/Dashboard URLs in extension options |
| Cannot see another user’s jobs | Expected — accounts are isolated |

---

## 8. Security (for users)

- Use a strong unique password for your SnapShot account.  
- Do not share your login with others if you need separate job history.  
- Download links expire after a limited time — download when the job completes.  
- Never ask SnapShot support to put third-party API keys into the Chrome extension — they belong only on the servers.

---

## 9. Demo checklist (for training)

1. Sign up / log in  
2. Confirm subscription  
3. Create job with address + recipient email  
4. Wait for **Completed**  
5. Download PDF + Excel  
6. Confirm email arrived  
7. Create a job from the Chrome extension on a live listing page  

---

## 10. Support

| | |
|---|---|
| **Product** | SnapShot Property Report |
| **Client / owner** | Hatem |
| **Delivery partner** | Dextersol |

For access URLs, extension package, or platform issues, contact your Dextersol project lead.

---

*SnapShot User Guide — September 2026*  
*© Dextersol — Prepared for Hatem*
