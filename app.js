const API = 'https://zero-code-platform.onrender.com';

// ─── State ───
let currentUser = localStorage.getItem('erp_user') || null;

// ─── Boot ───
window.addEventListener('DOMContentLoaded', () => {
  if (currentUser) bootApp();
  else showScreen('auth-screen');
});

function showScreen(id) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById(id).classList.add('active');
}

function bootApp() {
  document.getElementById('user-label').textContent = currentUser;
  document.getElementById('user-avatar').textContent = currentUser[0].toUpperCase();
  document.getElementById('topbar-user').textContent = currentUser;
  showScreen('app-screen');
  showPage('dashboard');
}

// ─── Auth Tab ───
function showTab(t) {
  document.getElementById('login-tab').style.display = t === 'login' ? 'block' : 'none';
  document.getElementById('register-tab').style.display = t === 'register' ? 'block' : 'none';
  document.querySelectorAll('.tab-btn').forEach((b, i) => b.classList.toggle('active', (i === 0) === (t === 'login')));
}

// ─── Login ───
async function doLogin() {
  const email = document.getElementById('login-email').value.trim();
  const pass = document.getElementById('login-pass').value.trim();
  const err = document.getElementById('login-err');
  if (!email || !pass) { err.textContent = 'All fields required'; return; }
  err.textContent = '';
  try {
    const res = await fetch(`${API}/login`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email, password: pass }) });
    if (res.ok) {
      const d = await res.json();
      currentUser = d.username;
      localStorage.setItem('erp_user', currentUser);
      bootApp();
    } else { err.textContent = 'Invalid credentials'; }
  } catch { err.textContent = 'Connection error'; }
}

async function doRegister() {
  const username = document.getElementById('reg-user').value.trim();
  const email = document.getElementById('reg-email').value.trim();
  const pass = document.getElementById('reg-pass').value.trim();
  const err = document.getElementById('reg-err');
  if (!username || !email || !pass) { err.textContent = 'All fields required'; return; }
  err.textContent = '';
  try {
    const res = await fetch(`${API}/register`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ username, email, password: pass }) });
    if (res.ok) { toast('Account created! Sign in.', 'success'); showTab('login'); }
    else { const d = await res.json(); err.textContent = d.detail || 'Registration failed'; }
  } catch { err.textContent = 'Connection error'; }
}

function doLogout() {
  currentUser = null; localStorage.removeItem('erp_user');
  showScreen('auth-screen');
}

// ─── Navigation ───
function showPage(page) {
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  const active = document.querySelector(`[onclick="showPage('${page}')"]`);
  if (active) active.classList.add('active');
  const titles = { dashboard: 'Dashboard', billing: 'Billing', workers: 'Workers', attendance: 'Attendance', rental: 'Rental Management', restaurant: 'Restaurant', invoices: 'Invoices', expenses: 'Expenses', marketing: 'Marketing', hr: 'Human Resources' };
  document.getElementById('page-title').textContent = titles[page] || page;
  const content = document.getElementById('page-content');
  content.innerHTML = '<div class="loading">Loading...</div>';
  pages[page]();
}

// ─── Toast ───
function toast(msg, type = 'success') {
  const t = document.getElementById('toast');
  t.textContent = msg; t.className = `toast show ${type}`;
  setTimeout(() => t.classList.remove('show'), 3000);
}

// ─── API Helpers ───
async function api(method, path, body) {
  const opts = { method, headers: { 'Content-Type': 'application/json' } };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(`${API}${path}`, opts);
  return res.ok ? res.json() : Promise.reject(await res.json());
}
async function get(path) { const res = await fetch(`${API}${path}`); return res.json(); }
async function getUrl(url) { const res = await fetch(url); return res.json(); }

function fmt(val) { if (!val) return '—'; const d = new Date(val); return isNaN(d) ? val : d.toLocaleDateString('en-IN'); }
function fmtCur(val) { return val != null ? '₹' + Number(val).toLocaleString('en-IN') : '—'; }

function badge(status) {
  const map = { Paid: 'green', Active: 'green', Present: 'green', Occupied: 'green', Pending: 'yellow', Overdue: 'red', Absent: 'red', Vacated: 'red', Inactive: 'red', Processing: 'blue', New: 'blue' };
  const cls = map[status] || 'blue';
  return `<span class="badge badge-${cls}">${status}</span>`;
}

// ─── Pages ───
const pages = {};

