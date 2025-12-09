# Quick Start Guide - 10 Minutes to Launch

## What You're Deploying

A cloud-hosted inventory management system that:
- ✅ Uses Google Sheets as database (free, real-time, multi-user)
- ✅ Hosted on Railway (free tier available)
- ✅ Accessible from any device with internet
- ✅ Mobile-optimized interface
- ✅ Everyone on your team can use it simultaneously

---

## Prerequisites

1. Google account
2. GitHub account (free)
3. Railway account (free - sign up with GitHub)
4. Your Excel file: `Pirana_Upload_Build_COMPLETE.xlsx`

---

## 3-Step Setup

### STEP 1: Google Sheets (5 min)

1. Upload Excel to Google Sheets: https://sheets.google.com
2. Copy the Sheet ID from URL
3. Create service account: https://console.cloud.google.com
4. Share sheet with service account email
5. Download JSON credentials file

**Detailed instructions**: See DEPLOYMENT_GUIDE.md Part 1

### STEP 2: GitHub (2 min)

1. Create new repository: https://github.com/new
2. Upload all files from `production` folder
3. Commit changes

**Detailed instructions**: See DEPLOYMENT_GUIDE.md Part 2, Steps 1-2

### STEP 3: Railway (3 min)

1. Sign up: https://railway.app
2. New Project > Deploy from GitHub
3. Select your repository
4. Add environment variables:
   - `GOOGLE_SHEET_ID` = your sheet ID
   - `GOOGLE_CREDENTIALS_JSON` = contents of JSON file
5. Generate domain

**Detailed instructions**: See DEPLOYMENT_GUIDE.md Part 2, Steps 3-6

---

## That's It!

Your inventory system is now live at:
```
https://your-app.up.railway.app
```

Share this URL with your team - everyone can access it!

---

## Quick Test

1. Visit your Railway URL
2. Search for a part (e.g., "9006507")
3. Update the stock level
4. Check Google Sheets - you should see the change!

---

## Daily Usage

**On Mobile**:
1. Open URL in browser
2. Search for part
3. Update stock
4. Done!

**Bulk Updates**:
1. Open Google Sheets
2. Edit cells directly
3. Changes sync to app instantly

---

## Need Full Instructions?

See `DEPLOYMENT_GUIDE.md` for:
- Detailed step-by-step with screenshots
- Troubleshooting guide
- Advanced features
- Custom domain setup

---

## Support

Common issues and fixes in DEPLOYMENT_GUIDE.md Part 5

---

**Total Time**: ~10 minutes
**Total Cost**: $0 (free tier)
**Benefits**: ∞ (priceless)
