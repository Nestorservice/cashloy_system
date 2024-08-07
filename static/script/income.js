/* static/scripts/income.js*/

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

    // Add click event listener to handle form submission
    categoryFormSubmitButton.addEventListener('click', function (e) {
        e.preventDefault(); // Prevent the default form submission

        // Collect form data manually
        const categoryNameInput = document.getElementById('categoryName');
        const incomeTypeInput = document.getElementById('incomeType');
        const categoryName = categoryNameInput.value.trim();
        const incomeType = incomeTypeInput.value;

        // Check for empty fields and category name length
        if (!categoryName || !incomeType || categoryName.length > 50) {
            // Display an error message to the user
            const errorElement = document.getElementById('categoryFormError');
            if (errorElement) {
                errorElement.textContent = "Le nom de la catégorie est obligatoire et doit comporter moins de 50 caractères.";
                errorElement.style.color = "#212529";
                errorElement.style.display = "block"; 
            }
            return; // Stop form submission
        }

        // Clear any previous error messages
        const errorElement = document.getElementById('categoryFormError');
        if (errorElement) {
            errorElement.textContent = "";
            errorElement.style.display = "none"; 
        }

        // Create FormData object and append form fields
        const formData = new FormData();
        formData.append('categoryName', categoryName);
        formData.append('incomeType', incomeType);

        // Create options object for fetch request
        const requestOptions = {
            method: 'POST',
            body: formData,
            headers: {
                // Include any headers if needed (e.g., for CSRF token)
            },
        };

        // Send fetch request to the backend
        fetch('/create_income_category', requestOptions)
            .then((response) => {
                if (!response.ok) {
                    // Handle the error response here
                    throw new Error(`Error: ${response.status} - ${response.statusText}`);
                }
                return response.json();
            })
            .then((data) => {
                if (data.error) {
                    // Handle server-side validation errors
                    console.error('Erreur de validation :', data.error);
                }
                
                // Close the form
                hideForm(categoryForm);

                // Update the #transactionForm select input options
                const transactionFormSelect = document.querySelector('#transactionForm select');
                const option = document.createElement('option');
                option.value = data.category_id;
                option.text = data.category_name;
                transactionFormSelect.add(option, 0);

                // Clear form fields
                categoryNameInput.value = "";
                incomeTypeInput.value = "";

                // Update #categoryCards div by appending a new .catCard div
                // Create a new card element
                var card = document.createElement('div');
                card.className = 'catCard';
                card.dataset.categoryname = data.category_name;

                // Create the card's inner elements
                var categoryNameElement = document.createElement('div');
                categoryNameElement.style.fontSize = '16px';
                categoryNameElement.style.fontWeight = '400';
                categoryNameElement.textContent = data.category_name;

                var amountElement = document.createElement('div');
                amountElement.style.color = '#bfd220';
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
                progressBar.style.backgroundColor = '#bfd220';
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

                // Display the success message
                successMessage=document.getElementById('successMessage');
                successMessage.textContent = 'Catégorie créée avec succès';
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
            .catch((error) => {
                // Handle any errors that occurred during the fetch request
                console.error('Erreur lors de l’envoi du formulaire de catégorie :', error);
                // Display an error message to the user
                const errorElement = document.getElementById('categoryFormError');
                if (errorElement) {
                    errorElement.textContent = 'Les noms de catégorie doivent être uniques';
                    errorElement.style.color = "#212529";
                    errorElement.style.display = "block"; 
                }
            });
    });


    // Add click event listener to handle form submission for income transactions
    const submitTransactionButton = document.getElementById('submitTransactionForm');
    submitTransactionButton.addEventListener('click', function (e) {
        e.preventDefault(); // Prevent the default form submission

        // Collect form data manually
        const incomeCategorySelect = document.getElementById('incomeCategory')
        const amountInput = document.getElementById('amount');
        const dateInput = document.getElementById('date');
        const descriptionInput =  document.getElementById('description');

        const transactionFormError = document.getElementById('transactionFormError');

        const incomeCategory = incomeCategorySelect.value;
        const amount = amountInput.value.trim();
        const date = dateInput.value.trim();
        const description = descriptionInput.value.trim();

        // Validate required fields: incomeCategory, amount, and date
        if (!incomeCategory || !amount || !date) {
            transactionFormError.textContent = 'Catégorie de revenu, Montant et Date sont des champs obligatoires.';
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
        formData.append('incomeCategory', incomeCategory);
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
        fetch('/create_income_transaction', requestOptions)
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
                    console.log('Transaction de revenu réalisée avec succès :', data);

                    transactionFormError.style.display = "none";

                    // Display the success message
                    successMessage=document.getElementById('successMessage');
                    successMessage.textContent = 'Transaction saisie avec succès';
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
                    //debtorSelect.value = '';
                    descriptionInput.value = '';

                    // Update the transaction table with the new transaction data
                    const { message, transaction_id, income_category_name, amount, description, date } = data;
                    
                    // Get a reference to the table body
                    const tableBody = document.getElementById('transactionTableBody');

                    // Create a new row for the income transaction
                    const row = document.createElement('tr');

                    // Create cells for each data point
                    const transactionIdCell = document.createElement('td');
                    transactionIdCell.textContent = 'CF'+transaction_id.toString().padStart(3, '0')+'INC';

                    const incomeCategoryCell = document.createElement('td');
                    incomeCategoryCell.textContent = income_category_name;

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



