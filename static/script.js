document.getElementById('loadDataBtn').addEventListener('click', loadData);
document.getElementById('toggleDataBtn').addEventListener('click', toggleDataVisibility);
document.getElementById('toggleLabelsBtn').addEventListener('click', toggleLabelsVisibility);
document.getElementById('toggleArtBtn').addEventListener('click', toggleArtVisibility);

let dataLoaded = false;
let chartsVisible = true; // Tracks whether charts are visible or hidden
let labelsVisible = true; // Track whether labels are visible
let artVisible = true; // Track whether art is visible

const chartOptions = {
    responsive: true,
    maintainAspectRatio: false, // Allow the chart to fill the container
    plugins: {
        legend: {
            position: 'top',
            onClick: (e, legendItem, legend) => {
                // Handle legend item click
                const index = legendItem.datasetIndex;
                const chart = legend.chart;
                const meta = chart.getDatasetMeta(index);

                meta.hidden = meta.hidden === null ? !chart.data.datasets[index].hidden : null;

                // Update chart
                chart.update();
            }
        },
        tooltip: {
            callbacks: {
                label: function (context) {
                    let label = context.label || '';
                    if (label) {
                        label += ': ';
                    }
                    if (context.parsed !== null) {
                        label += context.parsed + ' items';
                    }
                    return label;
                }
            }
        }
    }
};

async function loadData() {
    try {
        const response = await fetch('/api/data');
        const data = await response.json();

        if (data.error) {
            console.error('Error fetching data:', data.error);
            return;
        }

        // Process and display pie chart
        displayPieChart(data);

        // Process and display the bar chart
        displayBarChart(data);

        // Process and display line chart
        displayLineChart(data);

        // Display art data
        displayArt(data);

        dataLoaded = true; // Mark data as loaded
        if (!chartsVisible) {
            toggleDataVisibility(); // Make sure data is shown if it was hidden
        }
        if (!artVisible) {
            toggleArtVisibility(); // Make sure art is shown if it was hidden
        }

    } catch (error) {
        console.error('Error:', error);
    }
}

function displayPieChart(data) {
    const titles = data.map(item => item.title || 'Unknown Title');
    const titleCounts = titles.reduce((acc, title) => {
        acc[title] = (acc[title] || 0) + 1;
        return acc;
    }, {});

    const labels = Object.keys(titleCounts);
    const counts = Object.values(titleCounts);

    new Chart(document.getElementById('pieChart').getContext('2d'), {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: counts,
                backgroundColor: generateColors(labels.length),
                borderColor: 'rgba(0, 0, 0, 0.1)',
                borderWidth: 1
            }]
        },
        options: chartOptions
    });
}

function displayBarChart(data) {
    // Collect artists and handle 'Unknown Artist'
    const artists = data.map(item => item.artist_name || 'Unknown Artist');
    const artistCounts = artists.reduce((acc, artist) => {
        acc[artist] = (acc[artist] || 0) + 1;
        return acc;
    }, {});

    // Ensure 'Unknown Artist' is included
    if (!artistCounts['Unknown Artist']) {
        artistCounts['Unknown Artist'] = 0;
    }

    const labels = Object.keys(artistCounts);
    const counts = Object.values(artistCounts);

    new Chart(document.getElementById('barChart').getContext('2d'), {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Number of Artworks by Artist',
                data: counts,
                backgroundColor: generateColors(labels.length),
                borderColor: 'rgba(0, 0, 0, 0.1)',
                borderWidth: 1
            }]
        },
        options: {
            ...chartOptions,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function displayLineChart(data) {
    const titles = data.map(item => item.title || 'Unknown Title');
    const titleCounts = titles.reduce((acc, title) => {
        acc[title] = (acc[title] || 0) + 1;
        return acc;
    }, {});

    const labels = Object.keys(titleCounts);
    const counts = Object.values(titleCounts);

    window.lineChart = new Chart(document.getElementById('lineChart').getContext('2d'), {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Number of Objects by Title',
                data: counts,
                fill: false,
                borderColor: 'rgba(75, 192, 192, 1)',
                tension: 0.1
            }]
        },
        options: {
            ...chartOptions,
            plugins: {
                ...chartOptions.plugins,
                legend: {
                    ...chartOptions.plugins.legend,
                    display: labelsVisible
                }
            },
            scales: {
                x: {
                    ticks: {
                        display: labelsVisible,
                        autoSkip: !labelsVisible,
                        maxRotation: 90,
                        minRotation: 45
                    }
                },
                y: {
                    ticks: {
                        display: labelsVisible
                    }
                }
            }
        }
    });
}

function displayArt(data) {
    const artContainer = document.getElementById('artContainer');
    artContainer.innerHTML = ''; // Clear existing content

    data.forEach(item => {
        const artItem = document.createElement('div');
        artItem.className = 'art-item';

        const title = document.createElement('h2');
        title.textContent = item.title || 'Untitled';

        const image = document.createElement('img');
        image.src = item.image_url || 'path_to_placeholder_image';
        image.alt = item.title || 'Art Image';

        artItem.appendChild(title);
        artItem.appendChild(image);
        artContainer.appendChild(artItem);
    });
}

function generateColors(count) {
    const colors = [];
    for (let i = 0; i < count; i++) {
        const hue = Math.floor(Math.random() * 360);
        colors.push(`hsl(${hue}, 70%, 70%)`);
    }
    return colors;
}

function toggleDataVisibility() {
    const chartsContainer = document.getElementById('chartsContainer');
    if (chartsVisible) {
        chartsContainer.style.display = 'none'; // Hide charts
        document.getElementById('toggleDataBtn').textContent = 'Show Data'; // Update button text
    } else {
        if (dataLoaded) {
            chartsContainer.style.display = 'block'; // Show charts
        }
        document.getElementById('toggleDataBtn').textContent = 'Hide Data'; // Update button text
    }
    chartsVisible = !chartsVisible; // Toggle the state
}

function toggleLabelsVisibility() {
    labelsVisible = !labelsVisible;

    // Update the line chart with updated options
    if (window.lineChart) {
        lineChart.options.plugins.legend.display = labelsVisible;
        lineChart.options.scales.x.ticks.display = labelsVisible;
        lineChart.options.scales.x.ticks.autoSkip = !labelsVisible;
        lineChart.options.scales.y.ticks.display = labelsVisible; // Optionally toggle y-axis labels visibility
        lineChart.update();
    }

    // Update button text based on current state
    document.getElementById('toggleLabelsBtn').textContent = labelsVisible ? 'Hide Titles/Artists' : 'Show Titles/Artists';
}

function toggleArtVisibility() {
    const artContainer = document.getElementById('artContainer');
    if (artVisible) {
        artContainer.style.display = 'none'; // Hide art
        document.getElementById('toggleArtBtn').textContent = 'Show Art'; // Update button text
    } else {
        artContainer.style.display = 'grid'; // Show art
        document.getElementById('toggleArtBtn').textContent = 'Hide Art'; // Update button text
    }
    artVisible = !artVisible; // Toggle the state
}
