const API_URL = '';

// Format Currency for Display
const formatCurrency = (amount) => {
    return new Intl.NumberFormat('es-CO', {
        style: 'currency',
        currency: 'COP',
        minimumFractionDigits: 0
    }).format(amount);
};

// Format Input Field (User Typing) -> 50.000 (Integer for COP)
window.formatAmountInput = (input) => {
    let value = input.value.replace(/\D/g, '');
    // Integer only for COP, no cents by default
    value = value.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    input.value = value;
};

// Parse Formatted Input back to Float/Int
const parseAmount = (value) => {
    if (!value) return 0;
    // Remove dots only
    return parseInt(value.replace(/\./g, ''));
}

// State
let transactions = [];
let budgets = [];

// DOM Elements
const balanceDisplay = document.getElementById('balanceDisplay');
const incomeDisplay = document.getElementById('incomeDisplay');
const expenseDisplay = document.getElementById('expenseDisplay');
const transactionList = document.getElementById('transactionList');
const budgetAlerts = document.getElementById('budgetAlerts');
const budgetMgmtGrid = document.getElementById('budgetMgmtGrid');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    if (!localStorage.getItem('isLoggedIn')) {
        window.location.href = 'login.html';
        return;
    }

    // Show admin link if user is admin
    const userRole = localStorage.getItem('user_role');
    const adminLink = document.getElementById('adminLink');
    if (adminLink && userRole === 'admin') {
        adminLink.style.display = 'flex';
    }

    // Use stored username if available
    const storedName = localStorage.getItem('user_name');
    if (storedName) {
        document.getElementById('userNameDisplay').innerText = `Hola, ${storedName}`;
    }

    fetchSummary();
    fetchTransactions();
    fetchBudgets();
    fetchProfile();
    setupModals();
});

// Logout function
window.logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_role');
    localStorage.removeItem('user_name');
    localStorage.removeItem('isLoggedIn');
    window.location.href = 'login.html';
};

// Fetch Data
async function fetchProfile() {
    try {
        const res = await fetch(`${API_URL}/profile`);
        if (!res.ok) throw new Error('Failed to fetch profile');
        const data = await res.json();

        // If name exists, use it. If "Usuario" (default), try to redirect only if strictly needed (optional).
        // For now just fix the "undefined" bug.
        const name = data.name || "Usuario";
        document.getElementById('userNameDisplay').innerText = `Hola, ${name}`;
    } catch (err) {
        // Fallback
        document.getElementById('userNameDisplay').innerText = `Hola, Usuario`;
        console.error(err);
    }
}

async function fetchSummary() {
    try {
        const res = await fetch(`${API_URL}/summary`);
        const data = await res.json();
        updateDashboard(data);
    } catch (err) { console.error(err); }
}

async function fetchTransactions() {
    try {
        const res = await fetch(`${API_URL}/transactions/`);
        transactions = await res.json();
        renderTransactions();
        updateCharts();
    } catch (err) { console.error(err); }
}

async function fetchBudgets() {
    try {
        const res = await fetch(`${API_URL}/budgets/`);
        budgets = await res.json();
        renderBudgetsMgmt();
    } catch (err) { console.error(err); }
}

// Update UI
function updateDashboard(data) {
    balanceDisplay.textContent = formatCurrency(data.balance);

    // Income Card with Breakdown
    let incomeHtml = `<div style="font-size: 1.5rem; font-weight: bold;">${formatCurrency(data.income)}</div>`;

    if (data.income_breakdown && Object.keys(data.income_breakdown).length > 0) {
        let details = Object.entries(data.income_breakdown)
            .map(([cat, amount]) => `${cat}: ${formatCurrency(amount)}`)
            .join(', ');
        if (details.length > 50) details = details.substring(0, 50) + '...';
        incomeHtml += `<div style="font-size: 0.75rem; color: #10b981; margin-top: 5px;">${details}</div>`;
    }
    incomeDisplay.innerHTML = incomeHtml;

    expenseDisplay.textContent = formatCurrency(data.expenses);

    // Budget Alerts (Filter out zero budgets)
    budgetAlerts.innerHTML = '';
    const activeBudgets = data.budgets.filter(b => b.limit > 0 || b.spent > 0);

    if (activeBudgets.length === 0) {
        budgetAlerts.innerHTML = '<p style="color: var(--text-muted)">Nenhum orçamento ativo.</p>';
        return;
    }

    activeBudgets.forEach(b => {
        const percentage = Math.min(b.percentage, 100);
        let statusClass = '';
        if (b.alert) statusClass = 'warning';
        if (b.critical) statusClass = 'danger';

        // Show Income Boost Note
        let incomeNote = '';
        if (b.income_boost > 0) {
            incomeNote = `<div style="font-size: 0.75rem; color: #10b981; margin-top: 4px;">
                <i data-lucide="trending-up" style="width:12px; height:12px; display:inline;"></i> 
                Aumentado em ${formatCurrency(b.income_boost)} por renda
             </div>`;
        }

        budgetAlerts.innerHTML += `
            <div class="budget-item">
                <div style="display: flex; justify-content: space-between; font-size: 0.9rem;">
                    <strong>${b.category}</strong>
                    <span style="color: var(--text-muted)">${Math.round(b.percentage)}%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill ${statusClass}" style="width: ${percentage}%"></div>
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: var(--text-muted);">
                    <span>${formatCurrency(b.spent)}</span>
                    <span>Disponível: ${formatCurrency(b.limit)}</span>
                </div>
                ${incomeNote}
            </div>
        `;
    });
    lucide.createIcons();
}

