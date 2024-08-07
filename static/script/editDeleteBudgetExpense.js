document.addEventListener("DOMContentLoaded", function() {
    // ... Other code ...

    // Add click event listeners to edit icons
    const editIcons = document.querySelectorAll('.edit-transaction');
    editIcons.forEach(editIcon => {
        editIcon.addEventListener('click', function() {
            // Get data attributes from the icon
            const budgetExpenseId = editIcon.getAttribute('data-budgetexpense-id');        
            const estimate = editIcon.getAttribute('data-estimate');
            const expenseId = editIcon.getAttribute('data-expenseid');
            const budgetId = editIcon.getAttribute('data-budget-id');

             // Prepopulate the edit modal fields 
            const editExpectedAmountInput = document.getElementById('editExpectedamount');
            editExpectedAmountInput.value = estimate;

            // Show the edit modal
            const editModal = document.getElementById('modal-edit');
            editModal.style.display = 'block';

            // Add click event listener to edit modal submit button
            const editSubmitButton = document.getElementById('editsubmit');
            editSubmitButton.addEventListener('click', function() {
                // Get the edited values
                //const editedExpenseId = editExpenseSelect.value;
                const editedExpectedAmount = editExpectedAmountInput.value;

                // Call a function to send the edited data to the server for processing
                sendEditDataToServer(budgetExpenseId, budgetId, expenseId, editedExpectedAmount);

                // Hide the edit modal after submitting
                editModal.style.display = 'none';
            });

            // Add click event listener to edit modal cancel button
            const editCancelButton = document.getElementById('editcancel');
            editCancelButton.addEventListener('click', function() {
                // Hide the edit modal without saving changes
                editModal.style.display = 'none';
            });
        });
    });

    // Add click event listeners to delete icons
    const deleteIcons = document.querySelectorAll('.delete-transaction');
    deleteIcons.forEach(deleteIcon => {
        deleteIcon.addEventListener('click', function() {
            // Show the delete confirmation modal
            const deleteModal = document.getElementById('modal-delete');
            deleteModal.style.display = 'block';

            // Add click event listener to delete modal delete button
            const deleteButton = document.getElementById('modal-content-delete');
            deleteButton.addEventListener('click', function() {
                // Get the budgetExpenseId to delete
                const budgetExpenseId = deleteIcon.getAttribute('data-budgetexpense-id');

                // Call a function to send the delete request to the server
                sendDeleteRequestToServer(budgetExpenseId);

                // Hide the delete confirmation modal after deleting
                deleteModal.style.display = 'none';
            });

            // Add click event listener to delete modal cancel button
            const cancelButton = document.getElementById('modal-content-cancel');
            cancelButton.addEventListener('click', function() {
                // Hide the delete confirmation modal without deleting
                deleteModal.style.display = 'none';
            });
        });
    });

    // ... Rest of your code ...
});


async function sendEditDataToServer(budgetExpenseId, budgetId, expenseId, editedExpectedAmount) {
    try {
        // Send an asynchronous request to the server to edit the BudgetExpense
        const response = await fetch('/edit_budget_expense', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                budget_expense_id: budgetExpenseId,
                budget_id: budgetId,
                expenseId: expenseId,
                edited_expected_amount: editedExpectedAmount,
            }),
        });

        if (!response.ok) {
            throw new Error('Échec de la modification de BudgetExpense');
        }

        const responseData = await response.json();

        // Handle success, e.g., update the UI with the edited data
        // Find the corresponding table row and update the expected amount cell
        const tableRow = document.querySelector(`tr[data-row-id="${budgetExpenseId}"]`);
        const expectedAmountCell = tableRow.querySelector('td:nth-child(2)'); // Adjust the index if needed

        // Update the expected amount in the UI
        expectedAmountCell.textContent = `${responseData.updated_expected_amount}/=`;

        // Display the success message
        successMessage=document.getElementById('successMessage');
        successMessage.textContent = 'Montant prévu mis à jour avec succès';
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
        console.error('Erreur lors de la modification de BudgetExpense :', error);
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

async function sendDeleteRequestToServer(budgetExpenseId) {
    try {
        // Send an asynchronous request to the server to delete the BudgetExpense
        const response = await fetch('/delete_budget_expense', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                budget_expense_id: budgetExpenseId,
            }),
        });

        if (!response.ok) {
            throw new Error('Échec de la suppression de la dépense budgétaire');
        }

        const responseData = await response.json();

        const tableRow = document.querySelector(`tr[data-row-id="${budgetExpenseId}"]`);
        // Add the 'fadeOut' class to initiate the animation
        tableRow.classList.add('fadeOut');
        // Wait for the animation to complete (0.5s in this example)
        setTimeout(() => {
            tableRow.classList.remove('fadeOut');
            const tableBody = document.getElementById('transactionTableBody');
            tableBody.removeChild(tableRow);
        }, 500);

         // Display the success message
         successMessage=document.getElementById('successMessage');
         successMessage.textContent = 'Dépense budgétaire supprimée avec succès';
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
        console.error('Erreur lors de la suppression de BudgetExpense :', error);
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
