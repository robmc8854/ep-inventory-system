from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import gspread
from google.oauth2.service_account import Credentials
import json
import os
from datetime import datetime

app = Flask(__name__, static_folder='static')
CORS(app)

# Google Sheets setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def get_sheets_client():
    """Initialize Google Sheets client"""
    try:
        # Get credentials from environment variable (JSON string)
        creds_json = os.environ.get('GOOGLE_CREDENTIALS_JSON')
        if not creds_json:
            raise Exception("GOOGLE_CREDENTIALS_JSON environment variable not set")
        
        # Parse JSON credentials
        creds_dict = json.loads(creds_json)
        
        # Create credentials object
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        
        # Create client
        client = gspread.authorize(creds)
        
        return client
    except Exception as e:
        print(f"Error initializing Google Sheets client: {e}")
        raise

def get_worksheet():
    """Get the main worksheet"""
    sheet_id = os.environ.get('GOOGLE_SHEET_ID')
    if not sheet_id:
        raise Exception("GOOGLE_SHEET_ID environment variable not set")
    
    client = get_sheets_client()
    spreadsheet = client.open_by_key(sheet_id)
    
    # Get the "Parts" worksheet (or first sheet)
    try:
        worksheet = spreadsheet.worksheet("Parts")
    except:
        worksheet = spreadsheet.get_worksheet(0)
    
    return worksheet

@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_from_directory('static', 'index.html')

@app.route('/api/parts', methods=['GET'])
def get_parts():
    """Get all parts from Google Sheets"""
    try:
        worksheet = get_worksheet()
        
        # Get all values
        all_values = worksheet.get_all_values()
        
        if not all_values:
            return jsonify({'parts': []})
        
        # First row is headers
        headers = all_values[0]
        
        # Convert to list of dictionaries
        parts = []
        for row in all_values[1:]:
            if len(row) >= len(headers):
                part = {}
                for i, header in enumerate(headers):
                    part[header] = row[i] if i < len(row) else ''
                parts.append(part)
        
        return jsonify({'parts': parts, 'count': len(parts)})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/parts/search', methods=['GET'])
def search_parts():
    """Search for parts"""
    try:
        query = request.args.get('q', '').lower()
        
        worksheet = get_worksheet()
        all_values = worksheet.get_all_values()
        
        if not all_values:
            return jsonify({'parts': []})
        
        headers = all_values[0]
        
        # Search in Stock Code, Description, and Category
        matching_parts = []
        for row_idx, row in enumerate(all_values[1:], start=2):
            if len(row) >= len(headers):
                # Check if query matches
                stock_code = row[1].lower() if len(row) > 1 else ''
                description = row[3].lower() if len(row) > 3 else ''
                category = row[6].lower() if len(row) > 6 else ''
                
                if query in stock_code or query in description or query in category:
                    part = {'_row': row_idx}
                    for i, header in enumerate(headers):
                        part[header] = row[i] if i < len(row) else ''
                    matching_parts.append(part)
        
        return jsonify({'parts': matching_parts, 'count': len(matching_parts)})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/parts/critical', methods=['GET'])
def get_critical_parts():
    """Get critical parts and low stock items"""
    try:
        worksheet = get_worksheet()
        all_values = worksheet.get_all_values()
        
        if not all_values:
            return jsonify({'parts': []})
        
        headers = all_values[0]
        
        # Find column indices
        critical_col = headers.index('Critical') if 'Critical' in headers else 5
        current_col = headers.index('Current') if 'Current' in headers else 9
        min_col = headers.index('Min') if 'Min' in headers else 10
        
        critical_parts = []
        for row_idx, row in enumerate(all_values[1:], start=2):
            if len(row) >= len(headers):
                # Check if critical or low stock
                is_critical = str(row[critical_col]).upper() in ['TRUE', 'YES', '1']
                
                try:
                    current = float(row[current_col]) if row[current_col] else 0
                    min_val = float(row[min_col]) if row[min_col] else 0
                    is_low_stock = current <= min_val
                except:
                    is_low_stock = False
                
                if is_critical or is_low_stock:
                    part = {'_row': row_idx}
                    for i, header in enumerate(headers):
                        part[header] = row[i] if i < len(row) else ''
                    critical_parts.append(part)
        
        return jsonify({'parts': critical_parts, 'count': len(critical_parts)})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/parts/update', methods=['POST'])