function formatDateDisplay(dateString) {
    if (!dateString) return '';
    const [year, month, day] = dateString.split('-');
    return `${day}-${month}-${year}`;
}

function renderTransactions() {
    transactionList.innerHTML = '';
    transactions.slice().reverse().forEach(t => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${formatDateDisplay(t.date)}</td>
            <td>${t.description}</td>
            <td><span class="badge">${t.category}</span></td>
            <td class="amount ${t.type === 'income' ? 'income' : 'expense'}" style="font-size: 1rem;">
                ${t.type === 'income' ? '+' : '-'} ${formatCurrency(t.amount)}
            </td>
            <td class="btn-icon-group">
                <button class="btn-edit" onclick="openTransactionModal(${t.id})">
                    <i data-lucide="edit-2" width="16"></i>
                </button>
                <button class="btn-delete" onclick="deleteTransaction(${t.id})">
                    <i data-lucide="trash-2" width="16"></i>
                </button>
            </td>
        `;
        transactionList.appendChild(row);
    });
    lucide.createIcons();
}

function renderBudgetsMgmt() {
    budgetMgmtGrid.innerHTML = '';
    budgets.forEach(b => {
        const card = document.createElement('div');
        card.className = 'budget-mgmt-card';
        card.onclick = () => openBudgetModal(b.id);
        card.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: start;">
                 <div>
                    <h3 style="font-size: 1rem; color: var(--text-main); margin-bottom: 0.2rem;">${b.category}</h3>
                    <span style="font-size: 0.85rem; color: var(--text-muted);">Límite</span>
                 </div>
                 <i data-lucide="chevron-right" style="color: var(--text-muted);" width="20"></i>
            </div>
            <p style="font-size: 1.5rem; font-weight: 700; color: var(--primary); margin-top: 1rem;">
                ${formatCurrency(b.limit_amount)}
            </p>
        `;
        budgetMgmtGrid.appendChild(card);
    });
    lucide.createIcons();
}

// Transaction Actions
window.openTransactionModal = (id = null) => {
    document.getElementById('transactionModal').style.display = 'flex';
    const form = document.getElementById('transactionForm');
    const amountInput = document.getElementById('amount');

    if (id) {
        // Edit Mode
        const t = transactions.find(x => x.id === id);
        document.getElementById('transModalTitle').innerText = 'Editar Transacción';
        document.getElementById('transId').value = t.id;
        document.getElementById('type').value = t.type;

        // Format existing amount to input string
        let val = t.amount.toFixed(2).replace('.', ',');
        val = val.replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1.');
        amountInput.value = val;

        document.getElementById('description').value = t.description;
        document.getElementById('category').value = t.category;
        document.getElementById('date').value = t.date;
    } else {
        // New Mode
        document.getElementById('transModalTitle').innerText = 'Nueva Transacción';
        form.reset();
        document.getElementById('transId').value = '';
        document.getElementById('date').valueAsDate = new Date();
    }
};

window.deleteTransaction = async (id) => {
    if (confirm('¿Eliminar esta transacción?')) {
        await fetch(`${API_URL}/transactions/${id}`, { method: 'DELETE' });
        fetchSummary();
        fetchTransactions();
    }
};

// Budget Actions
window.openBudgetModal = (id = null) => {
    document.getElementById('budgetModal').style.display = 'flex';
    const form = document.getElementById('budgetForm');
    const btnSave = document.getElementById('btnSaveBudget');
    const btnDelete = document.getElementById('btnDeleteBudget');

    if (id) {
        // Edit Mode
        const b = budgets.find(x => x.id === id);
        document.getElementById('budgetModalTitle').innerText = 'Editar Presupuesto';
        document.getElementById('budgetId').value = b.id;
        document.getElementById('budgetCategory').value = b.category;

        // Format existing amount
        let val = b.limit_amount.toFixed(2).replace('.', ',');
        val = val.replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1.');
        document.getElementById('budgetLimit').value = val;

        btnSave.innerText = 'Alterar';
        btnDelete.style.display = 'block';
    } else {
        // New Mode
        document.getElementById('budgetModalTitle').innerText = 'Nuevo Presupuesto';
        form.reset();
        document.getElementById('budgetId').value = '';

        btnSave.innerText = 'Incluir';
        btnDelete.style.display = 'none';
        btnDelete.type = 'button'; // Ensure it's not submit
    }
};

