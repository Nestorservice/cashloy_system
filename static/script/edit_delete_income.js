// Function to display a success message
function displaySuccessMessage(message) {
    const successMessage = document.getElementById('successMessage');
    successMessage.textContent = message;
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

// Handle edit transaction button click
let incomeTransactionId;
let amount;
document.querySelectorAll('.edit-transaction').forEach(editButton => {
    editButton.addEventListener('click', () => {
        // Extract data attributes from the edit icon
        incomeTransactionId = editButton.getAttribute('data-transaction-id');
        const description = editButton.getAttribute('data-description');
        amount = editButton.getAttribute('data-amount');
        amount = parseFloat(amount.replace(/,|\/=|\s/g, ''))
        const date = editButton.getAttribute('data-date');
        const incomeCategoryId = editButton.getAttribute('data-categoryId');
        const incomeCategoryName = editButton.getAttribute('data-categoryname');

        console.log('Originals:', incomeTransactionId, description, amount, date, incomeCategoryId, incomeCategoryName);

        // Populate the edit form with data from the row
        document.getElementById('Editdate').value = date;
        document.getElementById('Editamount').value = amount;
        document.getElementById('Editdescription').value = description;

        // Preselect the category based on category ID
        const categorySelect = document.getElementById('editIncomeCategory');
        for (let i = 0; i < categorySelect.options.length; i++) {
            if (categorySelect.options[i].value === incomeCategoryId) {
                categorySelect.selectedIndex = i;
                break;
            }
        }

        // Display the edit form
        document.getElementById('modal-edit').style.display = 'block';
    });
});

// Handle cancel edit button click
document.getElementById('cancelEditTransaction').addEventListener('click', () => {
    // Hide the edit form
    document.getElementById('modal-edit').style.display = 'none';
});

// Handle edit form submission
document.getElementById('submitEditTransactionForm').addEventListener('click', () => {
    // Collect data from the edit form
    const newIncomeDate = document.getElementById('Editdate').value;
    const newIncomeAmount = parseFloat(document.getElementById('Editamount').value);
    const amtDiff = newIncomeAmount - amount;
    const newIncomeDescription = document.getElementById('Editdescription').value;
    const newIncomeCategoryId = document.getElementById('editIncomeCategory').value;

    console.log('Edits:', newIncomeDate, newIncomeAmount, newIncomeDescription, newIncomeCategoryId);

    // Perform data validations
    if (!newIncomeDate || !newIncomeAmount|| !newIncomeCategoryId) {
        // Required fields are missing, display an error message
        alert('Veuillez remplir tous les champs obligatoires.');
        return; // Stop further execution
    }

    if (new Date(newIncomeDate) > new Date()) {
        // Date is in the future, display an error message
        alert('Veuillez sélectionner une date qui n’est pas dans le futur.');
        return; // Stop further execution
    }

    if (newIncomeAmount < 0) {
        // Amount is negative, display an error message
        alert('Veuillez saisir un montant non négatif.');
        return; // Stop further execution
    }

    if (newIncomeDescription.length > 100) {
        // Description is too long, display an error message
        alert('La description ne doit pas dépasser 100 caractères.');
        return; // Stop further execution
    }

    // Construct a JSON object with the data
    const data = {
        transaction_id: incomeTransactionId,
        new_date: newIncomeDate,
        new_amount: newIncomeAmount,
        new_description: newIncomeDescription,
        new_category_id: newIncomeCategoryId,
        amtDiff: amtDiff
    };

    // Send a POST request to the edit route for Income transactions
    fetch('/edit_income_transaction', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
    .then(response => {
        if (response.ok) {
            // Transaction updated successfully
            response.json().then(data => {
                // Access specific data fields from the JSON response, e.g., edited_transaction
                const editedTransaction = data.edited_transaction;

                // Find the table row with the corresponding transaction_id
                const tableRow = document.querySelector(`tr[data-row-id="${editedTransaction.transaction_id}"]`);

                if (tableRow) {
                    // Update the table row data with the new data
                    tableRow.querySelector('td:nth-child(2)').textContent = editedTransaction.new_category_name; // Column 2 (Category Name)
                    tableRow.querySelector('td:nth-child(3)').textContent = editedTransaction.new_description;   // Column 3 (Description)
                    tableRow.querySelector('td:nth-child(4)').textContent = editedTransaction.new_date;          // Column 4 (Date)
                    tableRow.querySelector('td:nth-child(5)').textContent = editedTransaction.new_amount;        // Column 5 (Amount)

                    // Update data attributes of edit and delete icons
                    const editIcon = tableRow.querySelector('.edit-transaction');
                    const deleteIcon = tableRow.querySelector('.delete-transaction');

                    editIcon.setAttribute('data-description', editedTransaction.new_description);
                    editIcon.setAttribute('data-date', editedTransaction.new_date);
                    editIcon.setAttribute('data-amount', editedTransaction.new_amount);
                    editIcon.setAttribute('data-categoryname', editedTransaction.new_category_name);

                   // Hide the edit form
                   document.getElementById('modal-edit').style.display = 'none';

                   displaySuccessMessage(data.message)
                }
            });
        } else {
            // Handle errors and display an error message
            response.json().then(errorData => {
                console.error('Erreur du serveur :', errorData);
            });
        }
    });

    // Hide the edit form
    document.getElementById('modal-edit-income').style.display = 'none';
});



// Handle delete transaction button click
document.querySelectorAll('.delete-transaction').forEach(deleteButton => {
    deleteButton.addEventListener('click', () => {
        // Extract data attributes from the delete icon
        const incomeTransactionId = deleteButton.getAttribute('data-transaction-id');

        // Display a confirmation modal for deletion
        document.getElementById('modal-delete').style.display = 'block';

        // Add an event listener for the delete button in the modal
        document.getElementById('modal-content-delete').addEventListener('click', () => {
            // Send a POST request to the delete route for Income transactions
            fetch('/delete_income_transaction', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ transaction_id: incomeTransactionId }),
            })
            .then(response => {
                if (response.ok) {
                    // Transaction deleted successfully
                    response.json().then(data => {
                        // Find the table row with the corresponding transaction_id
                        const tableRow = document.querySelector(`tr[data-row-id="${incomeTransactionId}"]`);
                        // Add the 'fadeOut' class to initiate the animation
                        tableRow.classList.add('fadeOut');
                        // Wait for the animation to complete (0.5s in this example)
                        setTimeout(() => {
                            tableRow.classList.remove('fadeOut');
                            const tableBody = document.getElementById('transactionTableBody');
                            tableBody.removeChild(tableRow);
                        }, 500);
                        // Hide the delete modal
                        document.getElementById('modal-delete').style.display = 'none';
                        // Display a success message
                        displaySuccessMessage(data.message);
                    });
                } else {
                    // Handle errors and display an error message
                }
            });

            // Hide the confirmation modal
            document.getElementById('modal-delete').style.display = 'none';
        });
    });
});

// Handle cancel delete button click
document.getElementById('modal-content-cancel').addEventListener('click', () => {
    // Hide the delete confirmation modal
    document.getElementById('modal-delete').style.display = 'none';
});
