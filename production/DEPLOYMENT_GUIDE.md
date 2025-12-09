# Complete Deployment Guide: Google Sheets + Railway

## Overview

This guide will help you deploy the EP Engineering Stores inventory system using:
- **Google Sheets** as the database (free, multi-user, real-time)
- **Railway** as the hosting platform (accessible from anywhere)

**Time Required**: 30-40 minutes
**Cost**: FREE (both Google Sheets and Railway have free tiers)

---

## Part 1: Google Sheets Setup (15 minutes)

### Step 1: Upload Your Excel File to Google Sheets

1. Go to https://sheets.google.com
2. Click "Blank" to create a new spreadsheet
3. Click **File > Import**
4. Choose **Upload** tab
5. Click **Browse** and select `Pirana_Upload_Build_COMPLETE.xlsx`
6. Import settings:
   - **Import location**: Replace spreadsheet
   - **Separator type**: Detect automatically
7. Click **Import data**
8. Rename the sheet to "Parts" (bottom tab)

### Step 2: Get Your Google Sheet ID

1. Look at the URL in your browser:
   ```
   https://docs.google.com/spreadsheets/d/1ABC...XYZ/edit
                                          ^^^^^^^^^
                                          This is your Sheet ID
   ```
2. Copy the Sheet ID (the long string between `/d/` and `/edit`)
3. Save it somewhere - you'll need it later

Example Sheet ID: `1ngfZOQCAciUVZXKtrgoNz0-vQX31VSf3`

### Step 3: Create Google Cloud Project

1. Go to https://console.cloud.google.com
2. Click **"Select a project"** at the top
3. Click **"New Project"**
4. Project name: `EP-Inventory` (or any name)
5. Click **Create**
6. Wait for the project to be created (~30 seconds)

### Step 4: Enable Google Sheets API

1. In the Google Cloud Console, go to **APIs & Services > Library**
2. Search for "Google Sheets API"
3. Click on it
4. Click **Enable**
5. Wait for it to enable (~10 seconds)

### Step 5: Create Service Account

1. Go to **APIs & Services > Credentials**
2. Click **+ Create Credentials** at the top
3. Select **Service Account**
4. Fill in:
   - **Service account name**: `ep-inventory-service`
   - **Service account ID**: (auto-fills)
   - **Description**: "Service account for EP inventory system"
5. Click **Create and Continue**
6. **Grant this service account access** (Step 2):
   - Skip this step, click **Continue**
7. **Grant users access** (Step 3):
   - Skip this step, click **Done**

### Step 6: Create Service Account Key

1. Click on the service account you just created
2. Go to the **Keys** tab
3. Click **Add Key > Create new key**
4. Choose **JSON** format
5. Click **Create**
6. A JSON file will download automatically
7. **IMPORTANT**: Keep this file safe! You'll need it in the next section

### Step 7: Share Sheet with Service Account

1. Open the JSON file you downloaded
2. Find the `"client_email"` field - it looks like:
   ```
   "client_email": "ep-inventory-service@ep-inventory-123456.iam.gserviceaccount.com"
   ```
