from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

# Replace with your API key
API_KEY = '7c0ce3d0-b26b-424d-81b1-2e46b7491ab5'
BASE_URL = 'https://api.harvardartmuseums.org/object'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    try:
        response = requests.get(f'{BASE_URL}?apikey={API_KEY}')
        response.raise_for_status()
        data = response.json()
        return jsonify(data)
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
