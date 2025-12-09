# Deployment Checklist - Follow This Step by Step

## Pre-Deployment Checklist

### ☐ Accounts Setup (5 minutes)
- [ ] Google account created/ready
- [ ] GitHub account created at https://github.com/signup
- [ ] Railway account created at https://railway.app (use GitHub login)

### ☐ Files Ready
- [ ] Downloaded production folder from Claude
- [ ] Have Pirana_Upload_Build_COMPLETE.xlsx
- [ ] Have Parts_For_Google_Sheets.csv

---

## Phase 1: Google Sheets Setup (15 minutes)

### ☐ Upload Data to Google Sheets
- [ ] Go to https://sheets.google.com
- [ ] Create new blank spreadsheet
- [ ] File > Import > Upload
- [ ] Select `Pirana_Upload_Build_COMPLETE.xlsx`
- [ ] Import location: "Replace spreadsheet"
- [ ] Click "Import data"
- [ ] Wait for import to complete
- [ ] Rename sheet tab to "Parts" (bottom left)
- [ ] Verify: Should see 3,294 rows + 1 header row

### ☐ Get Sheet ID
- [ ] Look at URL bar
- [ ] Copy the ID between `/d/` and `/edit`
- [ ] Example: `1ngfZOQCAciUVZXKtrgoNz0-vQX31VSf3`
- [ ] Save this ID in a text file for later

**Your Sheet ID:** ___________________________________________

### ☐ Create Google Cloud Project
- [ ] Go to https://console.cloud.google.com
- [ ] Click "Select a project" dropdown (top)
- [ ] Click "New Project"
- [ ] Name: `EP-Inventory`
- [ ] Click "Create"
- [ ] Wait ~30 seconds for creation

### ☐ Enable Google Sheets API
- [ ] In Cloud Console: APIs & Services > Library
- [ ] Search: "Google Sheets API"
- [ ] Click on it
- [ ] Click "Enable"
- [ ] Wait ~10 seconds

### ☐ Create Service Account
- [ ] Go to: APIs & Services > Credentials
- [ ] Click "+ Create Credentials"
- [ ] Select "Service Account"
- [ ] Service account name: `ep-inventory-service`
- [ ] Click "Create and Continue"
- [ ] Skip roles (click Continue)
- [ ] Skip user access (click Done)

### ☐ Generate JSON Key
- [ ] Click on the service account you just created
- [ ] Go to "Keys" tab
- [ ] Add Key > Create new key
- [ ] Choose JSON
- [ ] Click Create
- [ ] File downloads automatically
- [ ] **IMPORTANT**: Save this file securely!

### ☐ Share Sheet with Service Account
- [ ] Open the downloaded JSON file
- [ ] Find `"client_email"` (looks like: `ep-inventory-service@...iam.gserviceaccount.com`)
- [ ] Copy the full email address
- [ ] Go back to your Google Sheet
- [ ] Click "Share" button (top right)
- [ ] Paste the service account email
- [ ] Set permission to "Editor"
- [ ] **UNCHECK** "Notify people"
- [ ] Click "Share"

**Service Account Email:** ___________________________________________

✅ **Phase 1 Complete!** Google Sheets is ready.

---

## Phase 2: GitHub Setup (5 minutes)

### ☐ Create Repository
- [ ] Go to https://github.com/new
- [ ] Repository name: `ep-inventory-system`
- [ ] Description: "EP Engineering Stores Inventory Management"
- [ ] Choose "Public" (required for free Railway)
- [ ] **DO NOT** initialize with README
- [ ] Click "Create repository"

### ☐ Upload Files
Choose ONE method:

**Method A: Web Upload (Easier)**
- [ ] On your repo page: "Add file" > "Upload files"
- [ ] Drag ALL files from production folder:
  - [ ] app.py
  - [ ] requirements.txt
  - [ ] Procfile
  - [ ] runtime.txt
  - [ ] .gitignore
  - [ ] README.md
  - [ ] static/ folder (contains index.html)
