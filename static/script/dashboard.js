// Function to fetch chart data and render the chart
async function renderChart() {
    try {
        // Fetch chart data from the '/chart_data' route
        const response = await fetch('/chart_data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            throw new Error('Failed to fetch chart data');
        }

        const chartData = await response.json();

        // Get the chart container elements
        const incomechartContainer = document.getElementById('incomeChart');
        const chartContainer = document.getElementById('expenseChart');
        const trendContainer = document.getElementById('extraChart');

        // Create a canvas element to render the chart
        const canvas = document.createElement('canvas');
        chartContainer.appendChild(canvas);

        const incomecanvas = document.createElement('canvas');
        incomechartContainer.appendChild(incomecanvas);

        const trendcanvas = document.createElement('canvas');
        trendContainer.appendChild(trendcanvas);

        const ctx = canvas.getContext('2d');
        const incomectx = incomecanvas.getContext('2d');
        const trendctx = trendcanvas.getContext('2d');

        // Create and configure the chart using Chart.js
        const incomechart = new Chart(incomectx, {
            type: 'doughnut',
            data: {
                labels: chartData.income_chart_data.labels,
                datasets: [{
                    label: 'Income',
                    data: chartData.income_chart_data.values,
                    backgroundColor: chartData.expense_chart_data.colors,
                    borderColor: '#d4d9d6',  // Set border color for pie chart slices
                    borderWidth: 1,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,  // Allow chart resizing
                devicePixelRatio: 2,  // Increase the pixel ratio as needed
                plugins: {
                    legend: {
                        position: 'right',  // Move the legend to the right
                        labels: {
                            font: {
                                size: 12,  // Set legend label font size
                            },
                        },
                    },
                    title: {
                        display: true,
                        text: 'Répartition du revenu',
                        position: 'bottom',
                        align: 'start',
                        font: {
                            size: 12, // Set the font size for the title
                            weight: 'bold', // Set the font weight (optional)
                        },
                        padding: {
                            top: 3,
                            bottom: 0,
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                // Format the tooltip label as a percentage with a percent symbol
                                const value = context.parsed;
                                return value.toFixed(2) + '%'; // Two decimal places and a percent symbol
                            },
                        },
                    },
                },
            },
        });

        // Create and configure the chart using Chart.js
        const chart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: chartData.expense_chart_data.labels,
                datasets: [{
                    label: 'Dépense',
                    data: chartData.expense_chart_data.values,
                    backgroundColor: chartData.expense_chart_data.colors,
                    borderColor: '#d4d9d6',  // Set border color for pie chart slices
                    borderWidth: 1,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,  // Allow chart resizing
                devicePixelRatio: 2,  // Increase the pixel ratio as needed
                plugins: {
                    legend: {
                        position: 'right',  // Move the legend to the right
                        labels: {
                            font: {
                                size: 12,  // Set legend label font size
                            },
                        },
                    },
                    title: {
                        display: true,
                        text: 'Répartition des charges / revenus',
                        position: 'bottom',
                        align: 'start',
                        font: {
                            size: 12, // Set the font size for the title
                            weight: 'bold', // Set the font weight (optional)
                        },
                        padding: {
                            top: 3,
                            bottom: 0
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                // Format the tooltip label as a percentage with a percent symbol
                                const value = context.parsed;
                                return value.toFixed(2) + '%'; // Two decimal places and a percent symbol
                            },
                        },
                    },
                },
            },
        });

        // Create and configure the chart using Chart.js
        const trendchart = new Chart(trendctx, {
            type: 'line',
            data: {
                labels: chartData.cash_out_chart_data.labels,
                datasets: [{
                    label: '',
                    data: chartData.cash_out_chart_data.values,
                    fill: false,
                    tension: 0.5,
                    borderWidth: 1.5,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,  // Allow chart resizing
                devicePixelRatio: 2,  // Increase the pixel ratio as needed
                scales: {
                    x: {
                        grid: {
                            display: true, // Show X-axis grid lines
                            color: 'rgba(255, 255, 255, 0.3)', // Set the color of X-axis grid lines
                        },
                    },
                    y: {
                        grid: {
                            display: true, // Show Y-axis grid lines
                            color: 'rgba(255, 255, 255, 0.3)', // Set the color of Y-axis grid lines
                        },
                    },
                },
                plugins: {
                    legend: {
                        display: false, // Hide legend
                    },
                    title: {
                        display: true,
                        text: 'Tendance des dépenses',
                        position: 'bottom',
                        align: 'start',
                        font: {
                            size: 12, // Set the font size for the title
                            weight: 'bold', // Set the font weight (optional)
                        },
                        padding: {
                            top: 3,
                            bottom: 0
                        }
                    },
                },
            },
        });

    } catch (error) {
        console.error('Erreur lors de la récupération des données du graphique:', error);
    }
}

Chart.defaults.color = 'white';
// Call the function when the page loads
window.onload = renderChart;