// DASHBOARD
pages.dashboard = async () => {
  const c = document.getElementById('page-content');
  c.innerHTML = `
  <div class="stats-grid">
    <div class="stat-card"><div class="stat-label">Total Bills</div><div class="stat-value" id="s-bills">—</div><div class="stat-icon">🧾</div></div>
    <div class="stat-card"><div class="stat-label">Active Workers</div><div class="stat-value" id="s-workers">—</div><div class="stat-icon">👷</div></div>
    <div class="stat-card"><div class="stat-label">Open Invoices</div><div class="stat-value" id="s-invoices">—</div><div class="stat-icon">📄</div></div>
    <div class="stat-card"><div class="stat-label">Rental Rooms</div><div class="stat-value" id="s-rental">—</div><div class="stat-icon">🏠</div></div>
  </div>
  <div style="margin-bottom:24px"><h3 style="margin-bottom:16px;font-size:17px;font-weight:600">Quick Access</h3>
  <div class="modules-grid">
    ${[['🧾', 'Billing', 'Record & view bills', 'billing'], ['👷', 'Workers', 'Manage your team', 'workers'], ['📅', 'Attendance', 'Daily attendance', 'attendance'], ['🏠', 'Rental', 'Tenant management', 'rental'], ['🍴', 'Restaurant', 'Table billing', 'restaurant'], ['📄', 'Invoices', 'Generate invoices', 'invoices'], ['💸', 'Expenses', 'Track expenses', 'expenses'], ['📢', 'Marketing', 'Leads & campaigns', 'marketing'], ['👥', 'HR', 'Leave & payroll', 'hr']].map(([icon, name, desc, page]) => `
    <div class="module-card" onclick="showPage('${page}')"><div class="module-icon">${icon}</div><div class="module-name">${name}</div><div class="module-desc">${desc}</div></div>`).join('')}
  </div></div>`;

  try {
    const [bills, workers, invoices, rental] = await Promise.all([
      get(`/billing?username=${currentUser}`),
      get(`/workers?username=${currentUser}&only_active=true`),
      get(`/invoices?username=${currentUser}`),
      get(`/rental?username=${currentUser}&status=Occupied`)
    ]);
    document.getElementById('s-bills').textContent = bills.length;
    document.getElementById('s-workers').textContent = workers.length;
    document.getElementById('s-invoices').textContent = invoices.length;
    document.getElementById('s-rental').textContent = rental.length;
  } catch { }
};

// BILLING
pages.billing = async () => {
  const c = document.getElementById('page-content');
  c.innerHTML = `
  <div class="card" style="margin-bottom:24px">
    <div class="section-header"><div class="section-title">New Bill Entry</div></div>
    <div class="form-row">
      <div class="form-group"><label>Customer Name</label><input id="b-cust" placeholder="Customer"></div>
      <div class="form-group"><label>Item Name</label><input id="b-item" placeholder="Item"></div>
    </div>
    <div class="form-row">
      <div class="form-group"><label>Cost (₹)</label><input id="b-cost" type="number" placeholder="0.00"></div>
      <div class="form-group"><label>Quantity</label><input id="b-qty" type="number" placeholder="1"></div>
    </div>
    <div class="form-actions"><button class="btn-primary" onclick="saveBill()">Save Bill</button></div>
  </div>
  <div class="card">
    <div class="section-header"><div class="section-title">Billing Records</div><button class="btn-ghost" onclick="loadBills()">↻ Refresh</button></div>
    <div id="bills-table"><div class="loading">Loading...</div></div>
  </div>`;
  loadBills();
};

async function saveBill() {
  const cust = document.getElementById('b-cust').value.trim();
  const item = document.getElementById('b-item').value.trim();
  const cost = parseFloat(document.getElementById('b-cost').value);
  const qty = parseInt(document.getElementById('b-qty').value);
  if (!cust || !item || !cost) { toast('Fill all fields', 'error'); return; }
  try {
    await api('POST', '/billing', { username: currentUser, customer_name: cust, item_name: item, cost, quantity: qty || 1 });
    toast('Bill saved!', 'success');
    ['b-cust', 'b-item', 'b-cost', 'b-qty'].forEach(id => document.getElementById(id).value = '');
    loadBills();
  } catch { toast('Failed to save', 'error'); }
}

async function loadBills() {
  const el = document.getElementById('bills-table');
  if (!el) return;
  try {
    const data = await get(`/billing?username=${currentUser}`);
    if (!data.length) { el.innerHTML = '<div class="empty"><div class="empty-icon">🧾</div>No bills yet</div>'; return; }
    el.innerHTML = `<div class="table-wrap"><table><thead><tr><th>#</th><th>Customer</th><th>Item</th><th>Cost</th><th>Qty</th><th>Total</th><th>Date</th></tr></thead><tbody>
    ${data.map((b, i) => `<tr><td>${i + 1}</td><td>${b.customer_name}</td><td>${b.item_name}</td><td>${fmtCur(b.cost)}</td><td>${b.quantity}</td><td>${fmtCur(b.cost * b.quantity)}</td><td>${fmt(b.date_of_entering)}</td></tr>`).join('')}
    </tbody></table></div>`;
  } catch { el.innerHTML = '<div class="empty">Failed to load</div>'; }
}

