function createBudget() {
    fetch('/budget', {
        method: 'POST',
    })
    .then(response => response.json())
    .then(data => {
        // Handle the response, e.g., display a success message
        console.log('Budget créé :', data);

        // Map month numbers to their names
        const monthNames = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ];

        // Get the month name based on the month number
        const monthName = monthNames[data.month - 1];

        // Update the <h4> element with the received JSON data
        const currentBudgetElement = document.getElementById('currentBudgetInfo');
        if (currentBudgetElement) {
            currentBudgetElement.textContent = `${data.year} ${monthName}`;
        }

        // Create a new budget card
        const previousBudgetsContainer = document.getElementById('previousBudgets');
        if (previousBudgetsContainer) {
            const newBudgetCard = document.createElement('div');
            newBudgetCard.classList.add('budgetcard');
            newBudgetCard.setAttribute('data-budget-id', data.id);

            // Populate the new budget card with data
            newBudgetCard.innerHTML = `
                <h4>${monthName} ${data.year}</h4>
                <p>Estimer: ${data.expected_amount || '0.00'}</p>
                <p>Actuel: ${data.spent_amount || '0.00'}</p>
            `;

            // Append the new budget card as the first child of the container
            previousBudgetsContainer.insertBefore(newBudgetCard, previousBudgetsContainer.firstChild);

            // set the budget expense ID to the modal create data attribute
            const modalCreate = document.getElementById('modal-create');
            modalCreate.setAttribute('data-budget-id', data.id);

            // Display the success message
            successMessage=document.getElementById('successMessage');
            successMessage.textContent = 'Budget créé avec succès';
            successMessage.style.display = 'block';
            successMessage.style.opacity = '1'; 

            // Use setTimeout to hide the message after a delay
            setTimeout(() => {
                successMessage.style.opacity = '0';
                setTimeout(() => {
                    successMessage.style.display = 'none';
                }, 500);
            }, 2000);
        }

        const addBudgetExpensesBtn = document.getElementById('addBudgetExpenses');
        if(addBudgetExpensesBtn){
            addBudgetExpensesBtn.style.display='inline';              
        }
        document.getElementById('createBudget').style.display='none'; 
    })
    .catch(error => {
        // Handle errors
        console.error('Erreur lors de la création du budget :', error);
        // Display the error message
        errorMessage=document.getElementById('errorMessage');
        errorMessage.textContent = 'Erreur lors de la création du budget : ${error}';
        errorMessage.style.display = 'block';
        errorMessage.style.opacity = '1'; 

        // Use setTimeout to hide the message after a delay
        setTimeout(() => {
            errorMessage.style.opacity = '0';
            setTimeout(() => {
                errorMessage.style.display = 'none';
            }, 500);
        }, 2000);
    });
}

document.addEventListener('DOMContentLoaded', function() {
    // Attach the click event listener to the createBudget icon
    const createBudgetIcon = document.getElementById('createBudget');
    if (createBudgetIcon) {
        createBudgetIcon.addEventListener('click', createBudget);
    }
});


 // Function to render the horizontal bar chart
 async function renderBudgetChart() {
    try {
        // Retrieve data attributes from the 'budgetChart' element
        const budgetChartElement = document.getElementById('budgetChart');
        const actualAmount = parseFloat(budgetChartElement.dataset.actual_amount);
        const expectedAmount = parseFloat(budgetChartElement.dataset.expected_amount);

        // Create a canvas element to render the chart
        const canvas = document.createElement('canvas');
        budgetChartElement.appendChild(canvas);

        // Create a chart using Chart.js
        const ctx = canvas.getContext('2d');
        const budgetData = {
            labels: ['Total actuel', 'Total estimer'],
            datasets: [{
                data: [actualAmount, expectedAmount],
                backgroundColor: ['#bfd220', '#f95395'], // Use your desired colors
                borderColor: 'white', // Set border color for the bars
                borderWidth: 1,
            }],
        };

        const budgetChart = new Chart(ctx, {
            type: 'bar',
            data: budgetData,
            options: {
                indexAxis: 'y',
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
                        text: 'Aperçu du budget', // Set your chart title here
                        font: {
                            size: 15, // Set the font size for the title
                            weight: 'bold', // Set the font weight (optional)
                        },
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
        });

    } catch (error) {
        console.error('Erreur lors du rendu du graphique budgétaire :', error);
    }
}

Chart.defaults.color = 'white';
// Call the function when the page loads
window.onload = renderBudgetChart;