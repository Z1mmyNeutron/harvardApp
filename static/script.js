document.getElementById('loadDataBtn').addEventListener('click', loadData);
document.getElementById('toggleDataBtn').addEventListener('click', toggleDataVisibility);

let dataLoaded = false;
let chartsVisible = true; // Tracks whether charts are visible or hidden

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

        // Process and display line chart
        displayLineChart(data);

        dataLoaded = true; // Mark data as loaded
        if (!chartsVisible) {
            toggleDataVisibility(); // Make sure data is shown if it was hidden
        }

    } catch (error) {
        console.error('Error:', error);
    }
}

function displayPieChart(data) {
    const titles = data.records.map(item => item.title || 'Unknown Title');
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
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
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
        }
    });
}

function displayLineChart(data) {
    const titles = data.records.map(item => item.title || 'Unknown Title');
    const titleCounts = titles.reduce((acc, title) => {
        acc[title] = (acc[title] || 0) + 1;
        return acc;
    }, {});

    const labels = Object.keys(titleCounts);
    const counts = Object.values(titleCounts);

    new Chart(document.getElementById('lineChart').getContext('2d'), {
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
            responsive: true,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed !== null) {
                                label += context.parsed;
                            }
                            return label;
                        }
                    }
                }
            }
        }
    });
}

// Helper function to generate colors for pie chart segments
function generateColors(count) {
    const colors = [];
    for (let i = 0; i < count; i++) {
        const hue = Math.floor(Math.random() * 360);
        colors.push(`hsl(${hue}, 70%, 70%)`);
    }
    return colors;
}

// Toggle visibility of the charts
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
