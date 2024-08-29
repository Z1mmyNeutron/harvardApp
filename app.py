from flask import Flask, render_template, jsonify, send_file
import requests
from flask_caching import Cache
from dotenv import load_dotenv
from statistics import mean, mode, median, StatisticsError
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import io
import os
import json
import matplotlib.pyplot as plt
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
    plt.figure(figsize=(10, 8))
    title_counts = {title: titles.count(title) for title in set(titles)}
    cleaned_labels = [title.strip('[]').strip() for title in title_counts.keys()]
    labels = cleaned_labels
    counts = list(title_counts.values())
    plt.pie(counts, labels=labels, autopct='%1.1f%%', startangle=140, pctdistance=0.85)
    plt.title('Pieces of Art with the Same Name', fontsize=20)
    pie_chart_path = 'static/pie_chart.png'
    plt.savefig(pie_chart_path)
    plt.close()

    # Generate bar chart
    plt.figure(figsize=(10, 6))
    artist_counts = {artist: artists.count(artist) for artist in set(artists)}
    if 'Unknown Artist' not in artist_counts:
        artist_counts['Unknown Artist'] = 0
    cleaned_artist_labels = [artist.strip('[]').strip() for artist in artist_counts.keys()]
    labels = cleaned_artist_labels
    counts = list(artist_counts.values())
    plt.bar(labels, counts, color='skyblue')
    plt.xlabel('Names of Artists', fontsize=15)
    plt.ylabel('Count', fontsize=15)
    plt.title('Artist Count Bar Chart', fontsize=20)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    bar_chart_path = 'static/bar_chart.png'
    plt.savefig(bar_chart_path)
    plt.close()

    # Generate line chart
    plt.figure(figsize=(10, 8))
    title_counts = {title: titles.count(title) for title in set(titles)}
    cleaned_title_labels = [title.strip('[]').strip() for title in title_counts.keys()]
    labels = cleaned_title_labels
    counts = list(title_counts.values())
    plt.plot(labels, counts, marker='o', linestyle='-', color='b')
    plt.xlabel('Names of Pieces', fontsize=14)  # Adjust font size
    plt.ylabel('Count', fontsize=14)  # Adjust font size
    plt.title('Pieces with the Same Title', fontsize=20)  # Adjust font size
    plt.xticks(rotation=45, ha='right', fontsize=13)  # Adjust font size
    plt.yticks(fontsize=10)  # Adjust font size
    plt.tight_layout()
    line_chart_path = 'static/line_chart.png'
    plt.savefig(line_chart_path)
    plt.close()

    return pie_chart_path, bar_chart_path, line_chart_path

def format_counts_as_table(counts):
    data = [['Title', 'Count']]
    for title, count in counts.items():
        clean_title = title.strip('[]').strip()
        data.append([clean_title, count])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), '#d0d0d0'),
        ('GRID', (0, 0), (-1, -1), 1, 'black'),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONT', (0, 1), (-1, -1), 'Helvetica'),
        ('SIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    return table

def create_pdf_report(pie_chart_path, bar_chart_path, line_chart_path, title_counts, artist_counts):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    width, height = letter
    margin = 50
    chart_height = 400
    title_space = 20  # Increased space for the chart title
    chart_space = 20  # Space between title and chart
    additional_space = 20

    def add_chart(title, image_path, conclusion_text, table_data):
        elements.append(Paragraph(title, ParagraphStyle(name='Title', fontSize=14, fontName='Helvetica-Bold')))
        elements.append(Spacer(1, title_space))  # Space for the title
        elements.append(Image(image_path, width=width - 2 * margin, height=chart_height))
        elements.append(Spacer(1, chart_space))  # Space between chart and conclusion
        
        if conclusion_text:
            elements.append(Paragraph("Conclusion:", ParagraphStyle(name='ConclusionTitle', fontSize=12, fontName='Helvetica-Bold')))
            elements.append(Spacer(1, 10))
            elements.append(Paragraph(conclusion_text, ParagraphStyle(name='ConclusionText', fontSize=12, fontName='Helvetica')))
            elements.append(Spacer(1, 10))

        if table_data:
            elements.append(table_data)
            elements.append(Spacer(1, additional_space))
        
        elements.append(PageBreak())

    pie_chart_conclusion = (
        f"The pie chart illustrates the distribution of pieces with the same title. The following\n"
        f"are the counts for each title:"
    )
    add_chart("Pie Chart", pie_chart_path, pie_chart_conclusion, format_counts_as_table(title_counts))

    bar_chart_conclusion = (
        f"The bar chart shows the number of pieces attributed to each artist. The artist counts\n"
        f"are:"
    )
    add_chart("Bar Chart", bar_chart_path, bar_chart_conclusion, format_counts_as_table(artist_counts))

    line_chart_conclusion = (
        f"The line chart represents the number of pieces with the same title over time. The\n"
        f"counts for each title are:"
    )
    add_chart("Line Chart", line_chart_path, line_chart_conclusion, format_counts_as_table(title_counts))

    doc.build(elements)
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