- [ ] Commit message: "Initial commit"
- [ ] Click "Commit changes"
- [ ] Verify all files appear in repo

**Method B: Git Command Line**
```bash
cd /path/to/production
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/ep-inventory-system.git
git branch -M main
git push -u origin main
```

### ☐ Verify Upload
- [ ] Refresh GitHub page
- [ ] Should see all files listed
- [ ] Click on app.py to verify code is there
- [ ] Click on static/index.html to verify HTML is there

**Your GitHub Repo URL:** ___________________________________________

✅ **Phase 2 Complete!** Code is on GitHub.

---

## Phase 3: Railway Deployment (10 minutes)

### ☐ Create Railway Project
- [ ] Go to https://railway.app/dashboard
- [ ] Click "New Project"
- [ ] Select "Deploy from GitHub repo"
- [ ] Choose `ep-inventory-system` from list
- [ ] Railway auto-detects Python app
- [ ] Click "Deploy Now"
- [ ] Wait for initial build (~2 minutes)

### ☐ Add Environment Variables
- [ ] Click on your service/project
- [ ] Go to "Variables" tab
- [ ] Click "+ New Variable"

**Variable 1: GOOGLE_SHEET_ID**
- [ ] Variable name: `GOOGLE_SHEET_ID`
- [ ] Value: Paste your Sheet ID from Phase 1
- [ ] Click "Add"

**Variable 2: GOOGLE_CREDENTIALS_JSON**
- [ ] Click "+ New Variable" again
- [ ] Variable name: `GOOGLE_CREDENTIALS_JSON`
- [ ] Value: Open your downloaded JSON file in text editor
- [ ] Copy ENTIRE contents (including `{ }`)
- [ ] Paste into value field
- [ ] Click "Add"

### ☐ Wait for Redeploy
- [ ] Railway automatically redeploys with new variables
- [ ] Wait ~2 minutes
- [ ] Check "Deployments" tab
- [ ] Latest deployment should show "Success" or "Active"

### ☐ Generate Public Domain
- [ ] Go to "Settings" tab
- [ ] Scroll to "Environment"
- [ ] Click "Generate Domain"
- [ ] Railway creates a URL like:
  `https://ep-inventory-system-production.up.railway.app`
- [ ] Copy this URL

**Your Railway URL:** ___________________________________________

✅ **Phase 3 Complete!** App is deployed!

---

## Phase 4: Testing (5 minutes)

### ☐ Basic Functionality Test
- [ ] Open your Railway URL in browser
- [ ] Page loads successfully (shows "EP Engineering Stores")
- [ ] Can see stats (Total Parts, Critical, Low Stock)
- [ ] Parts load in "ALL" tab

### ☐ Search Test
- [ ] Click search box
- [ ] Type: `9006507` (or any part code you know)
- [ ] Click search button
- [ ] Results appear
- [ ] Part details show correctly

### ☐ Stock Update Test
- [ ] Find any part in the list
- [ ] Note current stock value
- [ ] Enter new value in update box
- [ ] Click "Update" button
- [ ] Should see success message
- [ ] Go to Google Sheets
- [ ] Find same part
- [ ] Verify stock value changed

### ☐ Critical Parts Test
- [ ] Click "CRITICAL" tab
- [ ] Critical parts load
- [ ] Shows parts marked as Critical
- [ ] Color coding appears (red/gold badges)

### ☐ Mobile Test
- [ ] Open URL on phone or tablet
- [ ] Interface is mobile-friendly
- [ ] Can search and update from mobile
- [ ] All features work

### ☐ Multi-User Test
- [ ] Share URL with colleague
- [ ] Both access at same time
- [ ] One person updates a part
- [ ] Other person refreshes
- [ ] Change appears for both

✅ **Phase 4 Complete!** Everything works!

---

## Phase 5: Team Rollout (10 minutes)

### ☐ Share with Team
- [ ] Copy your Railway URL
- [ ] Send to team via email/Slack/Teams
- [ ] Include brief instructions (see below)