def update_part():
    """Update a part's Current stock value"""
    try:
        data = request.json
        stock_code = data.get('stock_code')
        new_current = data.get('current')
        
        if not stock_code:
            return jsonify({'error': 'stock_code is required'}), 400
        
        worksheet = get_worksheet()
        all_values = worksheet.get_all_values()
        
        headers = all_values[0]
        stock_code_col = headers.index('Stock Code') if 'Stock Code' in headers else 1
        current_col = headers.index('Current') if 'Current' in headers else 9
        
        # Find the row
        for row_idx, row in enumerate(all_values[1:], start=2):
            if len(row) > stock_code_col and row[stock_code_col] == stock_code:
                # Update the Current value
                worksheet.update_cell(row_idx, current_col + 1, new_current)
                
                return jsonify({
                    'success': True,
                    'stock_code': stock_code,
                    'new_current': new_current,
                    'updated_at': datetime.now().isoformat()
                })
        
        return jsonify({'error': 'Part not found'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/parts/batch-update', methods=['POST'])
def batch_update_parts():
    """Update multiple parts at once"""
    try:
        data = request.json
        updates = data.get('updates', [])
        
        if not updates:
            return jsonify({'error': 'updates array is required'}), 400
        
        worksheet = get_worksheet()
        all_values = worksheet.get_all_values()
        
        headers = all_values[0]
        stock_code_col = headers.index('Stock Code') if 'Stock Code' in headers else 1
        current_col = headers.index('Current') if 'Current' in headers else 9
        
        results = []
        
        for update in updates:
            stock_code = update.get('stock_code')
            new_current = update.get('current')

@app.route('/api/parts/update-full', methods=['POST'])
def update_part_full():
    """Update multiple fields of a part (Current, Min, Bin)"""
    try:
        data = request.json
        stock_code = data.get('stock_code')
        
        if not stock_code:
            return jsonify({'error': 'stock_code is required'}), 400
        
        worksheet = get_worksheet()
        all_values = worksheet.get_all_values()
        
        headers = all_values[0]
        
        # Find column indices
        stock_code_col = headers.index('Stock Code') if 'Stock Code' in headers else 1
        current_col = headers.index('Current') if 'Current' in headers else 9
        min_col = headers.index('Min') if 'Min' in headers else 10
        bin_col = headers.index('Bin') if 'Bin' in headers else 12
        
        # Find the row
        row_idx = None
        for idx, row in enumerate(all_values[1:], start=2):
            if len(row) > stock_code_col and row[stock_code_col] == stock_code:
                row_idx = idx
                break
        
        if not row_idx:
            return jsonify({'error': 'Part not found'}), 404
        
        # Prepare batch updates
        updates = []
        updated_fields = []
        
        # Update Current stock
        if 'current' in data:
            updates.append({
                'range': f'{chr(65 + current_col)}{row_idx}',
                'values': [[data['current']]]
            })
            updated_fields.append('current')
        
        # Update Min
        if 'min' in data:
            updates.append({
                'range': f'{chr(65 + min_col)}{row_idx}',
                'values': [[data['min']]]
            })
            updated_fields.append('min')
        
        # Update Bin
        if 'bin' in data:
            updates.append({
                'range': f'{chr(65 + bin_col)}{row_idx}',
                'values': [[data['bin']]]
            })
            updated_fields.append('bin')
        
        # Perform batch update
        if updates:
            worksheet.batch_update(updates)
        
        return jsonify({
            'success': True,
            'stock_code': stock_code,
            'updated_fields': updated_fields,
            'updated_at': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
            
            # Find the row
            for row_idx, row in enumerate(all_values[1:], start=2):
                if len(row) > stock_code_col and row[stock_code_col] == stock_code:
                    # Update the Current value
                    worksheet.update_cell(row_idx, current_col + 1, new_current)
                    results.append({
                        'stock_code': stock_code,
                        'success': True,
                        'new_current': new_current
                    })
                    break
            else:
                results.append({
                    'stock_code': stock_code,
                    'success': False,
                    'error': 'Part not found'
                })
        
        return jsonify({
            'results': results,
            'total': len(results),
            'successful': sum(1 for r in results if r['success']),
            'updated_at': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test Google Sheets connection
        worksheet = get_worksheet()
        worksheet.get('A1')
        
        return jsonify({
            'status': 'healthy',
            'google_sheets': 'connected',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