// WORKERS
pages.workers = async () => {
  const c = document.getElementById('page-content');
  c.innerHTML = `
  <div class="page-tabs">
    <button class="page-tab active" onclick="wTab('list',this)">Worker List</button>
    <button class="page-tab" onclick="wTab('add',this)">Add Worker</button>
  </div>
  <div id="w-list">
    <div class="card">
      <div class="section-header"><div class="section-title">Current Workforce</div><button class="btn-ghost" onclick="loadWorkers()">↻ Refresh</button></div>
      <div id="workers-table"><div class="loading">Loading...</div></div>
    </div>
  </div>
  <div id="w-add" style="display:none">
    <div class="card">
      <div class="section-title" style="margin-bottom:20px">Onboard New Worker</div>
      <div class="form-row">
        <div class="form-group"><label>Full Name</label><input id="w-name" placeholder="John Doe"></div>
        <div class="form-group"><label>Email</label><input id="w-email" type="email" placeholder="john@email.com"></div>
      </div>
      <div class="form-row">
        <div class="form-group"><label>Phone</label><input id="w-phone" placeholder="+91..."></div>
        <div class="form-group"><label>Worker Type</label>
          <select id="w-type"><option>Full-Time</option><option>Part-Time</option><option>Contract</option><option>Intern</option></select>
        </div>
      </div>
      <div class="form-row">
        <div class="form-group"><label>Salary (₹/month)</label><input id="w-sal" type="number" placeholder="30000"></div>
        <div class="form-group"><label>Address</label><input id="w-addr" placeholder="City, State"></div>
      </div>
      <div class="form-actions"><button class="btn-primary" onclick="saveWorker()">Add Worker</button></div>
    </div>
  </div>`;
  loadWorkers();
};

function wTab(tab, btn) {
  document.querySelectorAll('.page-tab').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  document.getElementById('w-list').style.display = tab === 'list' ? 'block' : 'none';
  document.getElementById('w-add').style.display = tab === 'add' ? 'block' : 'none';
}

async function loadWorkers() {
  const el = document.getElementById('workers-table');
  if (!el) return;
  try {
    const data = await get(`/workers?username=${currentUser}`);
    if (!data.length) { el.innerHTML = '<div class="empty"><div class="empty-icon">👷</div>No workers yet</div>'; return; }
    el.innerHTML = `<div class="table-wrap"><table><thead><tr><th>ID</th><th>Name</th><th>Type</th><th>Email</th><th>Phone</th><th>Salary</th><th>Status</th><th>Action</th></tr></thead><tbody>
    ${data.map(w => `<tr><td>${w.worker_id}</td><td>${w.name}</td><td>${w.worker_type}</td><td>${w.email || '—'}</td><td>${w.phone_number || '—'}</td><td>${fmtCur(w.salary)}</td><td>${w.removed_date ? badge('Removed') : badge('Active')}</td><td>${!w.removed_date ? `<button class="btn-ghost" style="padding:4px 10px;font-size:12px" onclick="fireWorker(${w.worker_id})">Remove</button>` : '—'}</td></tr>`).join('')}
    </tbody></table></div>`;
  } catch { el.innerHTML = '<div class="empty">Failed to load</div>'; }
}

async function saveWorker() {
  const name = document.getElementById('w-name').value.trim();
  const email = document.getElementById('w-email').value.trim();
  const phone = document.getElementById('w-phone').value.trim();
  const worker_type = document.getElementById('w-type').value;
  const salary = parseFloat(document.getElementById('w-sal').value);
  const address = document.getElementById('w-addr').value.trim();
  if (!name || !salary) { toast('Name and salary required', 'error'); return; }
  try {
    await api('POST', '/workers', { username: currentUser, name, email, phone, address, worker_type, salary });
    toast('Worker added!', 'success');
    ['w-name', 'w-email', 'w-phone', 'w-sal', 'w-addr'].forEach(id => document.getElementById(id).value = '');
  } catch { toast('Failed to add worker', 'error'); }
}

async function fireWorker(id) {
  if (!confirm('Remove this worker?')) return;
  try {
    await api('PUT', `/workers/${id}/fire`);
    toast('Worker removed', 'success');
    loadWorkers();
  } catch { toast('Failed', 'error'); }
}

// ATTENDANCE
pages.attendance = async () => {
  const c = document.getElementById('page-content');
  c.innerHTML = `
  <div class="card" style="margin-bottom:24px">
    <div class="section-header"><div class="section-title">Mark Today's Attendance</div></div>
    <div id="att-form"><div class="loading">Loading workers...</div></div>
    <div class="form-actions" style="margin-top:16px"><button class="btn-primary" onclick="saveAttendance()">Save Attendance</button></div>
  </div>
  <div class="card">
    <div class="section-title" style="margin-bottom:16px">Attendance History</div>
    <div id="att-hist"><div class="loading">Loading...</div></div>
  </div>`;
  loadAttForm();
  loadAttHist();
};

let attWorkers = [];
async function loadAttForm() {
  const el = document.getElementById('att-form');
  if (!el) return;
  try {
    attWorkers = await get(`/workers?username=${currentUser}&only_active=true`);
    if (!attWorkers.length) { el.innerHTML = '<div class="empty">No active workers</div>'; return; }
    el.innerHTML = `<div class="table-wrap"><table><thead><tr><th>ID</th><th>Name</th><th>Type</th><th>Status</th></tr></thead><tbody>
    ${attWorkers.map(w => `<tr><td>${w.worker_id}</td><td>${w.name}</td><td>${w.worker_type}</td><td><select id="att-${w.worker_id}" style="background:var(--surface2);border:1px solid var(--border);border-radius:6px;padding:4px 8px;color:var(--text);font-family:inherit"><option>Present</option><option>Absent</option></select></td></tr>`).join('')}
    </tbody></table></div>`;
  } catch { el.innerHTML = '<div class="empty">Failed to load</div>'; }
}

