document.addEventListener('DOMContentLoaded', function() {

    // Add a click event handler to all cards with the class 'catCard'
    document.querySelectorAll('.catCard').forEach(function(card) {
        card.addEventListener('click', function() {
            var category_name = this.getAttribute('data-categoryname');
            
            console.log(category_name);

            fetch('/income', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ category_name: category_name }),
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('La réponse du réseau n’était pas OK');
                }
                return response.json();
            })
            .then(data => {
                // Handle the retrieved transactions data here
                console.log(data.transactions);

                if (data.transactions.length == 0){
                    // Display the success message
                    successMessage=document.getElementById('successMessage');
                    successMessage.textContent = 'Aucune transaction existante au cours de cette période';
                    successMessage.style.backgroundColor = '#f95395';
                    successMessage.style.color = 'black';
                    successMessage.style.display = 'block';
                    successMessage.style.opacity = '1'; 

                    // Use setTimeout to hide the message after a delay
                    setTimeout(() => {
                        // Set the opacity to 0 for fading out
                        successMessage.style.opacity = '0';

                        // After the transition completes (0.5 seconds), hide the message
                        setTimeout(() => {
                            successMessage.style.display = 'none';
                        }, 500);
                    }, 2000);
                }
                document.getElementById('incomeSummaryAmount').textContent = data.total
                // Update your table or display the filtered data as needed
                const tableBody = document.getElementById('transactionTableBody');
                tableBody.innerHTML = '';  // Clear the table body

                // Iterate through the income transactions and create rows
                data.transactions.forEach((transaction) => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>CF${transaction.id.toString().padStart(3, '0')}INC</td>
                        <td>${transaction.category}</td>
                        <td>${transaction.description}</td>
                        <td>${transaction.date}</td>
                        <td class="income_amount_cell">${transaction.amount}</td>
                        <td class="actions">
                            <i class="fas fa-edit edit-transaction" data-transaction-id="${transaction.id}" data-description="${transaction.description}" data-amount="${transaction.amount}" data-date="${transaction.date}"></i>
                            <i class="fas fa-trash-alt delete-transaction" data-transaction-id="${transaction.id}"></i> 
                        </td>
                    `;
                    tableBody.appendChild(row);
                });
            })
            .catch(error => {
                // Handle errors here
                console.error(error.message);
            });
        });
    });
    


    const fromInput = document.getElementById('dateRangePickerFrom');
    const toInput = document.getElementById('dateRangePickerTo');
    const searchButton = document.getElementById('searchButton');

    searchButton.addEventListener('click', function() {
        const fromDate = fromInput.value;
        const toDate = toInput.value;

        console.log(fromDate, toDate)

        // Perform date validation
        if (!fromDate || !toDate) {
            alert('Veuillez sélectionner les dates « De » et « À ».');
            return;
        }

        const currentDate = new Date().toISOString().split('T')[0];

        if (fromDate > toDate) {
            alert('La date de début ne doit pas être supérieure à la date de fin.');
            return;
        }

        if (fromDate > currentDate || toDate > currentDate) {
            alert('Les dates sélectionnés ne doivent pas être dans le futur.');
            return;
        }

        // Perform an asynchronous request to search income transactions
        const url = `/search_income_transactions?from=${fromDate}&to=${toDate}`;
        
        fetch(url)
            .then(response => response.json())
            .then(data => {
                // Handle the response and update the UI with the search results
                console.log('Search results:', data);
                if (data.individual_incomes.length == 0){
                    // Display the success message
                    successMessage=document.getElementById('successMessage');
                    successMessage.textContent = 'Aucune transaction existante au cours de cette période';
                    successMessage.style.backgroundColor = '#f95395';
                    successMessage.style.color = 'black';
                    successMessage.style.display = 'block';
                    successMessage.style.opacity = '1'; 

                    // Use setTimeout to hide the message after a delay
                    setTimeout(() => {
                        // Set the opacity to 0 for fading out
                        successMessage.style.opacity = '0';

                        // After the transition completes (0.5 seconds), hide the message
                        setTimeout(() => {
                            successMessage.style.display = 'none';
                        }, 500);
                    }, 2000);
                }

                // Clear existing cards
                const categoryCardsContainer = document.getElementById('categoryCards');
                categoryCardsContainer.innerHTML = '';

                // Iterate through the data and create cards
                for (const category in data.income_totals) {
                    if (data.income_totals.hasOwnProperty(category)) {
                        const [amount, percentage] = data.income_totals[category];
                        // Create a new card element
                        const card = document.createElement('div');
                        card.className = 'catCard';
                        card.dataset.categoryname = category;

                        // Create the card's inner elements
                        const categoryNameElement = document.createElement('div');
                        categoryNameElement.style.fontSize = '16px';
                        categoryNameElement.style.fontWeight = '400';
                        categoryNameElement.textContent = category;

                        const amountElement = document.createElement('div');
                        amountElement.style.color = '#bfd220';
                        amountElement.style.fontWeight = '600';
                        amountElement.style.fontSize = '27px';
                        amountElement.textContent = amount;

                        const percentageElement = document.createElement('div');
                        percentageElement.style.fontSize = '12px';
                        percentageElement.textContent = percentage + '%';

                        const progressBarContainer = document.createElement('div');
                        progressBarContainer.style.maxWidth = '150px';
                        progressBarContainer.style.width = '150px';
                        progressBarContainer.style.height = '4px';
                        progressBarContainer.style.backgroundColor = 'white';
                        progressBarContainer.style.paddingBottom = '3px';

                        const progressBar = document.createElement('div');
                        progressBar.style.backgroundColor = '#141c33';
                        progressBar.style.height = '4px';
                        progressBar.style.width = percentage+'%';

                        // Append the inner elements to the card
                        progressBarContainer.appendChild(progressBar);
                        card.appendChild(categoryNameElement);
                        card.appendChild(amountElement);
                        card.appendChild(percentageElement);
                        card.appendChild(progressBarContainer);

                        // Append the card to the categoryCards container
                        categoryCardsContainer.appendChild(card);
                    }
                }

                /* Update summary section:*/
                // Format the dates in the desired format (e.g., 'Month Day, Year')
                const formatDate = (dateString) => {
                    const options = { year: 'numeric', month: 'short', day: 'numeric' };
                    const date = new Date(dateString);
                    return date.toLocaleDateString('en-US', options);
                };

                const formatIncome = (amount) => {
                    // Format the number with commas as thousands separator and add '/='
                    return amount.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',') + '/=';
                };

                const from = formatDate(fromDate);
                const to = formatDate(toDate);
                const formattedIncome = formatIncome(data.total_income);
                document.getElementById('incomeSummaryAmount').textContent = formattedIncome;
                document.getElementById('fromincomeSummaryDateRange').textContent = from;
                document.getElementById('toincomeSummaryDateRange').textContent = to;


                // Update your table or display the filtered data as needed
                const tableBody = document.getElementById('transactionTableBody');
                tableBody.innerHTML = '';  // Clear the table body

                // Iterate through the income transactions and create rows
                data.individual_incomes.forEach((transaction) => {
                    // Format the date as 'yyyy-mm-dd'
                    const formattedDate = new Date(transaction.date).toISOString().split('T')[0];
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>CF${transaction.id.toString().padStart(3, '0')}INC</td>
                        <td>${transaction.name}</td>
                        <td>${transaction.description}</td>
                        <td>${formattedDate}</td>
                        <td class="income_amount_cell">${transaction.amount}</td>
                        <td class="actions">
                            <i class="fas fa-edit edit-transaction" data-transaction-id="${transaction.id}" data-description="${transaction.description}" data-amount="${transaction.amount}" data-date="${formattedDate}"></i>
                            <i class="fas fa-trash-alt delete-transaction" data-transaction-id="${transaction.id}"></i> 
                        </td>
                    `;
                    tableBody.appendChild(row);
                });
            })
            .catch(error => {
                console.error('Erreur lors de la recherche de transactions :', error);
            });
    });
});
