document.addEventListener("DOMContentLoaded", function () {
    // Get references to the open and close icons for the category form
    const openCategoryForm = document.getElementById('openCategoryForm');
    const closeCategoryForm = document.getElementById('closeCategoryForm');
    const categoryForm = document.getElementById('categoryForm');
    const categoryFormSubmitButton = document.getElementById('submitCategoryForm');

    // Get references to the open and close icons for the transaction form
    const openTransactionForm = document.getElementById('openTransactionForm');
    const closeTransactionForm = document.getElementById('closeTransactionForm');
    const transactionForm = document.getElementById('transactionForm');

    // Function to show a form and hide the other form
    function showFormAndHideOther(formToShow, formToHide) {
        formToShow.style.display = 'block';
        formToHide.style.display = 'none';
    }

    // Function to hide a form
    function hideForm(formToHide) {
        formToHide.style.display = 'none';
    }

    // Add click event listener to open the category form and close the transaction form
    openCategoryForm.addEventListener('click', function () {
        showFormAndHideOther(categoryForm, transactionForm);
    });

    // Add click event listener to close the category form
    closeCategoryForm.addEventListener('click', function () {
        hideForm(categoryForm);
    });

    // Add click event listener to open the transaction form and close the category form
    openTransactionForm.addEventListener('click', function () {
        showFormAndHideOther(transactionForm, categoryForm);
    });

    // Add click event listener to close the transaction form
    closeTransactionForm.addEventListener('click', function () {
        hideForm(transactionForm);
    });

    /* Attach a click event handler to the submit button */
    var submitButton = document.getElementById("submitCategoryForm");
    submitButton.addEventListener("click", function (e) {
    e.preventDefault();

    // Get the category name from the input field
    var categoryName = document.getElementById("categoryName").value;
    
    // Get the error display
    const errorDisplayElement = document.getElementById("categoryFormError");

    // Validate the category name
    if (categoryName.length === 0) {    
        errorDisplayElement.textContent = "Le nom de la catégorie ne peut pas être vide.";
        errorDisplayElement.style.display = 'Block';
        return;
        
    } else if (categoryName.length > 100) {
        errorDisplayElement.textContent = "Category name cannot exceed 100 characters.";
    } else {
        // Clear any previous error messages
        document.getElementById("categoryFormError").textContent = "";
        errorDisplayElement.style.display = 'none';

        // Create a data object to send in the POST request
        var data = {
        categoryName: categoryName,
        };

        // Send an asynchronous POST request using fetch
        fetch("/create_expense_category", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
        })
        .then(function (response) {
            return response.json();
        })
        .then(function (response) {
            // Handle the successful response here
            if (response.success) {

            console.log(response);

            // Clear the input field
            document.getElementById("categoryName").value = "";

            // hide the form
            hideForm(categoryForm);
            
            // Update the #transactionForm select input options
            const transactionFormSelect = document.querySelector('#transactionForm select');
            const option = document.createElement('option');
            option.value = response.id;
            option.text = response.name;
            transactionFormSelect.add(option, 0);

            var card = document.createElement('div');
            card.className = 'catCard';
            card.dataset.categoryname = response.name;

            // Create the card's inner elements
            var categoryNameElement = document.createElement('div');
            categoryNameElement.style.fontSize = '16px';
            categoryNameElement.style.fontWeight = '400';
            categoryNameElement.textContent = response.name;

            var amountElement = document.createElement('div');
            amountElement.style.color = '#f5599a';
            amountElement.style.fontWeight = '600';
            amountElement.style.fontSize = '27px';
            amountElement.textContent = '0.00/=';

            var percentageElement = document.createElement('div');
            percentageElement.style.fontSize = '12px';
            percentageElement.textContent = '0.00%';

            var progressBarContainer = document.createElement('div');
            progressBarContainer.style.maxWidth = '150px';
            progressBarContainer.style.width = '150px';
            progressBarContainer.style.height = '4px';
            progressBarContainer.style.backgroundColor = 'white';
            progressBarContainer.style.paddingBottom = '3px';

            var progressBar = document.createElement('div');
            progressBar.style.backgroundColor = '#141c33';
            progressBar.style.height = '4px';
            progressBar.style.width = '0.00%';

            // Append the inner elements to the card
            progressBarContainer.appendChild(progressBar);
            card.appendChild(categoryNameElement);
            card.appendChild(amountElement);
            card.appendChild(percentageElement);
            card.appendChild(progressBarContainer);

            // Append the card to the categoryCards container
            var categoryCardsContainer = document.getElementById('categoryCards');
            categoryCardsContainer.insertBefore(card, categoryCardsContainer.firstChild);

            // success message display
            const successMessageElement = document.getElementById('successMessage');
            successMessageElement.textContent = 'Catégorie de dépenses créée avec succès';
            successMessageElement.style.display = 'block';
            successMessageElement.style.opacity = '1';

            // Use setTimeout to hide the message after a delay
            setTimeout(() => {
                successMessage.style.opacity = '0';
                setTimeout(() => {
                    successMessageElement.style.display = 'none';
                }, 500);
            }, 2000);


            
            } else {
                // Handle the case where an error occurred
                const errorElement = document.getElementById('categoryFormError');
                if (errorElement) {
                    errorElement.textContent = 'Les noms de catégorie doivent être uniques';
                    errorElement.style.color = "#212529";
                    errorElement.style.display = "block"; 
                }
            }
        })
        .catch(function (error) {
            // Handle any network or other errors
            const errorElement = document.getElementById('categoryFormError');
            if (errorElement) {
                errorElement.textContent = "Error: " + error.message;
                errorElement.style.color = "#212529";
                errorElement.style.display = "block"; 
            }
            
        });
    }
    });

    // Add click event listener to handle form submission for Expense transactions
    const submitTransactionButton = document.getElementById('submitTransactionForm');
    submitTransactionButton.addEventListener('click', function (e) {
        e.preventDefault(); // Prevent the default form submission

        // Collect form data manually
        const expenseCategorySelect = document.getElementById('ExpenseCategory')
        const amountInput = document.getElementById('amount');
        const dateInput = document.getElementById('date');
        const descriptionInput =  document.getElementById('description');

        const transactionFormError = document.getElementById('transactionFormError');

        const expenseCategory = expenseCategorySelect.value;
        const amount = amountInput.value.trim();
        const date = dateInput.value.trim();
        const description = descriptionInput.value.trim();

        console.log(expenseCategory, amount, date, description )

        // Validate required fields: incomeCategory, amount, and date
        if (!expenseCategory || !amount || !date) {
            transactionFormError.textContent = 'Les champs Catégorie de dépense, Montant et Date sont obligatoires.';
            transactionFormError.style.color = "#212529";
            transactionFormError.style.display = "block";
            return;
        }

        // Get the current date
        const currentDate = new Date();
        entereddate = new Date(date);
        if (entereddate > currentDate) {
            // Display an error message for a future date
            transactionFormError.textContent = 'Veuillez sélectionner une date qui n’est pas dans le futur.';
            transactionFormError.style.color = "#212529";
            transactionFormError.style.display = "block";
            return;
        }


        // Validate description length
        if (description.length > 100) {
            transactionFormError.textContent = 'La description ne doit pas dépasser 100 caractères.';
            transactionFormError.style.color = "#212529";
            transactionFormError.style.display = "block";
            return;
        }

        // Clear any previous error messages
        transactionFormError.textContent = '';
        transactionFormError.style.display = "none";

        // Create FormData object and append form fields
        const formData = new FormData();
        formData.append('expenseCategory', expenseCategory);
        formData.append('amount', amount);
        formData.append('date', date);
        formData.append('description', description);

        // Create options object for fetch request
        const requestOptions = {
            method: 'POST',
            body: formData,
            headers: {
                // Include any headers if needed (e.g., for CSRF token)
            },
        };

        // Send fetch request to the backend to create the income transaction
        fetch('/create_expense_transaction', requestOptions)
            .then((response) => {
                if (!response.ok) {
                    // Handle the error response here
                    throw new Error(`Error: ${response.status} - ${response.statusText}`);
                }
                return response.json(); // Assuming the server responds with JSON data
            })
            .then((data) => {
                if (data.error) {
                    // Handle server-side validation errors
                    transactionFormError.textContent = data.error;
                    transactionFormError.style.color = "#212529";
                    transactionFormError.style.display = "block";
                } else {

                    // Handle the success response here
                    console.log('Transaction de dépense créée avec succès :', data);

                    transactionFormError.style.display = "none";

                    // Display the success message
                    successMessage=document.getElementById('successMessage');
                    successMessage.textContent = 'Transaction de dépense saisie avec succès';
                    successMessage.style.display = 'block';
                    successMessage.style.backgroundColor = '#2f9a6a';
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

                    // Close the form
                    hideForm(transactionForm);

                    // Clear form fields
                    //incomeCategorySelect.value = '';
                    amountInput.value = '';
                    dateInput.value = '';
                    descriptionInput.value = '';

                    // Update the transaction table with the new transaction data
                    const { message, transaction_id, expense_category_name, amount, description, date } = data;
                    
                    // Get a reference to the table body
                    const tableBody = document.getElementById('transactionTableBody');

                    // Create a new row for the expense transaction
                    const row = document.createElement('tr');
                    
                    // Create cells for each data point
                    const transactionIdCell = document.createElement('td');
                    transactionIdCell.textContent = 'CF'+transaction_id.toString().padStart(3, '0')+'EXP';

                    const incomeCategoryCell = document.createElement('td');
                    incomeCategoryCell.textContent = expense_category_name;

                    const descriptionCell = document.createElement('td');
                    descriptionCell.textContent = description;

                    const dateCell = document.createElement('td');
                    dateCell.textContent = date;

                    const amountCell = document.createElement('td');
                    amountCell.textContent = amount;
                    amountCell.classList.add('income_amount_cell');

                    // Create the "Actions" cell
                    
                    const actionsCell = document.createElement('td');
                    const editLink = document.createElement('i');
                    editLink.classList.add('edit-transaction', 'fas', 'fa-edit');
                    // Add transaction data attributes
                    editLink.dataset.transactionId = transaction_id;                 
                    editLink.dataset.description = description;
                    editLink.dataset.amount = amount;
                    editLink.dataset.date = date;
                    actionsCell.appendChild(editLink);

                    const deleteLink = document.createElement('i');
                    deleteLink.classList.add('delete-transaction', 'fas', 'fa-trash-alt');
                    deleteLink.dataset.transactionId = transaction_id;
                    actionsCell.appendChild(deleteLink);

                    // Append cells to the row
                    row.appendChild(transactionIdCell);
                    row.appendChild(incomeCategoryCell);
                    row.appendChild(descriptionCell);
                    row.appendChild(dateCell);
                    row.appendChild(amountCell);
                    row.appendChild(actionsCell)

                    // Insert the row as the first child of the table body
                    tableBody.insertBefore(row, tableBody.firstChild);                     

                }
            })
            .catch((error) => {
                // Handle any errors that occurred during the fetch request
                console.error('Erreur lors de la création de la transaction de revenu :', error);
                transactionFormError.textContent = 'Une erreur s’est produite lors de la création de la transaction de revenu.';
                transactionFormError.style.color = '#FF0000';
            });
    });

});