async function saveAttendance() {
  const entries = attWorkers.map(w => ({ id: w.worker_id, name: w.name, type: w.worker_type, status: document.getElementById(`att-${w.worker_id}`)?.value || 'Absent' }));
  try {
    await api('POST', '/attendance', { username: currentUser, entries });
    toast('Attendance saved!', 'success');
    loadAttHist();
  } catch { toast('Failed', 'error'); }
}

async function loadAttHist() {
  const el = document.getElementById('att-hist');
  if (!el) return;
  try {
    const data = await get(`/attendance?username=${currentUser}`);
    if (!data.length) { el.innerHTML = '<div class="empty">No records</div>'; return; }
    el.innerHTML = `<div class="table-wrap"><table><thead><tr><th>Worker ID</th><th>Name</th><th>Type</th><th>Status</th><th>Date</th></tr></thead><tbody>
    ${data.map(a => `<tr><td>${a.worker_id}</td><td>${a.worker_name}</td><td>${a.worker_type}</td><td>${badge(a.status)}</td><td>${fmt(a.date)}</td></tr>`).join('')}
    </tbody></table></div>`;
  } catch { }
}

// RENTAL
pages.rental = async () => {
  const c = document.getElementById('page-content');
  c.innerHTML = `
  <div class="page-tabs">
    <button class="page-tab active" onclick="rTab('book',this)">Book Tenant</button>
    <button class="page-tab" onclick="rTab('hist',this)">History</button>
  </div>
  <div id="r-book">
    <div class="card" style="margin-bottom:24px">
      <div class="section-title" style="margin-bottom:20px">New Tenant Booking</div>
      <div class="form-row">
        <div class="form-group"><label>Tenant Name</label><input id="r-name" placeholder="Name"></div>
        <div class="form-group"><label>Phone</label><input id="r-phone" placeholder="+91..."></div>
      </div>
      <div class="form-row three">
        <div class="form-group"><label>Room Number</label><input id="r-room" placeholder="101"></div>
        <div class="form-group"><label>Monthly Rent (₹)</label><input id="r-rent" type="number" placeholder="5000"></div>
        <div class="form-group"><label>Security Deposit (₹)</label><input id="r-dep" type="number" placeholder="10000"></div>
      </div>
      <div class="form-actions"><button class="btn-primary" onclick="saveRental()">Book Room</button></div>
    </div>
    <div class="card">
      <div class="section-header"><div class="section-title">Occupied Rooms</div><button class="btn-ghost" onclick="loadOccupied()">↻</button></div>
      <div id="r-occupied"><div class="loading">Loading...</div></div>
    </div>
    <div class="card" style="margin-top:20px">
      <div class="section-title" style="margin-bottom:16px">Vacate a Room</div>
      <div class="form-row"><div class="form-group"><label>Room Number</label><input id="r-vroom" placeholder="101"></div></div>
      <div class="form-actions"><button class="btn-primary danger" onclick="vacateRoom()">Mark Vacated</button></div>
    </div>
  </div>
  <div id="r-hist" style="display:none">
    <div class="card">
      <div class="section-header"><div class="section-title">Full Rental History</div><button class="btn-ghost" onclick="loadRentHist()">↻</button></div>
      <div id="r-hist-table"><div class="loading">Loading...</div></div>
    </div>
  </div>`;
  loadOccupied();
};

function rTab(tab, btn) {
  document.querySelectorAll('.page-tab').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  document.getElementById('r-book').style.display = tab === 'book' ? 'block' : 'none';
  document.getElementById('r-hist').style.display = tab === 'hist' ? 'block' : 'none';
  if (tab === 'hist') loadRentHist();
}

async function saveRental() {
  const name = document.getElementById('r-name').value.trim();
  const room = document.getElementById('r-room').value.trim();
  const rent = parseFloat(document.getElementById('r-rent').value);
  const deposit = parseFloat(document.getElementById('r-dep').value) || 0;
  const phone = document.getElementById('r-phone').value.trim();
  if (!name || !room || !rent) { toast('Name, room and rent required', 'error'); return; }
  try {
    await api('POST', '/rental', { username: currentUser, name, room, rent, deposit, phone });
    toast('Room booked!', 'success');
    ['r-name', 'r-room', 'r-rent', 'r-dep', 'r-phone'].forEach(id => document.getElementById(id).value = '');
    loadOccupied();
  } catch { toast('Failed', 'error'); }
}

async function vacateRoom() {
  const room = document.getElementById('r-vroom').value.trim();
  if (!room) { toast('Enter room number', 'error'); return; }
  try {
    await api('POST', `/rental/vacate?room_number=${encodeURIComponent(room)}&username=${encodeURIComponent(currentUser)}`);
    toast('Room vacated!', 'success');
    document.getElementById('r-vroom').value = '';
    loadOccupied();
  } catch { toast('Room not found or already vacated', 'error'); }
}

