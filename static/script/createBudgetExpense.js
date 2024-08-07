document.addEventListener('DOMContentLoaded', function() {
    // Attach the click event listener to the "Add Budget Expenses" icon
    const addBudgetExpensesIcon = document.getElementById('addBudgetExpenses');
    if (addBudgetExpensesIcon) {
        addBudgetExpensesIcon.addEventListener('click', function() {
            // Display the modal
            const modalCreate = document.getElementById('modal-create');
            if (modalCreate) {
                modalCreate.style.display = 'block';
            }
        });
    }

    // Attach the click event listener to the "Cancel" button in the modal
    const cancelButton = document.getElementById('cancel');
    if (cancelButton) {
        cancelButton.addEventListener('click', function() {
            // Hide the modal
            const modalCreate = document.getElementById('modal-create');
            if (modalCreate) {
                modalCreate.style.display = 'none';
            }
        });
    }

    // Attach the click event listener to the "Submit" button in the modal
    const submitButton = document.getElementById('submit');
    if (submitButton) {
        submitButton.addEventListener('click', function() {
            // Get input values from the modal
            const expenseId = document.getElementById('Expense').value;
            const expectedAmount = parseFloat(document.getElementById('Expectedamount').value);
            // Get the budget expense ID from the data attribute
            const modalCreate = document.getElementById('modal-create');
            const budgetId = modalCreate.getAttribute('data-budget-id');

            // Validate input data
            if (expenseId && expectedAmount && expectedAmount > 0) {
                // Data is valid, send it to the server
                fetch('/create_budget_expense', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        expense_id: expenseId,
                        expected_amount: expectedAmount,
                        budgetId: budgetId ,
                    }),
                })
                .then(response => response.json())
                .then(data => {
                    // Handle the response, e.g., display a success message
                    console.log('Budget expense created:', data);
                    if(data.error){

                        // Display the error message
                        errorMessage=document.getElementById('errorMessage');
                        errorMessage.textContent = 'Budget expense must be unique';
                        errorMessage.style.display = 'block';
                        errorMessage.style.opacity = '1'; 

                        // Use setTimeout to hide the message after a delay
                        setTimeout(() => {
                            errorMessage.style.opacity = '0';
                            setTimeout(() => {
                                errorMessage.style.display = 'none';
                            }, 500);
                        }, 2000);
                        document.getElementById('modal-create').style.display='none'
                        return;

                    }
                    // Close the modal
                    const modalCreate = document.getElementById('modal-create');
                    if (modalCreate) {
                        modalCreate.style.display = 'none';
                    }

                    // Create a new table row
                    const newRow = document.createElement('tr');
                    newRow.setAttribute('data-row-id', data.budget_expense_id); // Use the correct ID from the response

                    // Fill in the table row with data
                    newRow.innerHTML = `
                        <td>${data.expense_name}</td>
                        <td>${data.expected_amount}</td>
                        <td>${data.actual_amount}</td>
                        <td>${(0).toFixed(2)}%</td>
                        <td class="actions">
                            <!-- Edit and Delete buttons with appropriate data attributes -->
                            <i class="fas fa-edit edit-transaction"
                            data-budgetexpense-id="${data.budget_expense_id}"
                            data-budget-id="${data.budget_id}"
                            data-estimate="${data.expected_amount}"
                            data-expensename="${data.expense_name}"
                            data-expenseid="${data.expense_id}"
                            aria-hidden="true"></i>
                            <i class="fas fa-trash-alt delete-transaction"
                            data-budgetexpense-id="${data.budget_expense_id}"
                            aria-hidden="true"></i>
                        </td>
                    `;

                    // Get the table body and insert the new row as the first child
                    const tableBody = document.getElementById('transactionTableBody');
                    if (tableBody) {
                        tableBody.insertBefore(newRow, tableBody.firstChild);
                    }

                    // Display the success message
                    successMessage=document.getElementById('successMessage');
                    successMessage.textContent = 'Dépense budgétaire créée avec succès';
                    successMessage.style.display = 'block';
                    successMessage.style.opacity = '1'; 

                    // Use setTimeout to hide the message after a delay
                    setTimeout(() => {
                        successMessage.style.opacity = '0';
                        setTimeout(() => {
                            successMessage.style.display = 'none';
                        }, 500);
                    }, 2000);
                })
                .catch(error => {
                    // Handle errors
                    console.error('Erreur lors de la création d’une dépense budgétaire:', error);
                    // Display an error message
                    errorMessage=document.getElementById('errorMessage');
                    errorMessage.textContent = 'Dépense budgétaire créée avec succès';
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
            } else {
                alert('Tous les champs doivent être fournis. Le montant doit être un nombre positif')
            }
        });
    }
});
