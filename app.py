from flask import Flask, render_template, jsonify, send_file
import requests
from flask_caching import Cache
from dotenv import load_dotenv
import os
import json
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer
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

def create_charts(data):
    titles = []
    artists = []

    for item in data:
        titles.append(item.get('title', 'Unknown Title'))
        artist_name = item.get('artist_name', 'Unknown Artist')
        if artist_name == 'Unknown Artist':
            if 'people' in item and len(item['people']) > 0:
                artist_name = item['people'][0].get('name', 'Unknown Artist')
        artists.append(artist_name)

    # Generate pie chart
    plt.figure(figsize=(8, 6))
    title_counts = {title: titles.count(title) for title in set(titles)}
    labels = list(title_counts.keys())
    counts = list(title_counts.values())
    plt.pie(counts, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title('Pieces of Art with the Same Name')
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
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    bar_chart_path = 'static/bar_chart.png'
    plt.savefig(bar_chart_path)
    plt.close()

    # Generate line chart
    plt.figure(figsize=(12, 8))
    title_counts = {title: titles.count(title) for title in set(titles)}
    labels = list(title_counts.keys())
    counts = list(title_counts.values())
    plt.plot(labels, counts, marker='o', linestyle='-', color='b')
    plt.xlabel('Names of Pieces')
    plt.ylabel('Count')
    plt.title('Pieces with the Same Title')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    line_chart_path = 'static/line_chart.png'
    plt.savefig(line_chart_path)
    plt.close()

    return pie_chart_path, bar_chart_path, line_chart_path


def format_counts(counts):
    # Define the width for indentation and count columns
    indent = " " * 4  # Adjust as needed
    count_width = 4
    formatted_counts = ""

    for title, count in counts.items():
        clean_title = title.strip('[]')
        formatted_counts += f"{indent}{count:>{count_width}}: {clean_title}\n"
    
    return formatted_counts.strip()

def format_conclusion(title_counts, artist_counts):
    intro_indent = " " * 3
    conclusion_text = (
        "Conclusion:\n\n"
        "Based on the data collected, we can observe the following insights:\n\n"
        "1. Pie Chart Analysis:\n"
        f"{intro_indent}- The pie chart illustrates the distribution of pieces with the same title. The following\n"
        f"{intro_indent}are the counts for each title:\n"
        f"{intro_indent}{intro_indent}{format_counts(title_counts)}\n"
        "2. Bar Chart Analysis:\n"
        f"{intro_indent}- The bar chart shows the number of pieces attributed to each artist. The artist counts\n"
        f"{intro_indent}are:\n"
        f"{intro_indent}{intro_indent}{format_counts(artist_counts)}\n"
        "3. Line Chart Analysis:\n"
        f"{intro_indent}- The line chart represents the number of pieces with the same title over time. The\n"
        f"{intro_indent}counts for each title are:\n"
        f"{intro_indent}{intro_indent}{format_counts(title_counts)}"
    )
    return conclusion_text

def create_pdf_report(pie_chart_path, bar_chart_path, line_chart_path, title_counts, artist_counts):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    margin = 75
    chart_height = 400
    title_space = 20
    additional_space = 50
    y_position = height - margin

    def add_chart(title, image_path, y_position):
        total_height = chart_height + title_space + additional_space

        if y_position < total_height + margin:
            c.showPage()
            y_position = height - margin

        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin, y_position, title)
        c.drawImage(image_path, margin, y_position - chart_height - title_space, width=width - 2 * margin, height=chart_height)

        y_position -= (total_height + margin)

        return y_position

    y_position = add_chart("Pie Chart", pie_chart_path, y_position)
    y_position = add_chart("Bar Chart", bar_chart_path, y_position)
    y_position = add_chart("Line Chart", line_chart_path, y_position)

    def draw_conclusion_section(title, counts, y_position):
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin, y_position, title)
        y_position -= 20

        c.setFont("Helvetica", 12)
        text_object = c.beginText(margin, y_position)
        text_object.setFont("Helvetica", 12)

        intro_indent = " " * 4
        for line in counts.split('\n'):
            text_object.textLine(f"{intro_indent}{line}")

        c.drawText(text_object)
        y_position -= len(counts.split('\n')) * 15  # Adjust spacing based on line count

        return y_position

    c.showPage()

    conclusion_text = format_conclusion(title_counts, artist_counts)
    y_position = draw_conclusion_section("Conclusion:", conclusion_text, height - margin - 50)

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
        response = requests.get(f'{BASE_URL}?apikey={API_KEY}')
        response.raise_for_status()
        data = response.json().get('records', [])

        # Generate charts and get paths
        pie_chart_path, bar_chart_path, line_chart_path = create_charts(data)

        # Extract titles and artists from the data
        titles = [item.get('title', 'Unknown Title') for item in data]
        artists = [item.get('artist_name', 'Unknown Artist') for item in data]
        # Handle cases where 'people' field is present
        for item in data:
            if 'people' in item and len(item['people']) > 0:
                artist_name = item['people'][0].get('name', 'Unknown Artist')
                if artist_name not in artists:
                    artists.append(artist_name)

        # Get counts for the conclusion
        title_counts = {title: titles.count(title) for title in set(titles)}
        artist_counts = {artist: artists.count(artist) for artist in set(artists)}

        # Generate PDF report with counts
        pdf_buffer = create_pdf_report(pie_chart_path, bar_chart_path, line_chart_path, title_counts, artist_counts)

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