async function loadOccupied() {
  const el = document.getElementById('r-occupied');
  if (!el) return;
  try {
    const data = await get(`/rental?username=${currentUser}&status=Occupied`);
    if (!data.length) { el.innerHTML = '<div class="empty">No occupied rooms</div>'; return; }
    el.innerHTML = `<div class="table-wrap"><table><thead><tr><th>Tenant</th><th>Room</th><th>Rent</th><th>Deposit</th><th>Phone</th><th>Status</th><th>Since</th></tr></thead><tbody>
    ${data.map(r => `<tr><td>${r.tenant_name}</td><td>${r.room_number}</td><td>${fmtCur(r.monthly_rent)}</td><td>${fmtCur(r.security_deposit)}</td><td>${r.phone || '—'}</td><td>${badge(r.status)}</td><td>${fmt(r.join_date)}</td></tr>`).join('')}
    </tbody></table></div>`;
  } catch { el.innerHTML = '<div class="empty">Failed to load</div>'; }
}

async function loadRentHist() {
  const el = document.getElementById('r-hist-table');
  if (!el) return;
  try {
    const data = await get(`/rental?username=${currentUser}`);
    if (!data.length) { el.innerHTML = '<div class="empty">No history</div>'; return; }
    el.innerHTML = `<div class="table-wrap"><table><thead><tr><th>Tenant</th><th>Room</th><th>Rent</th><th>Status</th><th>Joined</th><th>Vacated</th></tr></thead><tbody>
    ${data.map(r => `<tr><td>${r.tenant_name}</td><td>${r.room_number}</td><td>${fmtCur(r.monthly_rent)}</td><td>${badge(r.status)}</td><td>${fmt(r.join_date)}</td><td>${fmt(r.vacate_date)}</td></tr>`).join('')}
    </tbody></table></div>`;
  } catch { }
}

// RESTAURANT
pages.restaurant = async () => {
  const c = document.getElementById('page-content');
  c.innerHTML = `
  <div class="card" style="margin-bottom:24px">
    <div class="section-title" style="margin-bottom:20px">New Table Order</div>
    <div class="form-row">
      <div class="form-group"><label>Table Number</label><input id="rs-tbl" type="number" placeholder="1"></div>
      <div class="form-group"><label>Payment Mode</label><select id="rs-mode"><option>Cash</option><option>Card</option><option>Online</option></select></div>
    </div>
    <div class="form-group"><label>Items Ordered</label><textarea id="rs-items" placeholder="2x Biryani, 1x Coke..."></textarea></div>
    <div class="form-group"><label>Total Amount (₹)</label><input id="rs-amt" type="number" placeholder="0.00"></div>
    <div class="form-actions"><button class="btn-primary" onclick="saveRestSale()">Generate Bill</button></div>
  </div>
  <div class="card">
    <div class="section-header"><div class="section-title">Sales Report</div><button class="btn-ghost" onclick="loadRestSales()">↻</button></div>
    <div id="rest-table"><div class="loading">Loading...</div></div>
  </div>`;
  loadRestSales();
};

async function saveRestSale() {
  const table_no = parseInt(document.getElementById('rs-tbl').value);
  const items = document.getElementById('rs-items').value.trim();
  const amount = parseFloat(document.getElementById('rs-amt').value);
  const mode = document.getElementById('rs-mode').value;
  if (!table_no || !amount) { toast('Table and amount required', 'error'); return; }
  try {
    await api('POST', '/restaurant/sales', { username: currentUser, table_no, items, amount, mode });
    toast('Bill saved!', 'success');
    ['rs-tbl', 'rs-items', 'rs-amt'].forEach(id => document.getElementById(id).value = '');
    loadRestSales();
  } catch { toast('Failed', 'error'); }
}

async function loadRestSales() {
  const el = document.getElementById('rest-table');
  if (!el) return;
  try {
    const data = await get(`/restaurant/sales?username=${currentUser}`);
    if (!data.length) { el.innerHTML = '<div class="empty"><div class="empty-icon">🍴</div>No sales yet</div>'; return; }
    el.innerHTML = `<div class="table-wrap"><table><thead><tr><th>Table</th><th>Items</th><th>Amount</th><th>Mode</th><th>Date</th></tr></thead><tbody>
    ${data.map(s => `<tr><td>Table ${s.table_number}</td><td>${s.items_ordered}</td><td>${fmtCur(s.total_amount)}</td><td>${s.payment_mode}</td><td>${fmt(s.sale_date)}</td></tr>`).join('')}
    </tbody></table></div>`;
  } catch { }
}

