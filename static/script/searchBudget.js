document.addEventListener("DOMContentLoaded", function() {
    // Populate year select options
    var currentYear = new Date().getFullYear();
    var yearSelect = document.getElementById('yearSelect');
    for (var year = currentYear; year >= currentYear - 20; year--) {
        var option = document.createElement('option');
        option.value = year;
        option.text = year;
        yearSelect.appendChild(option);
    }

    // Populate month select options
    var monthSelect = document.getElementById('monthSelect');
    var months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
    for (var i = 0; i < months.length; i++) {
        var monthValue = (i + 1).toString().padStart(2, '0'); // Zero-padding for single-digit months
        var option = document.createElement('option');
        option.value = monthValue;
        option.text = months[i];
        monthSelect.appendChild(option);
    }

    document.getElementById('searchButton').addEventListener('click', function() {
        // Get selected year and month values
        var selectedYear = yearSelect.value;
        var selectedMonth = monthSelect.value;

        console.log("Recherche de budget avec l’année : " + selectedYear + " et Mois : " + selectedMonth);

        searchBudgetByYearMonth(selectedYear, selectedMonth)

        
    });
});

// Function to search for a budget by year and month
async function searchBudgetByYearMonth(year, month) {
    try {
        // Send an asynchronous request to the server
        const response = await fetch('/search_budget_by_year_month', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                year: year,
                month: month,
            }),
        });

        if (!response.ok) {
            throw new Error('Echec de la recherche de budget');
        }

        const searchData = await response.json();

        console.log(searchData);

        populateTableWithData(searchData)

        // Retrieve data attributes from the 'budgetChart' element
        const budgetChartElement = document.getElementById('budgetChart');
        console.log(budgetChartElement);
        
        // Get the existing chart instance
        const existingChart = budgetChartElement.firstElementChild;

        console.log(existingChart);

        // If an existing chart instance exists, destroy it
        if (existingChart) {
            existingChart.remove();
        }

        renderBudgetChart(parseFloat(searchData.total_spent_amount), parseFloat(searchData.total_expected_amount))

        const currentBudgetInfo = document.getElementById('currentBudgetInfo');
        currentBudgetInfo.textContent = `${searchData.year} ${searchData.month}`

        // Populate budget summary information
        const budgetSummaryElement = document.getElementById('budgetSummary');
        const percentElement = budgetSummaryElement.querySelector('#percent h4');
        const countElement = budgetSummaryElement.querySelector('#count h4');

        percentElement.textContent = searchData.percent;

        // Update the expense count
        countElement.textContent = searchData.expense_count;

        console.log(percentElement, countElement);
        // Display the success message
        successMessage=document.getElementById('successMessage');
        successMessage.textContent = 'Budget trouvé';
        successMessage.style.display = 'block';
        successMessage.style.opacity = '1'; 

        // Use setTimeout to hide the message after a delay
        setTimeout(() => {
            successMessage.style.opacity = '0';
            setTimeout(() => {
                successMessage.style.display = 'none';
            }, 500);
        }, 2000);

    } catch (error) {
        console.error('Erreur lors de la recherche du budget par année et par mois :', error);
        // Display the error message
        errorMessage=document.getElementById('errorMessage');
        errorMessage.textContent = error;
        errorMessage.style.display = 'block';
        errorMessage.style.opacity = '1'; 

        // Use setTimeout to hide the message after a delay
        setTimeout(() => {
            errorMessage.style.opacity = '0';
            setTimeout(() => {
                errorMessage.style.display = 'none';
            }, 500);
        }, 2000);
    }
}


// Function to populate the table with data
function populateTableWithData(data) {
    // Clear the existing table rows
    const tableBody = document.getElementById('transactionTableBody');
    tableBody.innerHTML = '';

    // Loop through the data and create table rows
    data.budget_expenses.forEach(expense => {
        const newRow = document.createElement('tr');
        newRow.setAttribute('data-row-id', expense.id);

        newRow.innerHTML = `
            <td>${expense.expense_name}</td>
            <td style="color: #bfd220;">${expense.expected_amount}</td>
            <td style="color:${expense.expected_amount >= expense.spent_amount ? '#bfd220' : '#f95395'};">${expense.spent_amount}</td>
            <td>${expense.percentage}%</td>
            <td class="actions">
                <!-- Edit and Delete buttons with appropriate data attributes -->
                <i class="fas fa-edit edit-transaction"
                data-budgetexpense-id="${expense.id}"
                data-budget-id="${expense.budget_id}"
                data-estimate="${expense.expected_amount}"
                data-expensename="${expense.expense_name}"
                data-expenseid="${expense.expense_id}"
                aria-hidden="true"></i>
                <i class="fas fa-trash-alt delete-transaction"
                data-budgetexpense-id="${expense.id}"
                aria-hidden="true"></i>
            </td>
        `;

        console.log(newRow);
        
        tableBody.appendChild(newRow);
    });
}

// Function to render the horizontal bar chart
async function renderBudgetChart(actualAmount, expectedAmount) {
    try {
        // Create a canvas element to render the chart
        const budgetChartElement = document.getElementById('budgetChart');
        const canvas = document.createElement('canvas');
        budgetChartElement.appendChild(canvas);

        // Create a chart using Chart.js
        const ctx = canvas.getContext('2d');
        const budgetData = {
            labels: ['Total actuel', 'Estimation totale'],
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
