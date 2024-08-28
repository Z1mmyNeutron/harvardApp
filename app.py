from flask import Flask, render_template, jsonify, send_file
import requests
from flask_caching import Cache
from dotenv import load_dotenv
import os
import json
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Get API key from environment variable
API_KEY = os.getenv('HARVARD_API_KEY')
if not API_KEY:
    raise ValueError("API_KEY environment variable not set")

BASE_URL = 'https://api.harvardartmuseums.org/object'

import matplotlib.pyplot as plt

def create_charts(data):
    # Initialize lists for titles and artists
    titles = []
    artists = []

    # Extract titles and artists from data, with default values if keys are missing
    for item in data:
        titles.append(item.get('title', 'Unknown Title'))
        artist_name = item.get('artist_name', 'Unknown Artist')
        if artist_name == 'Unknown Artist':
            # Additional check to see if 'artist_name' exists
            if 'people' in item and len(item['people']) > 0:
                artist_name = item['people'][0].get('name', 'Unknown Artist')
        artists.append(artist_name)

    # Debugging: Print out extracted artist names
    print(f"Extracted artist names: {artists}")

    # Generate pie chart
    plt.figure(figsize=(8, 6))
    title_counts = {title: titles.count(title) for title in set(titles)}
    labels = list(title_counts.keys())
    counts = list(title_counts.values())
    plt.pie(counts, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title('Pie Chart Title')
    pie_chart_path = 'static/pie_chart.png'
    plt.savefig(pie_chart_path)
    plt.close()

    # Generate bar chart
    plt.figure(figsize=(10, 6))
    artist_counts = {artist: artists.count(artist) for artist in set(artists)}
    if 'Unknown Artist' not in artist_counts:
        artist_counts['Unknown Artist'] = 0
    labels = list(artist_counts.keys())
    counts = list(artist_counts.values())
    plt.bar(labels, counts, color='skyblue')
    plt.xlabel('Artists')
    plt.ylabel('Count')
    plt.title('Artist Count Bar Chart')

    # Debugging: Print out artist counts
    print(f"Artist counts: {artist_counts}")

    # Adjust layout to fit labels
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    bar_chart_path = 'static/bar_chart.png'
    plt.savefig(bar_chart_path)
    plt.close()

    # Generate line chart
    plt.figure(figsize=(12, 8))  # Increase figure size to accommodate long labels
    title_counts = {title: titles.count(title) for title in set(titles)}
    labels = list(title_counts.keys())
    counts = list(title_counts.values())
    plt.plot(labels, counts, marker='o', linestyle='-', color='b')
    plt.xlabel('Labels')
    plt.ylabel('Values')
    plt.title('Line Chart Title')

    # Rotate x-axis labels and adjust layout
    plt.xticks(rotation=45, ha='right')  # Rotate labels 45 degrees
    plt.tight_layout()  # Adjust layout to fit labels

    line_chart_path = 'static/line_chart.png'
    plt.savefig(line_chart_path)
    plt.close()

    return pie_chart_path, bar_chart_path, line_chart_path

    # Initialize lists for titles and artists
    titles = []
    artists = []

    # Extract titles and artists from data, with default values if keys are missing
    for item in data:
        titles.append(item.get('title', 'Unknown Title'))
        artists.append(item.get('artist_name', 'Unknown Artist'))

    # Generate pie chart
    plt.figure(figsize=(12, 8))
    title_counts = {title: titles.count(title) for title in set(titles)}
    labels = list(title_counts.keys())
    counts = list(title_counts.values())
    plt.pie(counts, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title('Percentage of Pieces with the Same Title')
    pie_chart_path = 'static/pie_chart.png'
    plt.savefig(pie_chart_path)
    plt.close()

    # Generate bar chart
    plt.figure(figsize=(12, 8))
    artist_counts = {artist: artists.count(artist) for artist in set(artists)}
    if 'Unknown Artist' not in artist_counts:
        artist_counts['Unknown Artist'] = 0
    labels = list(artist_counts.keys())
    counts = list(artist_counts.values())
    plt.bar(labels, counts, color='skyblue')
    plt.xlabel('Name of Artists')
    plt.ylabel('Number of Pieces')
    plt.title('Bar Chart of Artists')
    bar_chart_path = 'static/bar_chart.png'
    plt.savefig(bar_chart_path)
    plt.close()

    # Generate line chart
    plt.figure(figsize=(12, 8))
    title_counts = {title: titles.count(title) for title in set(titles)}
    labels = list(title_counts.keys())
    counts = list(title_counts.values())
    plt.plot(labels, counts, marker='o', linestyle='-', color='b')
    plt.xlabel('Name of Pieces')
    plt.ylabel('Number of Pieces')
    plt.title('Number of Pieces with the Same Title')

    # Rotate x-axis labels
    plt.xticks(rotation=25, ha='right')  # Rotate labels 25 degrees
    plt.tight_layout()  # Adjust layout to fit labels

    line_chart_path = 'static/line_chart.png'
    plt.savefig(line_chart_path)
    plt.close()

    return pie_chart_path, bar_chart_path, line_chart_path
def create_pdf_report(pie_chart_path, bar_chart_path, line_chart_path):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    margin = 50

    # Function to add chart with title and handle page break
    def add_chart(title, image_path, y_position):
        nonlocal c
        chart_height = 350
        space_for_next_item = 300

        if y_position - chart_height < margin:  # Adjust position for new page
            c.showPage()  # Create a new page
            y_position = height - margin

        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin, y_position, title)
        c.drawImage(image_path, margin, y_position - chart_height, width=width - 2 * margin, height=chart_height)

        # Update y_position for next item
        y_position -= space_for_next_item

        return y_position

    y_position = height - margin

    # Add pie chart
    y_position = add_chart("Pie Chart", pie_chart_path, y_position)

    # Add bar chart
    y_position = add_chart("Bar Chart", bar_chart_path, y_position)

    # Add line chart
    y_position = add_chart("Line Chart", line_chart_path, y_position)

    # Finalize PDF
    c.save()
    buffer.seek(0)
    return buffer

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
                image_url = 'https://cdn.vectorstock.com/i/500p/82/99/no-image-available-like-missing-picture-vector-43938299.jpg'

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

@app.route('/api/report')
def generate_report():
    try:
        # Fetch data (You may need to adjust this to fit your actual data source)
        response = requests.get(f'{BASE_URL}?apikey={API_KEY}')
        response.raise_for_status()
        data = response.json().get('records', [])

        # Generate charts and PDF report
        pie_chart_path, bar_chart_path, line_chart_path = create_charts(data)
        pdf_buffer = create_pdf_report(pie_chart_path, bar_chart_path, line_chart_path)

        # Send PDF file to client
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name='report.pdf',
            mimetype='application/pdf'
        )
    except requests.RequestException as e:
        app.logger.error(f'Error fetching data: {e}')
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