// INVOICES
pages.invoices = async () => {
  const c = document.getElementById('page-content');
  c.innerHTML = `
  <div class="card" style="margin-bottom:24px">
    <div class="section-title" style="margin-bottom:20px">Create Invoice</div>
    <div class="form-row">
      <div class="form-group"><label>Customer Name</label><input id="inv-cust" placeholder="Customer"></div>
      <div class="form-group"><label>Amount (₹)</label><input id="inv-amt" type="number" placeholder="0.00"></div>
    </div>
    <div class="form-row">
      <div class="form-group"><label>Due Date</label><input id="inv-due" type="date"></div>
      <div class="form-group"><label>Status</label><select id="inv-stat"><option>Pending</option><option>Paid</option><option>Overdue</option></select></div>
    </div>
    <div class="form-actions"><button class="btn-primary" onclick="saveInvoice()">Create Invoice</button></div>
  </div>
  <div class="card">
    <div class="section-header"><div class="section-title">Invoice History</div><button class="btn-ghost" onclick="loadInvoices()">↻</button></div>
    <div id="inv-table"><div class="loading">Loading...</div></div>
  </div>`;
  loadInvoices();
};

async function saveInvoice() {
  const customer = document.getElementById('inv-cust').value.trim();
  const amount = parseFloat(document.getElementById('inv-amt').value);
  const due_date = document.getElementById('inv-due').value;
  const status = document.getElementById('inv-stat').value;
  if (!customer || !amount || !due_date) { toast('Fill all fields', 'error'); return; }
  try {
    await api('POST', '/invoices', { username: currentUser, customer, amount, due_date, status });
    toast('Invoice created!', 'success');
    ['inv-cust', 'inv-amt', 'inv-due'].forEach(id => document.getElementById(id).value = '');
    loadInvoices();
  } catch { toast('Failed', 'error'); }
}

async function loadInvoices() {
  const el = document.getElementById('inv-table');
  if (!el) return;
  try {
    const data = await get(`/invoices?username=${currentUser}`);
    if (!data.length) { el.innerHTML = '<div class="empty"><div class="empty-icon">📄</div>No invoices</div>'; return; }
    el.innerHTML = `<div class="table-wrap"><table><thead><tr><th>#</th><th>Customer</th><th>Amount</th><th>Due Date</th><th>Status</th><th>Created</th></tr></thead><tbody>
    ${data.map((inv, i) => `<tr><td>${i + 1}</td><td>${inv.customer_name}</td><td>${fmtCur(inv.amount)}</td><td>${fmt(inv.due_date)}</td><td>${badge(inv.status)}</td><td>${fmt(inv.created_date)}</td></tr>`).join('')}
    </tbody></table></div>`;
  } catch { }
}

// EXPENSES
pages.expenses = async () => {
  const c = document.getElementById('page-content');
  c.innerHTML = `
  <div class="card" style="margin-bottom:24px">
    <div class="section-title" style="margin-bottom:20px">Log Expense</div>
    <div class="form-row">
      <div class="form-group"><label>Category</label><input id="ex-cat" placeholder="e.g. Rent, Food"></div>
      <div class="form-group"><label>Amount (₹)</label><input id="ex-amt" type="number" placeholder="0.00"></div>
    </div>
    <div class="form-group"><label>Description</label><textarea id="ex-desc" placeholder="What was this expense for?"></textarea></div>
    <div class="form-actions"><button class="btn-primary" onclick="saveExpense()">Log Expense</button></div>
  </div>
  <div class="card">
    <div class="section-header"><div class="section-title">Expense History</div><button class="btn-ghost" onclick="loadExpenses()">↻</button></div>
    <div id="exp-table"><div class="loading">Loading...</div></div>
  </div>`;
  loadExpenses();
};

async function saveExpense() {
  const category = document.getElementById('ex-cat').value.trim();
  const amount = parseFloat(document.getElementById('ex-amt').value);
  const description = document.getElementById('ex-desc').value.trim();
  if (!category || !amount) { toast('Category and amount required', 'error'); return; }
  try {
    await api('POST', '/expenses', { username: currentUser, category, amount, description });
    toast('Expense logged!', 'success');
    ['ex-cat', 'ex-amt', 'ex-desc'].forEach(id => document.getElementById(id).value = '');
    loadExpenses();
  } catch { toast('Failed', 'error'); }
}

async function loadExpenses() {
  const el = document.getElementById('exp-table');
  if (!el) return;
  try {
    const data = await get(`/expenses?username=${currentUser}`);
    if (!data.length) { el.innerHTML = '<div class="empty"><div class="empty-icon">💸</div>No expenses</div>'; return; }
    el.innerHTML = `<div class="table-wrap"><table><thead><tr><th>Category</th><th>Description</th><th>Amount</th><th>Date</th></tr></thead><tbody>
    ${data.map(e => `<tr><td>${e.category}</td><td>${e.description || '—'}</td><td>${fmtCur(e.amount)}</td><td>${fmt(e.expense_date)}</td></tr>`).join('')}
    </tbody></table></div>`;
  } catch { }
}

