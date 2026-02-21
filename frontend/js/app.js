// Configuração da API
const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
const API_URL = isLocal ? 'http://127.0.0.1:8000' : '';

// Interceptor para adicionar token JWT em todas as requisições
const originalFetch = window.fetch;
window.fetch = async (url, options = {}) => {
    const token = localStorage.getItem('access_token');

    // Garantir que headers seja um objeto
    if (!options.headers) {
        options.headers = {};
    }

    // Adicionar token se existir
    if (token) {
        options.headers['Authorization'] = `Bearer ${token}`;
    }

    try {
        const response = await originalFetch(url, options);

        // Se der erro de autenticação (401), fazer logout
        if (response.status === 401 && !url.includes('/login')) {
            console.warn("Sessão expirada ou inválida");
            if (typeof window.logout === 'function') {
                window.logout();
            }
        }

        return response;
    } catch (err) {
        throw err;
    }
};

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
let categories = [];
let isParent = false;

// DOM Elements
const balanceDisplay = document.getElementById('balanceDisplay');
const incomeDisplay = document.getElementById('incomeDisplay');
const expenseDisplay = document.getElementById('expenseDisplay');
const transactionList = document.getElementById('transactionList');
const budgetAlerts = document.getElementById('budgetAlerts');
const budgetMgmtGrid = document.getElementById('budgetMgmtGrid');
const categoryList = document.getElementById('categoryList');

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

    // Inicializar sistema de temas
    initTheme();

    // Use stored username if available
    const storedName = localStorage.getItem('user_name');
    if (storedName) {
        document.getElementById('userNameDisplay').innerText = `¡Hola, ${storedName}!`;
    }

    fetchSummary();
    fetchTransactions();
    fetchBudgets();
    fetchBudgetStatus();   // Feature #6
    fetchCategories();
    fetchProfile();
    applyRecurringTransactions(); // Feature #17 — aplica recorrentes do mês
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
        // Use new endpoint for authenticated user
        const res = await fetch(`${API_URL}/users/me`);
        if (!res.ok) throw new Error('Failed to fetch profile');
        const data = await res.json();

        // Use 'username' from User schema
        const name = data.username || "Usuario";
        document.getElementById('userNameDisplay').innerText = `¡Hola, ${name}!`;

        // Show Dependents link if user is a parent (no parent_id)
        const navDependents = document.getElementById('navDependents');
        isParent = !data.parent_id;
        if (navDependents && isParent) {
            navDependents.style.display = 'flex';
        }

        // Update transaction table header if parent
        const userHeader = document.getElementById('userTableHeader');
        if (userHeader) {
            userHeader.style.display = isParent ? 'table-cell' : 'none';
        }
    } catch (err) {
        const storedName = localStorage.getItem('user_name');
        document.getElementById('userNameDisplay').innerText = `¡Hola, ${storedName || 'Usuario'}!`;
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

// Feature #6 — Alertas de Orçamento
async function fetchBudgetStatus() {
    try {
        const res = await fetch(`${API_URL}/budgets/status/`);
        if (!res.ok) return; // Dependentes não têm status de orçamento
        const statusList = await res.json();
        renderBudgetStatusAlerts(statusList);
    } catch (err) { console.error(err); }
}

function renderBudgetStatusAlerts(statusList) {
    const container = document.getElementById('budgetAlerts');
    if (!container) return;
    container.innerHTML = '';

    if (statusList.length === 0) {
        container.innerHTML = '<p style="color: var(--text-muted)">No hay presupuestos configurados.</p>';
        return;
    }

    statusList.forEach(b => {
        const pct = Math.min(b.percentage, 100);
        const color = b.exceeded ? '#ef4444' : b.alert ? '#f59e0b' : '#10b981';
        const label = b.exceeded ? '🔴 Excedido' : b.alert ? '🟡 Atención' : '🟢 OK';
        container.innerHTML += `
            <div class="budget-item" style="margin-bottom:1rem;">
                <div style="display:flex; justify-content:space-between; font-size:0.9rem;">
                    <strong>${b.category}</strong>
                    <span style="color:${color}; font-size:0.8rem;">${label} — ${b.percentage}%</span>
                </div>
                <div class="progress-bar" style="height:8px; background:var(--border); border-radius:4px; margin:0.4rem 0;">
                    <div style="width:${pct}%; height:100%; background:${color}; border-radius:4px; transition:width 0.4s;"></div>
                </div>
                <div style="display:flex; justify-content:space-between; font-size:0.8rem; color:var(--text-muted);">
                    <span>Gastado: ${formatCurrency(b.spent)}</span>
                    <span>Límite: ${formatCurrency(b.limit_amount)}</span>
                </div>
            </div>
        `;
    });
}

// Feature #17 — Aplicar transações recorrentes do mês
async function applyRecurringTransactions() {
    try {
        const res = await fetch(`${API_URL}/transactions/apply-recurring/`, { method: 'POST' });
        if (!res.ok) return;
        const data = await res.json();
        if (data.applied > 0) {
            showToast(`🔄 ${data.applied} transacción(es) recurrente(s) aplicada(s) este mes.`, 'success');
            fetchSummary();
            fetchTransactions();
        }
    } catch (err) { console.error(err); }
}

async function fetchCategories() {
    try {
        const res = await fetch(`${API_URL}/categories/`);
        categories = await res.json();

        // Auto-populate defaults if empty (DX improvement)
        if (categories.length === 0) {
            const defaults = ['Alimentación', 'Transporte', 'Vivienda', 'Entretenimiento', 'Salud', 'Educación', 'Servicios', 'Otros'];
            for (const name of defaults) {
                await fetch(`${API_URL}/categories/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name })
                });
            }
            // Re-fetch to get IDs
            const res2 = await fetch(`${API_URL}/categories/`);
            categories = await res2.json();
        }

        renderCategoryOptions();
        renderCategoryList();
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
        budgetAlerts.innerHTML = '<p style="color: var(--text-muted)">No hay presupuestos activos.</p>';
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
                Aumentado en ${formatCurrency(b.income_boost)} por ingreso
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
                    <span>Disponible: ${formatCurrency(b.limit)}</span>
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
    return `${day}/${month}/${year}`;
}

// Helper para formatar data no estilo DD/MM/YYYY para display nos badges
function formatDateBadge(isoDate) {
    if (!isoDate) return '';
    const [year, month, day] = isoDate.split('-');
    return `${day}/${month}/${year}`;
}

function renderTransactions() {
    transactionList.innerHTML = '';
    transactions.slice().reverse().forEach(t => {
        const row = document.createElement('tr');

        // Columna de usuario (solo si es padre)
        const userCol = isParent ? `<td><span style="font-size: 0.8rem; color: var(--text-muted);">${t.user ? t.user.username : 'Yo'}</span></td>` : '';

        row.innerHTML = `
            <td>${formatDateDisplay(t.date)}</td>
            ${userCol}
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
    const currentText = document.getElementById('userNameDisplay').innerText;
    const name = currentText.replace('¡Hola, ', '').replace('!', '');
    document.getElementById('profileName').value = name;
};

window.openCategoryModal = () => {
    document.getElementById('categoryModal').style.display = 'flex';
    renderCategoryList();
};

window.deleteCategory = async (id) => {
    if (confirm('¿Eliminar esta categoría? Esto no afectará a las transacciones existentes, pero no podrás seleccionarla para nuevas.')) {
        try {
            await fetch(`${API_URL}/categories/${id}`, { method: 'DELETE' });
            fetchCategories();
        } catch (err) {
            console.error(err);
            showToast('Error al eliminar categoría', 'error');
        }
    }
};


function renderCategoryOptions() {
    const selects = [
        document.getElementById('category'),
        document.getElementById('budgetCategory'),
        document.getElementById('filterCategoria')  // Adicionar select de filtro
    ];
    selects.forEach(select => {
        if (!select) return;
        // Keep the first option (placeholder) and remove others
        while (select.options.length > 1) {
            select.remove(1);
        }

        categories.forEach(cat => {
            const option = document.createElement('option');
            option.value = cat.name; // Value is name for now as backend expects strings in some places, or ID? 
            // Wait, previous backend code for Transaction expects 'category' as string. 
            // Budget expects 'category' as string.
            // So value should be the name.
            option.textContent = cat.name;
            option.dataset.id = cat.id; // Store ID just in case
            select.appendChild(option);
        });
    });
}

function renderCategoryList() {
    const list = document.getElementById('categoryList');
    if (!list) return;
    list.innerHTML = '';

    categories.forEach(cat => {
        const li = document.createElement('li');
        li.innerHTML = `
            <span>${cat.name}</span>
            <button class="btn-delete" onclick="deleteCategory(${cat.id})" title="Eliminar categoría">
                <i data-lucide="trash-2" width="18"></i>
            </button>
        `;
        list.appendChild(li);
    });
    lucide.createIcons();
}

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
            date: document.getElementById('date').value,
            // Feature #17 — Recorrência
            is_recurring: document.getElementById('isRecurring')?.checked || false,
            recurrence_day: document.getElementById('isRecurring')?.checked
                ? parseInt(document.getElementById('recurrenceDay')?.value || 0) || null
                : null
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

    // Category Submit
    document.getElementById('categoryForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const nameInput = document.getElementById('newCategoryName');
        const name = nameInput.value.trim();
        if (!name) return;

        try {
            const res = await fetch(`${API_URL}/categories/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name })
            });

            if (!res.ok) throw new Error('Error al crear categoría');

            nameInput.value = '';
            showToast('Categoría creada', 'success');
            fetchCategories();
        } catch (error) {
            console.error(error);
            showToast('No se pudo crear (¿ya existe?)', 'error');
        }
    });
}

// Dependent Actions
window.generateInvite = async () => {
    try {
        const res = await fetch(`${API_URL}/invite`, { method: 'POST' });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Erro ao gerar convite');
        }
        const data = await res.json();

        // Link formatado para WhatsApp (Espanhol)
        const message = `¡Hola! Te invito a unirte a mi grupo familiar en Agente Financeiro para gestionar nuestros gastos juntos. Regístrate aquí: ${data.invite_link}`;
        const waLink = `https://wa.me/?text=${encodeURIComponent(message)}`;

        // Abrir em nova aba
        window.open(waLink, '_blank');

    } catch (err) {
        console.error(err);
        showToast(err.message, 'error');
    }
};

window.fetchDependents = async () => {
    const list = document.getElementById('dependentsList');
    try {
        const res = await fetch(`${API_URL}/users/dependents`);
        if (!res.ok) throw new Error('Error al obtener dependientes');
        const deps = await res.json();

        if (deps.length === 0) {
            list.innerHTML = `
                <p style="text-align:center; padding:1rem;">Ningún dependiente registrado aún.</p>
                <p style="text-align:center; color: var(--text-muted); font-size: 0.85em;">
                    Usa el botón de arriba para enviar la invitación.
                </p>
            `;
            return;
        }

        list.innerHTML = deps.map(d => `
            <div class="budget-item" style="display: flex; justify-content: space-between; align-items: center; padding: 1rem; border-bottom: 1px solid var(--border);">
                <div>
                    <div style="font-weight: 600;">${d.username}</div>
                    <div style="font-size: 0.8rem; color: var(--text-muted);">Dependiente Activo</div>
                </div>
                <i data-lucide="user-check" style="color: #10b981;"></i>
            </div>
        `).join('');
        lucide.createIcons();
    } catch (e) {
        console.error(e);
        list.innerHTML = '<p style="text-align:center; color: var(--danger);">Error al cargar la lista.</p>';
    }
};

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

    if (tabId === 'dependents') {
        fetchDependents();
    }

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

// Feature #3 — Análise por Categoria (usa endpoint de analytics)
async function updateCharts(period = null) {
    try {
        let url = `${API_URL}/analytics/categories/`;
        if (period) url += `?period=${period}`;
        const res = await fetch(url);
        if (!res.ok) throw new Error('analytics error');
        const data = await res.json();

        if (window.myChart) window.myChart.destroy();
        const ctx = document.getElementById('categoryChart').getContext('2d');
        const labels = data.expenses_by_category.map(c => c.category);
        const values = data.expenses_by_category.map(c => c.total);

        if (labels.length === 0) {
            ctx.canvas.parentElement.innerHTML = '<p style="text-align:center;color:var(--text-muted);padding:2rem;">Sin gastos en el período</p>';
            return;
        }

        window.myChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels,
                datasets: [{
                    data: values,
                    backgroundColor: ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#6366f1', '#14b8a6'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom', labels: { color: '#6b7280' } },
                    tooltip: {
                        callbacks: {
                            label: ctx => ` ${ctx.label}: ${formatCurrency(ctx.raw)} (${data.expenses_by_category[ctx.dataIndex].percentage}%)`
                        }
                    }
                }
            }
        });
    } catch (err) {
        // Fallback: usar dados locais de transactions
        if (window.myChart) window.myChart.destroy();
        const ctx = document.getElementById('categoryChart').getContext('2d');
        const cats = {};
        transactions.filter(t => t.type === 'expense').forEach(t => cats[t.category] = (cats[t.category] || 0) + t.amount);
        window.myChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(cats),
                datasets: [{ data: Object.values(cats), backgroundColor: ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#6366f1'], borderWidth: 0 }]
            },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom', labels: { color: '#6b7280' } } } }
        });
    }
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


// ============ FILTROS DE TRANSAÇÕES ============

let currentFilters = {};
let reportData = null;

window.applyFilters = async () => {
    const dataInicio = document.getElementById('filterDataInicio').value;
    const dataFim = document.getElementById('filterDataFim').value;
    const tipo = document.getElementById('filterTipo').value;
    const categoria = document.getElementById('filterCategoria').value;
    const busca = document.getElementById('filterBusca').value;

    // Construir query string
    const params = new URLSearchParams();
    if (dataInicio) params.append('data_inicio', dataInicio);
    if (dataFim) params.append('data_fim', dataFim);
    if (tipo) params.append('tipo', tipo);
    if (categoria) params.append('categoria', categoria);
    if (busca) params.append('busca', busca);

    // Salvar filtros atuais
    currentFilters = { dataInicio, dataFim, tipo, categoria, busca };

    try {
        const res = await fetch(`${API_URL}/transactions/?${params.toString()}`);
        transactions = await res.json();
        renderTransactions();
        updateFilterIndicators();
        showToast('Filtros aplicados', 'success');
    } catch (err) {
        console.error(err);
        showToast('Error al aplicar filtros', 'error');
    }
};

window.clearFilters = () => {
    document.getElementById('filterDataInicio').value = '';
    document.getElementById('filterDataFim').value = '';
    document.getElementById('filterTipo').value = '';
    document.getElementById('filterCategoria').value = '';
    document.getElementById('filterBusca').value = '';
    currentFilters = {};
    updateFilterIndicators();
    fetchTransactions();
    showToast('Filtros limpiados', 'success');
};

function updateFilterIndicators() {
    const indicators = document.getElementById('filterIndicators');
    const hasFilters = Object.values(currentFilters).some(v => v);

    if (!hasFilters) {
        indicators.style.display = 'none';
        return;
    }

    indicators.style.display = 'block';
    let html = '<div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">';

    if (currentFilters.dataInicio) html += `<span class="badge">Desde: ${formatDateBadge(currentFilters.dataInicio)}</span>`;
    if (currentFilters.dataFim) html += `<span class="badge">Hasta: ${formatDateBadge(currentFilters.dataFim)}</span>`;
    if (currentFilters.tipo) html += `<span class="badge">Tipo: ${currentFilters.tipo === 'income' ? 'Ingreso' : 'Gasto'}</span>`;
    if (currentFilters.categoria) html += `<span class="badge">Categoría: ${currentFilters.categoria}</span>`;
    if (currentFilters.busca) html += `<span class="badge">Búsqueda: "${currentFilters.busca}"</span>`;

    html += '</div>';
    indicators.innerHTML = html;
}


// ============ RELATÓRIOS ============

window.generateReport = async () => {
    const dataInicio = document.getElementById('reportDataInicio').value;
    const dataFim = document.getElementById('reportDataFim').value;
    const agrupar = document.getElementById('reportAgrupar').value;

    if (!dataInicio || !dataFim) {
        showToast('Por favor, seleccione el período', 'error');
        return;
    }

    try {
        const res = await fetch(
            `${API_URL}/transactions/report?data_inicio=${dataInicio}&data_fim=${dataFim}&agrupar_por=${agrupar}`
        );
        reportData = await res.json();
        renderReport(reportData);
        showToast('Informe generado', 'success');
    } catch (err) {
        console.error(err);
        showToast('Error al generar informe', 'error');
    }
};

function renderReport(data) {
    // Mostrar cards de estatísticas
    document.getElementById('reportStatsCards').style.display = 'grid';
    document.getElementById('reportTotalReceitas').textContent = formatCurrency(data.estatisticas.total_receitas);
    document.getElementById('reportTotalDespesas').textContent = formatCurrency(data.estatisticas.total_despesas);
    document.getElementById('reportSaldo').textContent = formatCurrency(data.estatisticas.saldo);
    document.getElementById('reportQuantidade').textContent = data.estatisticas.quantidade_transacoes;

    // Renderizar gráfico de evolução
    document.getElementById('reportChartCard').style.display = 'block';
    renderReportChart(data.evolucao_temporal);

    // Renderizar top categorias
    document.getElementById('reportTopCategories').style.display = 'grid';
    renderTopCategories(data.top_categorias_despesas, 'topCategoriasDespesas');
    renderTopCategories(data.top_categorias_receitas, 'topCategoriasReceitas');
}

let reportChart = null;

function renderReportChart(evolucao) {
    if (reportChart) reportChart.destroy();

    const ctx = document.getElementById('reportChart').getContext('2d');
    const labels = evolucao.map(e => e.periodo);
    const receitas = evolucao.map(e => e.receitas);
    const despesas = evolucao.map(e => e.despesas);

    reportChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Ingresos',
                    data: receitas,
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    tension: 0.4
                },
                {
                    label: 'Gastos',
                    data: despesas,
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'top' }
            },
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

function renderTopCategories(categorias, elementId) {
    const container = document.getElementById(elementId);
    if (!categorias || categorias.length === 0) {
        container.innerHTML = '<p style="color: var(--text-muted); text-align: center;">Sin datos</p>';
        return;
    }

    container.innerHTML = categorias.map(cat => `
        <div style="display: flex; justify-content: space-between; padding: 0.75rem; border-bottom: 1px solid var(--border);">
            <span style="font-weight: 500;">${cat.categoria}</span>
            <div style="text-align: right;">
                <div style="font-weight: 600; color: var(--primary);">${formatCurrency(cat.total)}</div>
                <div style="font-size: 0.8rem; color: var(--text-muted);">${cat.quantidade} transacciones</div>
            </div>
        </div>
    `).join('');
}


// ============ EXPORTAÇÃO CSV ============

window.exportToCSV = () => {
    if (!reportData || !reportData.transacoes) {
        showToast('Genere un informe primero', 'error');
        return;
    }

    // Criar CSV
    const headers = ['Fecha', 'Descripción', 'Categoría', 'Tipo', 'Monto'];
    const rows = reportData.transacoes.map(t => [
        t.date,
        t.description,
        t.category,
        t.type === 'income' ? 'Ingreso' : 'Gasto',
        t.amount
    ]);

    let csvContent = headers.join(',') + '\n';
    rows.forEach(row => {
        csvContent += row.map(cell => `"${cell}"`).join(',') + '\n';
    });

    // Download
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `informe_${reportData.data_inicio}_${reportData.data_fim}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    showToast('CSV exportado con éxito', 'success');
};


// ============ SISTEMA DE TEMAS ============

/**
 * Inicializa o sistema de temas lendo preferência salva ou do sistema.
 * Deve ser chamado no DOMContentLoaded.
 */
function initTheme() {
    const saved = localStorage.getItem('theme') || 'system';
    applyTheme(saved);
    updateThemeButtons(saved);
}

/**
 * Aplica o tema especificado no elemento <html>.
 * @param {'light'|'dark'|'system'} theme 
 */
function applyTheme(theme) {
    const html = document.documentElement;
    if (theme === 'dark') {
        html.setAttribute('data-theme', 'dark');
    } else if (theme === 'light') {
        html.setAttribute('data-theme', 'light');
    } else {
        // Sistema: detecta preferência do OS
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        html.setAttribute('data-theme', prefersDark ? 'dark' : 'light');
    }
}

/**
 * Atualiza os botões de tema para refletir a seleção atual.
 * @param {'light'|'dark'|'system'} theme
 */
function updateThemeButtons(theme) {
    document.querySelectorAll('.theme-option').forEach(btn => btn.classList.remove('active'));
    const activeBtn = document.getElementById(`theme-${theme}`);
    if (activeBtn) activeBtn.classList.add('active');
    lucide.createIcons(); // Reinicializa ícones caso necessário
}

/**
 * Define e persiste o tema escolhido pelo usuário.
 * @param {'light'|'dark'|'system'} theme
 */
window.setTheme = function (theme) {
    localStorage.setItem('theme', theme);
    applyTheme(theme);
    updateThemeButtons(theme);
};

// Escutar mudanças de preferência do sistema (para o modo 'system')
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
    const saved = localStorage.getItem('theme') || 'system';
    if (saved === 'system') {
        applyTheme('system');
    }
});