**Message Template:**
```
Hi Team,

Our new inventory system is now live!

🔗 URL: [Your Railway URL]

📱 How to use:
1. Open the URL on any device (phone, tablet, computer)
2. Search for parts using the search box
3. Update stock levels directly from the app
4. Changes sync instantly to everyone

💡 Tips:
- Bookmark the URL or add to home screen
- Works on all devices, no app install needed
- Everyone can use it at the same time
- Updates appear in real-time

For bulk edits, you can also edit the Google Sheet directly:
[Your Google Sheets URL]

Questions? Let me know!
```

### ☐ Create Shortcuts
- [ ] Desktop: Bookmark in browser
- [ ] Mobile (iOS): Safari > Share > Add to Home Screen
- [ ] Mobile (Android): Chrome > Menu > Add to Home Screen

### ☐ Brief Training
- [ ] Show how to search
- [ ] Show how to update stock
- [ ] Show critical parts tab
- [ ] Show how to read bin locations
- [ ] Explain Google Sheets can also be edited

✅ **Phase 5 Complete!** Team is onboarded!

---

## Post-Deployment Checklist

### ☐ Documentation
- [ ] Save all URLs in a secure document
- [ ] Save Google Cloud credentials securely
- [ ] Document any custom changes made
- [ ] Keep backup of JSON key file

### ☐ Monitoring Setup
- [ ] Bookmark Railway dashboard
- [ ] Set up error notifications (Railway settings)
- [ ] Check deployment logs weekly
- [ ] Monitor usage stats

### ☐ Maintenance Schedule
- [ ] Weekly: Check critical parts list
- [ ] Weekly: Review stock levels
- [ ] Monthly: Verify all data accurate
- [ ] Monthly: Check Railway usage/costs
- [ ] Quarterly: Review and update part list

---

## Troubleshooting Common Issues

### ❌ "Error loading parts"
**Cause:** Google Sheets not properly shared or API not enabled
**Fix:**
1. Verify Sheet shared with service account (Editor access)
2. Check Google Sheets API is enabled in Cloud Console
3. Verify GOOGLE_SHEET_ID is correct in Railway
4. Check Railway deployment logs for specific error

### ❌ "Can't update stock"
**Cause:** Service account has Viewer instead of Editor permissions
**Fix:**
1. Go to Google Sheets
2. Click Share
3. Find service account email
4. Change permission to "Editor"
5. Save

### ❌ App won't load / Railway error
**Cause:** Missing environment variables or build error
**Fix:**
1. Go to Railway > Variables tab
2. Verify both variables are set
3. Check GOOGLE_CREDENTIALS_JSON is complete JSON (starts with `{`, ends with `}`)
4. Go to Deployments > Latest > View Logs
5. Look for specific error message

### ❌ Changes not syncing
**Cause:** Network issue or API rate limit
**Fix:**
1. Refresh the page
2. Check internet connection
3. Wait 1 minute and try again
4. Check Railway logs for API errors

---

## Success Criteria

You're successful when:
- [✓] All 3,294 parts visible in app
- [✓] Search returns correct results
- [✓] Stock updates work and sync to Sheets
- [✓] Critical parts tab shows 72+ critical items
- [✓] Mobile interface works smoothly
- [✓] Multiple users can access simultaneously
- [✓] Team is using it for daily operations

---

## Additional Resources

- **Quick Start:** QUICK_START.md (10 min guide)
- **Full Guide:** DEPLOYMENT_GUIDE.md (detailed 40 min guide)
- **Technical Docs:** README.md
- **Railway Docs:** https://docs.railway.app
- **Google Sheets API:** https://developers.google.com/sheets

---

## Completion

Date Deployed: _______________

Railway URL: _______________________________________________

Google Sheet URL: _______________________________________________

Team Members with Access: _________________________________

---

**Congratulations! Your inventory system is live! 🎉**

Print this checklist and check off items as you complete them.