// MARKETING
pages.marketing = async () => {
  const c = document.getElementById('page-content');
  c.innerHTML = `
  <div class="page-tabs">
    <button class="page-tab active" onclick="mTab('leads',this)">Leads</button>
    <button class="page-tab" onclick="mTab('camp',this)">Campaigns</button>
  </div>
  <div id="m-leads">
    <div class="card" style="margin-bottom:24px">
      <div class="section-title" style="margin-bottom:20px">Add Lead</div>
      <div class="form-row">
        <div class="form-group"><label>Lead Name</label><input id="l-name" placeholder="Name"></div>
        <div class="form-group"><label>Email</label><input id="l-email" type="email" placeholder="email@..."></div>
      </div>
      <div class="form-row">
        <div class="form-group"><label>Source</label><select id="l-src"><option>Web</option><option>Social</option><option>Referral</option><option>Cold Call</option></select></div>
        <div class="form-group"><label>Status</label><select id="l-stat"><option>New</option><option>Contacted</option><option>Qualified</option><option>Closed</option></select></div>
      </div>
      <div class="form-actions"><button class="btn-primary" onclick="saveLead()">Add Lead</button></div>
    </div>
    <div class="card"><div class="section-title" style="margin-bottom:16px">Leads</div><div id="leads-table"><div class="loading">Loading...</div></div></div>
  </div>
  <div id="m-camp" style="display:none">
    <div class="card" style="margin-bottom:24px">
      <div class="section-title" style="margin-bottom:20px">Launch Campaign</div>
      <div class="form-row">
        <div class="form-group"><label>Campaign Name</label><input id="c-name" placeholder="Summer Sale"></div>
        <div class="form-group"><label>Target Audience</label><input id="c-aud" placeholder="18-35 age group"></div>
      </div>
      <div class="form-row">
        <div class="form-group"><label>Budget (₹)</label><input id="c-budget" type="number" placeholder="5000"></div>
        <div class="form-group"><label>Status</label><select id="c-stat"><option>Active</option><option>Paused</option><option>Completed</option></select></div>
      </div>
      <div class="form-actions"><button class="btn-primary" onclick="saveCampaign()">Launch</button></div>
    </div>
    <div class="card"><div class="section-title" style="margin-bottom:16px">Campaigns</div><div id="camp-table"><div class="loading">Loading...</div></div></div>
  </div>`;
  loadLeads();
};

function mTab(tab, btn) {
  document.querySelectorAll('.page-tab').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  document.getElementById('m-leads').style.display = tab === 'leads' ? 'block' : 'none';
  document.getElementById('m-camp').style.display = tab === 'camp' ? 'block' : 'none';
  if (tab === 'camp') loadCampaigns();
}

async function saveLead() {
  const name = document.getElementById('l-name').value.trim();
  const email = document.getElementById('l-email').value.trim();
  const source = document.getElementById('l-src').value;
  const status = document.getElementById('l-stat').value;
  if (!name) { toast('Name required', 'error'); return; }
  try {
    await api('POST', '/leads', { username: currentUser, name, email, source, status });
    toast('Lead added!', 'success');
    ['l-name', 'l-email'].forEach(id => document.getElementById(id).value = '');
    loadLeads();
  } catch { toast('Failed', 'error'); }
}

async function loadLeads() {
  const el = document.getElementById('leads-table');
  if (!el) return;
  try {
    const data = await get(`/leads?username=${currentUser}`);
    if (!data.length) { el.innerHTML = '<div class="empty">No leads</div>'; return; }
    el.innerHTML = `<div class="table-wrap"><table><thead><tr><th>Name</th><th>Email</th><th>Source</th><th>Status</th><th>Date</th></tr></thead><tbody>
    ${data.map(l => `<tr><td>${l.lead_name}</td><td>${l.email || '—'}</td><td>${l.source}</td><td>${badge(l.status)}</td><td>${fmt(l.created_date)}</td></tr>`).join('')}
    </tbody></table></div>`;
  } catch { }
}

async function saveCampaign() {
  const name = document.getElementById('c-name').value.trim();
  const audience = document.getElementById('c-aud').value.trim();
  const budget = parseFloat(document.getElementById('c-budget').value);
  const status = document.getElementById('c-stat').value;
  if (!name) { toast('Name required', 'error'); return; }
  try {
    await api('POST', '/campaigns', { username: currentUser, name, audience, budget: budget || 0, status });
    toast('Campaign launched!', 'success');
    ['c-name', 'c-aud', 'c-budget'].forEach(id => document.getElementById(id).value = '');
    loadCampaigns();
  } catch { toast('Failed', 'error'); }
}

async function loadCampaigns() {
  const el = document.getElementById('camp-table');
  if (!el) return;
  try {
    const data = await get(`/campaigns?username=${currentUser}`);
    if (!data.length) { el.innerHTML = '<div class="empty">No campaigns</div>'; return; }
    el.innerHTML = `<div class="table-wrap"><table><thead><tr><th>Name</th><th>Audience</th><th>Budget</th><th>Status</th><th>Date</th></tr></thead><tbody>
    ${data.map(d => `<tr><td>${d.campaign_name}</td><td>${d.target_audience || '—'}</td><td>${fmtCur(d.budget)}</td><td>${badge(d.status)}</td><td>${fmt(d.start_date)}</td></tr>`).join('')}
    </tbody></table></div>`;
  } catch { }
}