window.deleteBudgetAction = async () => {
    const id = document.getElementById('budgetId').value;
    if (id && confirm('¿Eliminar este presupuesto?')) {
        await fetch(`${API_URL}/budgets/${id}`, { method: 'DELETE' });
        closeModal('budgetModal');
        fetchSummary();
        fetchBudgets();
    }
};

window.openProfileModal = () => {
    document.getElementById('profileModal').style.display = 'flex';
    // Load current name into input
    const currentText = document.getElementById('userNameDisplay').innerText;
    // Remove 'Hola, ' prefix
    const name = currentText.replace('Hola, ', '');
    document.getElementById('profileName').value = name;
};

// Form Handlers
function setupModals() {
    // Transaction Submit
    document.getElementById('transactionForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const id = document.getElementById('transId').value;
        const rawAmount = document.getElementById('amount').value;

        const data = {
            type: document.getElementById('type').value,
            amount: parseAmount(rawAmount),
            description: document.getElementById('description').value,
            category: document.getElementById('category').value,
            date: document.getElementById('date').value
        };

        const method = id ? 'PUT' : 'POST';
        const url = id ? `${API_URL}/transactions/${id}` : `${API_URL}/transactions/`;

        try {
            const res = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (!res.ok) {
                let errorMessage;
                const contentType = res.headers.get("content-type");
                if (contentType && contentType.indexOf("application/json") !== -1) {
                    const errorData = await res.json();
                    errorMessage = JSON.stringify(errorData.detail || errorData, null, 2);
                } else {
                    const text = await res.text();
                    errorMessage = `Server Error (${res.status}): ${text.substring(0, 100)}...`;
                }
                throw new Error(errorMessage);
            }

            closeModal('transactionModal');
            showToast('Transacción guardada con éxito', 'success');
            fetchSummary();
            fetchTransactions();
        } catch (error) {
            console.error(error);
            showToast(error.message, 'error');
        }
    });

    // Budget Submit
    document.getElementById('budgetForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const id = document.getElementById('budgetId').value;
        const rawLimit = document.getElementById('budgetLimit').value;

        const data = {
            category: document.getElementById('budgetCategory').value,
            limit_amount: parseAmount(rawLimit)
        };

        const method = id ? 'PUT' : 'POST';
        const url = id ? `${API_URL}/budgets/${id}` : `${API_URL}/budgets/`;

        await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        closeModal('budgetModal');
        fetchSummary();
        fetchBudgets();
    });
}

// Utils
// Mobile Sidebar Toggle
window.toggleSidebar = () => {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('menuOverlay');
    sidebar.classList.toggle('active');
    overlay.classList.toggle('active');
}

window.switchTab = (tabId) => {
    // Hide all views
    document.querySelectorAll('.view').forEach(el => el.style.display = 'none');
    document.getElementById(tabId).style.display = 'block';

    // Update active state in sidebar
    document.querySelectorAll('.sidebar nav a').forEach(el => el.classList.remove('active'));
    // Note: 'event' might not be available if called programmatically, but works for clicks
    if (window.event && window.event.currentTarget) {
        window.event.currentTarget.classList.add('active');
    }

    // Close sidebar if open (mobile)
    const sidebar = document.getElementById('sidebar');
    if (sidebar.classList.contains('active')) {
        toggleSidebar();
    }

    if (tabId === 'dashboard') fetchSummary();
    if (tabId === 'transactions') fetchTransactions();
    if (tabId === 'budgets') fetchBudgets();
};

window.closeModal = (id) => document.getElementById(id).style.display = 'none';
window.onclick = (e) => {
    if (e.target.classList.contains('modal')) e.target.style.display = 'none';
};

function updateCharts() {
    if (window.myChart) window.myChart.destroy();
    const ctx = document.getElementById('categoryChart').getContext('2d');
    const expenses = transactions.filter(t => t.type === 'expense');
    const categories = {};
    expenses.forEach(t => categories[t.category] = (categories[t.category] || 0) + t.amount);

    window.myChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(categories),
            datasets: [{
                data: Object.values(categories),
                backgroundColor: ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#6366f1'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom', labels: { color: '#6b7280' } }
            }
        }
    });
}

// Toast Notification System
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return; // Guard clause

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    // Icon based on type
    let icon = '';
    if (type === 'success') icon = '<i data-lucide="check-circle" style="margin-right:8px; width:18px;"></i>';
    if (type === 'error') icon = '<i data-lucide="alert-circle" style="margin-right:8px; width:18px;"></i>';

    toast.innerHTML = `${icon}<span>${message}</span>`;

    container.appendChild(toast);
    lucide.createIcons();

    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}
