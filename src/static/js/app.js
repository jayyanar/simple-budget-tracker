// static/js/app.js
document.addEventListener('DOMContentLoaded', function() {
    // Initialize
    loadExpenses();
    loadBalance();
    loadSummary();
    
    // Event listeners
    document.getElementById('expense-form').addEventListener('submit', addExpense);
    document.getElementById('refresh-expenses').addEventListener('click', loadExpenses);
    
    // Set default date to today
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('date').value = today;
});

// Load all expenses
function loadExpenses() {
    fetch('/expense')
        .then(response => response.json())
        .then(data => {
            const expenseList = document.getElementById('expense-list');
            const noExpenses = document.getElementById('no-expenses');
            
            expenseList.innerHTML = '';
            
            if (data.expenses && data.expenses.length > 0) {
                noExpenses.classList.add('d-none');
                
                data.expenses.forEach(expense => {
                    const row = document.createElement('tr');
                    row.className = 'expense-row';
                    
                    // Format date
                    const date = new Date(expense.date);
                    const formattedDate = date.toLocaleDateString();
                    
                    // Format amount
                    const amount = parseFloat(expense.amount).toFixed(2);
                    
                    row.innerHTML = `
                        <td>${formattedDate}</td>
                        <td>${expense.category}</td>
                        <td>${expense.description || '-'}</td>
                        <td>$${amount}</td>
                        <td>
                            <button class="btn btn-sm btn-outline-danger btn-action" onclick="confirmDelete('${expense.id}')">
                                Delete
                            </button>
                        </td>
                    `;
                    
                    expenseList.appendChild(row);
                });
            } else {
                noExpenses.classList.remove('d-none');
            }
        })
        .catch(error => {
            console.error('Error loading expenses:', error);
            alert('Failed to load expenses. Please try again.');
        });
}

// Load balance
function loadBalance() {
    fetch('/balance')
        .then(response => response.json())
        .then(data => {
            const balanceElement = document.getElementById('total-balance');
            const balance = parseFloat(data.balance || 0).toFixed(2);
            balanceElement.textContent = `$${balance}`;
        })
        .catch(error => {
            console.error('Error loading balance:', error);
        });
}

// Load category summary
function loadSummary() {
    fetch('/summary')
        .then(response => response.json())
        .then(data => {
            updateCategorySummary(data.summary);
            updateCategoryChart(data.summary);
        })
        .catch(error => {
            console.error('Error loading summary:', error);
        });
}

// Update category summary list
function updateCategorySummary(summary) {
    const summaryElement = document.getElementById('category-summary');
    summaryElement.innerHTML = '';
    
    if (summary && Object.keys(summary).length > 0) {
        const list = document.createElement('ul');
        list.className = 'list-group';
        
        Object.entries(summary).forEach(([category, amount]) => {
            const item = document.createElement('li');
            item.className = 'list-group-item d-flex justify-content-between align-items-center';
            
            const formattedAmount = parseFloat(amount).toFixed(2);
            
            item.innerHTML = `
                ${category}
                <span class="badge bg-primary rounded-pill">$${formattedAmount}</span>
            `;
            
            list.appendChild(item);
        });
        
        summaryElement.appendChild(list);
    } else {
        summaryElement.innerHTML = '<p class="text-muted text-center">No data available</p>';
    }
}

// Update category chart
function updateCategoryChart(summary) {
    const ctx = document.getElementById('category-chart').getContext('2d');
    
    // Destroy existing chart if it exists
    if (window.categoryChart) {
        window.categoryChart.destroy();
    }
    
    if (summary && Object.keys(summary).length > 0) {
        const labels = Object.keys(summary);
        const data = Object.values(summary).map(amount => parseFloat(amount));
        
        // Generate random colors
        const colors = labels.map(() => {
            const r = Math.floor(Math.random() * 200);
            const g = Math.floor(Math.random() * 200);
            const b = Math.floor(Math.random() * 200);
            return `rgba(${r}, ${g}, ${b}, 0.7)`;
        });
        
        window.categoryChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: colors,
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                    }
                }
            }
        });
    }
}

// Add new expense
function addExpense(event) {
    event.preventDefault();
    
    const amount = document.getElementById('amount').value;
    const category = document.getElementById('category').value;
    const date = document.getElementById('date').value;
    const description = document.getElementById('description').value;
    
    const expenseData = {
        amount: amount,
        category: category,
        date: date,
        description: description
    };
    
    fetch('/expense', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(expenseData)
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => { throw new Error(err.error || 'Failed to add expense'); });
        }
        return response.json();
    })
    .then(data => {
        // Reset form
        document.getElementById('expense-form').reset();
        document.getElementById('date').value = new Date().toISOString().split('T')[0];
        
        // Reload data
        loadExpenses();
        loadBalance();
        loadSummary();
        
        alert('Expense added successfully!');
    })
    .catch(error => {
        console.error('Error adding expense:', error);
        alert(error.message || 'Failed to add expense. Please try again.');
    });
}

// Confirm delete expense
function confirmDelete(expenseId) {
    const modal = new bootstrap.Modal(document.getElementById('deleteModal'));
    modal.show();
    
    document.getElementById('confirm-delete').onclick = function() {
        deleteExpense(expenseId);
        modal.hide();
    };
}

// Delete expense
function deleteExpense(expenseId) {
    fetch(`/expense/${expenseId}`, {
        method: 'DELETE'
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => { throw new Error(err.error || 'Failed to delete expense'); });
        }
        return response.json();
    })
    .then(data => {
        // Reload data
        loadExpenses();
        loadBalance();
        loadSummary();
    })
    .catch(error => {
        console.error('Error deleting expense:', error);
        alert(error.message || 'Failed to delete expense. Please try again.');
    });
}