// HR
pages.hr = async () => {
  const c = document.getElementById('page-content');
  c.innerHTML = `
  <div class="page-tabs">
    <button class="page-tab active" onclick="hrTab('leave',this)">Leave Requests</button>
    <button class="page-tab" onclick="hrTab('payroll',this)">Payroll</button>
  </div>
  <div id="hr-leave">
    <div class="card" style="margin-bottom:24px">
      <div class="section-title" style="margin-bottom:20px">Request Leave</div>
      <div class="form-row three">
        <div class="form-group"><label>Employee Name</label><input id="hr-ename" placeholder="Name"></div>
        <div class="form-group"><label>Leave Type</label><select id="hr-ltype"><option>Sick</option><option>Vacation</option><option>Personal</option><option>Emergency</option></select></div>
        <div class="form-group"><label>Days</label><input id="hr-days" type="number" placeholder="1" min="1"></div>
      </div>
      <div class="form-actions"><button class="btn-primary" onclick="saveLeave()">Submit Request</button></div>
    </div>
    <div class="card"><div class="section-title" style="margin-bottom:16px">Leave Requests</div><div id="leave-table"><div class="loading">Loading...</div></div></div>
  </div>
  <div id="hr-payroll" style="display:none">
    <div class="card" style="margin-bottom:24px">
      <div class="section-title" style="margin-bottom:20px">Process Payroll</div>
      <div class="form-row three">
        <div class="form-group"><label>Employee Name</label><input id="pay-name" placeholder="Name"></div>
        <div class="form-group"><label>Month</label><input id="pay-month" placeholder="March 2026"></div>
        <div class="form-group"><label>Amount (₹)</label><input id="pay-amt" type="number" placeholder="30000"></div>
      </div>
      <div class="form-actions"><button class="btn-primary" onclick="savePayroll()">Process Salary</button></div>
    </div>
    <div class="card"><div class="section-title" style="margin-bottom:16px">Payroll History</div><div id="payroll-table"><div class="loading">Loading...</div></div></div>
  </div>`;
  loadLeaves();
};

function hrTab(tab, btn) {
  document.querySelectorAll('.page-tab').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  document.getElementById('hr-leave').style.display = tab === 'leave' ? 'block' : 'none';
  document.getElementById('hr-payroll').style.display = tab === 'payroll' ? 'block' : 'none';
  if (tab === 'payroll') loadPayroll();
}

async function saveLeave() {
  const name = document.getElementById('hr-ename').value.trim();
  const l_type = document.getElementById('hr-ltype').value;
  const days = parseInt(document.getElementById('hr-days').value);
  if (!name || !days) { toast('Name and days required', 'error'); return; }
  try {
    await api('POST', '/hr/leaves', { username: currentUser, name, l_type, days });
    toast('Request submitted!', 'success');
    ['hr-ename', 'hr-days'].forEach(id => document.getElementById(id).value = '');
    loadLeaves();
  } catch { toast('Failed', 'error'); }
}

async function loadLeaves() {
  const el = document.getElementById('leave-table');
  if (!el) return;
  try {
    const data = await get(`/hr/leaves?username=${currentUser}`);
    if (!data.length) { el.innerHTML = '<div class="empty">No leave requests</div>'; return; }
    el.innerHTML = `<div class="table-wrap"><table><thead><tr><th>Employee</th><th>Type</th><th>Days</th><th>Status</th><th>Date</th></tr></thead><tbody>
    ${data.map(l => `<tr><td>${l.worker_name}</td><td>${l.leave_type}</td><td>${l.days}</td><td>${badge(l.status)}</td><td>${fmt(l.request_date)}</td></tr>`).join('')}
    </tbody></table></div>`;
  } catch { }
}

async function savePayroll() {
  const name = document.getElementById('pay-name').value.trim();
  const month = document.getElementById('pay-month').value.trim();
  const amount = parseFloat(document.getElementById('pay-amt').value);
  if (!name || !month || !amount) { toast('All fields required', 'error'); return; }
  try {
    await api('POST', '/hr/payroll', { username: currentUser, name, month, amount });
    toast('Salary processed!', 'success');
    ['pay-name', 'pay-month', 'pay-amt'].forEach(id => document.getElementById(id).value = '');
    loadPayroll();
  } catch { toast('Failed', 'error'); }
}

async function loadPayroll() {
  const el = document.getElementById('payroll-table');
  if (!el) return;
  try {
    const data = await get(`/hr/payroll?username=${currentUser}`);
    if (!data.length) { el.innerHTML = '<div class="empty">No payroll records</div>'; return; }
    el.innerHTML = `<div class="table-wrap"><table><thead><tr><th>Employee</th><th>Month</th><th>Amount</th><th>Date</th></tr></thead><tbody>
    ${data.map(p => `<tr><td>${p.worker_name}</td><td>${p.salary_month}</td><td>${fmtCur(p.amount_paid)}</td><td>${fmt(p.payment_date)}</td></tr>`).join('')}
    </tbody></table></div>`;
  } catch { }
}
