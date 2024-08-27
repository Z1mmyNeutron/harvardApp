document.getElementById('loadDataBtn').addEventListener('click', loadData);
document.getElementById('toggleDataBtn').addEventListener('click', toggleDataVisibility);

let chartsVisible = true; // Track visibility state

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

        // Ensure charts are visible
        if (chartsVisible) {
            document.getElementById('chartsContainer').classList.remove('hidden');
            updateToggleButtonText(false);
        }

    } catch (error) {
        console.error('Error:', error);
    }
}

function toggleDataVisibility() {
    const chartsContainer = document.getElementById('chartsContainer');
    chartsVisible = !chartsVisible; // Toggle visibility state
    chartsContainer.classList.toggle('hidden', !chartsVisible);
    updateToggleButtonText(!chartsVisible);
}

function updateToggleButtonText(hidden) {
    const button = document.getElementById('toggleDataBtn');
    button.textContent = hidden ? 'Show Data' : 'Hide Data';
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
