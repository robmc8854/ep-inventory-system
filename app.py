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
    """Search for parts by query"""
    try:
        query = request.args.get('q', '').lower()
        
        if not query:
            return jsonify({'parts': []})
        
        worksheet = get_worksheet()
        all_values = worksheet.get_all_values()
        
        if not all_values:
            return jsonify({'parts': []})
        
        headers = all_values[0]
        
        # Search through parts
        results = []
        for row in all_values[1:]:
            # Search in stock code, description, category
            row_text = ' '.join(str(cell).lower() for cell in row)
            if query in row_text:
                part = {}
                for i, header in enumerate(headers):
                    part[header] = row[i] if i < len(row) else ''
                results.append(part)
        
        return jsonify({'parts': results, 'count': len(results)})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/parts/critical', methods=['GET'])
def get_critical_parts():
    """Get critical and low stock parts"""
    try:
        worksheet = get_worksheet()
        all_values = worksheet.get_all_values()
        
        if not all_values:
            return jsonify({'parts': []})
        
        headers = all_values[0]
        critical_parts = []
        
        for row_idx, row in enumerate(all_values[1:], start=2):
            if len(row) >= len(headers):
                # Check if Critical column is True
                is_critical = False
                is_low_stock = False
                
                # Find Critical column
                if 'Critical' in headers:
                    critical_idx = headers.index('Critical')
                    if row[critical_idx].upper() in ['TRUE', 'YES', '1']:
                        is_critical = True
                
                # Check if low stock (Current <= Min)
                if 'Current' in headers and 'Min' in headers:
                    current_idx = headers.index('Current')
                    min_idx = headers.index('Min')
                    
                    try:
                        current = float(row[current_idx]) if row[current_idx] else 0
                        min_val = float(row[min_idx]) if row[min_idx] else 0
                        if current <= min_val:
                            is_low_stock = True
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

