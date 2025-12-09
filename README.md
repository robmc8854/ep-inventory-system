# EP Engineering Stores - Inventory Management System

Production-ready inventory management system with Google Sheets integration, deployed on Railway.

## Features

- 🔄 Real-time Google Sheets sync
- 📱 Mobile-first responsive design
- 🔍 Fast search functionality
- 🚨 Critical parts tracking
- 📊 Stock level monitoring
- ✏️ Easy stock updates
- 🌐 Cloud-hosted on Railway

## Tech Stack

- **Backend**: Python Flask
- **Database**: Google Sheets
- **Frontend**: HTML/CSS/JavaScript
- **Hosting**: Railway
- **API**: RESTful endpoints

## API Endpoints

### GET /api/parts
Get all parts from inventory

### GET /api/parts/search?q=query
Search for parts

### GET /api/parts/critical
Get critical and low stock parts

### POST /api/parts/update
Update stock level for a part

```json
{
  "stock_code": "12345",
  "current": 25
}
```

### POST /api/parts/batch-update
Update multiple parts at once

```json
{
  "updates": [
    {"stock_code": "12345", "current": 25},
    {"stock_code": "67890", "current": 10}
  ]
}
```

### GET /api/health
Health check endpoint

## Environment Variables

Required environment variables:

- `GOOGLE_SHEET_ID`: Your Google Sheet ID
- `GOOGLE_CREDENTIALS_JSON`: Service account credentials (JSON string)
- `PORT`: Port number (set by Railway automatically)

## Deployment

See DEPLOYMENT_GUIDE.md for complete deployment instructions.

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GOOGLE_SHEET_ID="your_sheet_id"
export GOOGLE_CREDENTIALS_JSON='{"type":"service_account",...}'

# Run locally
python app.py
```

## Google Sheets Structure

The system expects a Google Sheet with the following columns:

- Stock Code
- Manufacturer Part Number
- Description
- Supplier
- Critical
- Category
- Price
- Purchase Unit
- Current
- Min
- Issue Unit
- Bin
- Store

## Support

For issues or questions, contact the facilities team.

## Version

1.0.0 - Production Release
