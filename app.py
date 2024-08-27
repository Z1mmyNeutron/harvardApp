from flask import Flask, render_template, jsonify
import requests
from flask_caching import Cache
from dotenv import load_dotenv
import os
import json

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Get API key from environment variable
API_KEY = os.getenv('HARVARD_API_KEY')
if not API_KEY:
    raise ValueError("API_KEY environment variable not set")

BASE_URL = 'https://api.harvardartmuseums.org/object'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data')
@cache.cached(timeout=60)  # Cache the response for 60 seconds
def get_data():
    try:
        response = requests.get(f'{BASE_URL}?apikey={API_KEY}')
        response.raise_for_status()
        data = response.json()

        # Log raw response for debugging
        app.logger.info(f'Raw API response: {data}')

        # Extract relevant fields for the frontend
        art_data = []
        for item in data.get('records', []):
            title = item.get('title')
            image_url = item.get('primaryimageurl')
            artist_name = None
            persistent_link = item.get('url', 'No link available')  # Extract the persistent link

            # Log item being processed for debugging
            app.logger.info(f'Processing item: {item}')

            # Skip items without a title
            if not title:
                app.logger.info('Skipped item without title')
                continue

            # Extract artist name if available
            if 'people' in item and len(item['people']) > 0:
                artist_name = item['people'][0].get('name', 'Unknown artist')

            # Ensure image_url is valid
            if image_url:
                # If the image URL is relative, convert it to absolute
                if not image_url.startswith('http'):
                    image_url = f'https://api.harvardartmuseums.org{image_url}'
            else:
                # Provide a default image URL or placeholder if necessary
                image_url = 'https://via.placeholder.com/150'

            art_data.append({
                'title': title,
                'image_url': image_url,
                'artist_name': artist_name,
                'persistent_link': persistent_link  # Add the persistent link
            })

        # Log final art data for debugging
        app.logger.info(f'Final art data: {art_data}')

        # Write JSON data to a file
        with open('art_data.json', 'w') as file:
            json.dump(art_data, file, indent=4)

        return jsonify(art_data)
    except requests.RequestException as e:
        app.logger.error(f'Error fetching data: {e}')
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
