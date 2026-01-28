from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import gspread
from google.oauth2.service_account import Credentials
import os
import json

app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app)

# Google Sheets Configuration
SPREADSHEET_NAME = os.environ.get('SPREADSHEET_NAME', 'EP Engineering Stores Inventory')
SHEET_NAME = os.environ.get('SHEET_NAME', 'Parts')

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def get_google_sheet():
    """Connect to Google Sheet"""
    try:
        if 'GOOGLE_CREDENTIALS' in os.environ:
            creds_dict = json.loads(os.environ['GOOGLE_CREDENTIALS'])
            creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        else:
            creds = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
        
        client = gspread.authorize(creds)
        spreadsheet = client.open(SPREADSHEET_NAME)
        worksheet = spreadsheet.worksheet(SHEET_NAME)
        return worksheet
    except Exception as e:
        print(f"Error connecting to Google Sheets: {e}")
        return None

@app.route('/')
def index():
    """Serve index.html from static folder"""
    return send_from_directory('static', 'index.html')

@app.route('/api/parts', methods=['GET'])
def get_all_parts():
    """Get all parts"""
    try:
        worksheet = get_google_sheet()
        if not worksheet:
            return jsonify({'error': 'Could not connect to Google Sheets'}), 500
        
        all_values = worksheet.get_all_values()
        if len(all_values) < 2:
            return jsonify({'parts': []})
        
        headers = all_values[0]
        parts = []
        for row in all_values[1:]:
            while len(row) < len(headers):
                row.append('')
            part = {headers[i]: row[i] for i in range(len(headers))}
            parts.append(part)
        
        return jsonify({'parts': parts, 'count': len(parts)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/parts/critical', methods=['GET'])
def get_critical_parts():
    """Get critical parts"""
    try:
        worksheet = get_google_sheet()
        if not worksheet:
            return jsonify({'error': 'Could not connect to Google Sheets'}), 500
        
        all_values = worksheet.get_all_values()
        if len(all_values) < 2:
            return jsonify({'parts': []})
        
        headers = all_values[0]
        critical_idx = headers.index('Critical') if 'Critical' in headers else -1
        current_idx = headers.index('Current') if 'Current' in headers else -1
        min_idx = headers.index('Min') if 'Min' in headers else -1
        
        critical_parts = []
        for row in all_values[1:]:
            while len(row) < len(headers):
                row.append('')
            
            is_critical = row[critical_idx].upper() == 'TRUE' if critical_idx >= 0 else False
            
            try:
                current = float(row[current_idx]) if current_idx >= 0 and row[current_idx] else 0
                min_val = float(row[min_idx]) if min_idx >= 0 and row[min_idx] and row[min_idx].upper() != 'TBC' else None
                is_low_stock = (min_val is not None and current <= min_val)
            except:
                is_low_stock = False
            
            if is_critical or is_low_stock:
                part = {headers[i]: row[i] for i in range(len(headers))}
                critical_parts.append(part)
        
        return jsonify({'parts': critical_parts, 'count': len(critical_parts)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/parts/update-full', methods=['POST'])
def update_part_full():
    """Update part - ONLY CHANGE: Added mark_delete support"""
    try:
        data = request.json
        stock_code = data.get('stock_code')
        
        if not stock_code:
            return jsonify({'error': 'Stock code required'}), 400
        
        worksheet = get_google_sheet()
        if not worksheet:
            return jsonify({'error': 'Could not connect to Google Sheets'}), 500
        
        all_values = worksheet.get_all_values()
        headers = all_values[0]
        
        stock_code_idx = headers.index('Stock Code') if 'Stock Code' in headers else -1
        if stock_code_idx < 0:
            return jsonify({'error': 'Stock Code column not found'}), 500
        
        row_number = None
        for i, row in enumerate(all_values[1:], start=2):
            if len(row) > stock_code_idx and row[stock_code_idx] == stock_code:
                row_number = i
                break
        
        if not row_number:
            return jsonify({'error': f'Part {stock_code} not found'}), 404
        
        updated_fields = []
        
        # Update Current
        if 'current' in data:
            current_idx = headers.index('Current') if 'Current' in headers else -1
            if current_idx >= 0:
                col_letter = chr(65 + current_idx)
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
        
        # Update Mark for Delete (NEW - ONLY CHANGE)
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
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
