
document.addEventListener('DOMContentLoaded', function () {
    const createIcon = document.getElementById('create');
    const transactionForm = document.getElementById('transactionForm');
    const closeTransactionForm = document.getElementById('closeTransactionForm');

    createIcon.addEventListener('click', () => {
        // Show the transaction form
        transactionForm.style.display = 'block';
    });

    closeTransactionForm.addEventListener('click', () => {
        // Show the transaction form
        transactionForm.style.display = 'none';
    });

    const submitTransactionForm = document.getElementById('submitTransactionForm');
    submitTransactionForm.addEventListener('click', (event) => {
        event.preventDefault();

        // Collect user-entered data
        const debtor = document.getElementById('debtor').value.trim();
        const amount = parseFloat(document.getElementById('amount').value);
        const dateTaken = document.getElementById('dateTaken').value;
        let dateDue = document.getElementById('dateDue').value;
        
        const description = document.getElementById('description').value.trim();

        // Data validation
        if (!debtor || debtor.length > 20) {
            alert('Le nom du débiteur ne doit pas être vide et ne doit pas dépasser 20 caractères.');
            return;
        }

        if (isNaN(amount) || amount < 0) {
            alert('Le montant doit être un nombre non négatif.');
            return;
        }

        // Validate date taken (make sure it's not empty)
        if (!dateTaken) {
            alert('Veuillez sélectionner une date prise.');
            return;
        }

        const currentDate = new Date();
        if (new Date(dateTaken) > currentDate) {
            alert('La date prise ne peut pas être dans le futur.');
            return;
        }

        if (dateDue && dateDue < currentDate) {
            alert('La date d’échéance ne peut pas être passée.');
            return;
        }

        if (dateDue && dateDue < dateTaken) {
            alert('La date d’échéance ne peut pas être antérieure à la date prise.');
            return;
        }

        if (description.length > 100) {
            alert('La description ne doit pas dépasser 100 caractères.');
            return;
        }

        // Prepare data for the POST request
        const data = {
            debtor: debtor,
            amount: amount,
            dateTaken: dateTaken,
            dateDue: dateDue,
            description: description,
        };

        console.log('crédit pour créer', data)

        // Send data via POST request to the /credit route
        fetch('/credit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        })
            .then(response => response.json())
            .then(data => {
                // Handle the response, e.g., display a success message
                console.log('Crédit créé :', data);

                // Hide the transaction form
                transactionForm.style.display = 'none';

                // Create a new table row for the credit record
                const newRow = document.createElement('tr');
                newRow.dataset.rowId = data.id;

                // Add data to the new table row
                newRow.innerHTML = `
                    <td>${data.debtor}</td>
                    <td>${data.date_taken}</td>
                    <td>${data.amount}</td>
                    <td>${data.amount_paid}</td>
                    <td>${data.date_due ? data.date_due : ''}</td>
                    <td>0.00%</td>
                    <td class="actions">
                        <!-- Pay button with appropriate data attributes -->
                        <i class="bi bi-credit-card-fill"
                        data-transaction-id="${data.id}"
                        data-amount-owed="${data.amount}"
                        data-amount-paid="${data.amount_paid}"
                        data-debtor-name="${data.debtor}"
                        data-date-taken="${data.date_taken}"
                        data-date-due="${data.date_due ? data.date_due : ''}"></i>
                        
                        <!-- Delete button with appropriate data attribute -->
                        <i class="fas fa-trash-alt delete-transaction"
                        data-transaction-id="${data.id}"
                        aria-hidden="true"></i> 
                    </td>
                `;

                // Insert the new table row as the first child of the table body
                const tableBody = document.getElementById('transactionTableBody');
                tableBody.insertBefore(newRow, tableBody.firstChild);

                // Display the success message
                const successMessage = document.getElementById('successMessage');
                successMessage.textContent = 'Crédit créé avec succès';
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
                console.error('Erreur lors de la création du crédit :', error);
                // Display the error message
                const errorMessage = document.getElementById('errorMessage');
                errorMessage.textContent = `Erreur lors de la création du crédit : ${error}`;
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
    });

    let creditId;
    let dateTaken;
    // Attach a click event to all payment icons in the table rows
    const paymentIcons = document.querySelectorAll('.bi-credit-card-fill');
    paymentIcons.forEach(icon => {
        icon.addEventListener('click', (event) => {
            // Prepopulate the "Debtor" input field with the debtor name from the clicked row
            const debtorName = event.target.getAttribute('data-debtor-name');
            const debtorPaymentInput = document.getElementById('debtorPayment');
            debtorPaymentInput.value = debtorName;
            creditId = event.target.getAttribute('data-transaction-id');
            dateTaken = event.target.getAttribute('data-date-taken');

            // Show the payment form
            const transactionPaymentForm = document.getElementById('transactionPaymentForm');
            transactionPaymentForm.style.display = 'block';
        });
    });

    // Attach a click event to the "Close Payment Form" icon
    const closePaymentForm = document.getElementById('closePaymentForm');
    closePaymentForm.addEventListener('click', () => {
        // Hide the payment form
        const transactionPaymentForm = document.getElementById('transactionPaymentForm');
        transactionPaymentForm.style.display = 'none';
    });

    // Attach a click event to the "Submit" button in the payment form
    const submitPaymentForm = document.getElementById('submitPaymentForm');
    submitPaymentForm.addEventListener('click', (event) => {
        event.preventDefault();

        // Collect user-entered payment data
        const debtorPayment = document.getElementById('debtorPayment').value;
        const amountToPay = parseFloat(document.getElementById('amountToPay').value);
        const datePaid = document.getElementById('datePaid').value;
 
        // Data validation for amount and date fields
        if (datePaid < dateTaken) {
            alert('La date de règlement du crédit doit être postérieure à la date indiquée.');
            return;
        }

        if (isNaN(amountToPay) || amountToPay <= 0) {
            alert('Le montant doit être un nombre positif.');
            return;
        }

        if (!datePaid) {
            alert('Veuillez sélectionner une date pour le paiement.');
            return;
        }

        // Prepare data for the POST request
        const data = {
            debtorPayment: debtorPayment,
            amountToPay: amountToPay,
            datePaid: datePaid,
            creditId: creditId
        };

        console.log('Crédit à régler :', data);

        // Send data via POST request to the /credit/settle route
        fetch('/credit/settle', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        })
            .then(response => response.json())
            .then(data => {
                // Handle the response, e.g., display a success message
                //console.log('Credit settlement successful:', data);

                // Hide the payment form
                const transactionPaymentForm = document.getElementById('transactionPaymentForm');
                transactionPaymentForm.style.display = 'none';

                // Update the table with the new amount paid and progress
                const row = document.querySelector(`[data-row-id="${creditId}"]`);
                console.log(row)
                // Update the "Amount Paid" and "Progress" columns in the table
                row.querySelector('td:nth-child(4)').textContent = data.amountPaid; // 4th column (0-based index)
                row.querySelector('td:nth-child(6)').textContent = data.progress;   // 6th column (0-based index)

                // Update the payment icon attributes
                event.target.setAttribute('data-amount-paid', data.amountPaid);
                event.target.setAttribute('data-progress', data.progress);

                // Display the success message
                const successMessage = document.getElementById('successMessage');
                successMessage.textContent = 'Règlement de crédit enregistré avec succès';
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
                console.error('Erreur de règlement du crédit :', error);
                // Display the error message
                const transactionPaymentError = document.getElementById('transactionPaymentError');
                transactionPaymentError.textContent = `Erreur de règlement du crédit : ${error}`;
                transactionPaymentError.style.display = 'block';
                transactionPaymentError.style.opacity = '1';

                // Use setTimeout to hide the message after a delay
                setTimeout(() => {
                    transactionPaymentError.style.opacity = '0';
                    setTimeout(() => {
                        transactionPaymentError.style.display = 'none';
                    }, 500);
                }, 2000);
            });
    });
});
