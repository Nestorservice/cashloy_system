async function renderCreditChart() {
    try {
        // Retrieve data attributes from the 'Chart' element
        const ChartElement = document.getElementById('chart');
        const paidAmount = parseFloat(ChartElement.dataset.totalpaidamount);
        const owedAmount = parseFloat(ChartElement.dataset.totalowedamount);

        console.log(ChartElement, paidAmount, owedAmount)

        // Create a canvas element to render the chart
        const canvas = document.createElement('canvas');
        ChartElement.appendChild(canvas);

        console.log(ChartElement, paidAmount, owedAmount)

        // Create a chart using Chart.js
        const ctx = canvas.getContext('2d');
        const budgetData = {
            labels: ['Total payé', 'Total pris'],
            datasets: [{
                data: [paidAmount, owedAmount],
                backgroundColor: ['#bfd220', '#f95395'], // Use your desired colors
                borderColor: 'white', // Set border color for the bars
                borderWidth: 1,
                color: 'white',
            }],
        };

        // Check the viewport width
        const isMobile = window.innerWidth <= 768;

        // Configure chart options based on viewport width
        const options = {
            responsive: true,
            maintainAspectRatio: false,
            devicePixelRatio: 2,
            scales: {
                x: {
                    beginAtZero: true,
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
                    display: false,
                    text: 'Budget Overview', // Set your chart title here
                    font: {
                        size: 15, // Set the font size for the title
                        weight: 'bold', // Set the font weight (optional)
                    },
                },
                tooltips: {
                    callbacks: {
                        label: function (context) {
                            const value = context.parsed;
                            return `${value.toFixed(2)} /=`; // Format as currency
                        },
                    },
                },
            },
        };

        if (isMobile) {
            options.indexAxis = 'y'; // Set indexAxis to 'y' for mobile viewports
        }

        const creditChart = new Chart(ctx, {
            type: 'bar',
            data: budgetData,
            options: options,
        });

    } catch (error) {
        console.error('Erreur lors du rendu du graphique budgétaire :', error);
    }
}

Chart.defaults.color = 'white';
// Call the function when the page loads
window.onload = renderCreditChart;