3. Copy this email address
4. Go back to your Google Sheet
5. Click the **Share** button (top right)
6. Paste the service account email
7. Make sure it has **Editor** permissions
8. **UNCHECK** "Notify people" (it's a service account, not a person)
9. Click **Share** or **Send**

✅ **Google Sheets Setup Complete!**

---

## Part 2: Railway Deployment (15-20 minutes)

### Step 1: Create GitHub Repository

1. Go to https://github.com
2. Log in (or create an account if you don't have one)
3. Click the **+** icon (top right) > **New repository**
4. Repository name: `ep-inventory-system`
5. Description: "EP Engineering Stores Inventory Management"
6. Choose **Public** (required for free Railway deployment)
7. **DO NOT** check "Initialize with README"
8. Click **Create repository**

### Step 2: Upload Code to GitHub

You have two options:

**Option A: Using GitHub Web Interface (Easier)**

1. On your repository page, click **Add file > Upload files**
2. Drag and drop all files from the `production` folder:
   - `app.py`
   - `requirements.txt`
   - `Procfile`
   - `runtime.txt`
   - `.gitignore`
   - `README.md`
   - `static/` folder (with `index.html` inside)
3. Commit message: "Initial commit - inventory system"
4. Click **Commit changes**

**Option B: Using Git Commands (For developers)**

```bash
cd production
git init
git add .
git commit -m "Initial commit - inventory system"
git remote add origin https://github.com/YOUR_USERNAME/ep-inventory-system.git
git branch -M main
git push -u origin main
```

### Step 3: Create Railway Account

1. Go to https://railway.app
2. Click **Login** (top right)
3. Sign up with **GitHub** (easiest option)
4. Authorize Railway to access your GitHub account

### Step 4: Deploy to Railway

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose your repository: `ep-inventory-system`
4. Railway will automatically detect it's a Python app
5. Click **Deploy Now**
6. Wait for initial deployment (~2 minutes)

### Step 5: Add Environment Variables

1. In your Railway project, click on your service
2. Go to the **Variables** tab
3. Click **+ New Variable**

**Add these two variables:**

**Variable 1: GOOGLE_SHEET_ID**
- Name: `GOOGLE_SHEET_ID`
- Value: Your Sheet ID from Part 1, Step 2
- Example: `1ngfZOQCAciUVZXKtrgoNz0-vQX31VSf3`

**Variable 2: GOOGLE_CREDENTIALS_JSON**
- Name: `GOOGLE_CREDENTIALS_JSON`
- Value: Open the JSON file you downloaded, copy **ENTIRE CONTENTS**
- It should look like:
  ```json
  {
    "type": "service_account",
    "project_id": "ep-inventory-123456",
    "private_key_id": "abc123...",
    "private_key": "-----BEGIN PRIVATE KEY-----\n...",
    "client_email": "ep-inventory-service@...",
    "client_id": "12345...",
    ...
  }
  ```
- Paste the entire JSON (including the `{ }` brackets)

4. Railway will automatically redeploy with the new variables (~2 minutes)

### Step 6: Get Your Public URL

1. Go to the **Settings** tab in Railway
2. Scroll down to **Environment**
3. Click **Generate Domain**
4. Railway will give you a URL like:
   ```
   https://ep-inventory-system-production.up.railway.app
   ```
5. Copy this URL - this is your inventory system!

### Step 7: Test Your Deployment

1. Visit your Railway URL
2. You should see the inventory interface
3. Try searching for a part
4. Try updating a stock level
5. Check Google Sheets - the change should appear!

✅ **Deployment Complete!**

---

## Part 3: Usage & Access

### Accessing the System

**From Computer**:
- Visit: `https://your-railway-url.up.railway.app`

**From Mobile/Tablet**:
- Visit the same URL
- Add to home screen for app-like experience:
  - **iOS**: Tap Share > Add to Home Screen
  - **Android**: Tap Menu (⋮) > Add to Home Screen

### Multiple Users

**Everyone can use the system simultaneously!**
- Updates appear in real-time
- No conflicts - Google Sheets handles concurrent editing
- Each person sees the same data

### Editing the Data

**Two ways to edit**:

1. **Mobile App** (for stock updates on the go):
   - Search for part
   - Enter new stock level
   - Click Update
   
2. **Google Sheets** (for bulk edits):
   - Open the Google Sheet
   - Edit any cell
   - Changes sync to app automatically

### Backup & Version History

Google Sheets automatically:
- Saves every change
- Keeps version history (File > Version history)
- Can restore previous versions anytime

---

## Part 4: Maintenance

### Updating the App

To update code:
1. Make changes to files locally
2. Push to GitHub:
   ```bash
   git add .
   git commit -m "Description of changes"
   git push
   ```
3. Railway automatically redeploys

### Monitoring

Railway provides:
- **Metrics**: CPU, Memory, Network usage
- **Logs**: Real-time application logs
- **Deployments**: History of all deploys

Access in Railway dashboard > Your service

### Costs

**Free Tier Limits**:
- Railway: $5 credit/month (usually enough for this app)
- Google Sheets: Unlimited (completely free)

**If you exceed Railway free tier**:
- Railway will ask you to add payment method
- Typical cost: $1-3/month for light usage

---

## Part 5: Troubleshooting

### Problem: "Error loading parts"

**Check**:
1. Is the Google Sheet shared with the service account?
2. Are environment variables set correctly in Railway?
3. Check Railway logs for specific error

**Fix**:
- Go to **Deployments** tab in Railway
- Click latest deployment
- Check **Build Logs** and **Deploy Logs**

### Problem: "Can't update stock"

**Check**:
1. Service account has **Editor** permissions (not Viewer)
2. Sheet name is exactly "Parts"

**Fix**:
- Re-share sheet with Editor access
- Or rename your sheet to "Parts"

### Problem: Railway app sleeping

**Free tier limitation**:
- Apps sleep after 30 minutes of inactivity
- First request after sleep takes 10-15 seconds

**Fix** (if bothering you):
- Upgrade to Railway Pro ($5/month)
- Or accept the occasional delay

### Problem: Sheet has wrong structure

**Symptom**: Parts loading but data looks wrong

**Fix**:
1. Check column order matches:
   - Column A: Empty
   - Column B: Stock Code
   - Column C: Manufacturer Part Number
   - Column D: Description
   - (etc. - see README.md for full structure)
2. Headers must be in Row 1
3. Data starts in Row 2

---

## Part 6: Advanced Features

### Adding More Sheets

To add new sheets (e.g., "Orders", "Suppliers"):

1. Add sheet to Google Sheets
2. Update `app.py`:
   ```python
   def get_orders_worksheet():
       client = get_sheets_client()
       spreadsheet = client.open_by_key(sheet_id)
       return spreadsheet.worksheet("Orders")
   ```
3. Add new API endpoints
4. Push changes to GitHub

### Restricting Access

To make the system private:

1. **Railway**: Add authentication middleware
2. **Google Sheets**: 
   - Only share with specific people
   - Set service account permissions

### Custom Domain

To use your own domain (e.g., inventory.yourcompany.com):

1. Railway Settings > Domains
2. Add custom domain
3. Update DNS records (Railway provides instructions)

---

## Part 7: Quick Reference

### Important URLs

- Google Cloud Console: https://console.cloud.google.com
- Google Sheets: https://sheets.google.com
- Railway Dashboard: https://railway.app/dashboard
- GitHub: https://github.com

### Key Files

- `app.py` - Main application code
- `requirements.txt` - Python dependencies
- `Procfile` - Railway deployment config
- `static/index.html` - Web interface

### Support Commands

Check Railway logs:
```bash
# In Railway dashboard
Deployments > Latest > Deploy Logs
```

Test locally:
```bash
export GOOGLE_SHEET_ID="your_id"
export GOOGLE_CREDENTIALS_JSON='{"type":"service_account",...}'
python app.py
# Visit http://localhost:5000
```

---

## Success Checklist

Before going live, verify:

- [ ] Google Sheet has all 3,294 parts
- [ ] Service account has Editor access
- [ ] Environment variables set in Railway
- [ ] App loads at Railway URL
- [ ] Can search for parts
- [ ] Can update stock levels
- [ ] Changes sync to Google Sheets
- [ ] Mobile interface works
- [ ] Multiple users can access simultaneously

---

## Next Steps

Once deployed:

1. **Share the URL** with your team
2. **Test with real updates** during a shift
3. **Train users** on the interface
4. **Monitor usage** in first week
5. **Gather feedback** and iterate

---

## Need Help?

If stuck:

1. Check the **Troubleshooting** section above
2. Review Railway **Deploy Logs**
3. Verify **environment variables** are correct
4. Check **Google Sheet sharing** settings

---

**Congratulations! Your inventory system is now live! 🎉**
