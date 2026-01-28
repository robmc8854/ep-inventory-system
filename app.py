from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import gspread
from google.oauth2.service_account import Credentials
import os
import json

app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app)

# ============================================
# GOOGLE SHEETS CONFIGURATION
# ============================================
# UPDATE THESE VALUES WITH YOUR DETAILS:
SPREADSHEET_NAME = os.environ.get('SPREADSHEET_NAME', 'EP Engineering Stores Inventory')
SHEET_NAME = os.environ.get('SHEET_NAME', 'Parts')
CREDENTIALS_FILE = 'credentials.json'

# Scopes for Google Sheets API
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def get_google_sheet():
    """Connect to Google Sheet and return worksheet"""
    try:
        # Check if credentials are in environment variable (Railway deployment)
        if 'GOOGLE_CREDENTIALS' in os.environ:
            print("Using credentials from environment variable...")
            creds_dict = json.loads(os.environ['GOOGLE_CREDENTIALS'])
            creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        elif os.path.exists(CREDENTIALS_FILE):
            # Use credentials file (local development)
            print(f"Using credentials from {CREDENTIALS_FILE}...")
            creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
        else:
            raise Exception("No credentials found! Set GOOGLE_CREDENTIALS env var or provide credentials.json")
        
        client = gspread.authorize(creds)
        spreadsheet = client.open(SPREADSHEET_NAME)
        worksheet = spreadsheet.worksheet(SHEET_NAME)
        return worksheet
    except Exception as e:
        print(f"Error connecting to Google Sheets: {e}")
        return None

# ============================================
# API ROUTES
# ============================================

@app.route('/')
def index():
    """Serve the main HTML file"""
    try:
        # Try multiple locations
        for folder, filename in [('static', 'index.html'), ('static', 'ep_stores_inventory.html'), ('.', 'index.html')]:
            filepath = os.path.join(folder, filename) if folder != '.' else filename
            if os.path.exists(filepath):
                return send_from_directory(folder, filename)
        
        # If no file found, list what files we DO have
        files = os.listdir('.')
        static_files = os.listdir('static') if os.path.exists('static') else []
        return jsonify({
            'error': 'HTML file not found',
            'root_files': files,
            'static_files': static_files,
            'looking_for': ['static/index.html', 'static/ep_stores_inventory.html']
        }), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/parts', methods=['GET'])
