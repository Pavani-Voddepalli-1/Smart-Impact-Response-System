from flask import Flask, render_template, request, jsonify

import streamlit as st
app = Flask(__name__)

accident_data = []

# Fixed registry — keyed by bike_id exactly as Arduino sends it
BIKE_REGISTRY = {
    "BIKE01": {"bike_number": "TS01AB1234", "blood_group": "O+"},
}

@app.route('/data', methods=['POST'])
def receive_data():
    try:
        data = request.json
        if data:
            # Extract speed integer from e.g. "45.3 kmph"
            speed_str = data.get('speed_of_crash', '0')
            speed_int = int(float(''.join(c for c in speed_str if c.isdigit() or c == '.')))
            data['speed_int'] = speed_int

            # Attach fixed bike info from registry using bike_id
            bike_id = data.get('bike_id', '')
            info = BIKE_REGISTRY.get(bike_id, {})
            data['bike_number'] = info.get('bike_number', '—')

            # Fix blood group — Arduino hardcodes "B+" but registry has correct value
            data['owner_blood_group'] = info.get('blood_group', data.get('owner_blood_group', '—'))

            accident_data.insert(0, data)
            return jsonify({"status": "success"}), 200
        return jsonify({"status": "error"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/close', methods=['POST'])
def close_case():
    try:
        data = request.json
        bike_id = data.get('bike_id')
        before = len(accident_data)
        accident_data[:] = [a for a in accident_data if a.get('bike_id') != bike_id]
        removed = before - len(accident_data)
        return jsonify({"status": "success", "removed": removed}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/debug')
def debug():
    return jsonify(accident_data)


@app.route('/dashboard')
def dashboard():
    return render_template('index.html', accidents=accident_data)


@app.route('/get_updates')
def get_updates():
    return render_template('cards.html', accidents=accident_data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