@app.route('/api/parts/update-full', methods=['POST'])
def update_part_full():
    """Update multiple fields of a part (Current, Min, Max, Bin, Bin Checked, Pirana Status)"""
    try:
        data = request.json
        print(f"[UPDATE-FULL] Received data: {data}")
        
        stock_code = data.get('stock_code')
        
        if not stock_code:
            print("[UPDATE-FULL] Error: No stock code provided")
            return jsonify({'error': 'stock_code is required'}), 400
        
        worksheet = get_worksheet()
        all_values = worksheet.get_all_values()
        
        headers = all_values[0]
        print(f"[UPDATE-FULL] Headers: {headers}")
        
        # Find column indices
        stock_code_col = headers.index('Stock Code') if 'Stock Code' in headers else 1
        current_col = headers.index('Current') if 'Current' in headers else 9
        min_col = headers.index('Min') if 'Min' in headers else 10
        max_col = headers.index('Max') if 'Max' in headers else 11
        bin_col = headers.index('Bin') if 'Bin' in headers else 13
        bin_checked_col = headers.index('Bin Checked') if 'Bin Checked' in headers else 14
        ready_pirana_col = headers.index('Ready for Pirana') if 'Ready for Pirana' in headers else 15
        added_pirana_col = headers.index('Added to Pirana') if 'Added to Pirana' in headers else 16
        
        print(f"[UPDATE-FULL] Column indices - Stock Code: {stock_code_col}, Current: {current_col}, Min: {min_col}, Max: {max_col}, Bin: {bin_col}, Bin Checked: {bin_checked_col}, Ready Pirana: {ready_pirana_col}, Added Pirana: {added_pirana_col}")
        
        # Find the row
        row_idx = None
        for idx, row in enumerate(all_values[1:], start=2):
            if len(row) > stock_code_col and row[stock_code_col] == stock_code:
                row_idx = idx
                print(f"[UPDATE-FULL] Found part at row {row_idx}")
                break
        
        if not row_idx:
            print(f"[UPDATE-FULL] Part not found: {stock_code}")
            return jsonify({'error': 'Part not found'}), 404
        
        # Prepare batch updates
        updates = []
        updated_fields = []
        
        # Update Current stock
        if 'current' in data and data['current'] != '':
            cell_range = f'{chr(65 + current_col)}{row_idx}'
            updates.append({
                'range': cell_range,
                'values': [[data['current']]]
            })
            updated_fields.append('current')
            print(f"[UPDATE-FULL] Will update Current at {cell_range} to {data['current']}")
        
        # Update Min
        if 'min' in data and data['min'] != '':
            cell_range = f'{chr(65 + min_col)}{row_idx}'
            updates.append({
                'range': cell_range,
                'values': [[data['min']]]
            })
            updated_fields.append('min')
            print(f"[UPDATE-FULL] Will update Min at {cell_range} to {data['min']}")
        
        # Update Max
        if 'max' in data and data['max'] != '':
            cell_range = f'{chr(65 + max_col)}{row_idx}'
            updates.append({
                'range': cell_range,
                'values': [[data['max']]]
            })
            updated_fields.append('max')
            print(f"[UPDATE-FULL] Will update Max at {cell_range} to {data['max']}")
        
        # Update Bin
        if 'bin' in data and data['bin'] != '':
            cell_range = f'{chr(65 + bin_col)}{row_idx}'
            updates.append({
                'range': cell_range,
                'values': [[data['bin']]]
            })
            updated_fields.append('bin')
            print(f"[UPDATE-FULL] Will update Bin at {cell_range} to {data['bin']}")
        
        # Update Bin Checked (accepts boolean or string)
        if 'bin_checked' in data:
            cell_range = f'{chr(65 + bin_checked_col)}{row_idx}'
            bin_checked_value = 'TRUE' if data['bin_checked'] in [True, 'true', 'TRUE', '1', 1] else ''
            updates.append({
                'range': cell_range,
                'values': [[bin_checked_value]]
            })
            updated_fields.append('bin_checked')
            print(f"[UPDATE-FULL] Will update Bin Checked at {cell_range} to {bin_checked_value}")
        
        # Update Ready for Pirana (accepts boolean or string)
        if 'ready_pirana' in data:
            cell_range = f'{chr(65 + ready_pirana_col)}{row_idx}'
            ready_value = 'TRUE' if data['ready_pirana'] in [True, 'true', 'TRUE', '1', 1] else ''
            updates.append({
                'range': cell_range,
                'values': [[ready_value]]
            })
            updated_fields.append('ready_pirana')
            print(f"[UPDATE-FULL] Will update Ready for Pirana at {cell_range} to {ready_value}")
        
        # Update Added to Pirana (accepts boolean or string)
        if 'added_pirana' in data:
            cell_range = f'{chr(65 + added_pirana_col)}{row_idx}'
            added_value = 'TRUE' if data['added_pirana'] in [True, 'true', 'TRUE', '1', 1] else ''
            updates.append({
                'range': cell_range,
                'values': [[added_value]]
            })
            updated_fields.append('added_pirana')
            print(f"[UPDATE-FULL] Will update Added to Pirana at {cell_range} to {added_value}")
        
        # Perform batch update
        if updates:
            print(f"[UPDATE-FULL] Performing batch update with {len(updates)} updates")
            worksheet.batch_update(updates)
            print("[UPDATE-FULL] Batch update successful")
        else:
            print("[UPDATE-FULL] No updates to perform")
        
        response = {
            'success': True,
            'stock_code': stock_code,
            'updated_fields': updated_fields,
            'updated_at': datetime.now().isoformat()
        }
        print(f"[UPDATE-FULL] Returning success: {response}")
        
        return jsonify(response)
    
    except Exception as e:
        print(f"[UPDATE-FULL] Exception: {str(e)}")
        import traceback
        traceback.print_exc()
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