def get_all_parts():
    """Get all parts from the Parts sheet"""
    try:
        worksheet = get_google_sheet()
        if not worksheet:
            return jsonify({'error': 'Could not connect to Google Sheets'}), 500
        
        # Get all values
        all_values = worksheet.get_all_values()
        
        if len(all_values) < 2:
            return jsonify({'parts': []})
        
        # First row is headers
        headers = all_values[0]
        
        # Convert to list of dictionaries
        parts = []
        for row in all_values[1:]:
            # Pad row with empty strings if it's shorter than headers
            while len(row) < len(headers):
                row.append('')
            
            part = {}
            for i, header in enumerate(headers):
                part[header] = row[i] if i < len(row) else ''
            parts.append(part)
        
        return jsonify({'parts': parts, 'count': len(parts)})
    
    except Exception as e:
        print(f"Error getting parts: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/parts/critical', methods=['GET'])
def get_critical_parts():
    """Get critical parts (Critical=TRUE OR Current<=Min)"""
    try:
        worksheet = get_google_sheet()
        if not worksheet:
            return jsonify({'error': 'Could not connect to Google Sheets'}), 500
        
        all_values = worksheet.get_all_values()
        
        if len(all_values) < 2:
            return jsonify({'parts': []})
        
        headers = all_values[0]
        
        # Find column indices
        critical_idx = headers.index('Critical') if 'Critical' in headers else -1
        current_idx = headers.index('Current') if 'Current' in headers else -1
        min_idx = headers.index('Min') if 'Min' in headers else -1
        
        critical_parts = []
        for row in all_values[1:]:
            while len(row) < len(headers):
                row.append('')
            
            # Check if critical OR low stock
            is_critical = row[critical_idx].upper() == 'TRUE' if critical_idx >= 0 else False
            
            try:
                current = float(row[current_idx]) if current_idx >= 0 and row[current_idx] else 0
                min_val = float(row[min_idx]) if min_idx >= 0 and row[min_idx] and row[min_idx].upper() != 'TBC' else None
                is_low_stock = (min_val is not None and current <= min_val)
            except:
                is_low_stock = False
            
            if is_critical or is_low_stock:
                part = {}
                for i, header in enumerate(headers):
                    part[header] = row[i] if i < len(row) else ''
                critical_parts.append(part)
        
        return jsonify({'parts': critical_parts, 'count': len(critical_parts)})
    
    except Exception as e:
        print(f"Error getting critical parts: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/parts/update-full', methods=['POST'])
def update_part_full():
    """Update a part with multiple fields (Current, Min, Max, Bin, checkboxes)"""
    try:
        data = request.json
        stock_code = data.get('stock_code')
        
        if not stock_code:
            return jsonify({'error': 'Stock code required'}), 400
        
        worksheet = get_google_sheet()
        if not worksheet:
            return jsonify({'error': 'Could not connect to Google Sheets'}), 500
        
        # Get all values
        all_values = worksheet.get_all_values()
        headers = all_values[0]
        
        # Find the row with this stock code
        stock_code_idx = headers.index('Stock Code') if 'Stock Code' in headers else -1
        if stock_code_idx < 0:
            return jsonify({'error': 'Stock Code column not found'}), 500
        
        row_number = None
        for i, row in enumerate(all_values[1:], start=2):  # Start at row 2 (after headers)
            if len(row) > stock_code_idx and row[stock_code_idx] == stock_code:
                row_number = i
                break
        
        if not row_number:
            return jsonify({'error': f'Part {stock_code} not found'}), 404
        
        # Prepare updates
        updates = []
        updated_fields = []
        
        # Update Current
        if 'current' in data:
            current_idx = headers.index('Current') if 'Current' in headers else -1
            if current_idx >= 0:
                col_letter = chr(65 + current_idx)  # Convert to column letter (A, B, C...)
                worksheet.update(f'{col_letter}{row_number}', [[str(data['current'])]])
                updated_fields.append('Current')
        
        # Update Min
        if 'min' in data:
            min_idx = headers.index('Min') if 'Min' in headers else -1
            if min_idx >= 0:
                col_letter = chr(65 + min_idx)
                worksheet.update(f'{col_letter}{row_number}', [[str(data['min'])]])
                updated_fields.append('Min')
        
        # Update Max
        if 'max' in data:
            max_idx = headers.index('Max') if 'Max' in headers else -1
            if max_idx >= 0:
                col_letter = chr(65 + max_idx)
                worksheet.update(f'{col_letter}{row_number}', [[str(data['max'])]])
                updated_fields.append('Max')
        
        # Update Bin
        if 'bin' in data:
            bin_idx = headers.index('Bin') if 'Bin' in headers else -1
            if bin_idx >= 0:
                col_letter = chr(65 + bin_idx)
                worksheet.update(f'{col_letter}{row_number}', [[str(data['bin'])]])
                updated_fields.append('Bin')
        
        # Update Bin Checked
        if 'bin_checked' in data:
            bin_checked_idx = headers.index('Bin Checked') if 'Bin Checked' in headers else -1
            if bin_checked_idx >= 0:
                col_letter = chr(65 + bin_checked_idx)
                value = 'TRUE' if data['bin_checked'] else ''
                worksheet.update(f'{col_letter}{row_number}', [[value]])
                updated_fields.append('Bin Checked')
        
        # Update Ready for Pirana
        if 'ready_pirana' in data:
            ready_idx = headers.index('Ready for Pirana') if 'Ready for Pirana' in headers else -1
            if ready_idx >= 0:
                col_letter = chr(65 + ready_idx)
                value = 'TRUE' if data['ready_pirana'] else ''
                worksheet.update(f'{col_letter}{row_number}', [[value]])
                updated_fields.append('Ready for Pirana')
        
        # Update Added to Pirana
        if 'added_pirana' in data:
            added_idx = headers.index('Added to Pirana') if 'Added to Pirana' in headers else -1
            if added_idx >= 0:
                col_letter = chr(65 + added_idx)
                value = 'TRUE' if data['added_pirana'] else ''
                worksheet.update(f'{col_letter}{row_number}', [[value]])
                updated_fields.append('Added to Pirana')
        
        # Update Mark for Delete
        if 'mark_delete' in data:
            delete_idx = headers.index('Mark for Delete') if 'Mark for Delete' in headers else -1
            if delete_idx >= 0:
                col_letter = chr(65 + delete_idx)
                value = 'TRUE' if data['mark_delete'] else ''
                worksheet.update(f'{col_letter}{row_number}', [[value]])
                updated_fields.append('Mark for Delete')
        
        return jsonify({
            'success': True,
            'message': f'Updated {stock_code}',
            'updated_fields': updated_fields,
            'row': row_number
        })
    
    except Exception as e:
        print(f"Error updating part: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/parts/search', methods=['GET'])
def search_parts():
    """Search parts by stock code, description, bin, or category"""
    try:
        query = request.args.get('q', '').lower()
        
        if not query:
            return jsonify({'parts': [], 'count': 0})
        
        worksheet = get_google_sheet()
        if not worksheet:
            return jsonify({'error': 'Could not connect to Google Sheets'}), 500
        
        all_values = worksheet.get_all_values()
        
        if len(all_values) < 2:
            return jsonify({'parts': []})
        
        headers = all_values[0]
        
        # Search in Stock Code, Description, Category, Bin
        search_indices = []
        for field in ['Stock Code', 'Description', 'Category', 'Bin']:
            if field in headers:
                search_indices.append(headers.index(field))
        
        matching_parts = []
        for row in all_values[1:]:
            while len(row) < len(headers):
                row.append('')
            
            # Check if query matches any searchable field
            match = False
            for idx in search_indices:
                if idx < len(row) and query in row[idx].lower():
                    match = True
                    break
            
            if match:
                part = {}
                for i, header in enumerate(headers):
                    part[header] = row[i] if i < len(row) else ''
                matching_parts.append(part)
        
        return jsonify({'parts': matching_parts, 'count': len(matching_parts)})
    
    except Exception as e:
        print(f"Error searching parts: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================
# RUN SERVER
# ============================================

if __name__ == '__main__':
    # Check if credentials file exists
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"\n⚠️  WARNING: {CREDENTIALS_FILE} not found!")
        print("Please download your Google service account credentials and save as 'credentials.json'")
        print("\nHow to get credentials:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a project or select existing")
        print("3. Enable Google Sheets API")
        print("4. Create Service Account credentials")
        print("5. Download JSON key file and rename to 'credentials.json'")
        print("6. Share your Google Sheet with the service account email\n")
    
    # Get port from environment variable (Railway) or default to 5000
    port = int(os.environ.get('PORT', 5000))
    
    print(f"\n✅ EP Engineering Stores API Server")
    print(f"   Sheet: {SPREADSHEET_NAME}")
    print(f"   Writing to: {SHEET_NAME} (other sheets auto-update!)")
    print(f"   Server: http://0.0.0.0:{port}\n")
    
    app.run(host='0.0.0.0', port=port, debug=False)
